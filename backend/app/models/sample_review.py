import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID


REVIEW_DECISION_VALUES = ("Approved", "Rejected", "Correction Requested")


class SampleReview(Base):
    __tablename__ = "sample_reviews"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    sample_id = Column(GUID(), ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    decision = Column(Enum(*REVIEW_DECISION_VALUES, name="review_decision", native_enum=False), nullable=False, index=True)
    comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sample = relationship("Sample", lazy="selectin")
    reviewer = relationship("User", foreign_keys=[reviewer_id], lazy="selectin")
