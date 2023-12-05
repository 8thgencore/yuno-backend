from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class IAuthLogin(BaseModel):
    """Authentication Input Schema"""

    email: EmailStr
    password: str

    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def validate_email(cls, value: str, values: Any) -> str:
        return value.lower()


class IAuthRegister(BaseModel):
    """Registration Input Schema"""

    email: EmailStr
    username: str
    password: str

    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def validate_email(cls, value: str, values: Any) -> str:
        return value.lower()


class IAuthChangePassword(BaseModel):
    """ChangePassword Input Schema"""

    current_password: str = Field(description="Current password of a user")
    new_password: str = Field(description="New password of a user")


class IAuthForgotPassword(BaseModel):
    """ForgotPassword Input Schema"""

    email: str = Field(description="Email address of a user")

    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def validate_email(cls, value: str, values: Any) -> str:
        return value.lower()


class IAuthOtpCode(BaseModel):
    """OTP code Input Schema"""

    email: str = Field(description="Email address of a user")
    otp: str = Field(description="OTP code")

    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def validate_email(cls, value: str, values: Any) -> str:
        return value.lower()


class IAuthResetPassword(BaseModel):
    """ResetPassword Input Schema"""

    reset_token: str = Field(description="Reset password token")
    password: str = Field(description="New password of a user")
