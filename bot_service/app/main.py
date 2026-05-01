from contextlib import asynccontextmanager
from fastapi import FastAPI, status

from app.core.config import settings
from app.infra.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    print("Starting Bot Service API...")
    
    yield
    
    print("Shutting down Bot Service API...")
    await close_redis()
    print("Redis connections closed")


# Создание приложения FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="Telegram Bot Service с LLM консультациями",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


@app.get(
    "/health",
    tags=["System"],
    summary="Проверка здоровья сервиса",
    status_code=status.HTTP_200_OK
)
async def health_check():
    """
    Эндпоинт для проверки работоспособности сервиса
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENV
    }


@app.get(
    "/",
    tags=["System"],
    summary="Корневой эндпоинт"
)
async def root():
    """
    Корневой эндпоинт сервиса
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
    