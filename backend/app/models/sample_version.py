import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID, JSONDict


class SampleVersion(Base):
    __tablename__ = "sample_versions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    sample_id = Column(GUID(), ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    change_type = Column(String(64), nullable=False, index=True)
    snapshot = Column(JSONDict(), nullable=False)
    changed_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    comments = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sample = relationship("Sample", lazy="selectin")
    user = relationship("User", foreign_keys=[changed_by], lazy="selectin")
