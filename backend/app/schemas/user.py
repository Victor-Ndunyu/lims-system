from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    role_name: Optional[str] = None
    is_active: bool


class UserCreate(BaseModel):
    full_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    role_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role_name: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    permission_key: str
    description: Optional[str] = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    role_name: str
    description: Optional[str] = None
    permissions: Optional[list[PermissionRead]] = None

