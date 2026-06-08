from sqlalchemy import Column, BigInteger, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class AuditLogWebCheckin(Base):
    __tablename__ = "audit_logs_web_checkin"

    id = Column(BigInteger, primary_key=True, index=True)

    actor_user_id = Column(BigInteger, nullable=True, index=True)
    target_user_id = Column(BigInteger, nullable=True, index=True)

    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(BigInteger, nullable=True)

    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)

    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)