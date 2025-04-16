from aiogram.fsm.state import State, StatesGroup

class ChartStates(StatesGroup):
    waiting_for_file = State()     # бот ждёт файл для графика

class ReportStates(StatesGroup):
    waiting_for_file = State()     # бот ждёт файл для отчёта
