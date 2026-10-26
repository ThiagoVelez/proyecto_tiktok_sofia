from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VideoCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    video_url: str = Field(..., max_length=500)
    thumbnail_url: str = Field(..., max_length=500)
    duration_seconds: float = Field(15.0, ge=1.0, le=600.0)
    sound_id: Optional[int] = None
    hashtags: Optional[List[str]] = Field(default_factory=list)
    visibility: Optional[str] = Field("public", description="public, friends o private")
    allow_comments: Optional[bool] = True
    allow_duet: Optional[bool] = True


class SoundResponse(BaseModel):
    id: int
    title: str
    artist_name: str
    audio_url: str
    cover_url: Optional[str]
    duration_seconds: int


class AuthorSummary(BaseModel):
    id: int
    username: str
    full_name: str
    avatar_url: Optional[str]
    is_verified: bool


class VideoDetail(BaseModel):
    id: int
    title: str
    description: Optional[str]
    video_url: str
    thumbnail_url: str
    duration_seconds: float
    aspect_ratio: str
    views_count: int
    likes_count: int
    comments_count: int
    shares_count: int
    saves_count: int
    visibility: str
    audience_rating: str
    moderation_status: str
    author: AuthorSummary
    sound: Optional[SoundResponse]
    hashtags: List[str] = Field(default_factory=list)
    is_liked_by_viewer: bool = False
    is_saved_by_viewer: bool = False
    created_at: datetime


class MediaUploadResponse(BaseModel):
    file_url: str
    file_name: str
    media_type: str
    size_bytes: int


class FeedResponse(BaseModel):
    items: List[VideoDetail]
    next_cursor: Optional[int] = None
    screen_time_notice: Optional[str] = None

