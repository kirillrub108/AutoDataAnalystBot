from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states import ReportStates
from utils.analytics import generate_report
from utils.file_processing import save_temp_file

router = Router()


@router.message(F.text == "/report")
async def cmd_report(message: Message, state: FSMContext):
    await state.set_state(ReportStates.waiting_for_file)
    await message.answer(
        "📊 Отправьте Excel-файл для анализа. "
        "Поддерживаются колонки на русском/английском (цена, количество, категория, дата).",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(ReportStates.waiting_for_file, F.document)
async def process_file(message: Message, state: FSMContext):
    file_path = await save_temp_file(message)
    if not file_path:
        await message.answer("❌ Ошибка: требуется файл в формате .xlsx.")
        await state.clear()
        return

    await state.update_data(file_path=file_path)
    await state.set_state(ReportStates.waiting_for_columns)
    await message.answer(
        "🔍 Укажите параметры (через запятую):\n"
        "1. Колонка с датой (например: 'дата', 'saledate')\n"
        "2. Колонки для анализа (например: 'цена', 'количество', 'категория')\n"
        "3. Группировка (например: 'категория', 'месяц', 'клиент')\n\n"
        "Пример: `дата, цена количество, категория`"
    )


@router.message(ReportStates.waiting_for_columns)
async def process_columns(message: Message, state: FSMContext):
    user_input = message.text.split(',')
    if len(user_input) != 3:
        await message.answer("❌ Неверный формат. Попробуйте снова.")
        return

    date_col = user_input[0].strip().lower()
    analyze_cols = [col.strip() for col in user_input[1].split()]
    group_by = user_input[2].strip().lower()

    data = await state.get_data()
    report, plots = await generate_report(data['file_path'], date_col, analyze_cols, group_by)

    # Отправка текстового отчета
    await message.answer(report, parse_mode="Markdown")

    # Отправка графиков
    for plot_path in plots:
        with open(plot_path, 'rb') as plot_file:
            await message.answer_photo(plot_file)

    await state.clear()