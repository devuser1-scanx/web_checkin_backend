from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class RoleWebCheckin(Base):
    __tablename__ = "roles_web_checkin"

    id = Column(BigInteger, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    users = relationship("UserWebCheckin", back_populates="role")