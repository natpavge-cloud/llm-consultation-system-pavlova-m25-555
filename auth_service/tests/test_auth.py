import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import session as db_session
from app.db.base import Base
from app.main import app

# Настройка тестовой БД в памяти
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession)

# Подмена зависимости
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[db_session.get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db():
    """Фикстура для создания таблиц перед каждым тестом"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_full_auth_flow():
    """Проверка успешного сценария: Регистрация -> Логин -> Профиль"""
    
    # 0. Принудительная подмена во всех возможных местах импорта
    from app.api import deps
    from app.db import session
    
    app.dependency_overrides[session.get_db] = override_get_db
    app.dependency_overrides[deps.get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Регистрация
        reg_resp = await ac.post("/auth/register", json={
            "email": "integration@test.com", 
            "password": "strong_password_123"
        })
        assert reg_resp.status_code == 201

        # 2. Логин
        # Использование данных форм (data), как требует OAuth2PasswordRequestForm в ТЗ
        login_resp = await ac.post("/auth/login", data={
            "username": "integration@test.com",
            "password": "strong_password_123"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # 3. Профиль
        # Проверка того, что по токену сервис видит именно тестового юзера
        me_resp = await ac.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "integration@test.com"

@pytest.mark.asyncio
async def test_negative_scenarios():
    """Проверка негативных сценариев: Дубликат, неверный пароль, отсутствие токена"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Повторная регистрация (409)
        await ac.post("/auth/register", json={"email": "dupe@test.com", "password": "pass_12345"})
        resp = await ac.post("/auth/register", json={"email": "dupe@test.com", "password": "pass_12345"})
        assert resp.status_code == 409

        # 2. Неверный пароль (401)
        resp = await ac.post("/auth/login", data={"username": "dupe@test.com", "password": "wrong_password"})
        assert resp.status_code == 401

        # 3. Доступ к /me без токена (401)
        resp = await ac.get("/auth/me")
        assert resp.status_code == 401
