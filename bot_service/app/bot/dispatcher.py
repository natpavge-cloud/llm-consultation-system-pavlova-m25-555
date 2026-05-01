from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.bot import handlers


# Создание бота
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Создание хранилища состояний (Redis)
storage = RedisStorage.from_url(settings.REDIS_URL)

# Создание диспетчера
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
dp.include_router(handlers.router)


async def start_bot():
    """Запуск бота"""
    print("Starting Bot Service...")
    await dp.start_polling(bot)


async def stop_bot():
    """Остановка бота"""
    print("Stopping Bot Service...")
    await bot.session.close()
    await storage.close()
    