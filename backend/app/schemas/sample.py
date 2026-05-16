from datetime import datetime
from typing import Any, List, Optional
from typing_extensions import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class AttachmentCreate(BaseModel):
    file_name: str = Field(..., min_length=1)
    file_type: str = Field(..., min_length=1)
    file_url: HttpUrl


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_name: str
    file_type: str
    file_url: HttpUrl


class SampleCreate(BaseModel):
    sample_code: str = Field(..., min_length=3)
    sample_type_id: UUID
    collection_date: datetime
    collector_id: UUID
    location_id: UUID
    description: Optional[str] = None
    remarks: Optional[str] = None
    status: Literal["Draft", "Submitted"] = "Draft"
    attachments: List[AttachmentCreate] = Field(default_factory=list)


class SampleReviewRequest(BaseModel):
    decision: Literal["Approved", "Rejected", "Correction Requested"]
    comments: Optional[str] = None


class SampleVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sample_id: UUID
    version_number: int
    change_type: str
    snapshot: dict[str, Any]
    changed_by: Optional[UUID] = None
    comments: Optional[str] = None
    changed_at: datetime


class SampleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sample_code: str
    sample_type_id: UUID
    collection_date: datetime
    collector_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    status: str
    verification_status: str
    public_visibility: bool
    description: Optional[str] = None
    remarks: Optional[str] = None
    attachments: List[AttachmentRead] = Field(default_factory=list)

