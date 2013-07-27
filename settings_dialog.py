#! /usr/bin/env python3

import common
from PyQt4.QtCore import Qt, QUrl
from PyQt4.QtGui import QWidget, QIcon, QLabel, QMainWindow, QTabWidget, QToolBar, QToolButton, QLineEdit, QVBoxLayout, QComboBox, QSizePolicy, QAction, QPushButton, QListWidget

# Basic settings panel.
class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__(parent)
        # Create layout.
        newLayout = QVBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(4,4,4,4)
    def loadSettings(self):
        pass
    def saveSettings(self):
        pass

# General configuration panel
class GeneralSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(GeneralSettingsPanel, self).__init__(parent)

        # Homepage row.
        homepageRow = common.LineEditRow("Homepage:", self)
        self.homepageEntry = homepageRow.lineEdit
        self.layout().addWidget(homepageRow)

        # Default search.
        searchRow = common.LineEditRow("Search expression:", self)
        self.searchEntry = searchRow.lineEdit
        self.layout().addWidget(searchRow)

        self.layout().addWidget(common.Expander(self))

    def loadSettings(self):
        self.homepageEntry.setText(str(common.settings.value("homepage")))
        self.searchEntry.setText(str(common.settings.value("search")))

    def saveSettings(self):
        common.settings.setValue("homepage", self.homepageEntry.text())
        common.settings.setValue("search", self.searchEntry.text())

# Network configuration panel
class NetworkSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(NetworkSettingsPanel, self).__init__(parent)

        # Proxy label.
        proxyLabel = QLabel("<b>Proxy configuration</b>")
        self.layout().addWidget(proxyLabel)

        # Type row.
        typeRow = common.Row(self)
        self.layout().addWidget(typeRow)

        # Create a nice label.
        typeLabel = QLabel("Type:", self)
        typeRow.addWidget(typeLabel)

        # Combo box to select proxy type.
        self.proxySelect = QComboBox(self)
        self.proxySelect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.proxySelect.addItem("None")
        self.proxySelect.addItem('Socks5')
        self.proxySelect.addItem('Http')
        typeRow.addWidget(self.proxySelect)

        # Hostname row.
        self.hostNameRow = common.LineEditRow("Hostname:", self)
        self.hostNameEntry = self.hostNameRow.lineEdit
        self.layout().addWidget(self.hostNameRow)

        # Port row.
        self.portRow = common.LineEditRow("Port:", self)
        self.portRow.lineEdit.setInputMask("99999")
        self.portEntry = self.portRow.lineEdit
        self.layout().addWidget(self.portRow)

        # User row.
        self.userRow = common.LineEditRow("User:", self)
        self.userEntry = self.userRow.lineEdit
        self.layout().addWidget(self.userRow)

        # Password row.
        self.passwordRow = common.LineEditRow("Password:", self)
        self.passwordEntry = self.passwordRow.lineEdit
        self.layout().addWidget(self.passwordRow)

        # Add an expander.
        expander = common.Expander(self)
        self.layout().addWidget(expander)

    def loadSettings(self):
        self.hostNameEntry.setText(str(common.settings.value("proxy/hostname")))
        self.userEntry.setText(str(common.settings.value("proxy/user")))
        self.passwordEntry.setText(str(common.settings.value("proxy/password")))
        port = str(common.settings.value("proxy/port"))
        if port == "None":
            port = str(common.default_port)
        self.portEntry.setText(port)
        for index in range(0, self.proxySelect.count()):
            if self.proxySelect.itemText(index) == common.settings.value("proxy/type"):
                self.proxySelect.setCurrentIndex(index)
                break

    def saveSettings(self):
        common.settings.setValue("proxy/hostname", self.hostNameEntry.text())
        proxyType = self.proxySelect.currentText()
        if proxyType == "None":
            proxyType = "No"
        common.settings.setValue("proxy/type", proxyType)
        common.settings.setValue("proxy/port", int(self.portEntry.text()))
        common.settings.setValue("proxy/user", self.userEntry.text())
        common.settings.setValue("proxy/password", self.passwordEntry.text())
        common.settings.sync()

# Extension configuration panel
class ExtensionsSettingsPanel(SettingsPanel):
    def __init__(self, parent=None):
        super(ExtensionsSettingsPanel, self).__init__(parent)

        # List row
        listRow = common.Row(self)
        self.layout().addWidget(listRow)

        # Extensions whitelist.
        whitelistColumn = common.Column(self)
        listRow.addWidget(whitelistColumn)
        whitelistColumn.addWidget(QLabel("Enabled extensions:", self))
        self.whitelist = QListWidget(self)
        self.whitelist.itemActivated.connect(self.disableExtension)
        whitelistColumn.addWidget(self.whitelist)

        # Extensions blacklist.
        blacklistColumn = common.Column(self)
        listRow.addWidget(blacklistColumn)
        blacklistColumn.addWidget(QLabel("Disabled extensions:", self))
        self.blacklist = QListWidget(self)
        self.blacklist.itemActivated.connect(self.enableExtension)
        blacklistColumn.addWidget(self.blacklist)

        self.layout().addWidget(common.Expander(self))

    def disableExtension(self, item):
        name = item.text()
        self.blacklist.addItem(name)
        self.blacklist.sortItems(Qt.AscendingOrder)
        self.whitelist.takeItem(self.whitelist.row(item))
        self.whitelist.sortItems(Qt.AscendingOrder)

    def enableExtension(self, item):
        name = item.text()
        self.whitelist.addItem(name)
        self.whitelist.sortItems(Qt.AscendingOrder)
        self.blacklist.takeItem(self.blacklist.row(item))
        self.blacklist.sortItems(Qt.AscendingOrder)

    def loadSettings(self):
        self.whitelist.clear()
        for extension in common.settings.value("extensions/whitelist"):
            self.whitelist.addItem(extension)
        self.blacklist.clear()
        for extension in common.extensions_blacklist:
            self.blacklist.addItem(extension)

    def saveSettings(self):
        common.settings.setValue("extensions/whitelist", [self.whitelist.item(extension).text() for extension in range(0, self.whitelist.count())])
        common.reload_extensions_blacklist()

# Main settings dialog
class SettingsDialog(QMainWindow):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        # Set window title.
        self.setWindowTitle("Settings")

        # Tab widget
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(GeneralSettingsPanel(self), "&General")
        self.tabs.addTab(NetworkSettingsPanel(self), "&Network")
        self.tabs.addTab(ExtensionsSettingsPanel(self), "&Extensions")

        # Toolbar
        self.toolBar = QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.toolBar.setStyleSheet(common.blank_toolbar)
        self.addToolBar(Qt.BottomToolBarArea, self.toolBar)

        # Apply button
        applyButton = QPushButton("&Apply", self)
        applyButton.clicked.connect(self.saveSettings)
        self.toolBar.addWidget(applyButton)

        # Reload settings button
        reloadButton = QPushButton("&Reload", self)
        reloadButton.clicked.connect(self.loadSettings)
        self.toolBar.addWidget(reloadButton)

        # Load settings
        self.loadSettings()

    def url(self):
        return QUrl("")

    def icon(self):
        return QIcon().fromTheme("preferences-system")

    # Method to load all settings.
    def loadSettings(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).loadSettings()
    
    # Method to save all settings.
    def saveSettings(self):
        for index in range(0, self.tabs.count()):
            self.tabs.widget(index).saveSettings()
        for window in common.windows:
            window.reloadExtensions()
        for webview in common.webviews:
            webview.updateProxy()