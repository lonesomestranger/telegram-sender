import asyncio
import logging
from datetime import datetime, time, timedelta
from pathlib import Path

from telethon import TelegramClient
from telethon.errors.rpcerrorlist import (
    ChatWriteForbiddenError,
    PeerFloodError,
    UserIsBlockedError,
)

from .state import StateManager

BASE_DIR = Path(__file__).resolve().parent.parent


async def start_sending(config: dict):
    state_manager = StateManager()

    api_id = config["api_id"]
    api_hash = config["api_hash"]
    session_path = str(BASE_DIR / config["session_name"])
    daily_limit = config["daily_message_limit"]
    delay = config["delay_seconds"]
    targets = config["targets"]

    client = TelegramClient(session_path, api_id, api_hash)

    logging.info("Скрипт запущен. Попытка подключения к Telegram...")

    async with client:
        logging.info("Клиент успешно подключен.")

        while True:
            state_manager.check_and_reset_daily_counter()

            if state_manager.sent_count >= daily_limit:
                logging.info(f"Суточный лимит сообщений ({daily_limit}) достигнут.")
                now = datetime.now()
                tomorrow = now.date() + timedelta(days=1)
                midnight = datetime.combine(tomorrow, time.min)
                sleep_seconds = (midnight - now).total_seconds() + 5
                logging.info(
                    f"Работа будет возобновлена завтра. Сон на {int(sleep_seconds)} секунд."
                )
                await asyncio.sleep(sleep_seconds)
                continue

            logging.info("Начинаем цикл отправки сообщений.")
            for target in targets:
                if state_manager.sent_count >= daily_limit:
                    logging.warning(
                        "Лимит достигнут в середине цикла отправки. Прерываем."
                    )
                    break

                chat_id = target["chat_id"]
                message_text = target["message_text"]

                try:
                    await client.send_message(chat_id, message_text, parse_mode="md")
                    state_manager.increment_sent_count()
                    logging.info(
                        f"Сообщение успешно отправлено в '{chat_id}'. "
                        f"Всего за сегодня: {state_manager.sent_count}/{daily_limit}."
                    )
                except (ValueError, TypeError) as e:
                    logging.error(
                        f"Не удалось найти чат: '{chat_id}'. Проверьте ID или username. Ошибка: {e}"
                    )
                except (ChatWriteForbiddenError, UserIsBlockedError) as e:
                    logging.error(
                        f"Нет прав на отправку в '{chat_id}' или пользователь заблокировал. Ошибка: {e}"
                    )
                except PeerFloodError:
                    logging.critical(
                        "Аккаунт получил временное ограничение (флуд). "
                        "Скрипт будет остановлен, чтобы избежать бана. Увеличьте 'delay_seconds'."
                    )
                    return
                except Exception as e:
                    logging.error(
                        f"Непредвиденная ошибка при отправке в '{chat_id}': {e}"
                    )

                logging.info(f"Пауза на {delay} секунд...")
                await asyncio.sleep(delay)

            logging.info(
                "Цикл отправки по всем целям завершен. Следующий круг начнется после паузы."
            )
