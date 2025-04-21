import os
import pandas as pd

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.file_processing import save_temp_file, remove_temp_directory_by_file, remove_temp_directory_by_msg, get_columns_list, get_numeric_columns
from utils.chart_generation import build_correlation_plot

router = Router()

class CorrelationStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_first_column = State()
    waiting_for_second_column = State()

@router.message(F.text == "/correlation")
async def cmd_correlation(message: Message, state: FSMContext):
    await state.set_state(CorrelationStates.waiting_for_file)
    await message.answer(
        "📈 Пришлите Excel-файл (.xlsx), чтобы построить график корреляции между двумя числовыми столбцами.\n",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(CorrelationStates.waiting_for_file, F.document)
async def handle_file(message: Message, state: FSMContext):
    file_path = await save_temp_file(message)
    if not file_path:
        await message.answer("❌ Ошибка: требуется файл в формате .xlsx.")
        await state.clear()
        return

    try:
        columns = get_numeric_columns(file_path)
    except Exception as e:
        remove_temp_directory_by_file(file_path)
        await message.answer(f"❌ Ошибка при чтении Excel-файла: {e}")
        await state.clear()
        return

    if len(columns) < 2:
        remove_temp_directory_by_file(file_path)
        await message.answer("⚠️ В файле должно быть хотя бы два числовых столбца.")
        await state.clear()
        return

    await state.update_data(file_path=file_path, columns=columns)

    # Группируем кнопки по 3 в ряд
    keyboard_buttons = [KeyboardButton(text=col) for col in columns]
    grouped_buttons = [keyboard_buttons[i:i + 3] for i in range(0, len(keyboard_buttons), 3)]

    keyboard = ReplyKeyboardMarkup(
        keyboard=grouped_buttons,
        resize_keyboard=True
    )

    await state.set_state(CorrelationStates.waiting_for_first_column)
    await message.answer("🔹 Выберите *первый* числовой столбец:", reply_markup=keyboard)

@router.message(CorrelationStates.waiting_for_first_column)
async def handle_first_column(message: Message, state: FSMContext):
    data = await state.get_data()
    columns = data["columns"]

    col1 = message.text.strip()
    if col1 not in columns:
        await message.answer("⚠️ Пожалуйста, выберите столбец из списка.")
        return

    await state.update_data(col1=col1)
    await state.set_state(CorrelationStates.waiting_for_second_column)
    await message.answer("🔹 Теперь выберите *второй* столбец:")

@router.message(CorrelationStates.waiting_for_second_column)
async def handle_second_column(message: Message, state: FSMContext):
    data = await state.get_data()
    file_path = data["file_path"]
    columns = data["columns"]
    col1 = data["col1"]
    col2 = message.text.strip()

    if col2 not in columns:
        await message.answer("⚠️ Пожалуйста, выберите столбец из списка.")
        return

    if col1 == col2:
        await message.answer("⚠️ Столбцы должны быть разными. Попробуйте другой.")
        return

    try:
        image_path = build_correlation_plot(file_path, col1, col2)
    except ValueError as e:
        await message.answer(f"❌ {e}")
        return
    except Exception as e:
        await message.answer(f"❌ Ошибка при построении графика: {e}")
        return

    # Отправляем график
    photo = FSInputFile(path=image_path)
    await message.answer_photo(
        photo=photo,
        caption=f"📊 Корреляция между «{col1}» и «{col2}»"
    )

    # Предлагаем снова выбрать столбцы
    keyboard_buttons = [KeyboardButton(text=col) for col in columns]
    grouped_buttons = [keyboard_buttons[i:i + 3] for i in range(0, len(keyboard_buttons), 3)]

    keyboard = ReplyKeyboardMarkup(
        keyboard=grouped_buttons,
        resize_keyboard=True
    )

    await state.set_state(CorrelationStates.waiting_for_first_column)
    await message.answer(
        "🔁 Хотите построить другой график?\nВыберите *первый* столбец:",
        reply_markup=keyboard
    )
