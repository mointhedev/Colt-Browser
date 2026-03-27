from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QLineEdit,
    QPushButton, QTabWidget, QWidget, QApplication
)
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon

from tab import BrowserTab


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Colt")
        self.resize(1280, 800)

        self._setup_toolbar()
        self._setup_tabs()
        self.add_tab("https://google.com")

    def _setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)  # prevent user from dragging toolbar out
        self.addToolBar(toolbar)

        self.btn_back = QPushButton("←")
        self.btn_forward = QPushButton("→")
        self.btn_reload = QPushButton("↺")

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL...")
        self.address_bar.returnPressed.connect(self._on_address_entered)

        toolbar.addWidget(self.btn_back)
        toolbar.addWidget(self.btn_forward)
        toolbar.addWidget(self.btn_reload)
        toolbar.addWidget(self.address_bar)

        self.btn_back.clicked.connect(self._on_back)
        self.btn_forward.clicked.connect(self._on_forward)
        self.btn_reload.clicked.connect(self._on_reload)

    def _setup_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)       # shows X button on each tab
        self.tabs.setDocumentMode(True)        # cleaner look on macOS
        self.tabs.tabCloseRequested.connect(self._on_tab_close)
        self.tabs.currentChanged.connect(self._on_tab_switched)
        self.setCentralWidget(self.tabs)

    def add_tab(self, url: str):
        tab = BrowserTab()

        # Use lambda to pass the tab itself into each handler
        # so we always know which tab fired the signal
        tab.url_changed.connect(lambda u, t=tab: self._on_url_changed(u, t))
        tab.title_changed.connect(lambda title, t=tab: self._on_title_changed(title, t))

        self.tabs.addTab(tab.web_view, "New Tab")
        tab.web_view.setProperty("tab_object", tab)
        self.tabs.setCurrentWidget(tab.web_view)
        tab.load(url)

    def _current_tab(self) -> BrowserTab | None:
        """Returns the BrowserTab object for the currently active tab."""
        widget = self.tabs.currentWidget()
        if widget:
            return widget.property("tab_object")
        return None

    def _on_address_entered(self):
        url = self.address_bar.text()
        tab = self._current_tab()
        if tab:
            tab.load(url)

    def _on_back(self):
        tab = self._current_tab()
        if tab:
            tab.back()

    def _on_forward(self):
        tab = self._current_tab()
        if tab:
            tab.forward()

    def _on_reload(self):
        tab = self._current_tab()
        if tab:
            tab.reload()

    def _on_tab_close(self, index: int):
        if self.tabs.count() > 1:  # don't close the last tab
            self.tabs.removeTab(index)

    def _on_tab_switched(self, index: int):
        """When user clicks a different tab, update address bar to that tab's URL."""
        tab = self._current_tab()
        if tab:
            self.address_bar.setText(tab.url)

    def _on_url_changed(self, url: str, tab: BrowserTab):
        # Only update address bar if this signal came from the currently active tab
        if tab == self._current_tab():
            self.address_bar.setText(url)

    def _on_title_changed(self, title: str, tab: BrowserTab):
        # Find which index this tab is at, update that specific tab's label
        index = self.tabs.indexOf(tab.web_view)
        if index >= 0 and title:
            self.tabs.setTabText(index, title[:30])
