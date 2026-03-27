from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile


class BrowserTab(QObject):
    # Custom signals — browser.py will listen to these
    url_changed   = Signal(str)    # fires when page URL changes
    title_changed = Signal(str)    # fires when page title changes
    favicon_changed = Signal(object)  # fires when page icon changes

    def __init__(self, parent=None):
        super().__init__(parent)

        # This is the actual web page widget — Qt handles all rendering
        self.web_view = QWebEngineView()

        # Force English so sites serve English regardless of system locale
        profile = self.web_view.page().profile()
        profile.setHttpAcceptLanguage("en-US,en;q=0.9")

        # Connect Qt's built-in signals → our own methods
        self.web_view.urlChanged.connect(self._on_url_changed)
        self.web_view.titleChanged.connect(self._on_title_changed)
        self.web_view.iconChanged.connect(self._on_favicon_changed)

    def load(self, url: str):
        """Load a URL. Adds https:// if user didn't type it."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.web_view.load(QUrl(url))

    def _on_url_changed(self, qurl):
        self.url_changed.emit(qurl.toString())

    def _on_title_changed(self, title):
        self.title_changed.emit(title)

    def _on_favicon_changed(self, icon):
        self.favicon_changed.emit(icon)

    # Convenience wrappers so browser.py can call these directly
    def back(self):    self.web_view.back()
    def forward(self): self.web_view.forward()
    def reload(self):  self.web_view.reload()

    @property
    def url(self) -> str:
        return self.web_view.url().toString()

    @property
    def title(self) -> str:
        return self.web_view.title()
