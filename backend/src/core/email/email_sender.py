from email.message import EmailMessage

import aiosmtplib
from pydantic import EmailStr, SecretStr, AnyUrl

from src.core.email.interface import EmailSenderInterface


class EmailSenderManager(EmailSenderInterface):
    def __init__(
        self,
        email_host: str,
        email_port: int,
        email_host_user: EmailStr,
        from_email: EmailStr,
        app_password: SecretStr,
        use_tls: bool,
        app_url: AnyUrl,
    ):
        self._email_host = email_host
        self._email_port = email_port
        self._email_user = email_host_user
        self._from_email = from_email
        self._app_password = app_password.get_secret_value()
        self._use_tls = use_tls
        self._app_url = app_url

    async def _send_email(self, to_email: EmailStr, subject: str, body: str):
        message = EmailMessage()
        message["From"] = self._from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=self._email_host,
            port=self._email_port,
            start_tls=self._use_tls,
            username=self._email_user,
            password=self._app_password,
        )

    async def send_activation_email(self, email: EmailStr, token: str) -> None:
        subject = "Activate your account"
        body = f"Please click the link to activate your account: {self._app_url}/activate/{token}"
        await self._send_email(email, subject, body)

    async def send_password_reset_email(
        self, email: EmailStr, token: str
    ) -> None: ...
