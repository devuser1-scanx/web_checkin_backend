from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class AttendanceSessionWebCheckin(Base):
    __tablename__ = "attendance_sessions_web_checkin"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(BigInteger, ForeignKey("users_web_checkin.id"), nullable=False, index=True)

    check_in_at_utc = Column(DateTime(timezone=True), nullable=False)
    check_out_at_utc = Column(DateTime(timezone=True), nullable=True)

    display_timezone = Column(String(100), default="America/Chicago", nullable=False)

    total_minutes = Column(Integer, nullable=True)

    status = Column(String(30), default="open", nullable=False)

    check_in_source = Column(String(50), default="web", nullable=False)
    check_out_source = Column(String(50), nullable=True)

    check_in_ip = Column(String(50), nullable=True)
    check_out_ip = Column(String(50), nullable=True)

    check_in_user_agent = Column(Text, nullable=True)
    check_out_user_agent = Column(Text, nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("UserWebCheckin", back_populates="attendance_sessions")
    events = relationship("AttendanceEventWebCheckin", back_populates="attendance_session")