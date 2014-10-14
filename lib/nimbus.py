#! /usr/bin/env python3

# ---------
# nimbus.py
# ---------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This is the core module that contains all the very
#              specific components related to loading Nimbus.

# Import everything we need.
import sys
import os
import json
import copy

# This is a hack for installing Nimbus.
try:
    import paths
except ImportError:
    try:
        import lib.paths as paths
    except ImportError:
        import nimbus.paths as paths
sys.path.append(paths.app_folder)

import settings
import common
from session import *
import settings_dialog
import browser
import network
import filtering
import translate
from translate import tr
import custom_widgets
import clear_history_dialog
if not os.path.isdir(settings.extensions_folder) or not os.path.isfile(settings.startpage):
    import shutil
import extension_server
import data
import search_manager
from nwebkit import *
from mainwindow import *
from tray_icon import *

# This was made for an attempt to compile Nimbus to CPython,
# but it is now useless.
try: exec
except:
    def exec(code):
        pass

# Extremely specific imports from PyQt/PySide.
if not common.pyqt4:
    from PyQt5.QtCore import Qt, QCoreApplication, QUrl, QTimer
    from PyQt5.QtGui import QPalette, QColor
    from PyQt5.QtWidgets import QApplication, QAction, QDesktopWidget, QMessageBox
    from PyQt5.QtWebKit import QWebSettings
    from PyQt5.QtWebKitWidgets import QWebPage

    # Python DBus
    has_dbus = False
    if not "-no-remote" in sys.argv:
        try:
            import dbus
            import dbus.service
            from dbus.mainloop.pyqt5 import DBusQtMainLoop
            has_dbus = True
        except ImportError:
            pass
else:
    try:
        from PyQt4.QtCore import Qt, QCoreApplication, QUrl, QTimer
        from PyQt4.QtGui import QApplication, QAction, QDesktopWidget, QMessageBox, QPalette, QColor
        from PyQt4.QtWebKit import QWebPage, QWebSettings

        # Python DBus
        has_dbus = False
        if not "-no-remote" in sys.argv:
            try:
                import dbus
                import dbus.service
                from dbus.mainloop.qt import DBusQtMainLoop
                has_dbus = True
            except:
                pass
    except ImportError:
        from PySide.QtCore import Qt, QCoreApplication, QUrl, QTimer
        from PySide.QtGui import QApplication, QAction, QDesktopWidget, QMessageBox, QPalette, QColor
        from PySide.QtWebKit import QWebPage, QWebSettings


# chdir to the app folder. This way, we won't have issues related to
# relative paths.
os.chdir(common.app_folder)

# Create extension server.
server_thread = extension_server.ExtensionServerThread()

# Redundancy is redundant.
def addWindow(url=None):
    win = MainWindow()
    if not url or url == None:
        win.addTab(url=settings.settings.value("general/Homepage"))
    else:
        win.addTab(url=url)
    win.show()

# Preparations to quit.
def prepareQuit():
    try: os.remove(settings.crash_file)
    except: pass
    saveSession()
    settings.settings.hardSync()
    data.saveData()
    data.data.hardSync()
    filtering.adblock_filter_loader.quit()
    filtering.adblock_filter_loader.wait()
    server_thread.httpd.shutdown()
    server_thread.quit()
    server_thread.wait()

# DBus server.
if has_dbus:
    class DBusServer(dbus.service.Object):
        def __init__(self, bus=None):
            busName = dbus.service.BusName("org.nimbus.Nimbus", bus=bus)
            dbus.service.Object.__init__(self, busName, "/Nimbus")

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s",\
                             out_signature="s")
        def addWindow(self, url=None):
            addWindow(url)
            return url

        @dbus.service.method("org.nimbus.Nimbus", in_signature="s",\
                             out_signature="s")
        def addTab(self, url="about:blank"):
            if url == "--app":
                win = MainWindow(appMode=True)
                win.addTab(url="about:blank")
                win.show()
                return url
            else:
                for window in browser.windows[::-1]:
                    if window.isVisible():
                        window.addTab(url=url)
                        if not (window.tabWidget().widget(0).history().canGoBack() or window.tabWidget().widget(0).history().canGoForward()) and window.tabWidget().widget(0).url().toString() in ("about:blank", "", QUrl.fromUserInput(settings.new_tab_page).toString(),):
                            window.removeTab(0)
                        browser.windows[-1].activateWindow()
                        return url
                self.addWindow(url)
                browser.windows[-1].activateWindow()
                return url


