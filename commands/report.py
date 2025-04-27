import os
import pandas as pd

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums.parse_mode import ParseMode

from utils.file_processing import save_temp_file, remove_temp_directory_by_file
from utils.analytics import generate_report

router = Router()

class ReportStates(StatesGroup):
    waiting_for_file = State()

@router.message(F.text == "/report")
async def cmd_report(message: Message, state: FSMContext):
    await state.set_state(ReportStates.waiting_for_file)
    await message.answer(
        "📝 Пришлите Excel-файл (.xlsx), чтобы получить аналитический отчет по всем столбцам.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(ReportStates.waiting_for_file, F.document)
async def handle_report(message: Message, state: FSMContext):
    file_path = await save_temp_file(message)
    if not file_path:
        await message.answer("❌ Ошибка: требуется файл в формате .xlsx.")
        await state.clear()
        return

    await message.answer(
        "Отчет генерируется\n" \
        "Пожалуйста подождите",
        reply_markup=ReplyKeyboardRemove()
    )

    # Генерация отчета и диаграмм
    report_text, plots = generate_report(file_path)

    # Отправляем текст отчета
    MAX_LEN = 4000
    for i in range(0, len(report_text), MAX_LEN):
        await message.answer(report_text[i:i + MAX_LEN], parse_mode=ParseMode.MARKDOWN)

    # Отправляем диаграммы
    for plot_path in plots:
        if os.path.exists(plot_path):
            await message.answer_photo(photo=FSInputFile(plot_path))

    # Удаляем временные файлы
    remove_temp_directory_by_file(file_path)
    await state.clear()

    # Предложение повторить
    await message.answer(
        "✅ Отчет готов!\n" \
        "Для нового отчета отправьте /report",
        reply_markup=ReplyKeyboardRemove()
    )