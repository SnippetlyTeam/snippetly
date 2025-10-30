from pydantic import EmailStr

from .interface import EmailSenderInterface


class MockEmailSender(EmailSenderInterface):
    def __init__(self):
        self.sent_emails = []

    async def send_activation_email(self, email: str, token: str) -> None:
        self.sent_emails.append(
            {
                "type": "activation",
                "to": email,
                "token": token,
            }
        )

    async def send_password_reset_email(
        self, email: EmailStr, token: str
    ) -> None:
        self.sent_emails.append(
            {
                "type": "password_reset",
                "to": email,
                "token": token,
            }
        )

    def get_sent_emails(self, email: str = None) -> list:
        if email:
            return [e for e in self.sent_emails if e["to"] == email]
        return self.sent_emails

    def clear(self) -> None:
        self.sent_emails.clear()
