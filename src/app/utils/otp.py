from datetime import timedelta
from uuid import UUID

from redis.asyncio import Redis

from app.models.user_model import User


async def add_otp_to_redis(
    redis_client: Redis,
    user: User,
    otp_code: str,
    expire_time: int | None = None,
) -> None:
    otp_key = f"user:{user.id}:otp"
    valid_otps = await get_valid_otp(redis_client, user.id)
    await redis_client.sadd(otp_key, otp_code)
    if not valid_otps:
        await redis_client.expire(otp_key, timedelta(minutes=expire_time))


async def get_valid_otp(redis_client: Redis, user_id: UUID) -> set:
    otp_key = f"user:{user_id}:otp"
    valid_otps = await redis_client.smembers(otp_key)
    return valid_otps


async def delete_otps(redis_client: Redis, user: User) -> None:
    token_key = f"user:{user.id}:otp"
    valid_otps = await redis_client.smembers(token_key)
    if valid_otps is not None:
        await redis_client.delete(token_key)
