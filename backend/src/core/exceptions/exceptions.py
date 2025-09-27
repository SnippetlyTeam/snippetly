class UserNotFoundError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    """Raised when email or username is already taken."""

    pass


class UserNotActiveError(Exception):
    pass


class ActivationTokenNotFoundError(Exception):
    pass


class ActivationTokenExpiredError(Exception):
    pass
