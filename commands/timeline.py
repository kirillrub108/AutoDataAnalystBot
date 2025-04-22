import os
import pandas as pd

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.file_processing import save_temp_file, remove_temp_directory_by_file, detect_columns, get_numeric_columns
from utils.chart_generation import build_time_series_plot

router = Router()

class TimelineStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_value_column = State()

@router.message(F.text == "/timeline")
async def cmd_timeline(message: Message, state: FSMContext):
    await state.set_state(TimelineStates.waiting_for_file)
    await message.answer(
        "📈 Пришлите Excel-файл (.xlsx), чтобы построить временной ряд.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(TimelineStates.waiting_for_file, F.document)
async def handle_file(message: Message, state: FSMContext):
    file_path = await save_temp_file(message)
    if not file_path:
        await message.answer("❌ Ошибка: требуется файл в формате .xlsx.")
        await state.clear()
        return

    try:
        df = pd.read_excel(file_path)
        detected = detect_columns(df)
        date_col = detected.get("date_col")
        if not date_col:
            raise ValueError("Не удалось автоматически определить столбец с датой.")
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if df[date_col].isna().all():
            raise ValueError("Столбец с датой не содержит корректных значений.")
        df = df.dropna(subset=[date_col])

        numeric_cols = get_numeric_columns(file_path)
        if len(numeric_cols) == 0:
            raise ValueError("Не найдено числовых столбцов для анализа.")

        await state.update_data(file_path=file_path, date_col=date_col, numeric_cols=numeric_cols)

        keyboard_buttons = [KeyboardButton(text=col) for col in numeric_cols]
        grouped_buttons = [keyboard_buttons[i:i + 3] for i in range(0, len(keyboard_buttons), 3)]
        keyboard = ReplyKeyboardMarkup(keyboard=grouped_buttons, resize_keyboard=True)

        await state.set_state(TimelineStates.waiting_for_value_column)
        await message.answer("🔹 Выберите столбец значений для построения временного ряда:", reply_markup=keyboard)

    except Exception as e:
        remove_temp_directory_by_file(file_path)
        await message.answer(f"❌ Ошибка при обработке файла: {e}")
        await state.clear()

@router.message(TimelineStates.waiting_for_value_column)
async def handle_value_column(message: Message, state: FSMContext):
    value_col = message.text.strip()
    data = await state.get_data()
    numeric_cols = data.get("numeric_cols", [])
    if value_col not in numeric_cols:
        await message.answer("⚠️ Пожалуйста, выберите столбец из списка.")
        return

    file_path = data["file_path"]
    date_col = data["date_col"]

    try:
        image_paths = build_time_series_plot(file_path, date_col, value_col)
        for path in image_paths:
            photo = FSInputFile(path=path)
            await message.answer_photo(
                photo=photo,
                caption=f"📊 Временной ряд по столбцу «{value_col}»"
            )

        # Снова предлагаем выбрать столбец
        keyboard_buttons = [KeyboardButton(text=col) for col in numeric_cols]
        grouped_buttons = [keyboard_buttons[i:i + 3] for i in range(0, len(keyboard_buttons), 3)]
        keyboard = ReplyKeyboardMarkup(keyboard=grouped_buttons, resize_keyboard=True)

        await message.answer("🔁 Хотите построить другой временной ряд по этому же файлу?\nВыберите столбец значений.\n"
        "Или новый файл /timeline", reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"❌ Ошибка при построении графика: {e}")
