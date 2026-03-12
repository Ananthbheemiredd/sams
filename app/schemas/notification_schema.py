from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


# ======================================================
# BASE
# ======================================================

class NotificationBase(BaseModel):
    title: Optional[str] = None
    message: str
    module: str
    data: Optional[Dict[str, Any]] = None


# ======================================================
# RESPONSE
# ======================================================

class NotificationOut(NotificationBase):
    notification_id: int

    role: str
    reference_id: Optional[int] = None

    priority: str
    notification_type: str

    # Delivery
    in_app_sent: bool
    email_sent: bool
    sms_sent: bool
    push_sent: bool

    # Status
    is_read: bool
    is_archived: bool

    # Scheduling
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    created_at: datetime

    class Config:
        from_attributes = True
