#! /usr/bin/env python3

# -------------
# mainwindow.py
# -------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: Contains the main browser window interface.

# Import everything we need.
import os
import json
import copy
import traceback
import common
import browser
import translate
from translate import tr
import custom_widgets
import settings
import status_bar
import data
from nwebkit import *

# Extremely specific imports from PyQt4/PySide.
# We give PyQt4 priority because it supports Qt5.
try:
    from PyQt4.QtCore import Qt, QCoreApplication, QUrl, QTimer, QSize
    from PyQt4.QtGui import QApplication, QDockWidget, QWidget, QHBoxLayout,\
                            QKeySequence, QMessageBox, QSizePolicy, QIcon,\
                            QMenu, QAction, QMainWindow, QToolBar,\
                            QToolButton, QComboBox, QTabWidget
    from PyQt4.QtNetwork import QNetworkRequest
    from PyQt4.QtWebKit import QWebPage
except:
    from PySide.QtCore import Qt, QCoreApplication, QUrl, QTimer, QSize
    from PySide.QtGui import QApplication, QDockWidget, QWidget,\
                             QHBoxLayout, QKeySequence, QMessageBox,\
                             QSizePolicy, QIcon, QMenu, QAction,\
                             QMainWindow, QToolBar, QToolButton, QComboBox,\
                             QTabWidget
    from PySide.QtNetwork import QNetworkRequest
    from PySide.QtWebKit import QWebPage

tabbar_stylesheet = \
"""QTabBar { margin: 0; padding: 0; border-bottom: 0; }
   QTabBar::tab { min-width: 8em; border: 1px solid palette(dark);
                  border-left: 0; margin: 0; padding: 4px;
                  background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 palette(window),
                                              stop: 1 palette(dark)); }
   QTabBar::tab:selected { background: qlineargradient(x1: 0, y1: 0,
                                                       x2: 0, y2: 1,
                                       stop: 0 palette(light),
                                       stop: 1 palette(window)); }"""

# Extension button class.
class ExtensionButton(QToolButton):
    def __init__(self, script="", shortcut=None, parent=None):
        super(ExtensionButton, self).__init__(parent)
        if shortcut:
            self.setShortcut(QKeySequence.fromString(shortcut))
        settings.extension_buttons.append(self)
        self._parent = parent
        self.script = script
    def parentWindow(self):
        return self._parent
    def loadScript(self):
        try: exec(self.script)
        except:
            traceback.print_exc()
            self._parent.currentWidget().page().mainFrame().\
            evaluateJavaScript(self.script)

