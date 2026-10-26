from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    birth_date: date
    account_type: Optional[str] = Field("standard", description="standard, minor o parent")


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in_minutes: int


class UserSummary(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    birth_date: date
    role: str
    account_type: str
    is_minor: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponseData(BaseModel):
    user: UserSummary
    token: TokenData
