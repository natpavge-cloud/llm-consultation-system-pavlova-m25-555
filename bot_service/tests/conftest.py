import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import fakeredis.aioredis


@pytest.fixture
async def fake_redis():
    """
    Фикстура для создания fake Redis клиента
    """
    # Используем aioredis совместимый клиент из fakeredis
    redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis_client
    await redis_client.close()


@pytest.fixture
def mock_redis(fake_redis):
    """
    Патч get_redis для использования fake Redis в тестах.
    Подменяет источник redis-клиента для всего приложения.
    """
    mock_get = AsyncMock(return_value=fake_redis)
    
    # Патчим точку определения в infra.redis.
    with patch("app.infra.redis.get_redis", mock_get):
        yield fake_redis


@pytest.fixture
def mock_jwt_decode():
    """
    Мок для decode_and_validate (чтобы не проверять реальные JWT в тестах бота)
    """
    with patch("app.bot.handlers.decode_and_validate") as mock:
        mock.return_value = {
            "sub": "1",
            "role": "user",
            "exp": 9999999999
        }
        yield mock


@pytest.fixture
def mock_celery_task():
    """
    Мок для Celery задачи llm_request (чтобы не отправлять задачи в реальный RabbitMQ)
    """
    with patch("app.bot.handlers.llm_request") as mock:
        
        mock.delay = MagicMock() 
        yield mock
        