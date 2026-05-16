from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.audit import log_audit, make_sample_snapshot, record_sample_version
from app.core.deps import get_db, require_roles
from app.models.attachment import Attachment
from app.models.location import Location
from app.models.sample import Sample
from app.models.sample_review import SampleReview
from app.models.sample_type import SampleType
from app.models.sample_version import SampleVersion
from app.models.user import User
from app.schemas.sample import SampleCreate, SampleRead, SampleReviewRequest, SampleVersionRead

router = APIRouter(prefix="/staff", tags=["staff"])
LOCKED_SAMPLE_STATUSES = {"Approved", "Rejected", "Archived"}


def get_request_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else None


def validate_sample_payload(db: Session, sample_in: SampleCreate, sample_id: str | None = None) -> str:
    sample_code = sample_in.sample_code.strip()
    if not sample_code:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Sample code is required")

    duplicate_query = db.query(Sample).filter(Sample.sample_code == sample_code)
    if sample_id is not None:
        duplicate_query = duplicate_query.filter(Sample.id != sample_id)
    if duplicate_query.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sample code already exists")

    if not db.query(SampleType).filter(SampleType.id == sample_in.sample_type_id).first():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid sample type")
    if not db.query(Location).filter(Location.id == sample_in.location_id).first():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid location")
    if not db.query(User).filter(User.id == sample_in.collector_id, User.is_active.is_(True)).first():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid collector")

    return sample_code


@router.get("/samples", response_model=list[SampleRead], dependencies=[Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))])
def list_samples(
    status: Optional[str] = Query(None, description="Filter by sample status"),
    db: Session = Depends(get_db),
):
    query = db.query(Sample)
    if status:
        query = query.filter(Sample.status == status)
    return query.order_by(Sample.updated_at.desc()).limit(200).all()


@router.get("/samples/{sample_id}", response_model=SampleRead, dependencies=[Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))])
def get_sample(sample_id: str, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found")
    return sample


@router.post("/samples", response_model=SampleRead, dependencies=[Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))])
def create_sample(sample_in: SampleCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))):
    sample_code = validate_sample_payload(db, sample_in)
    sample = Sample(
        sample_code=sample_code,
        sample_type_id=sample_in.sample_type_id,
        collection_date=sample_in.collection_date,
        collector_id=sample_in.collector_id,
        location_id=sample_in.location_id,
        description=sample_in.description,
        remarks=sample_in.remarks,
        status=sample_in.status,
        verification_status="Pending" if sample_in.status == "Submitted" else "Draft",
        public_visibility=False,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)

    for attachment_data in sample_in.attachments:
        db.add(
            Attachment(
                sample_id=sample.id,
                file_name=attachment_data.file_name,
                file_type=attachment_data.file_type,
                file_url=str(attachment_data.file_url),
            )
        )
    db.commit()
    db.refresh(sample)

    version = record_sample_version(
        db=db,
        sample=sample,
        change_type="create",
        changed_by=str(current_user.id),
        comments="Initial sample creation",
    )

    log_audit(
        db=db,
        table_name="samples",
        record_id=str(sample.id),
        action="create",
        old_values=None,
        new_values=version.snapshot,
        performed_by=str(current_user.id),
        ip_address=get_request_ip(request),
    )
    return sample


@router.put("/samples/{sample_id}", response_model=SampleRead, dependencies=[Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))])
def update_sample(sample_id: str, sample_in: SampleCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))):
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found")
    if sample.status in LOCKED_SAMPLE_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{sample.status} records cannot be edited")
    sample_code = validate_sample_payload(db, sample_in, sample_id=sample_id)

    before_snapshot = make_sample_snapshot(sample)
    starting_status = sample.status

    sample.sample_code = sample_code
    sample.sample_type_id = sample_in.sample_type_id
    sample.collection_date = sample_in.collection_date
    sample.collector_id = sample_in.collector_id
    sample.location_id = sample_in.location_id
    sample.description = sample_in.description
    sample.remarks = sample_in.remarks
    sample.status = sample_in.status
    sample.verification_status = "Pending" if sample_in.status == "Submitted" else "Draft"
    sample.public_visibility = False
    db.commit()
    db.refresh(sample)

    for attachment_data in sample_in.attachments:
        db.add(
            Attachment(
                sample_id=sample.id,
                file_name=attachment_data.file_name,
                file_type=attachment_data.file_type,
                file_url=str(attachment_data.file_url),
            )
        )
    db.commit()
    db.refresh(sample)

    after_snapshot = make_sample_snapshot(sample)
    if before_snapshot != after_snapshot:
        action = "archive" if sample.status == "Archived" and starting_status != "Archived" else "status_update" if sample.status != starting_status else "update"

        record_sample_version(
            db=db,
            sample=sample,
            change_type=action,
            changed_by=str(current_user.id),
            comments="Sample updated",
        )

        log_audit(
            db=db,
            table_name="samples",
            record_id=str(sample.id),
            action=action,
            old_values=before_snapshot,
            new_values=after_snapshot,
            performed_by=str(current_user.id),
            ip_address=get_request_ip(request),
        )

    return sample


@router.post("/samples/{sample_id}/review", response_model=SampleRead)
def review_sample(
    sample_id: str,
    review_in: SampleReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("reviewer", "admin")),
):
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found")
    if sample.status not in {"Submitted", "Correction Requested"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted or correction requested samples can be reviewed",
        )

    before_snapshot = make_sample_snapshot(sample)

    if review_in.decision == "Approved":
        sample.status = "Approved"
        sample.verification_status = "Approved"
        sample.public_visibility = True
    elif review_in.decision == "Rejected":
        sample.status = "Rejected"
        sample.verification_status = "Rejected"
        sample.public_visibility = False
    else:
        sample.status = "Correction Requested"
        sample.verification_status = "Pending"
        sample.public_visibility = False

    review = SampleReview(
        sample_id=sample.id,
        reviewer_id=current_user.id,
        decision=review_in.decision,
        comments=review_in.comments,
    )
    db.add(review)
    db.commit()
    db.refresh(sample)

    after_snapshot = make_sample_snapshot(sample)
    record_sample_version(
        db=db,
        sample=sample,
        change_type="review_decision",
        changed_by=str(current_user.id),
        comments=review_in.comments,
    )

    log_audit(
        db=db,
        table_name="samples",
        record_id=str(sample.id),
        action="review_decision",
        old_values=before_snapshot,
        new_values=after_snapshot,
        performed_by=str(current_user.id),
        ip_address=get_request_ip(request),
    )

    return sample


@router.get("/samples/{sample_id}/versions", response_model=list[SampleVersionRead], dependencies=[Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))])
def get_sample_versions(sample_id: str, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found")
    versions = (
        db.query(SampleVersion)
        .filter(SampleVersion.sample_id == sample_id)
        .order_by(SampleVersion.version_number.desc())
        .all()
    )
    return versions


@router.get("/lookups", dependencies=[Depends(require_roles("field_officer", "analyst", "reviewer", "admin"))])
def get_staff_lookups(db: Session = Depends(get_db)):
    sample_types = db.query(SampleType).order_by(SampleType.name).all()
    locations = db.query(Location).order_by(Location.country, Location.county, Location.subcounty, Location.site_name).all()
    collectors = db.query(User).filter(User.is_active.is_(True)).order_by(User.full_name).all()
    return {
        "sample_types": sample_types,
        "locations": locations,
        "collectors": collectors,
    }
