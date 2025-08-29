import logging
from pathlib import Path

from telethon import TelegramClient

BASE_DIR = Path(__file__).resolve().parent.parent


async def get_all_chats(config: dict):
    api_id = config["api_id"]
    api_hash = config["api_hash"]
    session_path = str(BASE_DIR / config["session_name"])
    output_file = BASE_DIR / "chats.txt"

    client = TelegramClient(session_path, api_id, api_hash)

    logging.info("Подключаюсь к Telegram для получения списка чатов...")
    async with client:
        logging.info("Подключение успешно. Получаю список диалогов...")

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("Список ваших диалогов и их ID:\n")
                f.write("=" * 40 + "\n")
                async for dialog in client.iter_dialogs():
                    f.write(f'Название: "{dialog.name}" | ID: {dialog.id}\n')
            logging.info(f"ID диалогов успешно сохранены в файл: {output_file}")
        except IOError as e:
            logging.error(f"Не удалось записать в файл {output_file}: {e}")
