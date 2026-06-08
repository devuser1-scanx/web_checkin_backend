from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class StaffProfileWebCheckin(Base):
    __tablename__ = "staff_profiles_web_checkin"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(BigInteger, ForeignKey("users_web_checkin.id"), unique=True, nullable=False)

    employee_code = Column(String(100), nullable=True)
    job_title = Column(String(150), nullable=True)
    department = Column(String(150), nullable=True)

    default_timezone = Column(String(100), default="America/Chicago", nullable=False)

    joining_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("UserWebCheckin", back_populates="staff_profile")