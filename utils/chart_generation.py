import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os
from matplotlib.dates import AutoDateLocator, DateFormatter

def build_correlation_plot(file_path: str, col1: str, col2: str) -> str:
    # Читаем и чистим данные
    df = pd.read_excel(file_path)[[col1, col2]].replace([np.inf, -np.inf], np.nan).dropna()
    if df.empty:
        raise ValueError("Нет данных для построения графика.")

    x = df[col1]
    y = df[col2]

    # Вычисляем коэффициенты линии тренда
    slope, intercept = np.polyfit(x, y, 1)
    trend = slope * x + intercept

    # Создаём фигуру
    fig, ax = plt.subplots(figsize=(8, 6))

    # Рисуем гексагональную бинацию (hexbin) плотности точек
    hb = ax.hexbin(
        x, y,
        gridsize=40,          # плотность шестиугольников
        cmap='Blues',         # цветовая карта
        mincnt=1,             # игнорировать пустые бины
        linewidths=0.5,
        edgecolors='gray',
        alpha=0.8,
        zorder=0
    )
    # Цветовая шкала
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('Частота точек')

    # Рисуем линию тренда
    ax.plot(
        x, trend,
        color='crimson',
        linewidth=2,
        label='Линия тренда',
        zorder=1
    )

    # Подписи
    ax.set_title(f"Корреляция: {col1} vs {col2}", pad=15)
    ax.set_xlabel(col1)
    ax.set_ylabel(col2)
    ax.legend()

    plt.tight_layout()

    # Сохраняем в ту же папку, где файл
    out_dir = os.path.dirname(file_path)
    os.makedirs(out_dir, exist_ok=True)
    fname = f"corr_{uuid.uuid4().hex}.png"
    path = os.path.join(out_dir, fname)
    fig.savefig(path)
    plt.close(fig)
    return path

def build_time_series_plot(file_path: str, date_col: str, value_col: str) -> list[str]:
    import os
    import uuid
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.dates import AutoDateLocator, DateFormatter

    df = pd.read_excel(file_path)

    if date_col not in df.columns or value_col not in df.columns:
        raise ValueError("Указанные столбцы не найдены в данных.")

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna(subset=[date_col, value_col])
    df = df.sort_values(by=date_col)

    if df.empty:
        raise ValueError("Нет данных для построения графика.")

    min_date = df[date_col].min()
    max_date = df[date_col].max()
    total_days = (max_date - min_date).days

    # Разбиваем на сегменты по 60 дней (2 месяца)
    segment_length = 60
    segments = []
    start_date = min_date

    while start_date < max_date:
        end_date = start_date + pd.Timedelta(days=segment_length)
        segment_df = df[(df[date_col] >= start_date) & (df[date_col] < end_date)]
        if not segment_df.empty:
            segments.append(segment_df)
        start_date = end_date

    image_paths = []
    out_dir = os.path.dirname(file_path)
    os.makedirs(out_dir, exist_ok=True)

    for i, segment in enumerate(segments, start=1):
        x = segment[date_col]
        y = segment[value_col]

        # Преобразование дат в числовой формат для расчета линии тренда
        x_numeric = x.map(pd.Timestamp.toordinal)
        z = np.polyfit(x_numeric, y, 1)
        p = np.poly1d(z)
        trend = p(x_numeric)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, y, label='Значения', color='blue')
        ax.plot(x, trend, label='Тренд', color='red', linestyle='--')
        ax.set_title(f'Временной ряд: {value_col} по {date_col} (Сегмент {i} - до 2 месяцев)')
        ax.set_xlabel('Дата')
        ax.set_ylabel(value_col)
        ax.legend()
        ax.grid(True)

        # Настройка форматирования дат
        locator = AutoDateLocator()
        formatter = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout()

        filename = f"time_series_segment_{i}_{uuid.uuid4().hex}.png"
        path = os.path.join(out_dir, filename)
        fig.savefig(path)
        plt.close(fig)
        image_paths.append(path)

    return image_paths
