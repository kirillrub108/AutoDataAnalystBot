import os
from uuid import uuid4

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

async def save_temp_file(message):
    doc = message.document
    if not doc.file_name.lower().endswith(".xlsx"):
        return None
    path = os.path.join(TEMP_DIR, f"{uuid4().hex}_{doc.file_name}")
    await message.bot.download(doc, destination=path)
    return path

def remove_temp_file(path):
    if path and os.path.exists(path):
        os.remove(path)
