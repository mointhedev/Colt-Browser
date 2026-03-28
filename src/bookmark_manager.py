import json
import os
import platform


def _get_data_dir() -> str:
    system = platform.system()
    if system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Colt")
    elif system == "Windows":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Colt")
    else:
        return os.path.expanduser("~/.config/Colt")


class BookmarkManager:

    def __init__(self):
        data_dir = _get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        self.filepath = os.path.join(data_dir, "bookmarks.json")
        self.bookmarks = []
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.bookmarks = json.load(f)

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.bookmarks, f, indent=2)

    def add_bookmark(self, url: str, name: str):
        if not self.is_bookmarked(url):
            self.bookmarks.append({"url": url, "name": name})
            self._save()

    def remove_bookmark(self, url: str):
        self.bookmarks = [b for b in self.bookmarks if b["url"] != url]
        self._save()

    def is_bookmarked(self, url: str) -> bool:
        return any(b["url"] == url for b in self.bookmarks)

    def get_all(self):
        return list(self.bookmarks)
