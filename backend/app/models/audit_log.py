import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID, JSONDict


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(128), nullable=False, index=True)
    record_id = Column(GUID(), nullable=False, index=True)
    action = Column(String(64), nullable=False, index=True)
    old_values = Column(JSONDict(), nullable=True)
    new_values = Column(JSONDict(), nullable=True)
    performed_by = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    performed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(64), nullable=True)

    user = relationship("User", foreign_keys=[performed_by], lazy="selectin")
