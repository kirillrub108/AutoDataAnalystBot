import pandas as pd
from .file_processing import save_temp_file, remove_temp_file

async def generate_report_text(message):
    path = await save_temp_file(message)
    if not path:
        return "Ошибка: отправь корректный .xlsx файл."
    try:
        df = pd.read_excel(path)
        if df.empty:
            return "Файл пустой."
        desc = df.describe(include="all").transpose()
        report = "📋 *Аналитика данных:*\n"
        for col, stats in desc.iterrows():
            report += f"\n*{col}*\n"
            report += f"  • count: {int(stats['count'])}\n"
            if pd.api.types.is_numeric_dtype(df[col]):
                report += f"  • mean: {round(stats['mean'],2)}\n"
                report += f"  • min/max: {stats['min']}/{stats['max']}\n"
        return report
    except Exception as e:
        return f"Ошибка аналитики: {e}"
    finally:
        remove_temp_file(path)
