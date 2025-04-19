from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from utils.file_processing import remove_temp_directory_by_msg

router = Router()

# Обработчик команды /cancel
@router.message(F.text == "/cancel")
async def cancel_handler(message: Message, state: FSMContext):
    # Очистка временной папки пользователя
    remove_temp_directory_by_msg(message)

    # Очищаем состояние
    await state.clear()

    # Ответ пользователю
    await message.answer("❌ Команда успешно отменена. Память очищена.")