# Custom MainWindow class.
# This contains basic navigation controls, a location bar, and a menu.
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # These are used to store where the mouse pressed down.
        # This is used in a hack to drag the window by the toolbar.
        self.mouseX = False
        self.mouseY = False

        # Add self to global list of windows.
        browser.windows.append(self)

        # Set window icon.
        self.setWindowIcon(common.app_icon)

        # List of closed tabs.
        self.closedTabs = []

        # List of sidebars.
        # Sidebars are part of the (incomplete) extensions API.
        self.sideBars = {}

        # Tabs toolbar.
        self.tabsToolBar = custom_widgets.MenuToolBar(movable=False,\
                           contextMenuPolicy=Qt.CustomContextMenu,\
                           parent=self)
        self.addToolBar(self.tabsToolBar)

        self.addToolBarBreak(Qt.TopToolBarArea)

        # Main toolbar.
        self.toolBar = QToolBar(movable=False,\
                                contextMenuPolicy=Qt.CustomContextMenu,\
                                parent=self)
        self.addToolBar(self.toolBar)

        # Tab widget for tabbed browsing.
        self.tabs = QTabWidget(self)

        # Remove border around tabs.
        self.tabs.setDocumentMode(True)

        # Allow rearranging of tabs.
        self.tabs.setMovable(True)

        # Update tab titles and icons when the current tab is changed.
        self.tabs.currentChanged.connect(self.updateTabTitles)
        self.tabs.currentChanged.connect(self.updateTabIcons)

        # Hacky way of updating the location bar text when the tab is changed.
        self.tabs.currentChanged.connect(self.updateLocationText)
        self.tabs.currentChanged.connect(self.updateLocationIcon)

        # Allow closing of tabs.
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.removeTab)

        self.statusBar = status_bar.StatusBar(self)
        self.addToolBar(Qt.BottomToolBarArea, self.statusBar)
        self.addToolBarBreak(Qt.BottomToolBarArea)

        # Set tabs as central widget.
        self.setCentralWidget(self.tabs)

        self.tabsWidget = QWidget(self)
        tabsLayout = QHBoxLayout(self.tabsWidget)
        self.tabsWidget.setLayout(tabsLayout)
        self.tabsToolBar.addWidget(self.tabsWidget)
        self.tabsWidget.layout().setSpacing(0)
        self.tabsWidget.layout().setContentsMargins(0,0,0,0)
        self.tabsWidget.layout().addWidget(self.tabs.tabBar())
        self.tabs.tabBar().setExpanding(False)
        self.tabsToolBar.layout().setSpacing(0)
        self.tabsToolBar.layout().setContentsMargins(0,0,0,0)
        self.tabsToolBar.setStyleSheet("QToolBar { padding: 0; margin: 0; }")
        self.tabs.tabBar().setStyleSheet(tabbar_stylesheet)

        # New tab action.
        newTabAction = QAction(common.complete_icon("list-add"), tr("New &Tab"), self)
        newTabAction.setShortcut("Ctrl+T")
        newTabAction.triggered.connect(lambda: self.addTab())

        # New private browsing tab action.
        newIncognitoTabAction = QAction(common.complete_icon("face-devilish"), tr("New &Incognito Tab"), self)
        newIncognitoTabAction.setShortcut("Ctrl+Shift+I")
        newIncognitoTabAction.triggered.connect(lambda: self.addTab(incognito=True))

        # This is used so that the new tab button looks halfway decent,
        # and can actually be inserted into the corner of the tab widget.
        #newTabToolBar = QToolBar(movable=False, contextMenuPolicy=Qt.CustomContextMenu, parent=self)
        self.tabsToolBar.setIconSize(QSize(16, 16))

        # We don't want this widget to have any decorations.
        #newTabToolBar.setStyleSheet(common.blank_toolbar)

        #self.tabsToolBar.addAction(newIncognitoTabAction)
        self.tabsToolBar.addAction(newTabAction)
        #self.tabsToolBar.addWidget(newTabToolBar)
        #self.tabs.setCornerWidget(newTabToolBar, Qt.TopRightCorner)

        # These are hidden actions used for the Ctrl[+Shift]+Tab feature
        # you see in most browsers.
        nextTabAction = QAction(self, triggered=self.nextTab, shortcut="Ctrl+Tab")
        self.addAction(nextTabAction)

        previousTabAction = QAction(self, triggered=self.previousTab, shortcut="Ctrl+Shift+Tab")
        self.addAction(previousTabAction)

        # This is the Ctrl+W (Close Tab) shortcut.
        removeTabAction = QAction(self, triggered=lambda: self.removeTab(self.tabWidget().currentIndex()), shortcut="Ctrl+W")
        self.addAction(removeTabAction)

        # Dummy webpage used to provide navigation actions that conform to
        # the system's icon theme.
        self.actionsPage = QWebPage(self)

        # Regularly and forcibly enable and disable navigation actions
        # every few milliseconds.
        self.toggleActionsTimer = QTimer(timeout=self.toggleActions, parent=self)

        # Set up navigation actions.
        self.backAction = self.actionsPage.action(QWebPage.Back)
        self.backAction.setShortcut("Alt+Left")
        self.backAction.triggered.connect(self.back)
        self.toolBar.addAction(self.backAction)
        self.toolBar.widgetForAction(self.backAction).setPopupMode(QToolButton.MenuButtonPopup)

        # This is a dropdown menu for the back history items, but due to
        # instability, it is currently disabled.
        self.backHistoryMenu = QMenu(aboutToShow=self.aboutToShowBackHistoryMenu, parent=self)
        self.backAction.setMenu(self.backHistoryMenu)

        self.forwardAction = self.actionsPage.action(QWebPage.Forward)
        self.forwardAction.setShortcut("Alt+Right")
        self.forwardAction.triggered.connect(self.forward)
        self.toolBar.addAction(self.forwardAction)
        self.toolBar.widgetForAction(self.forwardAction).setPopupMode(QToolButton.MenuButtonPopup)

        # This is a dropdown menu for the forward history items, but due to
        # instability, it is currently disabled.
        self.forwardHistoryMenu = QMenu(aboutToShow=self.aboutToShowForwardHistoryMenu, parent=self)
        self.forwardAction.setMenu(self.forwardHistoryMenu)

        self.upAction = QAction(self, triggered=self.up, icon=common.complete_icon("go-up"), text=tr("Go Up"))
        self.toolBar.addAction(self.upAction)
        self.toolBar.widgetForAction(self.upAction).setPopupMode(QToolButton.MenuButtonPopup)
        self.upAction.setVisible(False)

        self.upAction2 = QAction(self, triggered=self.up, shortcut="Alt+Up")
        self.addAction(self.upAction2)

        self.upMenu = QMenu(aboutToShow=self.aboutToShowUpMenu, parent=self)
        self.upAction.setMenu(self.upMenu)

        self.nextAction = QAction(self, triggered=self.next, icon=common.complete_icon("media-skip-forward"), text=tr("Go Next"))
        self.toolBar.addAction(self.nextAction)

        self.stopAction = self.actionsPage.action(QWebPage.Stop)
        self.stopAction.triggered.connect(self.stop)
        self.stopAction.triggered.connect(lambda: self.stopAction.setEnabled(True))
        self.stopAction.triggered.connect(lambda: self.reloadAction.setEnabled(True))
        self.toolBar.addAction(self.stopAction)

        self.stopAction2 = QAction(self, triggered=self.stop, shortcut="Esc")
        self.addAction(self.stopAction2)

        self.reloadAction = self.actionsPage.action(QWebPage.Reload)
        self.reloadAction.triggered.connect(self.reload)
        self.reloadAction.triggered.connect(lambda: self.stopAction.setEnabled(True))
        self.reloadAction.triggered.connect(lambda: self.reloadAction.setEnabled(True))
        self.toolBar.addAction(self.reloadAction)

        self.reloadAction2 = QAction(self, triggered=self.reload)
        self.reloadAction2.setShortcuts(["F5", "Ctrl+R"])
        self.addAction(self.reloadAction2)

        # Go home button.
        self.homeAction = QAction(self, triggered=self.goHome, icon=common.complete_icon("go-home"), text=tr("Go Home"))
        self.toolBar.addAction(self.homeAction)
        self.homeAction.setVisible(False)

        self.homeAction2 = QAction(self, triggered=self.goHome, shortcut="Alt+Home")
        self.addAction(self.homeAction2)

        # Start timer to forcibly enable and disable navigation actions.
        self.toggleActionsTimer.start(256)

        # Location bar. Note that this is a combo box.
        # At some point, I should make a custom location bar
        # implementation that looks nicer.
        self.locationBar = custom_widgets.LocationBar(icon=None, parent=self)

        # Load stored browser history.
        for url in data.history:
            self.locationBar.addItem(url)

        # Combo boxes are not normally editable by default.
        self.locationBar.setEditable(True)

        # We want the location bar to stretch to fit the toolbar,
        # so we set its size policy to expand.
        self.locationBar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        # Load a page when Enter is pressed.
        self.locationBar.lineEdit().returnPressed.connect(lambda: self.load(self.locationBar.lineEdit().text()))
        self.locationBar.view().activated.connect(lambda index: self.load(index.data()))

        # This is so that the location bar can shrink to a width
        # shorter than the length of its longest item.
        self.locationBar.setStyleSheet("QComboBox { min-width: 6em; }")
        self.toolBar.addWidget(self.locationBar)

        self.feedMenuButton = QAction(common.complete_icon("application-rss+xml"), tr("Feeds"), self)
        self.feedMenuButton.setShortcut("Ctrl+Alt+R")
        self.toolBar.addAction(self.feedMenuButton)
        self.toolBar.widgetForAction(self.feedMenuButton).setPopupMode(QToolButton.InstantPopup)
        self.feedMenuButton.triggered.connect(lambda: self.toolBar.widgetForAction(self.feedMenuButton).showMenu())
        self.feedMenuButton.setVisible(False)

        self.feedMenu = QMenu(self)
        self.feedMenu.aboutToShow.connect(self.aboutToShowFeedMenu)
        self.feedMenuButton.setMenu(self.feedMenu)

        self.searchEditButton = QAction(common.complete_icon("system-search"), tr("Manage Search Engines"), self)
        self.searchEditButton.setShortcut("Ctrl+K")
        self.searchEditButton.triggered.connect(common.searchEditor.show)
        self.toolBar.addAction(self.searchEditButton)

        # Ctrl+L/Alt+D focuses the location bar.
        locationAction = QAction(self)
        locationAction.setShortcuts(["Ctrl+L", "Alt+D"])
        locationAction.triggered.connect(self.locationBar.setFocus)
        locationAction.triggered.connect(self.locationBar.lineEdit().selectAll)
        self.addAction(locationAction)

        # Extensions toolbar.
        self.extensionBar = QToolBar(self)
        self.extensionBar.setMovable(False)
        self.extensionBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.extensionBar.setStyleSheet("QToolBar { border: 0; border-right: 1px solid palette(dark); background: palette(window); }")
        self.addToolBar(Qt.LeftToolBarArea, self.extensionBar)
        self.extensionBar.hide()

        # Main menu.
        mainMenu = QMenu(self)

        # Add new tab actions to menu.
        mainMenu.addAction(newTabAction)
        mainMenu.addAction(newIncognitoTabAction)

        # Add new window action.
        newWindowAction = QAction(common.complete_icon("window-new"), tr("&New Window"), self)
        newWindowAction.setShortcut("Ctrl+N")
        newWindowAction.triggered.connect(self.addWindow)
        mainMenu.addAction(newWindowAction)

        mainMenu.addSeparator()

        # Add print preview action.
        printPreviewAction = QAction(common.complete_icon("document-print-preview"), tr("Print Previe&w"), self)
        printPreviewAction.setShortcut("Ctrl+Shift+P")
        printPreviewAction.triggered.connect(self.printPreview)
        mainMenu.addAction(printPreviewAction)

        # Add print page action.
        printAction = QAction(common.complete_icon("document-print"), tr("&Print..."), self)
        printAction.setShortcut("Ctrl+P")
        printAction.triggered.connect(self.printPage)
        mainMenu.addAction(printAction)

        # Add separator.
        mainMenu.addSeparator()

        # Save page action.
        savePageAction = QAction(common.complete_icon("document-save-as"), tr("Save Page &As..."), self)
        savePageAction.setShortcut("Ctrl+S")
        savePageAction.triggered.connect(lambda: self.tabWidget().currentWidget().downloadFile(QNetworkRequest(self.tabWidget().currentWidget().url())))
        mainMenu.addAction(savePageAction)

        mainMenu.addSeparator()

        viewMenu = QMenu(tr("Vi&ew"), self)
        mainMenu.addMenu(viewMenu)

        # Zoom actions.
        zoomInAction = QAction(common.complete_icon("zoom-in"), tr("Zoom In"), self)
        zoomInAction.triggered.connect(lambda: self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() + 0.1))
        zoomInAction.setShortcuts(["Ctrl+=", "Ctrl++"])
        viewMenu.addAction(zoomInAction)

        zoomOutAction = QAction(common.complete_icon("zoom-out"), tr("Zoom Out"), self)
        zoomOutAction.triggered.connect(lambda: self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor() - 0.1))
        zoomOutAction.setShortcut("Ctrl+-")
        viewMenu.addAction(zoomOutAction)

        zoomOriginalAction = QAction(common.complete_icon("zoom-original"), tr("Reset Zoom"), self)
        zoomOriginalAction.triggered.connect(lambda: self.tabs.currentWidget().setZoomFactor(1.0))
        zoomOriginalAction.setShortcut("Ctrl+0")
        viewMenu.addAction(zoomOriginalAction)

        viewMenu.addSeparator()

        # Add fullscreen button.
        self.toggleFullScreenButton = QAction(common.complete_icon("view-fullscreen"), tr("Toggle Fullscreen"), self)
        self.toggleFullScreenButton.setCheckable(True)
        self.toggleFullScreenButton.triggered.connect(lambda: self.setFullScreen(not self.isFullScreen()))
        self.toolBar.addAction(self.toggleFullScreenButton)
        self.toggleFullScreenButton.setVisible(False)

        # Add fullscreen action.
        self.toggleFullScreenAction = QAction(common.complete_icon("view-fullscreen"), tr("Toggle Fullscreen"), self)
        self.toggleFullScreenAction.setShortcuts(["F11", "Ctrl+Shift+F"])
        self.toggleFullScreenAction.setCheckable(True)
        self.toggleFullScreenAction.triggered.connect(lambda: self.setFullScreen(not self.isFullScreen()))
        self.addAction(self.toggleFullScreenAction)
        viewMenu.addAction(self.toggleFullScreenAction)

        mainMenu.addSeparator()

        # Add find text action.
        findAction = QAction(common.complete_icon("edit-find"), tr("&Find..."), self)
        findAction.setShortcut("Ctrl+F")
        findAction.triggered.connect(self.find)
        mainMenu.addAction(findAction)

        # Add find next action.
        findNextAction = QAction(common.complete_icon("media-seek-forward"), tr("Find Ne&xt"), self)
        findNextAction.setShortcut("Ctrl+G")
        findNextAction.triggered.connect(self.findNext)
        mainMenu.addAction(findNextAction)

        # Add find previous action.
        findPreviousAction = QAction(common.complete_icon("media-seek-backward"), tr("Find Pre&vious"), self)
        findPreviousAction.setShortcut("Ctrl+Shift+G")
        findPreviousAction.triggered.connect(self.findPrevious)
        mainMenu.addAction(findPreviousAction)

        mainMenu.addSeparator()

        historyMenu = QMenu(tr("&History"), self)
        historyMenu.setIcon(common.complete_icon("office-calendar"))
        mainMenu.addMenu(historyMenu)

        # Add reopen tab action.
        reopenTabAction = QAction(common.complete_icon("edit-undo"), tr("&Reopen Tab"), self)
        reopenTabAction.setShortcut("Ctrl+Shift+T")
        reopenTabAction.triggered.connect(self.reopenTab)
        self.addAction(reopenTabAction)
        historyMenu.addAction(reopenTabAction)

        # Add reopen window action.
        reopenWindowAction = QAction(common.complete_icon("reopen-window"), tr("R&eopen Window"), self)
        reopenWindowAction.setShortcut("Ctrl+Shift+N")
        reopenWindowAction.triggered.connect(self.reopenWindow)
        self.addAction(reopenWindowAction)
        historyMenu.addAction(reopenWindowAction)

        historyMenu.addSeparator()

        # Add clear history action.
        clearHistoryAction = QAction(common.complete_icon("edit-clear"), tr("&Clear Data..."), self)
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(self.clearHistory)
        historyMenu.addAction(clearHistoryAction)

        # Add view source dialog action.
        viewSourceAction = QAction(tr("Page S&ource"), self)
        viewSourceAction.setShortcut("Ctrl+Alt+U")
        viewSourceAction.triggered.connect(lambda: self.tabWidget().currentWidget().viewSource())
        mainMenu.addAction(viewSourceAction)

        # Add settings dialog action.
        settingsAction = QAction(common.complete_icon("preferences-system"), tr("&Settings..."), self)
        settingsAction.setShortcuts(["Ctrl+,", "Ctrl+Alt+P"])
        settingsAction.triggered.connect(self.openSettings)
        mainMenu.addAction(settingsAction)

        mainMenu.addSeparator()

        # About Qt action.
        aboutQtAction = QAction(common.complete_icon("qt"), tr("About &Qt"), self)
        aboutQtAction.triggered.connect(QApplication.aboutQt)
        mainMenu.addAction(aboutQtAction)

        # About Nimbus action.
        aboutAction = QAction(common.complete_icon("help-about"), tr("A&bout Nimbus"), self)
        aboutAction.triggered.connect(lambda: QMessageBox.about(self,\
                                               tr("About Nimbus"),\
                                               "<h3>" + tr("Nimbus") + " " +\
                                               common.app_version +\
                                               "</h3>" +\
                                               tr("Python 3/Qt 4-based Web browser.")))
        mainMenu.addAction(aboutAction)

        # Licensing information.
        licenseAction = QAction(tr("Credits && &Licensing"), self)
        licenseAction.triggered.connect(common.licenseDialog.show)
        mainMenu.addAction(licenseAction)

        mainMenu.addSeparator()

        # Quit action.
        quitAction = QAction(common.complete_icon("application-exit"),\
                             tr("Quit"), self)
        quitAction.setShortcut("Ctrl+Shift+Q")
        quitAction.triggered.connect(QCoreApplication.quit)
        mainMenu.addAction(quitAction)

        # Add main menu action/button.
        self.mainMenuAction =\
             QAction(common.complete_icon("document-properties"),\
                     tr("&Menu"), self)
        self.mainMenuAction.setShortcuts(["Alt+M", "Alt+F"])
        self.mainMenuAction.setMenu(mainMenu)
        self.toolBar.addAction(self.mainMenuAction)
        self.toolBar.widgetForAction(self.mainMenuAction).\
             setPopupMode(QToolButton.InstantPopup)
        self.mainMenuAction.triggered.\
             connect(lambda: self.toolBar.\
             widgetForAction(self.mainMenuAction).showMenu())

        # This is a dummy sidebar used to
        # dock extension sidebars with.
        # You will never actually see this sidebar.
        self.sideBar = QDockWidget(self)
        self.sideBar.setWindowTitle(tr("Sidebar"))
        self.sideBar.setMaximumWidth(320)
        self.sideBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sideBar.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sideBar)
        self.sideBar.hide()

        # Load browser extensions.
        # Ripped off of Ricotta.
        self.reloadExtensions()

    # Redefine show function.
    def show(self):
        self.setVisible(True)
        self.tabs.setStyleSheet("QTabWidget::pane { top: -%s; } " %\
             (self.tabs.tabBar().height(),))

    # Returns the tab widget.
    def tabWidget(self):
        return self.tabs

    # Check if window has a sidebar.
    # Part of the extensions API.
    def hasSideBar(self, name):
        if name in self.sideBars.keys():
            return True
        return False

    # Toggles the sidebar with name name.
    # Part of the extensions API.
    def toggleSideBar(self, name):
        if self.hasSideBar(name):
            self.sideBars[name]["sideBar"].\
                 setVisible(not self.sideBars[name]["sideBar"].isVisible())
            if type(self.sideBars[name]["clip"]) is str:
                clip = self.sideBars[name]["clip"]
                if not clip in self.sideBars[name]["sideBar"].\
                                     webView.url().toString():
                    self.sideBars[name]["sideBar"].\
                         webView.load(self.sideBars[name]["url"])

    # Adds a sidebar.
    # Part of the extensions API.
    def addSideBar(self, name="", url="about:blank", clip=None, ua=None):
        self.sideBars[name] = {"sideBar": QDockWidget(self),\
                               "url": QUrl(url), "clip": clip}
        self.sideBars[name]["sideBar"].setWindowTitle(name)
        self.sideBars[name]["sideBar"].setMaximumWidth(320)
        self.sideBars[name]["sideBar"].\
             setContextMenuPolicy(Qt.CustomContextMenu)
        self.sideBars[name]["sideBar"].\
             setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.sideBars[name]["sideBar"].\
             webView = WebView(self.sideBars[name]["sideBar"])
        self.sideBars[name]["sideBar"].\
             webView.windowCreated.connect(self.addTab)
        self.sideBars[name]["sideBar"].\
             webView.setUserAgent(ua)
        self.sideBars[name]["sideBar"].\
             webView.load(QUrl(url))
        self.sideBars[name]["sideBar"].setWidget(self.sideBars[name]\
                                                 ["sideBar"].webView)
        self.addDockWidget(Qt.LeftDockWidgetArea,\
                           self.sideBars[name]["sideBar"])
        self.tabifyDockWidget(self.sideBar, self.sideBars[name]["sideBar"])

    # This is so you can grab the window by its toolbar and move it.
    # It's an ugly hack, but it works.
    def mousePressEvent(self, ev):
        if ev.button() != Qt.LeftButton:
            return QMainWindow.mousePressEvent(self, ev)
        else:
            self.mouseX = ev.globalX()
            self.origX = self.x()
            self.mouseY = ev.globalY()
            self.origY = self.y()

    def mouseMoveEvent(self, ev):
        if self.mouseX and self.mouseY and not self.isMaximized():
            self.move(self.origX + ev.globalX() - self.mouseX,
self.origY + ev.globalY() - self.mouseY)

    # Deletes any closed windows above the reopenable window count,
    # and blanks all the tabs and sidebars.
    def closeEvent(self, ev):
        window_session = []
        for tab in range(self.tabWidget().count()):
            window_session.append(self.tabWidget().widget(tab).saveHistory())
        browser.closedWindows.append(window_session)
        while len(browser.closedWindows) >\
               settings.setting_to_int("general/ReopenableWindowCount"):
            browser.closedWindows.pop(0)
        self.deleteLater()

    def deleteLater(self):
        try: browser.windows.remove(self)
        except: pass
        QMainWindow.deleteLater(self)

    # Open settings dialog.
    def openSettings(self):
        settings.settingsDialog.show()

    # Reload extensions.
    def reloadExtensions(self):

        # Hide extensions toolbar if there aren't any extensions.
        self.extensionBar.hide()

        for extension in settings.extensions:
            if extension not in settings.extensions_whitelist:
                continue
            extension_path = os.path.join(settings.extensions_folder,\
                                          extension)

            if os.path.isdir(extension_path):
                script_path = os.path.join(extension_path, "script.py")
                if not os.path.isfile(script_path):
                    script_path = os.path.join(extension_path, "script.js")
                icon_path = os.path.join(extension_path, "icon.png")
                shortcut_path = os.path.join(extension_path, "shortcut.txt")
                if os.path.isfile(script_path):
                    f = open(script_path, "r")
                    script = copy.copy(f.read())
                    f.close()
                    shortcut = None
                    if os.path.isfile(shortcut_path):
                        f = open(shortcut_path, "r")
                        shortcut = copy.copy(f.read().replace("\n", ""))
                        f.close()
                    newExtension = ExtensionButton(script, shortcut, self)
                    newExtension.setToolTip(extension.replace("_", " ").\
                                            title() +\
                                            ("" if not shortcut\
                                                else "\n" + shortcut))
                    newExtension.clicked.connect(newExtension.loadScript)
                    self.extensionBar.show()
                    self.extensionBar.addWidget(newExtension)
                    if os.path.isfile(icon_path):
                        newExtension.setIcon(QIcon(icon_path))
                    else:
                        newExtension.setIcon(common.complete_icon("applications-other"))

    # Toggle all the navigation buttons.
    def toggleActions(self):
        try:
            self.backAction.setEnabled(self.tabWidget().currentWidget().\
                                       page().history().canGoBack())
            forwardEnabled = self.tabWidget().currentWidget().\
                             page().history().canGoForward()
            self.forwardAction.setEnabled(forwardEnabled)

            if not forwardEnabled:
                self.forwardAction.setShortcut("")
                self.nextAction.setShortcut("Alt+Right")
            else:
                self.forwardAction.setShortcut("Alt+Right")
                self.nextAction.setShortcut("")

            self.upAction.setEnabled(self.tabWidget().currentWidget().canGoUp())

            # This is a workaround so that hitting Esc will reset the location
            # bar text.
            self.stopAction.setVisible(self.tabWidget().currentWidget().\
                                       pageAction(QWebPage.Stop).isEnabled())
            self.stopAction.setEnabled(True)

            self.reloadAction.setVisible(self.tabWidget().currentWidget().\
                                         pageAction(QWebPage.Reload).\
                                         isEnabled())
            self.reloadAction.setEnabled(True)

            self.homeAction.setVisible(settings.\
                                       setting_to_bool\
                                       ("general/HomeButtonVisible"))
            self.upAction.setVisible(settings.\
                                     setting_to_bool\
                                     ("general/UpButtonVisible"))
            self.feedMenuButton.setVisible(settings.\
                                           setting_to_bool\
                                           ("general/FeedButtonVisible"))
        except:
            self.backAction.setEnabled(False)
            self.forwardAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.reloadAction.setEnabled(False)
        self.toggleActions2()

    def toggleActions2(self):
        try: self.nextAction.setEnabled(bool(self.tabWidget().\
                                             currentWidget().canGoNext()))
        except: self.nextAction.setEnabled(False)

    # Navigation methods.
    def back(self):
        self.tabWidget().currentWidget().back()

    # This is used to refresh the back history items menu,
    # but it is unstable.
    def aboutToShowBackHistoryMenu(self):
        try:
            self.backHistoryMenu.clear()
            history = self.tabWidget().currentWidget().history()
            backItems = history.backItems(10)
            for item in range(0, len(backItems)):
                try:
                    action = custom_widgets.\
                             WebHistoryAction(item,\
                                              backItems[item].title(),\
                                              self.backHistoryMenu)
                    action.triggered2.connect(self.loadBackHistoryItem)
                    self.backHistoryMenu.addAction(action)
                except:
                    traceback.print_exc()
        except:
            traceback.print_exc()

    def loadBackHistoryItem(self, index):
        history = self.tabWidget().currentWidget().history()
        history.goToItem(history.backItems(10)[index])

    def forward(self):
        self.tabWidget().currentWidget().forward()

    def aboutToShowForwardHistoryMenu(self):
        try:
            self.forwardHistoryMenu.clear()
            history = self.tabWidget().currentWidget().history()
            forwardItems = history.forwardItems(10)
            for item in range(0, len(forwardItems)):
                try:
                    action = custom_widgets.\
                             WebHistoryAction(item,
                                              forwardItems[item].title(),\
                                              self.forwardHistoryMenu)
                    action.triggered2.connect(self.loadForwardHistoryItem)
                    self.forwardHistoryMenu.addAction(action)
                except:
                    traceback.print_exc()
        except:
            traceback.print_exc()

    def loadForwardHistoryItem(self, index):
        history = self.tabWidget().currentWidget().history()
        history.goToItem(history.forwardItems(10)[index])

    def up(self):
        self.tabWidget().currentWidget().up()

    def next(self):
        self.tabWidget().currentWidget().next()

    def aboutToShowUpMenu(self):
        self.upMenu.clear()
        tab = self.tabWidget().currentWidget()
        components = tab.url().toString().split("/")
        for component in range(0, len(components)):
            if components[component] != "":
                try:
                    x = "/".join(components[:component])
                    if x != "":
                        action = custom_widgets.LinkAction(QUrl.fromUserInput(x),\
                                                           x,\
                                                           self.upMenu)
                        action.triggered2[QUrl].\
                        connect(self.tabWidget().currentWidget().load)
                        self.upMenu.addAction(action)
                except:
                    traceback.print_exc()

    def reload(self):
        self.tabWidget().currentWidget().reload()

    def stop(self):
        self.tabWidget().currentWidget().stop()
        self.locationBar.setEditText(self.tabWidget().\
                                     currentWidget().url().toString())

    def goHome(self):
        self.tabWidget().currentWidget().load(QUrl.\
                                              fromUserInput(settings.\
                                              settings.\
                                              value("general/Homepage")))

    # About to show feed menu.
    def aboutToShowFeedMenu(self):
        self.feedMenu.clear()
        feeds = self.tabWidget().currentWidget().rssFeeds()
        if len(feeds) == 0:
            self.feedMenu.addAction("N/A")
        else:
            for title, feed in feeds:
                action = custom_widgets.LinkAction(feed, title, self.feedMenu)
                action.triggered2[str].connect(self.tabWidget().\
                                               currentWidget().load2)
                self.feedMenu.addAction(action)

    # Find text/Text search methods.
    def find(self):
        self.tabWidget().currentWidget().find()

    def findNext(self):
        self.tabWidget().currentWidget().findNext()

    def findPrevious(self):
        self.tabWidget().currentWidget().findPrevious()

    # Page printing methods.
    def printPage(self):
        self.tabWidget().currentWidget().printPage()

    def printPreview(self):
        self.tabWidget().currentWidget().printPreview()

    # Clears the history after a prompt.
    def clearHistory(self):
        common.chistorydialog.display()

    # Method to load a URL.
    def load(self, url=False):
        if not url:
            url = self.locationBar.currentText()
        for keyword in common.search_engines.values()   :
            if type(url) is str:
                url3 = url
            else:
                try: url3 = url.toString()
                except: url3 = ""
            fkey = keyword[0] + " "
            if url3.startswith(fkey):
                self.tabWidget().currentWidget().load(QUrl(keyword[1]\
                                                           % (url3.\
                                                           replace(fkey,\
                                                           ""),)))
                return
        url2 = QUrl.fromUserInput(url)
        valid_url = (":" in url or os.path.exists(url) or url.count(".") > 2)
        this_tld = url2.topLevelDomain().upper()
        for tld in common.topLevelDomains():
            if tld in this_tld:
                valid_url = True
        if valid_url:
            self.tabWidget().currentWidget().load(QUrl.fromUserInput(url))
        else:
            self.tabWidget().currentWidget().load(QUrl(settings.\
                                                  settings.\
                                                  value("general/Search")\
                                                  % (url,)))

    # Status bar related methods.
    def setStatusBarMessage(self, message):
        try: self.statusBar.setStatusBarMessage(self.tabWidget().\
                                                currentWidget().\
                                                _statusBarMessage)
        except: self.statusBar.setStatusBarMessage("")

    def setProgress(self, progress):
        try: self.statusBar.setValue(self.tabWidget().\
                                     currentWidget()._loadProgress)
        except: self.statusBar.setValue(0)

    # Fullscreen mode.
    def setFullScreen(self, fullscreen=False):
        if fullscreen:
            try: self.toggleFullScreenButton.setChecked(True)
            except: pass
            try: self.toggleFullScreenAction.setChecked(True)
            except: pass
            self.toggleFullScreenButton.setVisible(True)
            self.showFullScreen()
        else:
            try: self.toggleFullScreenButton.setChecked(False)
            except: pass
            try: self.toggleFullScreenAction.setChecked(False)
            except: pass
            self.toggleFullScreenButton.setVisible(False)
            self.showNormal()

    # Tab-related methods.
    def currentWidget(self):
        return self.tabWidget().currentWidget()

    def addWindow(self, url=None):
        win = MainWindow()
        if not url or url == None:
            win.addTab(url=settings.settings.value("general/Homepage"))
        else:
            win.addTab(url=url)
        win.show()

    def loadSession(self, session):
        for tab in range(len(session)):
            self.addTab(index=tab)
            self.tabWidget().widget(tab).loadHistory(session[tab])

    def reopenWindow(self):
        if len(browser.closedWindows) > 0:
            session = browser.closedWindows.pop()
            win = MainWindow()
            win.loadSession(session)
            win.show()

    def addTab(self, webView=None, index=None, focus=True, **kwargs):
        # If a URL is specified, load it.
        if "incognito" in kwargs:
            webview = WebView(incognito=True, parent=self)
            if "url" in kwargs:
                webview.load(QUrl.fromUserInput(kwargs["url"]))

        elif "url" in kwargs:
            url = kwargs["url"]
            webview = WebView(incognito=not settings.\
                              setting_to_bool("data/RememberHistory"),\
                              parent=self)
            webview.load(QUrl.fromUserInput(url))

        # If a WebView object is specified, use it.
        elif webView != None:
            webview = webView

        # If nothing is specified, use a blank WebView.
        else:
            webview = WebView(incognito=not settings.setting_to_bool("data/RememberHistory"), parent=self)

        # Connect signals
        webview.loadProgress.connect(self.setProgress)
        webview.statusBarMessage.connect(self.setStatusBarMessage)
        webview.page().linkHovered.connect(self.setStatusBarMessage)
        webview.titleChanged.connect(self.updateTabTitles)
        webview.page().fullScreenRequested.connect(self.setFullScreen)
        webview.urlChanged.connect(self.updateLocationText)
        webview.iconChanged.connect(self.updateTabIcons)
        webview.iconChanged.connect(self.updateLocationIcon)
        webview.windowCreated.connect(lambda webView:\
                                      self.addTab(webView=webView,\
                                      index=self.tabWidget().\
                                            currentIndex()+1,\
                                      focus=False))
        webview.downloadStarted.connect(self.addDownloadToolBar)

        # Add tab
        if type(index) is not int:
            self.tabWidget().addTab(webview, tr("New Tab"))
        else:
            self.tabWidget().insertTab(index, webview, tr("New Tab"))

        # Switch to new tab
        if focus:
            self.tabWidget().setCurrentIndex(self.tabWidget().count()-1)

        # Update icons so we see the globe icon on new tabs.
        self.updateTabIcons()

    # Goes to the next tab.
    # Loops around if there is none.
    def nextTab(self):
        if self.tabWidget().currentIndex() == self.tabWidget().count() - 1:
            self.tabWidget().setCurrentIndex(0)
        else:
            self.tabWidget().setCurrentIndex(self.tabWidget().currentIndex() + 1)

    # Goes to the previous tab.
    # Loops around if there is none.
    def previousTab(self):
        if self.tabWidget().currentIndex() == 0:
            self.tabWidget().setCurrentIndex(self.tabWidget().count() - 1)
        else:
            self.tabWidget().setCurrentIndex(self.tabWidget().\
                                             currentIndex() - 1)

    # Update the titles on every single tab.
    def updateTabTitles(self):
        for index in range(0, self.tabWidget().count()):
            title = self.tabWidget().widget(index).windowTitle()
            self.tabWidget().setTabText(index, title[:24] + '...' if\
                                        len(title) > 24 else title)
            if index == self.tabWidget().currentIndex():
                self.setWindowTitle(title + " - " + tr("Nimbus"))

    # Update the icons on every single tab.
    def updateTabIcons(self):
        for index in range(0, self.tabWidget().count()):
            try: icon = self.tabWidget().widget(index).icon()
            except: continue
            self.tabWidget().setTabIcon(index, icon)

    # Removes a tab at index.
    def removeTab(self, index):
        if self.tabWidget().count() == 1 and settings.setting_to_bool("general/CloseWindowWithLastTab"):
            self.close()
            return
        try:
            webView = self.tabWidget().widget(index)
            if webView.history().canGoBack() or\
            webView.history().canGoForward() or\
            webView.url().toString() not in\
            ("about:blank", "",\
             QUrl.fromUserInput(settings.new_tab_page).toString(),):
                self.closedTabs.append((webView.saveHistory(), index))
                while len(self.closedTabs) >\
                settings.setting_to_int("general/ReopenableTabCount"):
                    self.closedTabs.pop(0)
            webView.deleteLater()
        except:
            traceback.print_exc()
        self.tabWidget().removeTab(index)
        if self.tabWidget().count() == 0 and\
        not settings.setting_to_bool("general/CloseWindowWithLastTab"):
            self.addTab(url="about:blank")

    # Reopens the last closed tab.
    def reopenTab(self):
        if len(self.closedTabs) > 0:
            index = self.closedTabs[-1][1]
            self.addTab(index=index)
            self.tabWidget().setCurrentIndex(index)
            self.tabWidget().widget(index).loadHistory(self.closedTabs[-1][0])
            del self.closedTabs[-1]

    # This method is used to add a DownloadBar to the window.
    def addDownloadToolBar(self, toolbar):
        self.statusBar.addToolBar(toolbar)

    # Method to update the location bar text.
    def updateLocationText(self, url=None):
        try:
            if type(url) != QUrl:
                url = self.tabWidget().currentWidget().url()
            currentUrl = self.tabWidget().currentWidget().url()
            if url == currentUrl:
                self.locationBar.setEditText(currentUrl.toString())
        except:
            pass

    def updateLocationIcon(self, url=None):
        try:
            if type(url) != QUrl:
                url = self.tabWidget().currentWidget().url()
            currentUrl = self.tabWidget().currentWidget().url()
            if url == currentUrl:
                self.locationBar.setIcon(self.tabs.currentWidget().icon())
        except:
            pass