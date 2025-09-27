from typing import Annotated

from fastapi.params import Depends

from src.core.config import Settings, get_settings
from src.core.email.email_sender import EmailSenderManager
from src.core.email.interface import EmailSenderInterface


async def get_email_sender(
    settings: Annotated[Settings, Depends(get_settings)],
) -> EmailSenderInterface:
    return EmailSenderManager(
        email_host=settings.EMAIL_HOST,
        email_port=settings.EMAIL_PORT,
        email_host_user=settings.EMAIL_HOST_USER,
        from_email=settings.FROM_EMAIL,
        email_app_password=settings.EMAIL_APP_PASSWORD,
        use_tls=settings.USE_TLS,
        app_url=settings.APP_URL,
    )
