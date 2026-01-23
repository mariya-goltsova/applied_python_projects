import logging
from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if isinstance(event, Message):
            logger.info(
                f"Получено сообщение: {event.text} от user_id={event.from_user.id}"
            )
        return await handler(event, data)
