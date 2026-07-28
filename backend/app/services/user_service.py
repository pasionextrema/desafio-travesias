from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserProfileUpdate
from app.core.config import get_settings

settings = get_settings()


async def get_user_profile(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user_profile(
    db: AsyncSession,
    user_id: str,
    data: UserProfileUpdate,
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"]:
        existing = await db.execute(
            select(User).where(
                User.username == update_data["username"],
                User.id != user_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("El nombre de usuario ya esta en uso")

    for field, value in update_data.items():
        if value is not None or field in update_data:
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def update_avatar(db: AsyncSession, user_id: str, avatar_url: str) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("Usuario no encontrado")

    user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(user)
    return user


async def get_referral_info(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("Usuario no encontrado")

    total_referrals_result = await db.execute(
        select(User).where(User.referred_by_id == user_id)
    )
    total_referrals = len(total_referrals_result.scalars().all())

    return {
        "referral_code": user.referral_code,
        "referral_url": f"{settings.frontend_url}/register?ref={user.referral_code}",
        "total_referrals": total_referrals,
    }
