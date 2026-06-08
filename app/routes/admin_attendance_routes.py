from typing import Optional
from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserWebCheckin
from app.models.attendance_session import AttendanceSessionWebCheckin
from app.utils.dependencies import require_admin


router = APIRouter(prefix="/api/web-checkin/admin/attendance", tags=["Admin Attendance"])


@router.get("")
def list_attendance(
    staff_user_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    query = db.query(AttendanceSessionWebCheckin)

    if staff_user_id:
        query = query.filter(AttendanceSessionWebCheckin.user_id == staff_user_id)

    if status:
        query = query.filter(AttendanceSessionWebCheckin.status == status)

    if start_date:
        start_dt = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc)
        query = query.filter(AttendanceSessionWebCheckin.check_in_at_utc >= start_dt)

    if end_date:
        end_dt = datetime.combine(end_date, time.max).replace(tzinfo=timezone.utc)
        query = query.filter(AttendanceSessionWebCheckin.check_in_at_utc <= end_dt)

    records = query.order_by(AttendanceSessionWebCheckin.check_in_at_utc.desc()).all()

    result = []

    for record in records:
        user = db.query(UserWebCheckin).filter(UserWebCheckin.id == record.user_id).first()

        result.append({
            "id": record.id,
            "user_id": record.user_id,
            "staff_name": user.full_name if user else None,
            "username": user.username if user else None,
            "check_in_at_utc": record.check_in_at_utc,
            "check_out_at_utc": record.check_out_at_utc,
            "display_timezone": record.display_timezone,
            "total_minutes": record.total_minutes,
            "total_hours": round(record.total_minutes / 60, 2) if record.total_minutes else None,
            "status": record.status,
        })

    return result


@router.get("/currently-checked-in")
def currently_checked_in(
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    records = db.query(AttendanceSessionWebCheckin).filter(
        AttendanceSessionWebCheckin.status == "open",
        AttendanceSessionWebCheckin.check_out_at_utc.is_(None),
    ).all()

    result = []

    for record in records:
        user = db.query(UserWebCheckin).filter(UserWebCheckin.id == record.user_id).first()

        result.append({
            "session_id": record.id,
            "user_id": record.user_id,
            "staff_name": user.full_name if user else None,
            "username": user.username if user else None,
            "check_in_at_utc": record.check_in_at_utc,
            "display_timezone": record.display_timezone,
        })

    return result


@router.get("/summary")
def attendance_summary(
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    total_sessions = db.query(AttendanceSessionWebCheckin).count()

    open_sessions = db.query(AttendanceSessionWebCheckin).filter(
        AttendanceSessionWebCheckin.status == "open"
    ).count()

    closed_sessions = db.query(AttendanceSessionWebCheckin).filter(
        AttendanceSessionWebCheckin.status == "closed"
    ).count()

    return {
        "total_sessions": total_sessions,
        "currently_checked_in": open_sessions,
        "closed_sessions": closed_sessions,
    }