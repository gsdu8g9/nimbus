import json
settings.settings.setValue("general/FeedButtonVisible", True)
settings.settings.sync()
try: common.feeds
except:
    feeds = data.data.value("data/Feeds")
    if not feeds:
        common.feeds = []
        data.data.setValue("data/Feeds", json.dumps(common.feeds))
        data.data.sync()
    else:
        common.feeds = json.loads(feeds)
self.feedMenuButton.setText(tr("Bookmarks"))
self.feedMenuButton.setShortcut("Ctrl+Shift+B")
try: self.feedMenuButton.setIcon(QIcon(common.complete_icon("bookmarks")))
except: traceback.print_exc()
self.toolBar.widgetForAction(self.feedMenuButton).setPopupMode(QToolButton.MenuButtonPopup)
self.feedMenuButton.setCheckable(True)
def toggleFeedsDock():
    try: browser.activeWindow().feedsDock
    except:
        mainWindow = browser.activeWindow()
        mainWindow.feedsDock = QDockWidget(mainWindow)
        mainWindow.feedsDock.setContextMenuPolicy(Qt.CustomContextMenu)
        mainWindow.feedsDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        mainWindow.feedsList = QListWidget(browser.activeWindow().feedsDock)
        mainWindow.feedsDock.setWindowTitle("Bookmarks")
        mainWindow.feedsList.addItem("+")
        for feed in common.feeds:
            mainWindow.feedsList.addItem(feed)
        mainWindow.feedsDock.setWidget(browser.activeWindow().feedsList)
        deleteAction = QAction(browser.activeWindow().feedsList)
        deleteAction.setShortcut("Del")
        mainWindow.feedsList.addAction(deleteAction)
        def removeBookmark():
            if browser.activeWindow().feedsList.hasFocus():
                import json
                currentItem = browser.activeWindow().feedsList.currentItem()
                url = currentItem.text()
                browser.activeWindow().feedsList.takeItem(browser.activeWindow().feedsList.row(currentItem))
                try: common.feeds.remove(url)
                except: pass
                data.data.setValue("data/Feeds", json.dumps(common.feeds))
                data.data.sync()
        deleteAction.triggered.connect(removeBookmark)
        def loadFeed(item):
            import json
            if item.text() == "+":
                url = QInputDialog.getText(None, "Add Feed", "Enter a URL here:", QLineEdit.Normal, browser.activeWindow().tabWidget().currentWidget().url().toString())
                if url[1]:
                    browser.activeWindow().feedsList.addItem(url[0])
                    common.feeds.append(url[0])
                    data.data.setValue("data/Feeds", json.dumps(common.feeds))
                    data.data.sync()
            else:
                browser.activeWindow().tabs.currentWidget().load(QUrl.fromUserInput(item.text()))
        browser.activeWindow().feedsList.itemActivated.connect(loadFeed)
        mainWindow.addDockWidget(Qt.RightDockWidgetArea, mainWindow.feedsDock)
    else:
        browser.activeWindow().feedsDock.setVisible(not browser.activeWindow().feedsDock.isVisible())
        browser.activeWindow().feedsList.clear()
        browser.activeWindow().feedsList.addItem("+")
        for feed in sorted(common.feeds):
            browser.activeWindow().feedsList.addItem(feed)
    try:
        browser.activeWindow().styleDock.hide()
        browser.activeWindow().styleMenuButton.setChecked(False)
    except: pass
    try:
        browser.activeWindow().notePadDock.hide()
        browser.activeWindow().notePadMenuButton.setChecked(False)
    except: pass
self.feedMenuButton.triggered.connect(toggleFeedsDock)
