import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    sample_id = Column(GUID(), ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_url = Column(String(1024), nullable=False)
    uploaded_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sample = relationship("Sample", back_populates="attachments", lazy="selectin")
    uploader = relationship("User", foreign_keys=[uploaded_by], lazy="selectin")
