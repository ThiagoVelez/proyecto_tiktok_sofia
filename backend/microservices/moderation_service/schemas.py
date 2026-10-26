from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReportCreateRequest(BaseModel):
    target_type: str = Field(..., description="video, comment o user")
    target_id: int
    reason_category: str = Field(..., description="inappropriate_for_minors, violence_graphic, hate_speech, harassment_bullying, sexual_content, spam_scam, self_harm, other")
    details: Optional[str] = Field(None, max_length=1000)


class ReportResponse(BaseModel):
    id: int
    reporter_user_id: int
    target_type: str
    target_id: int
    reason_category: str
    details: Optional[str]
    status: str
    created_at: datetime


class ModActionRequest(BaseModel):
    action: str = Field(..., description="approve, hide_content, ban_content, dismiss")
    moderator_notes: Optional[str] = None


class ModerationAuditResponse(BaseModel):
    id: int
    target_type: str
    target_id: Optional[int]
    rule_triggered: str
    severity_level: str
    action_applied: str
    reason: str
    evaluated_text_snippet: Optional[str]
    created_at: datetime
