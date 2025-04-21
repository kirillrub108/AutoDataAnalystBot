import os
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

# Замените на ID вашего закрытого канала (начинается с -100...)
FEEDBACK_CHANNEL_ID = -1002538719877

class FeedbackStates(StatesGroup):
    waiting_for_feedback = State()

@router.message(F.text == "/feedback")
async def cmd_feedback(message: Message, state: FSMContext):
    await state.set_state(FeedbackStates.waiting_for_feedback)
    await message.answer(
        "📝 Напишите отзыв или пожелание в ответном сообщении.\n"
        "Чтобы отменить, нажмите /cancel.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(FeedbackStates.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    try:
        # Пересылаем полностью, со всеми вложениями
        await message.bot.forward_message(
            chat_id=FEEDBACK_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        await message.answer("✅ Отзыв отправлен. Спасибо!")
    except Exception as e:
        await message.answer(f"❌ Не удалось переслать отзыв: {e}")
    finally:
        # Завершаем FSM
        await state.clear()

@router.message(F.text == "/cancel")
async def cancel_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отмена.", reply_markup=ReplyKeyboardRemove())