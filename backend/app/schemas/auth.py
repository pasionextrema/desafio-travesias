import re
from datetime import datetime
from uuid import UUID
from typing import Annotated

from pydantic import BaseModel, EmailStr, field_validator, BeforeValidator


PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    referral_code: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_PATTERN.match(v):
            raise ValueError(
                "La contrasena debe tener al menos 8 caracteres, "
                "incluir mayusculas, minusculas, numeros y caracteres especiales"
            )
        return v


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_PATTERN.match(v):
            raise ValueError(
                "La contrasena debe tener al menos 8 caracteres, "
                "incluir mayusculas, minusculas, numeros y caracteres especiales"
            )
        return v


class OAuthCallbackRequest(BaseModel):
    code: str


class AuthUserResponse(BaseModel):
    id: Annotated[str, BeforeValidator(lambda v: str(v))]
    email: str
    username: str | None
    full_name: str | None
    role: str
    email_verified: bool
    referral_code: str

    model_config = {"from_attributes": True}
