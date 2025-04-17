import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Tuple
from aiogram.types import Message
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import pandas as pd
from states import AggregateStates
from utils.file_processing import save_temp_file, remove_temp_directory

# Автоматическое определение колонок по ключевым словам
def detect_columns(df: pd.DataFrame) -> dict:
    columns = {
        'date_col': None,
        'price_col': None,
        'quantity_col': None,
        'category_col': None,
        'product_col': None
    }
    for col in df.columns:
        col_lower = col.lower()
        if any(word in col_lower for word in ['дата', 'date']):
            columns['date_col'] = col
        if any(word in col_lower for word in ['цена', 'price']):
            columns['price_col'] = col
        if any(word in col_lower for word in ['количество', 'quantity']):
            columns['quantity_col'] = col
        if any(word in col_lower for word in ['категория', 'category']):
            columns['category_col'] = col
        if any(word in col_lower for word in ['товар', 'product']):
            columns['product_col'] = col
    return columns

async def analyze_columns(message: Message, df: pd.DataFrame, df_columns: list, text: str):
    text = text.strip()

    # Разбор запроса: столбец или столбец:top_n
    requests = []
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        if ":" in token:
            col, n = token.split(":", 1)
            try:
                top_n = int(n.strip())
            except ValueError:
                top_n = None
            requests.append((col.strip(), top_n))
        else:
            requests.append((token, None))

    # Проверка наличия столбцов
    invalid = [col for col, _ in requests if col not in df_columns]
    if invalid:
        await message.answer(
            f"❌ Не найден(ы) столбец(ы): {', '.join(invalid)}. Пожалуйста, проверьте и попробуйте снова."
        )
        return

    for col, top_n in requests:
        column_data = df[col]
        missing = column_data.isna().sum()
        total = len(column_data)

        header = f"📌 *{col}*"
        parts = [header, f"• Пропущено: {missing} из {total} ({round(missing/total*100, 2)}%)"]
        parts.append("*Статистика по столбцу:*")

        if top_n is not None:
            unique = column_data.nunique(dropna=True)
            parts.append(f"  – Уникальных значений: {unique}")
            freq = column_data.value_counts(dropna=False).head(top_n)
            parts.append(f"*Топ-{top_n} по частоте:*")
            for val, cnt in freq.items():
                display = val if pd.notna(val) else "<пустое>"
                parts.append(f"  – {display}: {cnt}")
        else:
            if pd.api.types.is_numeric_dtype(column_data):
                stats = column_data.describe()
                q1, q3 = column_data.quantile(0.25), column_data.quantile(0.75)
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outliers = column_data[(column_data < lower) | (column_data > upper)].count()
                mode = column_data.mode().tolist()
                mode_display = ', '.join(map(str, mode)) if mode else '–'
                parts += [
                    f"  – Среднее: {round(stats['mean'], 2)}",
                    f"  – Медиана: {round(column_data.median(), 2)}",
                    f"  – Мода: {mode_display}",
                    f"  – Мин: {round(stats['min'], 2)}",
                    f"  – Макс: {round(stats['max'], 2)}",
                    f"  – Ст. отклонение: {round(stats['std'], 2)}",
                    f"  – Выбросы: {int(outliers)}",
                ]
            else:
                unique = column_data.nunique(dropna=True)
                parts.append(f"  – Уникальных значений: {unique}")
                freq = column_data.value_counts(dropna=False).head(5)
                parts.append(f"*Топ-5 по частоте:*")
                for val, cnt in freq.items():
                    display = val if pd.notna(val) else "<пустое>"
                    parts.append(f"  – {display}: {cnt}")

        await message.answer("\n".join(parts), parse_mode="Markdown")

async def generate_report(file_path: str, date_col: str, analyze_cols: list, group_by: str) -> Tuple[str, list]:
    plots = []
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return "❌ Файл пустой.", []

        detected = detect_columns(df)
        report = ["📈 *Аналитический отчет:*"]

        # Расчет выручки, если есть цена и количество
        if detected['price_col'] and detected['quantity_col']:
            df['Выручка'] = df[detected['price_col']] * df[detected['quantity_col']]
            analyze_cols.append('Выручка')

        # Группировка данных
        if group_by and detected['date_col']:
            df[detected['date_col']] = pd.to_datetime(df[detected['date_col']], errors='coerce')
            df['Месяц'] = df[detected['date_col']].dt.to_period('M')
            grouped = df.groupby([group_by, 'Месяц'])[analyze_cols].agg(['sum', 'mean'])
            report.append(f"\n📅 *Динамика по {group_by}:*\n```{grouped.head().to_string()}```")

        # Топ-5 товаров по выручке
        if 'Выручка' in df.columns and detected['product_col']:
            top_products = df.nlargest(5, 'Выручка')[[detected['product_col'], 'Выручка']]
            report.append("\n🏆 *Топ-5 товаров:*")
            for _, row in top_products.iterrows():
                report.append(f"  • {row[detected['product_col']]}: {row['Выручка']} ₽")

        # Визуализация
        plt.figure()
        sns.barplot(data=df, x=detected['category_col'], y='Выручка', estimator=sum)
        plt.title('Выручка по категориям')
        plot_path = 'sales_by_category.png'
        plt.savefig(plot_path)
        plots.append(plot_path)

        return "\n".join(report), plots

    except Exception as e:
        return f"❌ Ошибка: {str(e)}", []
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)