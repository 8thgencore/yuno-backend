from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from redis.asyncio import Redis

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.auth_schema import (
    IAuthChangePassword,
    IAuthForgetPassword,
    IAuthLogin,
    IAuthRegister,
)
from app.schemas.common_schema import IMetaGeneral, TokenType
from app.schemas.response_schema import IPostResponseBase, create_response
from app.schemas.token_schema import RefreshToken, Token, TokenRead
from app.schemas.user_schema import IUserCreate, IUserRead
from app.tasks import send_verification_email
from app.utils.exceptions import EmailNotFoundException
from app.utils.otp import add_otp_to_redis, delete_otps
from app.utils.token import add_token_to_redis, delete_tokens, get_valid_tokens

router = APIRouter()


@router.post("/login")
async def login(
    login_user: IAuthLogin,
    meta_data: IMetaGeneral = Depends(deps.get_general_meta),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[Token]:
    """
    Authenticate a user with email and password.

    Args:
      - `IAuthLogin`: The user's login credentials.

    Returns:
      - `Token`: object containing a JWT access token and refresh token.

    Raises:
      - `HTTPException`: If the email or password is incorrect, or if the user is inactive.
    """
    user = await crud.user.authenticate(email=login_user.email, password=login_user.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email or Password incorrect")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(user.id, expires_delta=access_token_expires)
    refresh_token = security.create_refresh_token(user.id, expires_delta=refresh_token_expires)
    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=user,
    )

    valid_access_tokens = await get_valid_tokens(redis_client, user.id, TokenType.ACCESS)
    if valid_access_tokens:
        await add_token_to_redis(
            redis_client,
            user,
            access_token,
            TokenType.ACCESS,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    valid_refresh_tokens = await get_valid_tokens(redis_client, user.id, TokenType.REFRESH)
    if valid_refresh_tokens:
        await add_token_to_redis(
            redis_client,
            user,
            refresh_token,
            TokenType.REFRESH,
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    return create_response(meta=meta_data, data=data, message="Login correctly")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    register_user: IAuthRegister,
) -> IPostResponseBase[IUserRead]:
    """
    Register a new user.

    Args:
      - `IAuthRegister`: The user to register, including their email, username, and password.

    Returns:
      - `UserRead`: A response containing the newly created user's information.

    Raises:
      - `HTTPException`: If the user already exists.
    """
    register_user = await deps.user_exists(user=register_user)
    new_user = IUserCreate(
        first_name="",
        last_name="",
        email=register_user.email,
        username=register_user.username,
        password=register_user.password,
        is_active=True,
        is_superuser=False,
    )

    role = await crud.role.get_role_by_name(name="user")
    if not role:
        new_user.role_id = None
    else:
        new_user.role_id = role.id

    user = await crud.user.create_with_role(obj_in=new_user)
    return create_response(data=user)


@router.post("/token")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> TokenRead:
    """
    OAuth2 compatible token login, get an access token for future requests

    Parameters:
      - `OAuth2PasswordRequestForm`: Form data containing email and password of the user.

    Returns:
      - `TokenRead`: Access token generated for the user.

    Raises:
      - `HTTPException` : If the email or password is incorrect, or if the user is inactive.

    """
    user = await crud.user.authenticate(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(user.id, expires_delta=access_token_expires)
    valid_access_tokens = await get_valid_tokens(redis_client, user.id, TokenType.ACCESS)
    if valid_access_tokens:
        await add_token_to_redis(
            redis_client,
            user,
            access_token,
            TokenType.ACCESS,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", status_code=201)
async def get_new_access_token(
    body: RefreshToken = Body(...),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[TokenRead]:
    """
    OAuth2 compatible token, get an access token for future requests using refresh token

    Parameters:
      - `RefreshToken`: Request body containing the refresh token.

    Returns:
      - `TokenRead`: Response body containing the new access token.

    Raises:
      - `HTTPException`: If the refresh token is invalid, has expired or is not associated with the user.
    """
    try:
        payload = jwt.decode(
            body.refresh_token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=403, detail="Refresh token invalid")

    if payload["type"] == "refresh":
        user_id = payload["sub"]
        valid_refresh_tokens = await get_valid_tokens(redis_client, user_id, TokenType.REFRESH)
        if valid_refresh_tokens and body.refresh_token not in valid_refresh_tokens:
            raise HTTPException(status_code=403, detail="Refresh token invalid")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        user = await crud.user.get(id=user_id)
        if user.is_active:
            access_token = security.create_access_token(
                user.id, expires_delta=access_token_expires
            )
            valid_access_tokens = await get_valid_tokens(redis_client, user.id, TokenType.ACCESS)
            if valid_access_tokens:
                await add_token_to_redis(
                    redis_client,
                    user,
                    access_token,
                    TokenType.ACCESS,
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                )
            return create_response(
                data=TokenRead(access_token=access_token, token_type="bearer"),
                message="Access token generated correctly",
            )
        else:
            raise HTTPException(status_code=404, detail="User inactive")
    else:
        raise HTTPException(status_code=404, detail="Incorrect token")


@router.post("/change-password")
async def change_password(
    password: IAuthChangePassword,
    current_user: User = Depends(deps.get_current_user()),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[Token]:
    """
    This endpoint allows the user to change their password.

    Args:
      - `IAuthChangePassword`: The request body, which should include the user's current and new passwords.

    Returns:
      - `Token`: A response containing the new access token, refresh token, and user information.

    Raises:
      - `HTTPException`: If the current password is invalid or if the new password is the same as the current password.
    """
    if not verify_password(password.current, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid Current Password")

    if verify_password(password.new, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="New Password should be different that the current one",
        )

    # Update the user's password in the database
    new_hashed_password = get_password_hash(password.new)
    await crud.user.update(
        obj_current=current_user, obj_new={"hashed_password": new_hashed_password}
    )

    # Create new access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        current_user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        current_user.id, expires_delta=refresh_token_expires
    )
    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=current_user,
    )

    # Delete any existing access and refresh tokens for the user
    await delete_tokens(redis_client, current_user, TokenType.ACCESS)
    await delete_tokens(redis_client, current_user, TokenType.REFRESH)

    # Add the new access and refresh tokens to Redis
    await add_token_to_redis(
        redis_client,
        current_user,
        access_token,
        TokenType.ACCESS,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    await add_token_to_redis(
        redis_client,
        current_user,
        refresh_token,
        TokenType.REFRESH,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return create_response(data=data, message="New password generated")


@router.post("/forget-password", status_code=202)
async def forget_password(
    request_data: IAuthForgetPassword,
    redis_client: Redis = Depends(deps.get_redis_client),
):
    """
    This endpoint sends a verification email containing a one-time password to the provided email address.

    Args:
      - `IAuthForgetPassword`: The request body, which should include an email address.

    Returns:
      - `dict`: A dictionary containing a success message indicating that the OTP code has been sent to the email address.

    Raises:
      - `HTTPException`: If the provided email address is not associated with an existing user.
    """
    email = request_data.email
    current_user = await crud.user.get_by_email(email=email)
    if not current_user:
        raise EmailNotFoundException(email=email)

    otp_code = security.create_otp_code(length=6)
    await delete_otps(redis_client, current_user)
    await add_otp_to_redis(
        redis_client,
        current_user,
        otp_code,
        settings.OTP_EXPIRE_MINUTES,
    )

    # Send the verification email containing the OTP code
    send_verification_email.delay(email_to=email, otp_code=otp_code)

    return create_response(data={}, message="OTP code sent to e-mail")
