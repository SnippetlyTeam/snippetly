from email.message import EmailMessage
from typing import Optional

import aiosmtplib
from pydantic import EmailStr, SecretStr

from src.core.utils.logger import logger
from .interface import EmailSenderInterface


class EmailSenderManager(EmailSenderInterface):
    def __init__(
        self,
        email_host: str,
        email_port: int,
        email_host_user: str,
        from_email: EmailStr,
        use_tls: bool,
        app_url: str,
        email_app_password: Optional[SecretStr] = None,
    ):
        self._email_host = email_host
        self._email_port = email_port
        self._email_user = email_host_user
        self._from_email = from_email
        self._app_password = (
            email_app_password.get_secret_value()
            if email_app_password
            else None
        )
        self._use_tls = use_tls
        self._app_url = app_url

    async def _send_email(
        self, to_email: str, subject: str, body: str
    ) -> None:
        message = EmailMessage()
        message["From"] = self._from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=self._email_host,
                port=self._email_port,
                start_tls=self._use_tls,
                username=self._email_user,
                password=self._app_password,
                timeout=10.0,
            )
        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP auth failed: {e}")
            raise
        except aiosmtplib.SMTPRecipientsRefused as e:
            logger.warning(f"Recipient refused: {e.recipients}")
            raise
        except (aiosmtplib.SMTPConnectError, OSError, TimeoutError) as e:
            logger.error(f"SMTP connection error: {e}")
            raise
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP general error: {e}")
            raise

    async def send_activation_email(self, email: str, token: str) -> None:
        subject = "Activate your account"
        body = (
            f"Please click the link to activate your "
            f"account: {self._app_url}/activate-account/{token}"
        )
        await self._send_email(email, subject, body)

    async def send_password_reset_email(self, email: str, token: str) -> None:
        subject = "Password Reset"
        body = (
            f"Please click the link to reset your "
            f"password: {self._app_url}/reset-password/{token}"
        )
        await self._send_email(email, subject, body)
