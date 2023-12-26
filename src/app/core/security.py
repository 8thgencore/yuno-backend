import random
from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


def create_access_token(subject: str | Any, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.srv.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}

    return jwt.encode(
        payload=to_encode,
        key=settings.srv.SECRET_KEY,
        algorithm=settings.srv.JWT_ALGORITHM,
    )


def create_refresh_token(subject: str | Any, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.srv.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}

    return jwt.encode(
        payload=to_encode,
        key=settings.srv.SECRET_KEY,
        algorithm=settings.srv.JWT_ALGORITHM,
    )


def create_reset_token(subject: str | Any, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.srv.RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "reset"}

    return jwt.encode(
        payload=to_encode,
        key=settings.srv.SECRET_KEY,
        algorithm=settings.srv.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        jwt=token,
        key=settings.srv.SECRET_KEY,
        algorithms=[settings.srv.JWT_ALGORITHM],
    )


def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()

    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(plain_password: str | bytes) -> str:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()

    return bcrypt.hashpw(plain_password, bcrypt.gensalt()).decode()


def create_otp_code(length: int) -> str:
    otp = ""
    for _ in range(length):
        otp += str(random.randint(0, 9))

    return otp
