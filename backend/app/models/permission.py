import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, func, Table
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID


# Association table for role <-> permission
role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", GUID(), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


# User-level permission overrides (grant/deny)
class UserPermission(Base):
    __tablename__ = "user_permissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(GUID(), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)
    granted = Column(Boolean, nullable=False, default=True)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    permission_key = Column(String(128), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    roles = relationship("Role", secondary=role_permissions_table, backref="permissions", lazy="selectin")
    user_permissions = relationship("UserPermission", lazy="selectin")
