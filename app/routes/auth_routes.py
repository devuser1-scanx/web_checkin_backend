from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schema import LoginRequest, LoginResponse, CurrentUserResponse
from app.services.auth_service import authenticate_user
from app.utils.dependencies import get_current_user
from app.models.user import UserWebCheckin
from app.models.role import RoleWebCheckin
from app.services.audit_service import create_audit_log


router = APIRouter(prefix="/api/web-checkin/auth", tags=["Auth"])


def handle_login(
    username: str,
    password: str,
    request: Request,
    db: Session,
):
    result = authenticate_user(db, username, password)

    if not result:
        create_audit_log(
            db=db,
            action="login_failed",
            entity_type="users_web_checkin",
            new_value={"username": username},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user, role, token = result

    create_audit_log(
        db=db,
        action="login_success",
        actor_user_id=user.id,
        target_user_id=user.id,
        entity_type="users_web_checkin",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return LoginResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=role.role_name,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    JSON login endpoint.
    Use this from frontend.
    """
    return handle_login(
        username=payload.username,
        password=payload.password,
        request=request,
        db=db,
    )


@router.post("/token", response_model=LoginResponse)
def swagger_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Swagger OAuth2 login endpoint.
    This accepts form-data, which Swagger Authorize requires.
    """
    return handle_login(
        username=form_data.username,
        password=form_data.password,
        request=request,
        db=db,
    )


@router.get("/me", response_model=CurrentUserResponse)
def me(
    current_user: UserWebCheckin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = db.query(RoleWebCheckin).filter(
        RoleWebCheckin.id == current_user.role_id
    ).first()

    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=role.role_name if role else "",
        status=current_user.status,
        is_active=current_user.is_active,
    )