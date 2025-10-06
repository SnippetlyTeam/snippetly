class UserNotFoundError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserNotActiveError(Exception):
    pass


class TokenNotFoundError(Exception):
    pass


class TokenExpiredError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class SnippetNotFoundError(Exception):
    pass


class NoPermissionError(Exception):
    pass
