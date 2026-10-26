from pydantic import BaseModel, Field
from typing import List, Optional
from backend.microservices.video_service.schemas import VideoDetail, SoundResponse


class HashtagSummary(BaseModel):
    id: int
    tag: str
    videos_count: int
    views_count: int


class UserSearchItem(BaseModel):
    id: int
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    is_verified: bool = False
    followers_count: int = 0


class SearchResultResponse(BaseModel):
    query: str
    search_type: str
    videos: List[VideoDetail] = Field(default_factory=list)
    users: List[UserSearchItem] = Field(default_factory=list)
    hashtags: List[HashtagSummary] = Field(default_factory=list)
    sounds: List[SoundResponse] = Field(default_factory=list)
