from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, ForeignKey, func

from app.database import Base


class LoginSessionWebCheckin(Base):
    __tablename__ = "login_sessions_web_checkin"

    id = Column(BigInteger, primary_key=True, index=True)

    user_id = Column(BigInteger, ForeignKey("users_web_checkin.id"), nullable=False, index=True)

    token_id = Column(String(255), nullable=True, index=True)

    login_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    logout_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)