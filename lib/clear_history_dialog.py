#! /usr/bin/env python3

# -----------------------
# clear_history_dialog.py
# -----------------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains a dialog used for clearing out Nimbus'
#              history.

import sys
import os
import subprocess
import common
import settings
import network
import data
from translate import tr
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow, QAction, QToolBar, QComboBox, QPushButton
    from PyQt5.QtWebKit import QWebSettings
except ImportError:
    from PyQt4.QtCore import Qt
    from PyQt4.QtGui import QWidget, QVBoxLayout, QLabel, QMainWindow, QAction, QToolBar, QComboBox, QPushButton
    from PyQt4.QtWebKit import QWebSettings

class ClearHistoryDialog(QMainWindow):
    def __init__(self, parent=None):
        super(ClearHistoryDialog, self).__init__(parent)

        self.setWindowFlags(Qt.Dialog)

        self.setWindowTitle(tr("Clear Data"))

        closeWindowAction = QAction(self)
        closeWindowAction.setShortcuts(["Esc", "Ctrl+W", "Ctrl+Shift+Del"])
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        self.contents = QWidget()
        self.layout = QVBoxLayout()
        self.contents.setLayout(self.layout)
        self.setCentralWidget(self.contents)
        label = QLabel(tr("What to clear:"), self)
        self.layout.addWidget(label)
        self.dataType = QComboBox(self)
        self.dataType.addItem(tr("History"))
        self.dataType.addItem(tr("Cookies"))
        self.dataType.addItem(tr("Memory Caches"))
        self.dataType.addItem(tr("Persistent Storage"))
        self.dataType.addItem(tr("Everything"))
        self.layout.addWidget(self.dataType)
        self.toolBar = QToolBar(self)
        self.toolBar.setStyleSheet(common.blank_toolbar)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(Qt.BottomToolBarArea, self.toolBar)
        self.clearHistoryButton = QPushButton(tr("Clear"), self)
        self.clearHistoryButton.clicked.connect(self.clearHistory)
        self.toolBar.addWidget(self.clearHistoryButton)
        self.closeButton = QPushButton(tr("Close"), self)
        self.closeButton.clicked.connect(self.close)
        self.toolBar.addWidget(self.closeButton)

    def show(self):
        self.setVisible(True)

    def display(self):
        self.show()
        self.activateWindow()

    def clearHistory(self):
        clear_everything = (self.dataType.currentIndex() == self.dataType.count()-1)
        if self.dataType.currentIndex() == 0 or clear_everything:
            data.clearHistory()
        if self.dataType.currentIndex() == 1 or clear_everything:
            data.clearCookies()
        if self.dataType.currentIndex() == 2 or clear_everything:
            QWebSettings.globalSettings().clearMemoryCaches()
        if self.dataType.currentIndex() == 3 or clear_everything:
            QWebSettings.globalSettings().setIconDatabasePath("")
            QWebSettings.globalSettings().setLocalStoragePath("")
            QWebSettings.globalSettings().setOfflineStoragePath("")
            QWebSettings.globalSettings().setOfflineWebApplicationCachePath("")
            for subpath in ("WebpageIcons.db", "LocalStorage", "Databases",):
                path = os.path.abspath(os.path.join(settings.settings_folder, subpath))
                if os.path.isfile(path):
                    try: os.remove(path)
                    except: pass
                elif os.path.isdir(path):
                    if sys.platform.startswith("win"):
                        args = ["rmdir", "/s", "/q", "\"" + path + "\""]
                        try: os.system(" ".join(args))
                        except: pass
                    else:
                        try: subprocess.Popen(["rm", "-rf", path])
                        except: pass
            QWebSettings.globalSettings().enablePersistentStorage(settings.settings_folder)
