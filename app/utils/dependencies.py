from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import UserWebCheckin
from app.models.role import RoleWebCheckin


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/web-checkin/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserWebCheckin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(UserWebCheckin).filter(
        UserWebCheckin.id == int(user_id),
        UserWebCheckin.is_deleted == False,
    ).first()

    if not user:
        raise credentials_exception

    if not user.is_active or user.status in ["banned", "removed", "inactive"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not allowed to access this application",
        )

    return user


def require_admin(
    current_user: UserWebCheckin = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserWebCheckin:
    role = db.query(RoleWebCheckin).filter(RoleWebCheckin.id == current_user.role_id).first()

    if not role or role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user