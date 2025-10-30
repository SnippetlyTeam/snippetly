from abc import ABC, abstractmethod


class EmailSenderInterface(ABC):
    @abstractmethod
    async def send_activation_email(self, email: str, token: str) -> None:
        """
        Method for sending an Account Activation link

        :param email: Email string where mail will be sent
        :type: EmailStr
        :param token: Activation token
        :type: str
        :return: None
        """
        pass

    @abstractmethod
    async def send_password_reset_email(self, email: str, token: str) -> None:
        """
        Method for sending a Reset Password link

        :param email: Email string where mail will be sent
        :type: EmailStr
        :param token: Reset Password Token
        :type: str
        :return: None
        """
