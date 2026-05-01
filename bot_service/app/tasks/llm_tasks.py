import asyncio
from aiogram import Bot

from app.infra.celery_app import celery_app
from app.services.openrouter_client import openrouter_client, OpenRouterError
from app.core.config import settings


@celery_app.task(name="app.tasks.llm_tasks.llm_request", bind=True)
def llm_request(self, tg_chat_id: int, prompt: str):
    """
    Celery задача для обработки LLM запроса
    """
    # Запускаем async функцию в синхронном контексте Celery
    return asyncio.run(_process_llm_request(tg_chat_id, prompt))


async def _process_llm_request(tg_chat_id: int, prompt: str) -> str:
    """
    Асинхронная обработка LLM запроса
    """
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    try:
        # Отправляем запрос к LLM
        system_message = (
            "Ты полезный AI-ассистент. Отвечай кратко и по существу. "
            "После основного ответа, предложи два варианта следующего вопроса от лица пользователя. "
            "Пример: не 'Хотите узнать больше о ...?', а 'Расскажи подробнее о ...'. "
            "Формат должен быть строго следующим (включая фигурные скобки, без дополнительных пояснений):\n"
            "{Вопрос 1}\n"
            "{Вопрос 2}"
        )
        
        response = await openrouter_client.chat_completion(
            prompt=prompt,
            system_message=system_message
        )
        
        # Отправляем ответ пользователю
        await bot.send_message(
            chat_id=tg_chat_id,
            text=response
        )
        
        return response
        
    except OpenRouterError as e:
        error_message = f"Ошибка при обращении к LLM: {str(e)}"
        await bot.send_message(
            chat_id=tg_chat_id,
            text=error_message
        )
        raise
        
    except Exception as e:
        error_message = f"Неожиданная ошибка: {str(e)}"
        await bot.send_message(
            chat_id=tg_chat_id,
            text=error_message
        )
        raise
        
    finally:
        await bot.session.close()
        