from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def make_sample_snapshot(sample: object) -> dict[str, Any]:
    return {
        "id": str(sample.id),
        "sample_code": sample.sample_code,
        "sample_type_id": str(sample.sample_type_id),
        "collection_date": sample.collection_date.isoformat() if sample.collection_date else None,
        "collector_id": str(sample.collector_id) if sample.collector_id else None,
        "location_id": str(sample.location_id) if sample.location_id else None,
        "status": sample.status,
        "verification_status": sample.verification_status,
        "public_visibility": sample.public_visibility,
        "description": sample.description,
        "remarks": sample.remarks,
        "created_at": sample.created_at.isoformat() if sample.created_at else None,
        "updated_at": sample.updated_at.isoformat() if sample.updated_at else None,
        "attachments": [
            {
                "id": str(attachment.id),
                "file_name": attachment.file_name,
                "file_type": attachment.file_type,
                "file_url": attachment.file_url,
                "uploaded_by": str(attachment.uploaded_by) if attachment.uploaded_by else None,
                "uploaded_at": attachment.uploaded_at.isoformat() if attachment.uploaded_at else None,
            }
            for attachment in getattr(sample, "attachments", [])
        ],
    }


def record_sample_version(
    db: Session,
    sample: object,
    change_type: str,
    changed_by: str | None = None,
    comments: str | None = None,
):
    from app.models.sample_version import SampleVersion

    latest_version = (
        db.query(SampleVersion)
        .filter(SampleVersion.sample_id == sample.id)
        .order_by(SampleVersion.version_number.desc())
        .first()
    )
    next_version = (latest_version.version_number if latest_version else 0) + 1
    version = SampleVersion(
        sample_id=sample.id,
        version_number=next_version,
        change_type=change_type,
        snapshot=make_sample_snapshot(sample),
        changed_by=changed_by,
        comments=comments,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def log_audit(
    db: Session,
    table_name: str,
    record_id: str,
    action: str,
    old_values: Any | None = None,
    new_values: Any | None = None,
    performed_by: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    log = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        old_values=old_values,
        new_values=new_values,
        performed_by=performed_by,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
