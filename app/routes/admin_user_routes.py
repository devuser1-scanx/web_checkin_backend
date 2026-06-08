from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserWebCheckin
from app.models.role import RoleWebCheckin
from app.models.staff_profile import StaffProfileWebCheckin
from app.schemas.user_schema import (
    CreateUserRequest,
    UserResponse,
    ChangeRoleRequest,
    ChangeStatusRequest,
    ResetPasswordRequest,
)
from app.utils.dependencies import require_admin
from app.utils.security import hash_password
from app.services.audit_service import create_audit_log


router = APIRouter(prefix="/api/web-checkin/admin/users", tags=["Admin Users"])


@router.post("", response_model=UserResponse)
def create_user(
    payload: CreateUserRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    existing = db.query(UserWebCheckin).filter(
        UserWebCheckin.username == payload.username
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    role = db.query(RoleWebCheckin).filter(
        RoleWebCheckin.role_name == payload.role_name
    ).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    user = UserWebCheckin(
        full_name=payload.full_name,
        username=payload.username,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role_id=role.id,
        status="active",
        is_active=True,
        is_deleted=False,
        created_by=admin_user.id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    profile = StaffProfileWebCheckin(
        user_id=user.id,
        employee_code=payload.employee_code,
        job_title=payload.job_title,
        department=payload.department,
    )

    db.add(profile)
    db.commit()

    create_audit_log(
        db=db,
        action="user_created",
        actor_user_id=admin_user.id,
        target_user_id=user.id,
        entity_type="users_web_checkin",
        entity_id=user.id,
        new_value={
            "username": user.username,
            "role": role.role_name,
            "status": user.status,
        },
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        phone=user.phone,
        role=role.role_name,
        status=user.status,
        is_active=user.is_active,
    )


@router.get("")
def list_users(
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    users = db.query(UserWebCheckin).filter(
        UserWebCheckin.is_deleted == False
    ).order_by(UserWebCheckin.created_at.desc()).all()

    result = []

    for user in users:
        role = db.query(RoleWebCheckin).filter(RoleWebCheckin.id == user.role_id).first()

        result.append({
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": role.role_name if role else None,
            "status": user.status,
            "is_active": user.is_active,
            "created_at": user.created_at,
        })

    return result


@router.patch("/{user_id}/role")
def change_user_role(
    user_id: int,
    payload: ChangeRoleRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    user = db.query(UserWebCheckin).filter(
        UserWebCheckin.id == user_id,
        UserWebCheckin.is_deleted == False,
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_role = db.query(RoleWebCheckin).filter(
        RoleWebCheckin.role_name == payload.role_name
    ).first()

    if not new_role:
        raise HTTPException(status_code=400, detail="Invalid role")

    old_role_id = user.role_id
    user.role_id = new_role.id

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action="role_changed",
        actor_user_id=admin_user.id,
        target_user_id=user.id,
        entity_type="users_web_checkin",
        entity_id=user.id,
        old_value={"role_id": old_role_id},
        new_value={"role_id": new_role.id, "role_name": new_role.role_name},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"message": "Role updated successfully"}


@router.patch("/{user_id}/status")
def change_user_status(
    user_id: int,
    payload: ChangeStatusRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    allowed_statuses = ["active", "inactive", "banned", "removed"]

    if payload.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    user = db.query(UserWebCheckin).filter(
        UserWebCheckin.id == user_id,
        UserWebCheckin.is_deleted == False,
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_status = user.status

    user.status = payload.status
    user.is_active = payload.status == "active"

    if payload.status == "removed":
        user.is_deleted = True

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action="status_changed",
        actor_user_id=admin_user.id,
        target_user_id=user.id,
        entity_type="users_web_checkin",
        entity_id=user.id,
        old_value={"status": old_status},
        new_value={"status": user.status, "is_active": user.is_active},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"message": "Status updated successfully"}


@router.patch("/{user_id}/password")
def reset_password(
    user_id: int,
    payload: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: UserWebCheckin = Depends(require_admin),
):
    user = db.query(UserWebCheckin).filter(
        UserWebCheckin.id == user_id,
        UserWebCheckin.is_deleted == False,
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(payload.new_password)

    db.commit()

    create_audit_log(
        db=db,
        action="password_reset",
        actor_user_id=admin_user.id,
        target_user_id=user.id,
        entity_type="users_web_checkin",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return {"message": "Password reset successfully"}