#!/usr/bin/env python3

import os
import sys
import custom_widgets
import common
import system
import network
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QToolBar, QCalendarWidget, QToolButton

class StatusRocker(QToolBar):
    def __init__(self, *args, **kwargs):
        super(StatusRocker, self).__init__(*args, **kwargs)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # Displays the date and time while in fullscreen mode.
        self.dateTime = QAction(self)
        self.addAction(self.dateTime)
        self.dateTimeButton = self.widgetForAction(self.dateTime)
        self.dateTimeButton.setStyleSheet("QToolButton { font-family: monospace; border-radius: 4px; padding: 2px; background: palette(highlight); color: palette(highlighted-text); }")
        self.dateTimeButton.clicked.connect(self.showCalendar)
        self.dateTime.setVisible(False)
        
        self.batteryAction = custom_widgets.BatteryAction(self)
        self.addAction(self.batteryAction)
        self.batteryWidget = self.widgetForAction(self.batteryAction)
        self.batteryWidget.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Add stuff for linux
        self.networkManagerAction = QAction(common.complete_icon("network-idle"), "N/A", self)
        self.networkManagerAction.setToolTip("Network Management")
        self.networkManagerAction.setShortcut("Alt+N")
        self.addAction(self.networkManagerAction)
        self.networkManagerButton = self.widgetForAction(self.networkManagerAction)
        self.networkManagerButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addAction(self.networkManagerAction)
        if sys.platform.startswith("linux"):
            self.networkManagerMenu = QMenu(self)
            self.networkManagerMenu.aboutToShow.connect(self.aboutToShowNetworkManagerMenu)
            self.connectedToAction = QAction(self.networkManagerMenu)
            self.connectedToAction.setDisabled(True)
            self.networkManagerMenu.addAction(self.connectedToAction)
            
            self.connectAction = QAction("Connect to Wi-Fi Network...", self.networkManagerMenu)
            self.connectAction.triggered.connect(lambda: os.system("qdbus org.gnome.network_manager_applet /org/gnome/network_manager_applet ConnectToHiddenNetwork &"))
            self.networkManagerMenu.addAction(self.connectAction)
        
            self.connectionEditAction = QAction("Edit Connections...", self.networkManagerMenu)
            self.connectionEditAction.triggered.connect(lambda: os.system("nm-connection-editor &"))
            self.networkManagerMenu.addAction(self.connectionEditAction)
        
            self.networkManagerAction.triggered.connect(self.networkManagerButton.showMenu)
            self.networkManagerAction.setMenu(self.networkManagerMenu)
            self.networkManagerButton.setPopupMode(QToolButton.InstantPopup)
        else:
            self.networkManagerAction.triggered.connect(lambda: os.system("control ncpa.cpl"))
        self.timer = QTimer(timeout=self.updateNetworkStatus, parent=self)
        self.timer.start(500)
    def showCalendar(self):
        calendar.setVisible(not calendar.isVisible())
        y = self.dateTimeButton.mapToGlobal(QPoint(0,0)).y() + self.dateTimeButton.height()
        calendar.move(min(self.dateTimeButton.mapToGlobal(QPoint(0,0)).x(), common.desktop.width()-calendar.width()), self.dateTimeButton.mapToGlobal(QPoint(0,0)).y()-calendar.height() if y > common.desktop.height()-calendar.height() else y)
    def aboutToShowNetworkManagerMenu(self):
        if network.isConnectedToNetwork():
            self.connectedToAction.setText("Connected to %s" % system.get_ssid())
        else:
            self.connectedToAction.setText(tr("No Internet connection"))
    def updateNetworkStatus(self):
        self.networkManagerAction.setIcon(common.complete_icon("network-idle") if network.isConnectedToNetwork() else common.complete_icon("network-offline"))
        strength = system.get_signal_strength()
        self.networkManagerAction.setText(strength)

def main(argv):
    app = QApplication(argv)
    calendar = QCalendarWidget()
    win = StatusRocker()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)