def recoverLostTabs():
    killemall = []
    for webview in common.webviews:
        try:
            if webview.parent() == None:
                browser.activeWindow().addTab(webview)
        except:
            killemall.append(webview)
    for webview in killemall:
        common.webviews.remove(webview)

def cleanJavaScriptBars():
    killthem = []
    for webview in common.webviews:
        for bar in webview.javaScriptBars:
            try:
                bar.label
            except:
                killthem.append((webview, bar))
    for bar in killthem:
        bar[0].javaScriptBars.remove(bar)

# Main function to load everything.
def main(argv):
    # Start DBus loop
    if has_dbus:
        mainloop = DBusQtMainLoop(set_as_default = True)
        dbus.set_default_main_loop(mainloop)

    # Create app.
    app = QApplication(argv)
    if not common.pyqt4:
        app.setStyle("fusion")
    else:
        app.setStyle("cleanlooks")
    palette = QPalette(QColor("#2e3436"), QColor("#eeeeec"), QColor("#eeeeec"), QColor("#555753"), QColor("#D3D7CF"), QColor("#2e3436"), QColor("#eeeeec"), QColor("#ffffff"), QColor("#eeeeec"))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor("#BABDB6"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#BABDB6"))
    palette.setColor(QPalette.Highlight, QColor("#5382BA"))
    palette.setColor(QPalette.HighlightedText, QColor("#eeeeec"))
    app.setPalette(palette)
    app.setApplicationName(common.app_name + "/" + common.app_version)
    app.installTranslator(translate.translator)

    # We want Nimbus to stay open when the last window is closed,
    # so we set this.
    app.setQuitOnLastWindowClosed(False)

    # If D-Bus is present...
    if has_dbus:
        bus = dbus.SessionBus()

    try: proxy = bus.get_object("org.nimbus.Nimbus", "/Nimbus")
    except: dbus_present = False
    else: dbus_present = True

    # If Nimbus detects the existence of another Nimbus process, it
    # will send all the requested URLs to the existing process and
    # exit.
    if dbus_present:
        for arg in argv[1:]:
            proxy.addTab(arg)
        if len(argv) < 2:
            proxy.addWindow()
        return

    # Hack together the browser's icon. This needs to be improved.
    common.app_icon = common.complete_icon("nimbus")

    app.setWindowIcon(common.app_icon)

    common.searchEditor = search_manager.SearchEditor()
    common.downloadManager = QMainWindow(windowTitle=tr("Downloads"))
    common.downloadManager.resize(QSize(480, 320))
    closeWindowAction = QAction(common.downloadManager)
    closeWindowAction.triggered.connect(common.downloadManager.hide)
    closeWindowAction.setShortcuts(["Esc", "Ctrl+W", "Ctrl+J", "Ctrl+Shift+Y"])
    common.downloadManager.addAction(closeWindowAction)

    # Build the browser's default user agent.
    # This should be improved as well.
    common.createUserAgent()

    # Create tray icon.
    common.trayIcon = SystemTrayIcon(QCoreApplication.instance())
    common.trayIcon.newWindowRequested.connect(addWindow)
    #common.trayIcon.windowReopenRequested.connect(reopenWindow)
    common.trayIcon.show()

    # Creates a licensing information dialog.
    common.licenseDialog = custom_widgets.LicenseDialog()

    # Create instance of clear history dialog.
    common.chistorydialog = clear_history_dialog.ClearHistoryDialog()

    QWebSettings.globalSettings().setAttribute(QWebSettings.globalSettings().DeveloperExtrasEnabled, True)

    uc = QUrl.fromUserInput(settings.user_css)
    QWebSettings.globalSettings().setUserStyleSheetUrl(uc)
    print(QWebSettings.globalSettings().userStyleSheetUrl())
    print("Nyahahaha!")

    # Set up settings dialog.
    settings.settingsDialog = settings_dialog.SettingsDialog()
    settings.settingsDialog.setWindowFlags(Qt.Dialog)
    closeSettingsDialogAction = QAction(settings.settingsDialog)
    closeSettingsDialogAction.setShortcuts(["Esc", "Ctrl+W"])
    closeSettingsDialogAction.triggered.connect(settings.settingsDialog.hide)
    settings.settingsDialog.addAction(closeSettingsDialogAction)

    # Set up clippings manager.
    settings.clippingsManager = settings_dialog.ClippingsPanel()
    settings.clippingsManager.setWindowFlags(Qt.Dialog)
    closeClippingsManagerAction = QAction(settings.clippingsManager)
    closeClippingsManagerAction.setShortcuts(["Esc", "Ctrl+W"])
    closeClippingsManagerAction.triggered.connect(settings.clippingsManager.hide)
    settings.clippingsManager.addAction(closeClippingsManagerAction)

    # Create DBus server
    if has_dbus:
        server = DBusServer(bus)

    # Load adblock rules.
    filtering.adblock_filter_loader.start()

    if not os.path.isdir(settings.extensions_folder):
        try: shutil.copytree(common.extensions_folder,\
                             settings.extensions_folder)
        except: pass
    if not os.path.isfile(settings.startpage):
        try: shutil.copy2(common.startpage, settings.startpage)
        except: pass

    settings.reload_extensions()
    settings.reload_userscripts()

    server_thread.setDirectory(settings.extensions_folder)

    # Start extension server.
    server_thread.start()

    # On quit, save settings.
    app.aboutToQuit.connect(prepareQuit)

    # Load settings.
    data.loadData()

    # This is a baaad name.
    common.sessionSaver = QTimer(QCoreApplication.instance())
    common.sessionSaver.timeout.connect(saveSession)
    common.sessionSaver.timeout.connect(data.saveData)
    if common.portable:
        common.sessionSaver.start(50000)
    else:
        common.sessionSaver.start(30000)

    common.desktop = QDesktopWidget()

    lostTabsTimer = QTimer(timeout=recoverLostTabs, parent=QCoreApplication.instance())
    lostTabsTimer.timeout.connect(cleanJavaScriptBars)
    if common.portable:
        lostTabsTimer.start(1000)
    else:
        lostTabsTimer.start(500)

    if os.path.isfile(settings.crash_file):
        clearCache = QMessageBox.question(None, tr("Ow."), tr("Nimbus seems to have crashed during your last session. Fortunately, your tabs were saved up to 30 seconds beforehand. Would you like to restore them?"), QMessageBox.Yes | QMessageBox.No)
        if clearCache == QMessageBox.No:
            try: os.remove(settings.session_file)
            except: pass
    else:
        f = open(settings.crash_file, "w")
        f.write("")
        f.close()

    if not "--daemon" in argv and os.path.exists(settings.session_file):
        loadSession()
    if not "--daemon" in argv and len(argv[1:]) > 0:
        # Create instance of MainWindow.
        if len(browser.windows) > 0:
            win = browser.windows[-1]
        else:
            win = MainWindow(appMode = ("--app" in argv))

        # Open URLs from command line.
        if len(argv[1:]) > 0:
            for arg in argv[1:]:
                if "." in arg or ":" in arg:
                    win.addTab(url=arg)

        if win.tabWidget().count() < 1:
            win.addTab(url=settings.settings.value("general/Homepage"))

            # Show window.
        win.show()
    elif not "--daemon" in argv and len(argv[1:]) == 0 and len(browser.windows) == 0:
        win = MainWindow(appMode = ("--app" in argv))
        win.addTab(url=settings.settings.value("general/Homepage"))
        win.show()

    # Load filtering stuff.
    if not os.path.isdir(filtering.hosts_folder):
        filtering.download_rules()
    filtering.load_host_rules()

    # Start app.
    sys.exit(app.exec_())

# Start program
if __name__ == "__main__":
    main(sys.argv)
