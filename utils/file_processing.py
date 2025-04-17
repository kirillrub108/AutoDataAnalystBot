import os
import shutil
from uuid import uuid4

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)


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


def remove_temp_directory(message):
    user_id = message.from_user.id
    user_temp_dir = os.path.join(TEMP_DIR, str(user_id))
    if os.path.exists(user_temp_dir) and os.path.isdir(user_temp_dir):
        # Удаление папки с файлами пользователя
        shutil.rmtree(user_temp_dir)
