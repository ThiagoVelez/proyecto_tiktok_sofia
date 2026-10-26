from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime, time


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=250)
    avatar_url: Optional[str] = None
    is_private: Optional[bool] = None


class UserProfileView(BaseModel):
    id: int
    username: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    is_private: bool
    followers_count: int = 0
    following_count: int = 0
    videos_count: int = 0
    likes_count: int = 0
    is_following: bool = False
    created_at: datetime


class SetParentalPinRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$", description="Código PIN numérico de 4 o 6 dígitos")


class VerifyParentalPinRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$")


class ParentalSettingsUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    daily_screen_time_limit_minutes: Optional[int] = Field(None, ge=15, le=480)
    curfew_start_time: Optional[time] = None
    curfew_end_time: Optional[time] = None
    restricted_mode: Optional[bool] = None
    block_direct_messages: Optional[bool] = None
    filter_mature_comments: Optional[bool] = None
    allow_search: Optional[bool] = None


class ParentalStatusResponse(BaseModel):
    is_enabled: bool
    has_pin_configured: bool
    daily_screen_time_limit_minutes: int
    curfew_start_time: Optional[str]
    curfew_end_time: Optional[str]
    restricted_mode: bool
    block_direct_messages: bool
    filter_mature_comments: bool
    allow_search: bool


class PairChildRequest(BaseModel):
    child_username: str = Field(..., description="Nombre de usuario del menor a vincular")


class ParentChildLinkResponse(BaseModel):
    link_id: int
    parent_id: int
    child_id: int
    child_username: str
    child_full_name: str
    status: str
    created_at: datetime

