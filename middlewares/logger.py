# middlewares/logger.py

import os
from datetime import datetime
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

LOGS_DIR = "logs"

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Определяем user_id и текст события
        if isinstance(event, Message):
            user_id = event.from_user.id
            action = event.text or (
                event.document.file_name if event.document else
                event.photo[-1].file_id if event.photo else
                "<non-text message>"
            )
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            action = f"callback: {event.data}"
        else:
            # можно расширить для других типов
            return await handler(event, data)

        # Формируем строку лога
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} | {action}\n"

        # Пишем в файл
        log_path = os.path.join(LOGS_DIR, f"{user_id}.txt")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception:
            # на проде лучше отдельно логировать ошибки логгера
            pass

        return await handler(event, data)
