from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения Bot Service"""
    
    # Общие настройки приложения
    APP_NAME: str = "Bot Service"
    ENV: str = "development"
    DEBUG: bool = True
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = "8776387306:AAGPq3yWhP3bCХХХХХХХХХХХХХХХ"
    
    # Auth Service
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    
    # JWT настройки
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALG: str = "HS256"
    
    # Redis настройки
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # RabbitMQ настройки
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    
    # Celery настройки
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    
    # OpenRouter настройки
    OPENROUTER_API_KEY: str = "sk-or-v1-6dc0c2d5143772781e471ХХХХХХХХХХХХХХХ"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-oss-120b:free"
    OPENROUTER_MAX_TOKENS: int = 1000
    OPENROUTER_TEMPERATURE: float = 0.7
    OPENROUTER_SITE_URL: str = "https://example.com"
    OPENROUTER_APP_NAME: str = "bot-service"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Глобальный объект настроек
settings = Settings()
