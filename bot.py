import asyncio, logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from middlewares.logger import LoggingMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage  # хранение состояний в памяти

from middlewares.cleanup import CleanupMiddleware
from commands import start, cancel, correlation, report, aggregate, diagram, timeline, feedback

logging.basicConfig(level=logging.INFO)

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Настраиваем бот с ParseMode и FSM-хранилищем
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
storage = MemoryStorage()  # хранит состояния в памяти; теряется при перезапуске :contentReference[oaicite:0]{index=0}
dp = Dispatcher(storage=storage)
dp.message.middleware(CleanupMiddleware())
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())

# Регистрируем все роутеры (в том числе те, что будут работать в состоянии)
dp.include_routers(start.router, cancel.router, correlation.router, report.router, aggregate.router, diagram.router, timeline.router, feedback.router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
