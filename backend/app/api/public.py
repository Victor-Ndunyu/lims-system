from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db
from app.models.sample import Sample
from app.models.location import Location
from app.schemas.sample import SampleRead

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/samples", response_model=list[SampleRead])
def get_public_samples(db: Session = Depends(get_db)):
    samples = (
        db.query(Sample)
        .filter(Sample.public_visibility.is_(True))
        .order_by(Sample.created_at.desc())
        .limit(50)
        .all()
    )
    return samples


@router.get("/samples/{sample_id}", response_model=SampleRead)
def get_public_sample(sample_id: str, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id == sample_id, Sample.public_visibility.is_(True)).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Public sample not found")
    return sample


@router.get("/stats")
def public_stats(db: Session = Depends(get_db)):
    total_samples = db.query(func.count(Sample.id)).scalar() or 0
    published_records = db.query(func.count(Sample.id)).filter(Sample.public_visibility.is_(True)).scalar() or 0
    pending_approvals = db.query(func.count(Sample.id)).filter(Sample.status == "Submitted").scalar() or 0
    total_locations = db.query(func.count(Location.id)).scalar() or 0

    records_by_status = (
        db.query(Sample.status, func.count(Sample.id))
        .group_by(Sample.status)
        .all()
    )
    status_breakdown = [{"status": s, "count": c} for s, c in records_by_status]

    return {
        "total_samples": total_samples,
        "published_records": published_records,
        "pending_approvals": pending_approvals,
        "total_locations": total_locations,
        "records_by_status": status_breakdown,
    }
