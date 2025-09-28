from pydantic import (
    BaseModel,
    EmailStr,
    field_serializer,
    Field,
    field_validator,
    ConfigDict,
)

from src.core.security.validation import (
    password_validation,
    username_validation,
)


class EmailMixin(BaseModel):
    email: EmailStr = Field(..., max_length=255)

    @field_serializer("email")
    def serialize_email(self, value: str) -> str:
        return value.lower()


class PasswordMixin(BaseModel):
    password: str = Field(min_length=8, max_length=30)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return password_validation(value)


class UsernameMixin(BaseModel):
    username: str = Field(min_length=3, max_length=40)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return username_validation(value)


# --- Request ---
class UserRegistrationRequestSchema(
    EmailMixin, UsernameMixin, PasswordMixin, BaseModel
):
    pass


class PasswordResetRequestSchema(EmailMixin, BaseModel):
    pass


class PasswordResetCompletionSchema(EmailMixin, PasswordMixin, BaseModel):
    password_reset_token: str = Field(...)


class UserLoginRequestSchema(PasswordMixin, BaseModel):
    login: str = Field(..., min_length=3, max_length=40)

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        return value.strip()


class TokenRefreshRequestSchema(BaseModel):
    refresh_token: str = Field(..., max_length=512)


class LogoutRequestSchema(BaseModel):
    refresh_token: str = Field(..., max_length=512)


class ActivationRequestSchema(BaseModel):
    activation_token: str = Field(..., max_length=64)


# --- Response ---
class UserRegistrationResponseSchema(EmailMixin, UsernameMixin, BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserLoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
