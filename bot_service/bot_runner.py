import asyncio
import logging
from app.bot.dispatcher import start_bot

# Настройка логирования, чтобы видеть работу бота в консоли Docker
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    try:
        # Запуск асинхронной функции start_bot из dispatcher.py
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
        