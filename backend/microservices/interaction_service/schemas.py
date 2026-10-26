from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_comment_id: Optional[int] = None


class CommentAuthor(BaseModel):
    id: int
    username: str
    full_name: str
    avatar_url: Optional[str]
    is_verified: bool


class CommentResponse(BaseModel):
    id: int
    video_id: int
    parent_comment_id: Optional[int]
    content: str
    likes_count: int
    is_liked_by_viewer: bool = False
    is_flagged: bool
    moderation_status: str
    author: CommentAuthor
    created_at: datetime


class LikeToggleResponse(BaseModel):
    video_id: int
    is_liked: bool
    total_likes: int


class CommentLikeToggleResponse(BaseModel):
    comment_id: int
    is_liked: bool
    total_likes: int


class BookmarkToggleResponse(BaseModel):
    video_id: int
    is_saved: bool
    total_saves: int


class ShareRecordRequest(BaseModel):
    platform: str = Field("link_copy", description="whatsapp, facebook, instagram, twitter, link_copy, other")


class ShareResponse(BaseModel):
    video_id: int
    platform: str
    total_shares: int
    share_url: str

