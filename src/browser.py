from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QLineEdit,
    QPushButton, QTabWidget, QWidget, QTabBar,
    QListWidget, QVBoxLayout
)
from PySide6.QtGui import QShortcut, QKeySequence
from tab import BrowserTab
from history_manager import HistoryManager
from bookmark_manager import BookmarkManager


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Colt")
        self.resize(1280, 800)
        self.plus_tab_index = None  # we'll use this to track the "+" tab
        self.history_manager = HistoryManager()
        self.bookmark_manager = BookmarkManager()

        self._setup_toolbar()
        self._setup_tabs()
        self.add_tab("https://google.com")

        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(lambda: self.add_tab("https://google.com"))
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self._close_current_tab)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self._on_reload)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self._show_history)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self._on_bookmark_clicked)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self._show_bookmarks)

    def _setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)  # prevent user from dragging toolbar out
        self.addToolBar(toolbar)

        self.btn_back = QPushButton("←")
        self.btn_forward = QPushButton("→")
        self.btn_reload = QPushButton("↺")
        self.btn_bookmark = QPushButton("☆")

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL...")
        self.address_bar.returnPressed.connect(self._on_address_entered)

        toolbar.addWidget(self.btn_back)
        toolbar.addWidget(self.btn_forward)
        toolbar.addWidget(self.btn_reload)
        toolbar.addWidget(self.address_bar)
        toolbar.addWidget(self.btn_bookmark)

        self.btn_back.clicked.connect(self._on_back)
        self.btn_forward.clicked.connect(self._on_forward)
        self.btn_reload.clicked.connect(self._on_reload)
        self.btn_bookmark.clicked.connect(self._on_bookmark_clicked)

    def _setup_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)  # shows X button on each tab
        self.tabs.setDocumentMode(True)  # cleaner look on macOS
        self.tabs.tabCloseRequested.connect(self._on_tab_close)
        self.tabs.currentChanged.connect(self._on_tab_switched)

        self.setCentralWidget(self.tabs)

    def add_tab(self, url: str):
        tab = BrowserTab()

        # Use lambda to pass the tab itself into each handler
        # so we always know which tab fired the signal
        tab.url_changed.connect(lambda u, t=tab: self._on_url_changed(u, t))
        tab.title_changed.connect(lambda title, t=tab: self._on_title_changed(title, t))
        tab.favicon_changed.connect(lambda icon, t=tab: self._on_favicon_changed(icon, t))

        self.tabs.addTab(tab.web_view, "New Tab")
        tab.web_view.setProperty("tab_object", tab)
        self.tabs.setCurrentWidget(tab.web_view)

        self.tabs.currentChanged.disconnect(self._on_tab_switched)

        if self.plus_tab_index is not None:
            self.tabs.removeTab(self.plus_tab_index)
        self.tabs.addTab(QWidget(), "+")
        self.plus_tab_index = self.tabs.count() - 1
        self.tabs.tabBar().setTabButton(self.plus_tab_index, QTabBar.ButtonPosition.LeftSide, None)

        self.tabs.currentChanged.connect(self._on_tab_switched)
        if not url:
            url = "https://google.com"
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
        current_text = self.tabs.tabText(self.tabs.currentIndex())
        if current_text == "History":
            self._show_history()
            return
        if current_text == "Bookmarks":
            self._show_bookmarks()
            return
        tab = self._current_tab()
        if tab:
            tab.reload()

    def _close_current_tab(self):
        index = self.tabs.currentIndex()
        if index != self.plus_tab_index and self.tabs.count() > 2:
            self.tabs.removeTab(index)
            self.plus_tab_index = self.tabs.count() - 1

    def _on_tab_close(self, index: int):
        if index == self.plus_tab_index:
            return
        if self.tabs.count() > 2:
            self.tabs.currentChanged.disconnect(self._on_tab_switched)
            self.tabs.removeTab(index)
            self.plus_tab_index = self.tabs.count() - 1
            # make sure we never land on the + tab
            new_index = min(index, self.plus_tab_index - 1)
            self.tabs.setCurrentIndex(new_index)
            self.tabs.currentChanged.connect(self._on_tab_switched)
            tab = self._current_tab()
            if tab:
                self.address_bar.setText(tab.url)

    def _on_tab_switched(self, index: int):
        if index == self.plus_tab_index:
            self.add_tab("https://google.com")
            return

        tab = self._current_tab()
        if tab:
            self.address_bar.setText(tab.url)
            self._update_bookmark_button(tab.url)

    def _on_url_changed(self, url: str, tab: BrowserTab):
        # Only update address bar if this signal came from the currently active tab
        if tab == self._current_tab():
            self.address_bar.setText(url)
            self._update_bookmark_button(url)
        title = tab.title or url
        self.history_manager.add_entry(url, title)

    def _show_history(self):
        existing_index = None
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "History":
                existing_index = i
                self.tabs.removeTab(i)
                self.plus_tab_index = self.tabs.count() - 1
                break

        widget = QWidget()
        layout = QVBoxLayout(widget)
        list_widget = QListWidget()
        for entry in self.history_manager.get_all():
            list_widget.addItem(f"{entry['time']}  —  {entry['title']}  —  {entry['url']}")
        list_widget.itemDoubleClicked.connect(lambda item: self.add_tab(item.text().split("  —  ")[-1]))
        layout.addWidget(list_widget)

        insert_at = existing_index if existing_index is not None else self.plus_tab_index
        self.tabs.insertTab(insert_at, widget, "History")
        self.plus_tab_index = self.tabs.count() - 1
        self.tabs.setCurrentIndex(insert_at)

    def _on_bookmark_clicked(self):
        tab = self._current_tab()
        if not tab:
            return
        url = tab.url
        if self.bookmark_manager.is_bookmarked(url):
            self.bookmark_manager.remove_bookmark(url)
        else:
            self.bookmark_manager.add_bookmark(url, tab.title or url)
        self._update_bookmark_button(url)

    def _update_bookmark_button(self, url: str):
        if self.bookmark_manager.is_bookmarked(url):
            self.btn_bookmark.setText("★")
        else:
            self.btn_bookmark.setText("☆")

    def _show_bookmarks(self):
        existing_index = None
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Bookmarks":
                existing_index = i
                self.tabs.removeTab(i)
                self.plus_tab_index = self.tabs.count() - 1
                break

        widget = QWidget()
        layout = QVBoxLayout(widget)
        list_widget = QListWidget()
        for entry in self.bookmark_manager.get_all():
            list_widget.addItem(f"{entry['name']}  —  {entry['url']}")
        list_widget.itemDoubleClicked.connect(lambda item: self.add_tab(item.text().split("  —  ")[-1]))
        layout.addWidget(list_widget)

        insert_at = existing_index if existing_index is not None else self.plus_tab_index
        self.tabs.insertTab(insert_at, widget, "Bookmarks")
        self.plus_tab_index = self.tabs.count() - 1
        self.tabs.setCurrentIndex(insert_at)

    def _on_title_changed(self, title: str, tab: BrowserTab):
        # Find which index this tab is at, update that specific tab's label
        index = self.tabs.indexOf(tab.web_view)
        if index >= 0 and title:
            self.tabs.setTabText(index, title[:30])

    def _on_favicon_changed(self, icon, tab: BrowserTab):
        index = self.tabs.indexOf(tab.web_view)
        if index >= 0:
            self.tabs.setTabIcon(index, icon)