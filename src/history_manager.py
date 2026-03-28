import json
import os
import platform
from datetime import datetime


def _get_data_dir() -> str:
    system = platform.system()
    if system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Colt")
    elif system == "Windows":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Colt")
    else:
        return os.path.expanduser("~/.config/Colt")


class HistoryManager:

    def __init__(self):
        data_dir = _get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        self.filepath = os.path.join(data_dir, "history.json")
        self.history = []
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.history = json.load(f)

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.history, f, indent=2)

    def add_entry(self, url: str, title: str):
        entry = {
            "url": url,
            "title": title,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        self._save()

    def get_all(self):
        return list(reversed(self.history))  # newest first