import uuid

from sqlalchemy import Column, DateTime, Float, String, func

from app.db.base import Base
from app.db.types import GUID


class Location(Base):
    __tablename__ = "locations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    country = Column(String(128), nullable=False, index=True)
    county = Column(String(128), nullable=True, index=True)
    subcounty = Column(String(128), nullable=True, index=True)
    site_name = Column(String(255), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
