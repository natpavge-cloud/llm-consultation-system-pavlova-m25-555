from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.infra.redis import save_user_token, get_user_token, delete_user_token
from app.core.jwt import decode_and_validate, TokenValidationError, TokenExpiredError
from app.tasks.llm_tasks import llm_request

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я AI-ассистент с авторизацией.\n\n"
        "Для начала работы вам нужно:\n"
        "1. Зарегистрироваться в Auth Service\n"
        "2. Получить JWT токен\n"
        "3. Отправить мне токен командой: /token ВАШ_ТОКЕН\n\n"
        "После авторизации просто отправляйте мне свои вопросы!"
    )


@router.message(Command("token"))
async def cmd_token(message: Message):
    """Обработчик команды /token для сохранения JWT"""
    # Извлекаем токен из команды
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(
            "Неверный формат команды.\n"
            "Используйте: /token ВАШ_JWT_ТОКЕН"
        )
        return
    
    token = parts[1].strip()
    
    try:
        # Валидируем токен
        payload = decode_and_validate(token)
        
        # Сохраняем токен в Redis (TTL 30 минут = 1800 секунд)
        await save_user_token(message.from_user.id, token, ttl=1800)
        
        user_id = payload.get("sub")
        role = payload.get("role", "unknown")
        
        await message.answer(
            f"Токен успешно сохранён!\n\n"
            f"User ID: {user_id}\n"
            f"Role: {role}\n\n"
            f"Теперь вы можете задавать мне вопросы!"
        )
        
    except TokenExpiredError:
        await message.answer(
            "Токен истёк.\n"
            "Пожалуйста, получите новый токен в Auth Service."
        )
    except TokenValidationError as e:
        await message.answer(
            f"Невалидный токен: {str(e)}\n"
            "Пожалуйста, проверьте токен и попробуйте снова."
        )


@router.message(Command("logout"))
async def cmd_logout(message: Message):
    """Обработчик команды /logout для удаления токена"""
    await delete_user_token(message.from_user.id)
    await message.answer(
        "Вы вышли из системы.\n"
        "Для повторной авторизации используйте команду /token"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "Доступные команды:\n\n"
        "/start - Начать работу\n"
        "/token <JWT> - Авторизоваться\n"
        "/logout - Выйти из системы\n"
        "/help - Показать эту справку\n\n"
        "После авторизации просто отправляйте текстовые сообщения - "
        "я отвечу с помощью AI!"
    )


@router.message(F.text)
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений (запросы к LLM)"""
    user_id = message.from_user.id
    
    # Проверяем наличие токена
    token = await get_user_token(user_id)
    
    if not token:
        await message.answer(
            "Вы не авторизованы.\n\n"
            "Для начала работы:\n"
            "1. Зарегистрируйтесь в Auth Service\n"
            "2. Получите JWT токен\n"
            "3. Отправьте команду: /token ВАШ_ТОКЕН"
        )
        return
    
    try:
        # Валидируем токен
        decode_and_validate(token)
        
        # Отправляем задачу в Celery
        llm_request.delay(
            tg_chat_id=message.chat.id,
            prompt=message.text
        )
        
        await message.answer(
            "Ваш запрос принят в обработку...\n"
            "Пожалуйста, подождите, я думаю над ответом."
        )
        
    except TokenExpiredError:
        await delete_user_token(user_id)
        await message.answer(
            "Ваш токен истёк.\n"
            "Пожалуйста, получите новый токен и используйте /token"
        )
    except TokenValidationError:
        await delete_user_token(user_id)
        await message.answer(
            "Ваш токен невалиден.\n"
            "Пожалуйста, получите новый токен и используйте /token"
        )
        