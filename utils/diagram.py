import pandas as pd
import matplotlib.pyplot as plt
import uuid
import os

def build_diagram(file_path: str, cat_col: str, num_col: str) -> str:
    """
    Читает Excel-файл, агрегирует числовые значения по категориям
    и строит столбчатую диаграмму.
    Возвращает путь к сохранённому PNG.
    """
    df = pd.read_excel(file_path)

    # Проверка наличия столбцов
    if cat_col not in df.columns or num_col not in df.columns:
        raise ValueError("Один из выбранных столбцов не найден в файле.")

    # Приведение метрики к числовому и удаление пустых строк
    df[num_col] = pd.to_numeric(df[num_col], errors='coerce')
    df = df[[cat_col, num_col]].dropna()
    if df.empty:
        raise ValueError("Нет данных для построения диаграммы.")

    # Агрегируем и сортируем по возрастанию
    agg = df.groupby(cat_col)[num_col].sum().sort_values()

    # Построение диаграммы
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(agg.index.astype(str), agg.values, zorder=3)
    ax.set_title(f"Диаграмма: {cat_col} vs {num_col}", pad=15)
    ax.set_xlabel(cat_col)
    ax.set_ylabel(num_col)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7, zorder=0)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Сохранение в ту же временную папку, где лежит исходный файл
    temp_dir = os.path.dirname(file_path)
    os.makedirs(temp_dir, exist_ok=True)
    filename = f"diagram_{uuid.uuid4().hex}.png"
    path = os.path.join(temp_dir, filename)
    fig.savefig(path)
    plt.close(fig)

    return path
