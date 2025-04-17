from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        text=(
            "👋 Привет! Я — <b>AutoDataAnalystBot</b> 🤖\n"
            "Помогаю анализировать Excel-таблицы и быстро получать ценные инсайты 📊\n\n"
            "<b>📌 Доступные команды:</b>\n"
            "➤ <b>/aggregate</b> — рассчитаю <i>сумму, среднее, минимум и максимум</i> по выбранным столбцам\n"
            "➤ <b>/report</b> — сформирую <i>подробный отчёт</i> по вашей таблице\n"
            "➤ <b>/correlation</b> — покажу <i>график корреляции</i> между двумя числовыми столбцами 📈\n"
            "➤ <b>/timeline</b> — построю <i>временной график</i> изменения показателей по датам ⏳\n"
            "➤ <b>/feedback</b> — отправьте <i>отзыв или пожелания</i> 💬\n\n"
            "<b>📎 Как пользоваться:</b>\n"
            "1. Выберите нужную команду\n"
            "2. Отправьте Excel-файл (.xlsx)\n"
            "3. Следуйте подсказкам бота ✨\n\n"
            "<i>Если понадобится помощь — всегда рядом!</i> ❤️"
        ),
        parse_mode=ParseMode.HTML
    )
