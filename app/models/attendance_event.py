from sqlalchemy import Column, BigInteger, String, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class AttendanceEventWebCheckin(Base):
    __tablename__ = "attendance_events_web_checkin"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(BigInteger, ForeignKey("users_web_checkin.id"), nullable=False, index=True)
    attendance_session_id = Column(BigInteger, ForeignKey("attendance_sessions_web_checkin.id"), nullable=True)

    event_type = Column(String(50), nullable=False)
    event_time_utc = Column(DateTime(timezone=True), nullable=False)

    display_timezone = Column(String(100), default="America/Chicago", nullable=False)

    source = Column(String(50), default="web", nullable=False)

    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)

    metadata_json = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    attendance_session = relationship("AttendanceSessionWebCheckin", back_populates="events")