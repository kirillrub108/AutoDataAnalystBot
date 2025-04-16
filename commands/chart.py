from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from states import ChartStates
from utils.chart_generation import generate_chart_image

router = Router()

@router.message(F.text == "/chart")
async def cmd_chart(message: Message, state: FSMContext):
    # Переводим пользователя в состояние ожидания файла
    await state.set_state(ChartStates.waiting_for_file)
    await message.answer("Отправь мне Excel-файл, и я построю график.")

@router.message(ChartStates.waiting_for_file, F.document)
async def process_chart_file(message: Message, state: FSMContext):
    buf_or_error = await generate_chart_image(message)
    if isinstance(buf_or_error, str):
        # если вернулась ошибка
        await message.answer(buf_or_error)
    else:
        await message.answer_photo(
            BufferedInputFile(buf_or_error.getvalue(), filename="chart.png"),
            caption="Вот ваш график 📊"
        )
    # Сбрасываем состояние, чтобы бот не ловил файлы дальше
    await state.clear()
