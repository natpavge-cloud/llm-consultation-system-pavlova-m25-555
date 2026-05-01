import pytest
import respx
import httpx
from app.services.openrouter_client import OpenRouterClient, OpenRouterError
from app.core.config import settings

@pytest.mark.asyncio
@respx.mock  # Перехват HTTP-запросов
async def test_chat_completion_success():
    """Интеграционный мок-тест по ТЗ (успешный сценарий)"""
    client = OpenRouterClient()
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    
    # 1. Поднимаем мок-роут на POST запрос к OpenRouter
    mock_route = respx.post(url).mock(return_value=httpx.Response(
        200, 
        json={
            "choices": [
                {
                    "message": {
                        "content": "This is a test response from AI."
                    }
                }
            ]
        }
    ))
    
    # 2. Вызов функции
    result = await client.chat_completion("Test prompt")
    
    # 3. Проверка результата и факта вызова
    assert result == "This is a test response from AI."
    assert mock_route.called
    
    # 4. Проверка payload
    last_request = mock_route.calls.last.request
    assert b"Test prompt" in last_request.content
    assert "Authorization" in last_request.headers

@pytest.mark.asyncio
@respx.mock
async def test_chat_completion_api_error():
    """Тест обработки ошибки 500"""
    client = OpenRouterClient()
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    
    respx.post(url).mock(return_value=httpx.Response(500, text="Internal Server Error"))
    
    with pytest.raises(OpenRouterError, match="returned 500"):
        await client.chat_completion("Test prompt")

@pytest.mark.asyncio
@respx.mock
async def test_chat_completion_network_error():
    """Тест сетевой ошибки (например, таймаут)"""
    client = OpenRouterClient()
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    
    # Имитация ошибки на уровне сети
    respx.post(url).side_effect = httpx.ConnectError("Network error")
    
    with pytest.raises(OpenRouterError, match="Network error"):
        await client.chat_completion("Test prompt")

@pytest.mark.asyncio
@respx.mock
async def test_chat_completion_empty_response():
    """Тест пустого ответа от LLM"""
    client = OpenRouterClient()
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    
    respx.post(url).mock(return_value=httpx.Response(200, json={"choices": []}))
    
    with pytest.raises(OpenRouterError, match="No choices in response"):
        await client.chat_completion("Test prompt")
            