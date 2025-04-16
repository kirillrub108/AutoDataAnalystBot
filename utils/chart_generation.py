import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from .file_processing import save_temp_file, remove_temp_file

async def generate_chart_image(message):
    path = await save_temp_file(message)
    if not path:
        return "Ошибка: отправь корректный .xlsx файл."
    try:
        df = pd.read_excel(path)
        nums = df.select_dtypes(include="number").columns
        if nums.empty:
            return "В файле нет числовых столбцов."
        col = nums[0]
        fig, ax = plt.subplots()
        df[col].plot(kind="line", marker="o", ax=ax, title=col)
        ax.grid(True)
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        return f"Ошибка при построении: {e}"
    finally:
        remove_temp_file(path)
