from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserWebCheckin
from app.utils.dependencies import get_current_user
from app.services.attendance_service import (
    get_attendance_status,
    check_in,
    check_out,
)
from app.schemas.attendance_schema import AttendanceStatusResponse, AttendanceSessionResponse


router = APIRouter(prefix="/api/web-checkin/staff", tags=["Staff"])


@router.get("/status", response_model=AttendanceStatusResponse)
def status(
    current_user: UserWebCheckin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_attendance_status(db, current_user.id)


@router.post("/check-in", response_model=AttendanceSessionResponse)
def staff_check_in(
    request: Request,
    current_user: UserWebCheckin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return check_in(
        db=db,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.post("/check-out", response_model=AttendanceSessionResponse)
def staff_check_out(
    request: Request,
    current_user: UserWebCheckin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return check_out(
        db=db,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )