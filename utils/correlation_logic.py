import pandas as pd
import matplotlib.pyplot as plt
import uuid
import os

def get_columns_list(file_path: str) -> list[str]:
    df = pd.read_excel(file_path)
    return df.columns.tolist()

def build_correlation_plot(file_path: str, col1: str, col2: str) -> str:
    df = pd.read_excel(file_path)

    if col1 not in df.columns or col2 not in df.columns:
        raise ValueError("Один или оба выбранных столбца не найдены.")
    if not pd.api.types.is_numeric_dtype(df[col1]) or not pd.api.types.is_numeric_dtype(df[col2]):
        raise ValueError("Оба столбца должны содержать числовые значения.")

    # Создаём фигуру и оси
    fig, ax = plt.subplots(figsize=(8, 6))

    # Рисуем сетку позади точек
    ax.grid(
        True,
        which='major',
        linestyle='--',
        linewidth=0.5,
        alpha=0.7,
        zorder=0
    )

    # Рисуем точки поверх сетки
    ax.scatter(
        df[col1],
        df[col2],
        c='darkblue',          # более насыщенный оттенок
        alpha=0.7,             # чуть более плотные точки
        edgecolor='white',     # тонкий белый контур
        linewidth=0.5,
        zorder=1
    )

    # Подписи и заголовок
    ax.set_title(f"Корреляция: {col1} vs {col2}", pad=15)
    ax.set_xlabel(col1)
    ax.set_ylabel(col2)

    # Плотнее упакуем элементы
    plt.tight_layout()

    # Сохраняем
    temp_dir = os.path.dirname(file_path)
    os.makedirs(temp_dir, exist_ok=True)
    filename = f"plot_{uuid.uuid4().hex}.png"
    path = os.path.join(temp_dir, filename)
    fig.savefig(path)
    plt.close(fig)

    return path
