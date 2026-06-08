from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLogWebCheckin


def create_audit_log(
    db: Session,
    action: str,
    actor_user_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    audit = AuditLogWebCheckin(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit