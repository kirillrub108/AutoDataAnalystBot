from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import ReportStates
from utils.analytics import generate_report_text

router = Router()

@router.message(F.text == "/report")
async def cmd_report(message: Message, state: FSMContext):
    await state.set_state(ReportStates.waiting_for_file)
    await message.answer("Отправь мне Excel-файл, и я верну аналитический отчёт.")

@router.message(ReportStates.waiting_for_file, F.document)
async def process_report_file(message: Message, state: FSMContext):
    report = await generate_report_text(message)
    await message.answer(report)
    await state.clear()
