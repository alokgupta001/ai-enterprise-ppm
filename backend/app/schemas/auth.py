from pydantic import BaseModel
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

    role: str

    organization_name: str

    industry: Optional[str] = None

    employee_count: Optional[int] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str