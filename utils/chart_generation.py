import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os

def build_correlation_plot(file_path: str, col1: str, col2: str) -> str:
    df = pd.read_excel(file_path)

    if col1 not in df.columns or col2 not in df.columns:
        raise ValueError("Один или оба выбранных столбца не найдены.")
    if not pd.api.types.is_numeric_dtype(df[col1]) or not pd.api.types.is_numeric_dtype(df[col2]):
        raise ValueError("Оба столбца должны содержать числовые значения.")

    # Оставляем только нужные столбцы, заменяем бесконечности на NaN и убираем их
    df = df[[col1, col2]].replace([np.inf, -np.inf], np.nan).dropna()

    # Проверка: есть ли после очистки хоть какие-то данные
    if df.empty:
        raise ValueError("Нет достаточных данных для построения графика.")

    x = df[col1]
    y = df[col2]

    # Расчёт коэффициентов линии тренда
    slope, intercept = np.polyfit(x, y, 1)
    trend_line = slope * x + intercept

    # Создаём фигуру и оси
    fig, ax = plt.subplots(figsize=(8, 6))

    # Сетка
    ax.grid(
        True,
        which='major',
        linestyle='--',
        linewidth=0.5,
        alpha=0.7,
        zorder=0
    )

    # Точки
    ax.scatter(
        x,
        y,
        c='darkblue',
        alpha=0.7,
        edgecolor='white',
        linewidth=0.5,
        zorder=1
    )

    # Линия тренда
    ax.plot(
        x,
        trend_line,
        color='crimson',
        linewidth=2,
        label='Линия тренда',
        zorder=2
    )

    # Подписи и легенда
    ax.set_title(f"Корреляция: {col1} и {col2}", pad=15)
    ax.set_xlabel(col1)
    ax.set_ylabel(col2)
    ax.legend()

    # Плотная компоновка
    plt.tight_layout()

    # Сохранение
    temp_dir = os.path.dirname(file_path)
    os.makedirs(temp_dir, exist_ok=True)
    filename = f"plot_{uuid.uuid4().hex}.png"
    path = os.path.join(temp_dir, filename)
    fig.savefig(path)
    plt.close(fig)

    return path

def build_time_series_plot(file_path: str, date_col: str, value_col: str) -> str:
    df = pd.read_excel(file_path)

    if date_col not in df.columns or value_col not in df.columns:
        raise ValueError("Указанные столбцы не найдены в данных.")

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col, value_col])
    df = df.sort_values(by=date_col)

    x = df[date_col]
    y = pd.to_numeric(df[value_col], errors='coerce')

    # Удаление NaN значений
    mask = y.notna()
    x = x[mask]
    y = y[mask]

    # Преобразование дат в числовой формат для расчета линии тренда
    x_numeric = x.map(pd.Timestamp.toordinal)
    z = np.polyfit(x_numeric, y, 1)
    p = np.poly1d(z)
    trend = p(x_numeric)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, label='Значения', color='blue')
    ax.plot(x, trend, label='Тренд', color='red', linestyle='--')
    ax.set_title(f'Временной ряд: {value_col} по {date_col}')
    ax.set_xlabel('Дата')
    ax.set_ylabel(value_col)
    ax.legend()
    ax.grid(True)

    plt.tight_layout()

    filename = f"time_series_{uuid.uuid4().hex}.png"
    path = os.path.join(os.path.dirname(file_path), filename)
    fig.savefig(path)
    plt.close(fig)

    return path