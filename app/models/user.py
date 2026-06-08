from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class UserWebCheckin(Base):
    __tablename__ = "users_web_checkin"

    id = Column(BigInteger, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=True)

    password_hash = Column(String(255), nullable=False)

    role_id = Column(BigInteger, ForeignKey("roles_web_checkin.id"), nullable=False)

    status = Column(String(30), default="active", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    created_by = Column(BigInteger, ForeignKey("users_web_checkin.id"), nullable=True)

    last_login_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    role = relationship("RoleWebCheckin", back_populates="users")
    staff_profile = relationship("StaffProfileWebCheckin", back_populates="user", uselist=False)
    attendance_sessions = relationship("AttendanceSessionWebCheckin", back_populates="user")