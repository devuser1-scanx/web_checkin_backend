from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    full_name: str
    role: str


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    status: str
    is_active: bool