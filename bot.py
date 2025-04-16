import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage  # хранение состояний в памяти

from config import API_TOKEN
from commands import start, chart, report

logging.basicConfig(level=logging.INFO)

# Настраиваем бот с ParseMode и FSM-хранилищем
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
storage = MemoryStorage()  # хранит состояния в памяти; теряется при перезапуске :contentReference[oaicite:0]{index=0}
dp = Dispatcher(storage=storage)

# Регистрируем все роутеры (в том числе те, что будут работать в состоянии)
dp.include_routers(start.router, chart.router, report.router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
