import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID


class Sample(Base):
    __tablename__ = "samples"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    sample_code = Column(String(128), nullable=False, unique=True, index=True)
    sample_type_id = Column(GUID(), ForeignKey("sample_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    collection_date = Column(DateTime(timezone=True), nullable=False, index=True)
    collector_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id = Column(GUID(), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(60), nullable=False, index=True, server_default=text("Draft"))
    verification_status = Column(String(60), nullable=False, index=True, server_default=text("Pending"))
    public_visibility = Column(Boolean, nullable=False, default=False, server_default=text("false"), index=True)
    description = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sample_type = relationship("SampleType", lazy="selectin")
    collector = relationship("User", foreign_keys=[collector_id], lazy="selectin")
    location = relationship("Location", lazy="selectin")
    attachments = relationship("Attachment", back_populates="sample", lazy="selectin")
