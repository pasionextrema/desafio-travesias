import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User, RefreshToken, EmailVerification, PasswordReset, UserRole

settings = get_settings()


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    referral_code: str | None = None,
) -> User:
    email_lower = email.lower().strip()

    existing = await db.execute(select(User).where(User.email == email_lower))
    if existing.scalar_one_or_none():
        raise ValueError("El email ya esta registrado")

    referred_by = None
    if referral_code:
        result = await db.execute(select(User).where(User.referral_code == referral_code.upper()))
        referred_by = result.scalar_one_or_none()

    user = User(
        email=email_lower,
        password_hash=hash_password(password),
        referral_code=_generate_unique_referral_code(),
        referred_by_id=referred_by.id if referred_by else None,
    )

    db.add(user)
    await db.flush()

    verification = _create_email_verification(user.id)
    db.add(verification)
    await db.commit()
    await db.refresh(user)

    return user, verification


async def login_user(
    db: AsyncSession,
    email: str,
    password: str,
    remember_me: bool = False,
) -> tuple[User, str, str]:
    email_lower = email.lower().strip()

    result = await db.execute(
        select(User).where(
            (User.email == email_lower) | (User.username == email_lower)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Email o contrasena incorrectos")

    if not user.is_active:
        raise ValueError("Cuenta desactivada. Contacta al administrador.")

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})

    refresh_expire = datetime.now(timezone.utc) + (
        timedelta(days=30) if remember_me else timedelta(days=settings.jwt_refresh_token_expire_days)
    )

    refresh_token = RefreshToken(
        user_id=user.id,
        token=hash_password(refresh_token_str),
        expires_at=refresh_expire,
    )
    db.add(refresh_token)
    await db.commit()

    return user, access_token, refresh_token_str


async def refresh_access_token(
    db: AsyncSession,
    refresh_token_str: str,
) -> tuple[str, str]:
    payload = decode_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Token invalido")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token invalido")

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    tokens = result.scalars().all()

    valid_token = None
    for rt in tokens:
        if verify_password(refresh_token_str, rt.token):
            valid_token = rt
            break

    if not valid_token:
        raise ValueError("Token revocado o expirado")

    valid_token.is_revoked = True

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise ValueError("Usuario no encontrado o desactivado")

    new_access = create_access_token({"sub": str(user.id), "role": user.role.value})
    new_refresh_str = create_refresh_token({"sub": str(user.id)})

    new_refresh = RefreshToken(
        user_id=user.id,
        token=hash_password(new_refresh_str),
        expires_at=valid_token.expires_at,
    )
    db.add(new_refresh)
    await db.commit()

    return new_access, new_refresh_str


async def logout_user(db: AsyncSession, refresh_token_str: str) -> None:
    payload = decode_token(refresh_token_str)
    if not payload:
        return

    user_id = payload.get("sub")
    if not user_id:
        return

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
    )
    tokens = result.scalars().all()

    for rt in tokens:
        if verify_password(refresh_token_str, rt.token):
            rt.is_revoked = True

    await db.commit()


async def verify_email(db: AsyncSession, token: str) -> bool:
    result = await db.execute(
        select(EmailVerification).where(
            EmailVerification.token == token,
            EmailVerification.used == False,
            EmailVerification.expires_at > datetime.now(timezone.utc),
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        return False

    verification.used = True

    user_result = await db.execute(select(User).where(User.id == verification.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.email_verified = True

    await db.commit()
    return True


async def resend_verification(db: AsyncSession, user_id: str) -> EmailVerification:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("Usuario no encontrado")
    if user.email_verified:
        raise ValueError("El email ya esta verificado")

    verification = _create_email_verification(user_id)
    db.add(verification)
    await db.commit()
    return verification


async def create_password_reset(db: AsyncSession, email: str) -> PasswordReset | None:
    result = await db.execute(select(User).where(User.email == email.lower().strip()))
    user = result.scalar_one_or_none()
    if not user:
        return None

    reset = PasswordReset(
        user_id=user.id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset)
    await db.commit()
    return reset


async def reset_password(db: AsyncSession, token: str, new_password: str) -> bool:
    result = await db.execute(
        select(PasswordReset).where(
            PasswordReset.token == token,
            PasswordReset.used == False,
            PasswordReset.expires_at > datetime.now(timezone.utc),
        )
    )
    reset = result.scalar_one_or_none()
    if not reset:
        return False

    reset.used = True

    user_result = await db.execute(select(User).where(User.id == reset.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.password_hash = hash_password(new_password)

    await db.commit()
    return True


def _create_email_verification(user_id: str) -> EmailVerification:
    return EmailVerification(
        user_id=user_id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )


def _generate_unique_referral_code() -> str:
    import string
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(6))
