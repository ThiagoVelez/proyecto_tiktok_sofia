from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationItem(BaseModel):
    id: int
    user_id: int
    sender_id: Optional[int]
    type: str
    title: str
    message: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    is_read: bool
    created_at: datetime


class ParentalAlertRequest(BaseModel):
    child_user_id: int
    alert_type: str  # curfew, limit_reached, blocked_attempt
    message: str
