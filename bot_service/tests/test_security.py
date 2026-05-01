import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.jwt import decode_and_validate, TokenValidationError, TokenExpiredError
from app.core.config import settings


def test_decode_valid_token():
    """Тест декодирования валидного токена"""
    # Создаём валидный токен
    payload = {
        "sub": "123",
        "role": "user",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    
    # Декодируем
    result = decode_and_validate(token)
    
    assert result["sub"] == "123"
    assert result["role"] == "user"


def test_decode_expired_token():
    """Тест декодирования истекшего токена"""
    # Создаём истекший токен
    payload = {
        "sub": "123",
        "role": "user",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    
    # Проверяем, что выбрасывается исключение
    with pytest.raises(TokenExpiredError):
        decode_and_validate(token)


def test_decode_invalid_signature():
    """Тест декодирования токена с неверной подписью"""
    # Создаём токен с неверным секретом
    payload = {
        "sub": "123",
        "role": "user",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, "wrong_secret", algorithm=settings.JWT_ALG)
    
    # Проверяем, что выбрасывается исключение
    with pytest.raises(TokenValidationError):
        decode_and_validate(token)


def test_decode_token_missing_sub():
    """Тест декодирования токена без поля sub"""
    payload = {
        "role": "user",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    
    with pytest.raises(TokenValidationError, match="missing 'sub' field"):
        decode_and_validate(token)


def test_decode_token_missing_exp():
    """Тест декодирования токена без поля exp"""
    payload = {
        "sub": "123",
        "role": "user"
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    
    with pytest.raises(TokenValidationError, match="missing 'exp' field"):
        decode_and_validate(token)
