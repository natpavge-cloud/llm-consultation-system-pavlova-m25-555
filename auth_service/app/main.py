from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import BaseHTTPException
from app.db.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Auth Service...")
    await init_db()
    print("Database initialized")
    yield
    print("Shutting down Auth Service...")
    await close_db()
    print("Database connections closed")

# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис аутентификации и авторизации",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.exception_handler(BaseHTTPException)
async def custom_http_exception_handler(request: Request, exc: BaseHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None)
    )

@app.get("/health", tags=["System"], summary="Проверка здоровья сервиса")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

@app.get("/", tags=["System"], summary="Корневой эндпоинт")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"}

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
