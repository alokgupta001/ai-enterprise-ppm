from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.enums import UserRole

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^\S+@\S+\.\S+$")
    password: str = Field(..., min_length=8)
    role: UserRole
    organization_name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    employee_count: Optional[int] = Field(None, ge=1)

    model_config = {
        "extra": "forbid"
    }

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^\S+@\S+\.\S+$")
    password: str = Field(..., min_length=8)

    model_config = {
        "extra": "forbid"
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    model_config = {
        "extra": "forbid"
    }

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    organization_id: UUID

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
