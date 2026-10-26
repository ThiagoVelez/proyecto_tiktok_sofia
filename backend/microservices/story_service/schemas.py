"""
Esquemas Pydantic para el Microservicio de Historias (Stories)
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class StoryAuthorSummary(BaseModel):
    id: int
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    is_verified: bool = False

    class Config:
        from_attributes = True


class StoryDetail(BaseModel):
    id: int
    user_id: int
    media_url: str
    media_type: str  # 'video' | 'image'
    caption: Optional[str] = None
    duration_seconds: float = 5.0
    audience_rating: str
    moderation_status: str
    views_count: int
    expires_at: datetime
    created_at: datetime
    is_expired: bool = False
    is_viewed_by_viewer: bool = False
    author: StoryAuthorSummary

    class Config:
        from_attributes = True


class StoryCreateRequest(BaseModel):
    media_url: str = Field(..., max_length=500, description="URL del archivo multimedia de la historia")
    media_type: str = Field("video", description="'video' o 'image'")
    caption: Optional[str] = Field(None, max_length=300, description="Texto de la historia")
    duration_seconds: Optional[float] = Field(5.0, ge=1.0, le=60.0, description="Duración en segundos")


class UserStoriesGroup(BaseModel):
    user_id: int
    author: StoryAuthorSummary
    stories_count: int
    has_unseen: bool
    latest_story_at: datetime
    stories: List[StoryDetail]


class StoryFeedResponse(BaseModel):
    total_authors: int
    tray: List[UserStoriesGroup]


class StoryViewerItem(BaseModel):
    viewer_id: int
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    viewed_at: datetime


class StoryViewersResponse(BaseModel):
    story_id: int
    views_count: int
    viewers: List[StoryViewerItem]
