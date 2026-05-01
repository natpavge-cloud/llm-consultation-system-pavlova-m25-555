from fastapi import APIRouter

from app.api import routes_auth

# Главный роутер API
api_router = APIRouter()

# Подключение роутера аутентификации
api_router.include_router(routes_auth.router, prefix="/auth")
