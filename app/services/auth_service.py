from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.user import UserWebCheckin
from app.models.role import RoleWebCheckin
from app.utils.security import verify_password, create_access_token


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(UserWebCheckin).filter(
        UserWebCheckin.username == username,
        UserWebCheckin.is_deleted == False,
    ).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active or user.status in ["banned", "removed", "inactive"]:
        return None

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    role = db.query(RoleWebCheckin).filter(RoleWebCheckin.id == user.role_id).first()

    token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": role.role_name if role else None,
        }
    )

    return user, role, token