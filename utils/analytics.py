import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
from typing import Tuple
from aiogram.types import Message
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import pandas as pd
from states import AggregateStates
from utils.file_processing import save_temp_file, get_numeric_columns, detect_columns

async def analyze_columns(message: Message, df: pd.DataFrame, df_columns: list, text: str):
    text = text.strip()

    # Словарь для сопоставления lower‑версии имени столбца → оригинальное имя
    col_map = {col.lower(): col for col in df_columns}

    # Разбор запроса: столбец или столбец:top_n (регистр игнорируется)
    requests: list[tuple[str, int|None]] = []
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue

        if ":" in token:
            col_token, n = token.split(":", 1)
            col_key = col_token.strip().lower()
            top_n = None
            try:
                top_n = int(n.strip())
            except ValueError:
                top_n = None
        else:
            col_key = token.lower()
            top_n = None

        # Пытаемся найти реальное имя столбца
        real_col = col_map.get(col_key)
        requests.append((real_col, top_n) if real_col else (None, top_n))

    # Проверяем, какие столбцы не найдены
    invalid = [tok for tok, _ in requests if tok is None]
    if invalid:
        await message.answer(
            f"❌ Не найден(ы) столбец(ы): {', '.join(invalid)}. Пожалуйста, проверьте и попробуйте снова."
        )
        return

    # Для каждого валидного запроса выводим аналитику
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

def generate_report(file_path: str) -> Tuple[str, list]:
    """
    Генерирует текстовый отчет и список путей к сохраненным диаграммам.
    Бизнес‑метрики:
     - общая информация о DataFrame
     - пропуски/уникальности
     - описательные статистики для числовых столбцов
     - частотный анализ для категориальных
     - выручка (price*quantity): total, mean, median, max
     - временные метрики (первые/последние даты) если есть date_col
     - топ‑5 продуктов и категорий по выручке
     - сохраняет два графика: выручка по категориям и топ‑5 продуктов
    """
    plots = []
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return "❌ Файл пустой.", []

        report = ["📈 *Аналитический отчёт по файлу:*"]
        report.append(f"• Строк: {len(df)}, Столбцов: {len(df.columns)}")

        # Пропуски и уникальности
        report.append("\n*Пропуски и уникальности:*")
        for col in df.columns:
            miss = df[col].isna().sum()
            uniq = df[col].nunique(dropna=True)
            report.append(f"  • {col}: пропущено {miss}, уникальных {uniq}")

        # Описательные статистики для числовых
        num_cols = get_numeric_columns(file_path)
        if num_cols:
            report.append("\n*Числовые столбцы — описательная статистика:*")
            desc = df[num_cols].describe().T
            for col, row in desc.iterrows():
                report.append(
                    f"  • {col}: среднее={row['mean']:.2f}, медиана={df[col].median():.2f}, \n"
                    f"ст. отклонение={row['std']:.2f}, мин={row['min']:.2f}, макс={row['max']:.2f}"
                )

        # Частотный анализ категорий
        cat_cols = [c for c in df.columns if c not in num_cols]
        if cat_cols:
            report.append("\n*Категориальные столбцы — топ‑5 по частоте:*")
            for col in cat_cols:
                top5 = df[col].value_counts(dropna=False).head(5)
                report.append(f"  • {col}:")
                for val, cnt in top5.items():
                    disp = val if pd.notna(val) else "<пусто>"
                    report.append(f"      – {disp}: {cnt}")

        # Детектируем специальные поля
        detected = detect_columns(df)
        price_col = detected.get('price_col')
        qty_col   = detected.get('quantity_col')
        date_col  = detected.get('date_col')
        prod_col  = detected.get('product_col')
        cat_col   = detected.get('category_col')

        # Выручка
        if price_col and qty_col:
            df['Выручка'] = (
                pd.to_numeric(df[price_col], errors='coerce') *
                pd.to_numeric(df[qty_col], errors='coerce')
            )
            rev = df['Выручка'].dropna()
            report.append("\n*Метрики по выручке:*")
            report.append(f"  • Общая: {rev.sum():.2f}")
            report.append(f"  • Средняя: {rev.mean():.2f}")
            report.append(f"  • Медиана: {rev.median():.2f}")
            report.append(f"  • Максимум: {rev.max():.2f}")

            # Диаграмма выручки по категориям
            if cat_col:
                agg_cat = rev.groupby(df[cat_col]).sum().sort_values()
                fig, ax = plt.subplots(figsize=(8,5))
                sns.barplot(x=agg_cat.values, y=agg_cat.index.astype(str), ax=ax)
                ax.set_title("Выручка по категориям")
                plt.tight_layout()
                path_cat = os.path.join(
                    os.path.dirname(file_path),
                    f"rev_by_cat_{uuid.uuid4().hex}.png"
                )
                fig.savefig(path_cat); plt.close(fig)
                plots.append(path_cat)

            # Топ‑5 продуктов по выручке
            if prod_col:
                top_prod = df.groupby(prod_col)['Выручка'].sum().nlargest(5)
                fig, ax = plt.subplots(figsize=(8,5))
                sns.barplot(x=top_prod.values, y=top_prod.index.astype(str), ax=ax)
                ax.set_title("Топ‑5 продуктов по выручке")
                plt.tight_layout()
                path_prod = os.path.join(
                    os.path.dirname(file_path),
                    f"top5_prod_{uuid.uuid4().hex}.png"
                )
                fig.savefig(path_prod); plt.close(fig)
                plots.append(path_prod)

        # Временные метрики
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            valid_dates = df[date_col].dropna()
            if not valid_dates.empty:
                report.append("\n*Временные метрики:*")
                report.append(f"  • Первая дата: {valid_dates.min().date()}")
                report.append(f"  • Последняя дата: {valid_dates.max().date()}")
                report.append(f"  • Всего периодов: {valid_dates.nunique()}")

        return "\n".join(report), plots

    except Exception as e:
        return f"❌ Ошибка при формировании отчета: {e}", []