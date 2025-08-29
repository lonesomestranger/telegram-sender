import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Файл конфигурации {CONFIG_FILE} не найден. "
            f"Скопируйте 'config.example.json' в 'config.json' и настройте его."
        )

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        raise ValueError(
            f"Ошибка декодирования JSON в файле {CONFIG_FILE}. Проверьте синтаксис."
        )

    required_keys = [
        "api_id",
        "api_hash",
        "session_name",
        "daily_message_limit",
        "delay_seconds",
        "targets",
    ]
    for key in required_keys:
        if key not in config:
            raise ValueError(
                f"В файле конфигурации отсутствует обязательный ключ: '{key}'"
            )

    return config
