from typing import Optional
import redis.asyncio as redis

from app.core.config import settings


# Глобальный Redis клиент
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Получить Redis клиент (singleton)
    
    Returns:
        Асинхронный Redis клиент
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    return _redis_client


async def close_redis():
    """
    Закрыть соединение с Redis
    """
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


# Вспомогательные функции для работы с токенами
async def save_user_token(user_id: int, token: str, ttl: int = 3600) -> None:
    """
    Сохранить токен пользователя в Redis
    """
    redis_client = await get_redis()
    key = f"user_token:{user_id}"
    await redis_client.setex(key, ttl, token)


async def get_user_token(user_id: int) -> Optional[str]:
    """
    Получить токен пользователя из Redis
    """
    redis_client = await get_redis()
    key = f"user_token:{user_id}"
    return await redis_client.get(key)


async def delete_user_token(user_id: int) -> None:
    """
    Удалить токен пользователя из Redis
    """
    redis_client = await get_redis()
    key = f"user_token:{user_id}"
    await redis_client.delete(key)
    