from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.file_processing import remove_temp_directory


class CleanupMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        state: FSMContext = data['state']
        current_state = await state.get_state()

        if event.text and event.text.startswith("/") and current_state:
            remove_temp_directory(event)
            await state.clear()

        return await handler(event, data)
