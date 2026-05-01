import httpx
from typing import Optional

from app.core.config import settings


class OpenRouterError(Exception):
    """Ошибка при работе с OpenRouter API"""
    pass


class OpenRouterClient:
    """Клиент для работы с OpenRouter API"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.max_tokens = settings.OPENROUTER_MAX_TOKENS
        self.temperature = settings.OPENROUTER_TEMPERATURE
    
    async def chat_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None
    ) -> str:
        """
        Отправить запрос к LLM и получить ответ
        """
        # Формируем сообщения
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Формируем payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        # Заголовки
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/bot-service",
            "X-Title": "Bot Service"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                # Проверяем статус ответа
                if response.status_code != 200:
                    error_detail = response.text
                    raise OpenRouterError(
                        f"OpenRouter API returned {response.status_code}: {error_detail}"
                    )
                
                # Парсим ответ
                data = response.json()
                
                # Извлекаем текст ответа
                if "choices" not in data or len(data["choices"]) == 0:
                    raise OpenRouterError("No choices in response")
                
                message = data["choices"][0].get("message", {})
                content = message.get("content", "")
                
                if not content:
                    raise OpenRouterError("Empty response from LLM")
                
                return content.strip()
                
        except httpx.RequestError as e:
            raise OpenRouterError(f"Network error: {str(e)}")
        except Exception as e:
            if isinstance(e, OpenRouterError):
                raise
            raise OpenRouterError(f"Unexpected error: {str(e)}")


# Создаём глобальный экземпляр клиента
openrouter_client = OpenRouterClient()
