import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import setup_handlers
import logging
from middlewares import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

setup_handlers(dp)
dp.message.middleware(LoggingMiddleware())

async def main():
  logger.info('Бот запущен!')
  await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())