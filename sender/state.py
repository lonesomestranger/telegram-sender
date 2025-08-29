import json
import logging
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = BASE_DIR / "state.json"


class StateManager:
    def __init__(self):
        self.state = self._load()

    def _load(self):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning(
                f"Файл состояния {STATE_FILE} не найден или поврежден. Создается новый."
            )
            return {"date": str(date.today()), "sent_count": 0}

    def save(self):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            logging.error(f"Не удалось сохранить файл состояния {STATE_FILE}: {e}")

    def check_and_reset_daily_counter(self):
        today_str = str(date.today())
        if self.state.get("date") != today_str:
            logging.info("Наступил новый день. Сбрасываем суточный счетчик сообщений.")
            self.state["date"] = today_str
            self.state["sent_count"] = 0
            self.save()

    @property
    def sent_count(self):
        return self.state.get("sent_count", 0)

    def increment_sent_count(self):
        self.state["sent_count"] = self.sent_count + 1
        self.save()
