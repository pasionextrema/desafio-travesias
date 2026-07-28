from datetime import datetime, date
from pydantic import BaseModel, field_validator


class UserProfileResponse(BaseModel):
    id: str
    email: str
    username: str | None
    full_name: str | None
    avatar_url: str | None
    country: str | None
    nationality: str | None
    birth_date: date | None
    instagram_user: str | None
    youtube_user: str | None
    referral_code: str
    role: str
    email_verified: bool
    language: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    username: str | None = None
    country: str | None = None
    nationality: str | None = None
    birth_date: date | None = None
    instagram_user: str | None = None
    youtube_user: str | None = None

    @field_validator("birth_date")
    @classmethod
    def validate_age(cls, v: date | None) -> date | None:
        if v is None:
            return v
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 13:
            raise ValueError("Debes ser mayor de 13 anos")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) < 3 or len(v) > 50:
            raise ValueError("El nombre de usuario debe tener entre 3 y 50 caracteres")
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("El nombre de usuario solo permite letras, numeros, _ y .")
        return v.lower()


class ChangeRoleRequest(BaseModel):
    target_role: str


class ReferralInfoResponse(BaseModel):
    referral_code: str
    referral_url: str
    total_referrals: int = 0
