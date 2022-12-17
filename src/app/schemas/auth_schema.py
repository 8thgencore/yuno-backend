from pydantic import BaseModel, EmailStr


class IAuthLogin(BaseModel):
    email: EmailStr
    password: str


class IAuthRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class IAuthChangePassword(BaseModel):
    current: str
    new: str
