from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        text=(
            "👋 Привет! Я — <b>AutoDataAnalystBot</b> 🤖\n"
            "Помогаю анализировать Excel‑таблицы и быстро получать ценные инсайты 📊\n\n"
            "<b>📌 Доступные команды:</b>\n"
            "➤ <b>/aggregate</b> — агрегация по столбцу: рассчитаю сумму, среднее, минимум и максимум\n"
            "➤ <b>/report</b> — полный аналитический отчёт по всей таблице\n"
            "➤ <b>/diagram</b> — построение столбчатой диаграммы по выбранным столбцам\n"
            "➤ <b>/correlation</b> — Тепловая карта корреляции между двумя числовыми столбцами 📈\n"
            "➤ <b>/timeline</b> — временной график изменения показателей по датам ⏳\n"
            "➤ <b>/feedback</b> — оставить отзыв или пожелание разработчику 💬\n\n"
            "<b>📎 Как пользоваться:</b>\n"
            "1. Выберите нужную команду\n"
            "2. Отправьте Excel‑файл (.xlsx)\n"
            "3. Следуйте подсказкам бота ✨\n\n"
            "<i>Если нужна помощь — просто напишите /start или /feedback</i> ❤️"
        ),
        parse_mode=ParseMode.HTML
    )
