import uuid

from sqlalchemy import Column, DateTime, String, Text, func

from app.db.base import Base
from app.db.types import GUID


class SampleType(Base):
    __tablename__ = "sample_types"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
