from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AttendanceStatusResponse(BaseModel):
    is_checked_in: bool
    active_session_id: Optional[int] = None
    check_in_at_utc: Optional[datetime] = None
    display_timezone: str


class AttendanceSessionResponse(BaseModel):
    id: int
    user_id: int
    check_in_at_utc: datetime
    check_out_at_utc: Optional[datetime]
    display_timezone: str
    total_minutes: Optional[int]
    status: str

    class Config:
        from_attributes = True