from typing import Optional
from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    full_name: str
    username: str
    password: str
    role_name: str = "staff"
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    employee_code: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    username: str
    email: Optional[str]
    phone: Optional[str]
    role: str
    status: str
    is_active: bool

    class Config:
        from_attributes = True


class ChangeRoleRequest(BaseModel):
    role_name: str


class ChangeStatusRequest(BaseModel):
    status: str


class ResetPasswordRequest(BaseModel):
    new_password: str