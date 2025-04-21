from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import pandas as pd
from states import AggregateStates
from utils.analytics import analyze_columns
from utils.file_processing import save_temp_file, remove_temp_directory_by_file, remove_temp_directory_by_msg, get_columns_list

router = Router()

@router.message(F.text == "/aggregate")
async def cmd_column_info(message: Message, state: FSMContext):
    await state.set_state(AggregateStates.waiting_for_file)
    await message.answer(
        "🗂️ Отправьте Excel-файл для анализа выбранных столбцов.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(AggregateStates.waiting_for_file, F.document)
async def process_file(message: Message, state: FSMContext):
    file_path = await save_temp_file(message)
    if not file_path:
        await message.answer("❌ Ошибка: требуется файл в формате .xlsx.")
        await state.clear()
        return

    try:
        columns_list = get_columns_list(file_path)
        columns_text = "\n".join([f"• {col}" for col in columns_list])
        await state.update_data(file_path=file_path, df_columns=columns_list)
        await state.set_state(AggregateStates.waiting_for_column)
        await message.answer(
            f"📊 *Доступные столбцы*:\n{columns_text}\n\n"
            "🔹Введите столбцы (*без ошибок*) для анализа через запятую.\n"
            "🔹При необходимости вывода частотности, укажите после названия через двоеточие количество позиций топа, например:\n"
            "*категория:4, цена, город:10*\n"
            'так для столбцов с ":" будет выведен топ значений в указанном количестве и кол-во уникальных значений'
        )
    except Exception as e:
        remove_temp_directory_by_file(file_path)
        await message.answer(f"❌ Ошибка при чтении файла: {e}")
        await state.clear()

@router.message(AggregateStates.waiting_for_column)
async def process_columns(message: Message, state: FSMContext):
    data = await state.get_data()
    df = pd.read_excel(data['file_path'])
    await analyze_columns(message, df, data['df_columns'], message.text)

    await message.answer(
        "🔁 Хотите продолжить?\n"
        "Введите другие столбцы через запятую",
        reply_markup=kb
    )
