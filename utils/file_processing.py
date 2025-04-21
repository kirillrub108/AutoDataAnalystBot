import os
import pandas as pd
import shutil
from uuid import uuid4

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

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

def get_columns_list(file_path: str) -> list[str]:
    df = pd.read_excel(file_path)
    return df.columns.tolist()

def get_numeric_columns(file_path: str) -> list[str]:
    df = pd.read_excel(file_path)

    # Выбираем только числовые столбцы
    numeric_df = df.select_dtypes(include=['number'])

    return numeric_df.columns.tolist()

async def save_temp_file(message):
    user_id = message.from_user.id  # Получаем уникальный user_id
    user_temp_dir = os.path.join(TEMP_DIR, str(user_id))  # Создаем папку для конкретного пользователя
    os.makedirs(user_temp_dir, exist_ok=True)  # Если папка не существует, создаем её

    doc = message.document
    if not doc.file_name.lower().endswith(".xlsx"):
        return None

    # Генерируем уникальное имя для файла в рамках папки пользователя
    file_path = os.path.join(user_temp_dir, f"{uuid4().hex}_{doc.file_name}")

    # Загружаем файл в эту папку
    await message.bot.download(doc, destination=file_path)
    return file_path


def remove_temp_directory_by_file(file_path: str):
    """
    Удаляет временную директорию, в которой находится переданный файл.
    """
    temp_dir = os.path.dirname(file_path)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def remove_temp_directory_by_msg(message):
    user_id = message.from_user.id
    user_temp_dir = os.path.join(TEMP_DIR, str(user_id))
    if os.path.exists(user_temp_dir) and os.path.isdir(user_temp_dir):
        # Удаление папки с файлами пользователя
        shutil.rmtree(user_temp_dir)
