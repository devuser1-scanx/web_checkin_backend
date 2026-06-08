from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.attendance_session import AttendanceSessionWebCheckin
from app.models.attendance_event import AttendanceEventWebCheckin


def get_active_attendance_session(db: Session, user_id: int):
    return db.query(AttendanceSessionWebCheckin).filter(
        AttendanceSessionWebCheckin.user_id == user_id,
        AttendanceSessionWebCheckin.status == "open",
        AttendanceSessionWebCheckin.check_out_at_utc.is_(None),
    ).first()


def get_attendance_status(db: Session, user_id: int):
    active_session = get_active_attendance_session(db, user_id)

    if active_session:
        return {
            "is_checked_in": True,
            "active_session_id": active_session.id,
            "check_in_at_utc": active_session.check_in_at_utc,
            "display_timezone": active_session.display_timezone,
        }

    return {
        "is_checked_in": False,
        "active_session_id": None,
        "check_in_at_utc": None,
        "display_timezone": settings.DEFAULT_TIMEZONE,
    }


def check_in(
    db: Session,
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    active_session = get_active_attendance_session(db, user_id)

    if active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already checked in",
        )

    now_utc = datetime.now(timezone.utc)

    session = AttendanceSessionWebCheckin(
        user_id=user_id,
        check_in_at_utc=now_utc,
        display_timezone=settings.DEFAULT_TIMEZONE,
        status="open",
        check_in_source="web",
        check_in_ip=ip_address,
        check_in_user_agent=user_agent,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    event = AttendanceEventWebCheckin(
        user_id=user_id,
        attendance_session_id=session.id,
        event_type="check_in",
        event_time_utc=now_utc,
        display_timezone=settings.DEFAULT_TIMEZONE,
        source="web",
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(event)
    db.commit()

    return session


def check_out(
    db: Session,
    user_id: int,
    ip_address: str = None,
    user_agent: str = None,
):
    active_session = get_active_attendance_session(db, user_id)

    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not currently checked in",
        )

    now_utc = datetime.now(timezone.utc)

    total_minutes = int(
        (now_utc - active_session.check_in_at_utc).total_seconds() // 60
    )

    active_session.check_out_at_utc = now_utc
    active_session.total_minutes = total_minutes
    active_session.status = "closed"
    active_session.check_out_source = "web"
    active_session.check_out_ip = ip_address
    active_session.check_out_user_agent = user_agent

    db.commit()
    db.refresh(active_session)

    event = AttendanceEventWebCheckin(
        user_id=user_id,
        attendance_session_id=active_session.id,
        event_type="check_out",
        event_time_utc=now_utc,
        display_timezone=settings.DEFAULT_TIMEZONE,
        source="web",
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(event)
    db.commit()

    return active_session