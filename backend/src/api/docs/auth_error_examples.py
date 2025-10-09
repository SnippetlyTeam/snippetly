UNAUTHORIZED_ERROR_EXAMPLES = {
    "header": "Authorization header is missing",
    "invalid_header": "Invalid Authorization header format. "
    "Expected 'Bearer <token>'",
    "expired_token": "Token has expired",
    "invalid_token": "Invalid token",
    # "miss_jti": "Token missing jti claim",
    # "blacklisted": "Token is blacklisted",
}
FORBIDDEN_ERROR_EXAMPLES = {"not_active": "User account is not activated"}
NOT_FOUND_ERRORS_EXAMPLES = {
    "user_not_found": "User not found",
}
