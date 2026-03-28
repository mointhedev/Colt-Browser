import os
import platform
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest


def _get_downloads_dir() -> str:
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.path.expanduser("~"), "Downloads")
    else:
        return os.path.expanduser("~/Downloads")  # macOS and Linux


class DownloadManager:

    def __init__(self):
        self.downloads = []

    def connect_profile(self, profile):
        profile.downloadRequested.connect(self._on_download_requested)

    def _on_download_requested(self, download: QWebEngineDownloadRequest):
        save_path = os.path.join(_get_downloads_dir(), download.suggestedFileName())
        download.setDownloadDirectory(_get_downloads_dir())
        download.setDownloadFileName(download.suggestedFileName())
        download.accept()

        entry = {
            "filename": download.suggestedFileName(),
            "path": save_path,
            "download": download,
        }
        self.downloads.append(entry)
        download.receivedBytesChanged.connect(lambda: self._on_progress(download))
        download.isFinishedChanged.connect(lambda: self._on_finished(download))

    def _on_progress(self, download: QWebEngineDownloadRequest):
        pass  # progress updates handled live in the UI

    def _on_finished(self, download: QWebEngineDownloadRequest):
        pass  # UI will reflect finished state on its own

    def get_all(self):
        return list(reversed(self.downloads))