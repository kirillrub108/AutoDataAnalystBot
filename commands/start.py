from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я AutoDataAnalystBot 🤖\n\n"
        "— /chart — чтобы построить график 📊\n"
        "— /report — чтобы получить отчёт 📋"
    )
