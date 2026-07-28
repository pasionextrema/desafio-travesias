from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthUserResponse,
)
from app.services import auth_service
from app.services.email_service import send_verification_email, send_password_reset_email
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user, verification = await auth_service.register_user(
            db, data.email, data.password, data.referral_code
        )
        await send_verification_email(user.email, verification.token)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{type(e).__name__}: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        user, access_token, refresh_token = await auth_service.login_user(
            db, data.email, data.password, data.remember_me
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        access_token, refresh_token = await auth_service.refresh_access_token(db, data.refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
async def logout(
    data: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.logout_user(db, data.refresh_token)
    return {"message": "Sesion cerrada exitosamente"}


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    success = await auth_service.verify_email(db, token)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token invalido o expirado")
    return {"message": "Email verificado exitosamente"}


@router.post("/resend-verification")
async def resend_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        verification = await auth_service.resend_verification(db, str(current_user.id))
        await send_verification_email(current_user.email, verification.token)
        return {"message": "Email de verificacion reenviado"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    reset = await auth_service.create_password_reset(db, data.email)
    if reset:
        await send_password_reset_email(data.email, reset.token)
    return {"message": "Si el email existe, recibiras un enlace de recuperacion"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    success = await auth_service.reset_password(db, data.token, data.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token invalido o expirado")
    return {"message": "Contrasena actualizada exitosamente"}


@router.get("/me", response_model=AuthUserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
