import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, User, Chat

from app.bot.handlers import cmd_start, cmd_token, handle_text_message
from app.core.jwt import TokenValidationError, TokenExpiredError


@pytest.mark.asyncio
async def test_cmd_start():
    """Тест команды /start"""
# Создаём мок сообщения
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()
    
# Вызываем обработчик
    await cmd_start(message)
    
# Проверяем, что ответ был отправлен
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "Привет" in call_args
    assert "Auth Service" in call_args


@pytest.mark.asyncio
async def test_cmd_token_success(mock_redis, mock_jwt_decode):
    """Тест успешного сохранения токена"""
# Создаём мок сообщения
    message = MagicMock(spec=Message)
    message.text = "/token valid_jwt_token_here"
    message.answer = AsyncMock()
    message.from_user = User(id=12345, is_bot=False, first_name="Test")
    
# Вызываем обработчик
    await cmd_token(message)
    
# Проверяем успешный ответ
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "успешно сохранён" in call_args


@pytest.mark.asyncio
async def test_cmd_token_invalid_format():
    """Тест команды /token без токена"""
    message = MagicMock(spec=Message)
    message.text = "/token"
    message.answer = AsyncMock()
    
    await cmd_token(message)
    
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "Неверный формат" in call_args


@pytest.mark.asyncio
async def test_cmd_token_expired(mock_redis):
    """Тест с истекшим токеном"""
    message = MagicMock(spec=Message)
    message.text = "/token expired_token"
    message.answer = AsyncMock()
    message.from_user = User(id=12345, is_bot=False, first_name="Test")
    
    # Патчим decode_and_validate для выброса TokenExpiredError
    with patch("app.bot.handlers.decode_and_validate") as mock_decode:
        mock_decode.side_effect = TokenExpiredError("Token expired")
        
        await cmd_token(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "истёк" in call_args


@pytest.mark.asyncio
async def test_cmd_token_invalid(mock_redis):
    """Тест с невалидным токеном"""
    message = MagicMock(spec=Message)
    message.text = "/token invalid_token"
    message.answer = AsyncMock()
    message.from_user = User(id=12345, is_bot=False, first_name="Test")
    
    # Патчим decode_and_validate для выброса TokenValidationError
    with patch("app.bot.handlers.decode_and_validate") as mock_decode:
        mock_decode.side_effect = TokenValidationError("Invalid token")
        
        await cmd_token(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Невалидный токен" in call_args


@pytest.mark.asyncio
async def test_handle_text_message_no_token(mock_redis):
    """Тест обработки сообщения без токена"""
    message = MagicMock(spec=Message)
    message.text = "Hello, bot!"
    message.answer = AsyncMock()
    message.from_user = User(id=12345, is_bot=False, first_name="Test")
    
    await handle_text_message(message)
    
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "не авторизованы" in call_args


@pytest.mark.asyncio
async def test_handle_text_message_with_valid_token(mock_redis, mock_jwt_decode, mock_celery_task):
    """Тест обработки сообщения с валидным токеном"""
    # Сохраняем токен в fake Redis
    await mock_redis.set("user_token:12345", "valid_token")
    
    message = MagicMock(spec=Message)
    message.text = "What is AI?"
    message.answer = AsyncMock()
    message.from_user = User(id=12345, is_bot=False, first_name="Test")
    message.chat = Chat(id=12345, type="private")
    
    await handle_text_message(message)
    
    # Проверяем, что задача отправлена в Celery
    mock_celery_task.delay.assert_called_once_with(
        tg_chat_id=12345,
        prompt="What is AI?"
    )
    
    # Проверяем, что отправлено подтверждение
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "принят в обработку" in call_args