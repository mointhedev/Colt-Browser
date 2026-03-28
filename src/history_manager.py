import json
import os
from datetime import datetime


class HistoryManager:

    def __init__(self, filepath: str):
        self.filepath = filepath
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