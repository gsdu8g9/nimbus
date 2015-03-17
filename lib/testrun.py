#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication
from translate import tr
import common
import tray_icon
import browser
import nwebkit
import network
import filtering
import mainwindow
import session
import settings
import settings_dialog

def prepareQuit():
    common.downloadManager.saveSession()
    session.saveSession()

def main():
    app = QApplication(sys.argv)
    common.app_icon = common.complete_icon("nimbus")
    common.trayIcon = tray_icon.SystemTrayIcon()
    network.setup()
    filtering.setup()
    common.downloadManager = nwebkit.DownloadManager(windowTitle=tr("Downloads"))
    common.downloadManager.loadSession()
    settings.settingsDialog = settings_dialog.SettingsDialog()
    session.loadSession()
    if len(browser.windows) == 0:
        win = mainwindow.MainWindow()
        win.show()
        win.addTab()
    app.aboutToQuit.connect(prepareQuit)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
