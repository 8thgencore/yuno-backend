from pydantic import BaseModel, EmailStr, Field


class IAuthLogin(BaseModel):
    email: EmailStr
    password: str


class IAuthRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class IAuthChangePassword(BaseModel):
    """ChangePassword Input Schema"""

    current: str = Field(description="Current password of a user")
    new: str = Field(description="New password of a user")


class IAuthForgetPassword(BaseModel):
    """ForgetPassword Input Schema"""

    email: str = Field(description="Email address of a user.")
