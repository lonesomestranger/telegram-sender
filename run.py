import argparse
import asyncio
import logging

from sender.config import load_config
from sender.main import start_sending
from sender.utils import get_all_chats

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    parser = argparse.ArgumentParser(
        description="Telegram Sender: Автоматическая отправка сообщений по расписанию."
    )
    parser.add_argument(
        "--get-chats",
        action="store_true",
        help="Получить и вывести список всех ваших диалогов с их ID.",
    )
    args = parser.parse_args()

    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as e:
        logging.critical(f"Ошибка загрузки конфигурации: {e}")
        return

    if args.get_chats:
        await get_all_chats(config)
    else:
        await start_sending(config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Скрипт остановлен вручную.")
    except Exception as e:
        logging.critical(f"Произошла критическая ошибка: {e}", exc_info=True)
