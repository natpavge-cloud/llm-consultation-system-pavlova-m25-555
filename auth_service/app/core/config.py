from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения Auth Service"""
    
    # Общие настройки приложения
    APP_NAME: str = "Auth Service"
    ENV: str = "development"
    DEBUG: bool = True
    
    # JWT настройки
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Настройки базы данных
    SQLITE_PATH: str = "auth_service.db"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{SQLITE_PATH}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Глобальный объект настроек
settings = Settings()