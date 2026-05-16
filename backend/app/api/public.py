from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.sample import Sample
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
