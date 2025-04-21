import os

from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    FSInputFile,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.file_processing import (
    save_temp_file,
    remove_temp_directory_by_file,
    get_columns_list,
    get_numeric_columns,
)
from utils.diagram import build_diagram

router = Router()

class DiagramStates(StatesGroup):
    waiting_for_file = State()
    waiting_for_first_column = State()
    waiting_for_second_column = State()

@router.message(F.text == "/diagram")
async def cmd_diagram(message: Message, state: FSMContext):
    await state.set_state(DiagramStates.waiting_for_file)
    await message.answer(
        "📊 Пришлите Excel‑файл (.xlsx) с данными.\n"
        "Первый столбец — категории (например, сотрудники), второй — числовая метрика.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(DiagramStates.waiting_for_file, F.document)
async def handle_file(message: Message, state: FSMContext):
    file_path = await save_temp_file(message)
    if not file_path:
        await message.answer("❌ Ошибка: нужен файл в формате .xlsx.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    try:
        all_columns = get_columns_list(file_path)
        numeric_columns = get_numeric_columns(file_path)
    except Exception as e:
        remove_temp_directory_by_file(file_path)
        await message.answer(f"❌ Ошибка при чтении файла: {e}", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    if len(all_columns) < 2 or not numeric_columns:
        remove_temp_directory_by_file(file_path)
        await message.answer(
            "⚠️ Файл должен содержать минимум 2 столбца и как минимум 1 числовой.",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return

    # Сохраняем в состоянии
    await state.update_data(
        file_path=file_path,
        all_columns=all_columns,
        numeric_columns=numeric_columns
    )

    # Клавиатура для первого столбца
    buttons = [KeyboardButton(text=col) for col in all_columns]
    grouped = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    kb = ReplyKeyboardMarkup(
        keyboard=grouped,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(DiagramStates.waiting_for_first_column)
    await message.answer("🔹 Выберите *первый* столбец (категории):", reply_markup=kb)

@router.message(DiagramStates.waiting_for_first_column)
async def handle_first_column(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data["all_columns"]:
        await message.answer("⚠️ Пожалуйста, выберите столбец из списка.")
        return

    await state.update_data(col1=message.text)
    # Клавиатура для второго (числового) столбца
    buttons = [KeyboardButton(text=col) for col in data["numeric_columns"]]
    grouped = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    kb = ReplyKeyboardMarkup(
        keyboard=grouped,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(DiagramStates.waiting_for_second_column)
    await message.answer("🔹 Теперь выберите *второй* столбец (метрика):", reply_markup=kb)

@router.message(DiagramStates.waiting_for_second_column)
async def handle_second_column(message: Message, state: FSMContext):
    data = await state.get_data()
    file_path = data["file_path"]
    col1 = data["col1"]
    col2 = message.text

    if col2 not in data["numeric_columns"]:
        await message.answer("⚠️ Пожалуйста, выберите числовой столбец из списка.")
        return

    try:
        image_path = build_diagram(file_path, col1, col2)
    except ValueError as e:
        await message.answer(f"❌ {e}")
        return
    except Exception as e:
        await message.answer(f"❌ Ошибка при построении диаграммы: {e}")
        return

    # Отправляем пользователю график
    await message.answer_photo(
        photo=FSInputFile(path=image_path),
        caption=f"📊 Диаграмма: {col1} vs {col2}",
        reply_markup=ReplyKeyboardRemove()
    )

    # Предлагаем повторно выбрать столбцы
    buttons = [KeyboardButton(text=col) for col in data["all_columns"]]
    grouped = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    kb = ReplyKeyboardMarkup(
        keyboard=grouped,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(DiagramStates.waiting_for_first_column)
    await message.answer(
        "🔁 Хотите построить другую диаграмму?\n"
        "Выберите *первый* столбец:",
        reply_markup=kb
    )
