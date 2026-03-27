import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineQuick import QtWebEngineQuick
from browser import BrowserWindow

if __name__ == "__main__":
    QtWebEngineQuick.initialize()
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())
