import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def send_verification_email(email: str, token: str, language: str = "es") -> None:
    verification_url = f"{settings.frontend_url}/verify-email?token={token}"

    if settings.app_env == "development":
        logger.info(f"[DEV] Verification email for {email}: {verification_url}")
        return

    if settings.sendgrid_api_key:
        await _send_sendgrid(email, "Verifica tu email - Desafio de Travesias", _verification_body(verification_url))
    else:
        logger.warning(f"Email service not configured. Verification URL for {email}: {verification_url}")


async def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    if settings.app_env == "development":
        logger.info(f"[DEV] Password reset for {email}: {reset_url}")
        return

    if settings.sendgrid_api_key:
        await _send_sendgrid(email, "Recuperacion de contrasena - Desafio de Travesias", _reset_body(reset_url))
    else:
        logger.warning(f"Email service not configured. Reset URL for {email}: {reset_url}")


async def _send_sendgrid(to_email: str, subject: str, html_content: str) -> None:
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json={
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": settings.from_email},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": html_content}],
                },
                headers={
                    "Authorization": f"Bearer {settings.sendgrid_api_key}",
                    "Content-Type": "application/json",
                },
            )
    except Exception as e:
        logger.error(f"Failed to send email via SendGrid: {e}")


def _verification_body(url: str) -> str:
    return f"""
    <h1>Desafio de Travesias</h1>
    <p>Gracias por registrarte. Verifica tu email haciendo clic en el enlace:</p>
    <p><a href="{url}">Verificar Email</a></p>
    <p>Este enlace expira en 24 horas.</p>
    """


def _reset_body(url: str) -> str:
    return f"""
    <h1>Desafio de Travesias</h1>
    <p>Haz clic en el enlace para restablecer tu contrasena:</p>
    <p><a href="{url}">Restablecer Contrasena</a></p>
    <p>Este enlace expira en 1 hora.</p>
    """
