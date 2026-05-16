import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True, unique=True, index=True)
    role_id = Column(GUID(), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, index=True)
    mfa_enabled = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    role = relationship("Role", backref="users", lazy="selectin")

    @property
    def role_name(self) -> str | None:
        """Get the role name from the related role."""
        return self.role.role_name if self.role else None
