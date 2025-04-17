import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from .file_processing import save_temp_file, remove_temp_directory

async def generate_chart_image(message):
    path = await save_temp_file(message)
    if not path:
        return "Ошибка: отправь корректный .xlsx файл."
    try:
        df = pd.read_excel(path)
        plt.figure(figsize=(10, 6))

        # 1. Если есть дата — строим временной ряд
        date_cols = [c for c in df.columns if 'date' in c.lower() or 'дат' in c.lower()]
        if date_cols:
            dc = date_cols[0]
            df[dc] = pd.to_datetime(df[dc], errors='coerce')
            df = df.dropna(subset=[dc]).sort_values(dc)
            num = df.select_dtypes('number').columns
            if num.any():
                sns.lineplot(x=dc, y=num[0], data=df, marker='o')
                plt.title(f"Тренд: {num[0]} по {dc}")

        else:
            # 2. Корреляционная матрица
            corr = df.select_dtypes('number').corr()
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
            plt.title("Корреляционная матрица")

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        return buf

    except Exception as e:
        return f"Ошибка при построении графика: {e}"
    finally:
        remove_temp_file(path)
