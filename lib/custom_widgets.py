#! /usr/bin/env python3

# -----------------
# custom_widgets.py
# -----------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: Custom widgets used by Nimbus.

import os
import sys
try:
    import settings
except ImportError:
    pass
from common import app_folder, blank_toolbar, complete_icon, pyqt4
from translate import tr
import system

if not pyqt4:
    from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QUrl, QSize, QTimer, QCoreApplication
    Signal = pyqtSignal
    from PyQt5.QtGui import QIcon, QPixmap
    from PyQt5.QtWidgets import QMainWindow, QAction, QToolButton, QPushButton, QWidget, QComboBox, QHBoxLayout, QTabWidget, QTextEdit, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QSpinBox, QToolBar, QStyle, QStylePainter, QStyleOptionToolBar, QMenu, QTabBar, QWidgetAction, QListWidget
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QPoint, QUrl, QSize, QTimer, QCoreApplication
    Signal = pyqtSignal
    from PyQt4.QtGui import QPixmap, QMainWindow, QAction, QToolButton, QPushButton, QIcon, QWidget, QComboBox, QHBoxLayout, QTabWidget, QTextEdit, QVBoxLayout, QLabel, QSizePolicy, QLineEdit, QSpinBox, QToolBar, QStyle, QStylePainter, QStyleOptionToolBar, QMenu, QTabBar, QWidgetAction, QListWidget

# Custom LineEdit class with delete button.
if sys.platform.startswith("linux"):
    class LineEdit(QLineEdit):
        def __init__(self, *args, **kwargs):
            super(LineEdit, self).__init__(*args, **kwargs)
            self.clearButton = QToolButton(self)
            icon = complete_icon("fileclose")
            self.clearButton.setIcon(icon)
            self.clearButton.setIconSize(icon.pixmap(QSize(16, 16)).size())
            self.clearButton.setCursor(Qt.ArrowCursor)
            self.clearButton.setStyleSheet("QToolButton { border: none; padding: 0px; }")
            self.clearButton.hide()
            self.clearButton.clicked.connect(self.clear)
            self.textChanged.connect(self.updateCloseButton)
            frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
            self.setStyleSheet("QLineEdit { padding-right: %spx; }" % (self.clearButton.sizeHint().width() + frameWidth + 1,))
            msz = self.minimumSizeHint()
            self.setMinimumSize(max(msz.width(), self.clearButton.sizeHint().height() + frameWidth * 2 + 2),
                       max(msz.height(), self.clearButton.sizeHint().height() + frameWidth * 2 + 2));

        def resizeEvent(self, *args, **kwargs):
            super(LineEdit, self).resizeEvent(*args, **kwargs)
            sz = self.clearButton.sizeHint()
            frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
            self.clearButton.move(self.rect().right() - frameWidth - sz.width(),
                          (self.rect().bottom() + 1 - sz.height())/2)

        def updateCloseButton(self, text):
            self.clearButton.setVisible(text != "")
else:
    class LineEdit(QLineEdit):
        def __init__(self, *args, **kwargs):
            super(LineEdit, self).__init__(*args, **kwargs)
            self.setStyleSheet("QLineEdit { }")

# This action shows how much power the computer has left.
class BatteryAction(QAction):
    timer = QTimer(QCoreApplication.instance())
    def __init__(self, *args, **kwargs):
        super(BatteryAction, self).__init__(*args, **kwargs)
        self.setToolTip(tr("Power"))
        if system.battery:
            self.updateLife()
            self.timer.timeout.connect(self.updateLife)
            if not self.timer.isActive():
                self.timer.start(5000)
        elif system.is_on_ac():
            self.setIcon(complete_icon("charging"))
            self.setText(tr("AC"))
            self.setToolTip(tr("System is running on AC power"))
        else:
            self.setIcon(complete_icon("dialog-warning"))
            self.setText(tr("N/A"))
            self.setToolTip(tr("Battery not detected"))
    def deleteLater(self):
        try: self.timer.timeout.disconnect(self.updateLife)
        except: pass
        super(BatteryAction, self).deleteLater()
    def updateLife(self):
        percentage = system.get_battery_percentage()
        text_percentage = str(percentage) + "%"
        self.setText(text_percentage)
        percent = tr("Power remaining: %s%s")
        ac = system.is_on_ac()
        self.setToolTip(percent % (text_percentage, " (AC)" if ac else ""))
        if ac:
            self.setIcon(complete_icon("charging"))
            return
        if percentage >= 40:
            self.setIcon(complete_icon("battery"))
        elif percentage >= 10:
            self.setIcon(complete_icon("battery-caution"))
        else:
            self.setIcon(complete_icon("dialog-warning"))

# This QLineEdit can be shoved into a menu.
class LineEditAction(QWidgetAction):
    def __init__(self, *args, **kwargs):
        super(LineEditAction, self).__init__(*args, **kwargs)
        self._lineEdit = QLineEdit()
        self.setDefaultWidget(self._lineEdit)
    def lineEdit(self):
        return self._lineEdit

# This toolbar can be shoved into a menu.
class ToolBarAction(QWidgetAction):
    def __init__(self, *args, **kwargs):
        super(ToolBarAction, self).__init__(*args, **kwargs)
        self._toolBar = QToolBar(styleSheet="QToolBar {background: transparent; border: 0;}")
        self._toolBar.setIconSize(QSize(16, 16))
        self.setDefaultWidget(self._toolBar)
    def toolBar(self):
        return self._toolBar
    def addAction(self, action):
        self._toolBar.addAction(action)
        if action.shortcut().toString() > "":
            action.setToolTip(action.text().replace("&", "") + "<br>" + action.shortcut().toString())
    def widgetForAction(self, *args, **kwargs):
        return self._toolBar.widgetForAction(*args, **kwargs)
    def addWidget(self, *args, **kwargs):
        self._toolBar.addWidget(*args, **kwargs)
    def addSeparator(self):
        self._toolBar.addSeparator()

# List widget as an action
class ListWidgetAction(QWidgetAction):
    def __init__(self, *args, **kwargs):
        super(ListWidgetAction, self).__init__(*args, **kwargs)
        self._listWidget = QListWidget()
        self._listWidget.setAlternatingRowColors(True)
        self.setDefaultWidget(self._listWidget)
    def listWidget(self):
        return self._listWidget

# Blank widget to take up space.
class Expander(QLabel):
    def __init__(self, parent=None):
        super(Expander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class HorizontalExpander(QLabel):
    def __init__(self, parent=None):
        super(HorizontalExpander, self).__init__(parent)
        self.setText("")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

# Row widget.
class Row(QWidget):
    def __init__(self, parent=None):
        super(Row, self).__init__(parent)
        newLayout = QHBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

# This toolbar can be shoved into a menu.
class RowAction(QWidgetAction):
    def __init__(self, *args, **kwargs):
        super(RowAction, self).__init__(*args, **kwargs)
        self._row = Row()
        self.setDefaultWidget(self._row)
    def row(self):
        return self._row
    def addWidget(self, widget):
        self._row.addWidget(widget)

# This is a row with a label and a QLineEdit.
class LineEditRow(Row):
    def __init__(self, text="Enter something here:", parent=None):
        super(LineEditRow, self).__init__(parent)
        self.label = QLabel(text, self)
        self.addWidget(self.label)
        self.lineEdit = LineEdit(self)
        self.addWidget(self.lineEdit)

# This is a row with a label and a QSpinBox.
class SpinBoxRow(Row):
    def __init__(self, text="Enter something here:", parent=None):
        super(SpinBoxRow, self).__init__(parent)
        self.label = QLabel(text, self)
        self.addWidget(self.label)
        self.spinBox = QSpinBox(self)
        self.addWidget(self.spinBox)
        self.expander = HorizontalExpander()
        self.addWidget(self.expander)

# Column widget.
class Column(QWidget):
    def __init__(self, parent=None):
        super(Column, self).__init__(parent)
        newLayout = QVBoxLayout()
        self.setLayout(newLayout)
        self.layout().setContentsMargins(0,0,0,0)
    def addWidget(self, widget):
        self.layout().addWidget(widget)

# Invisible menu.
class InvisibleMenu(QMenu):
    def setVisible(self, visible):
        QMenu.setVisible(self, False)

# Toolbar that looks like a menubar.
class _MenuToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super(_MenuToolBar, self).__init__(*args, **kwargs)
        self._isMenuBar = True
    def isMenuBar(self):
        return self._isMenuBar
    def addAction(self, action):
        super(_MenuToolBar, self).addAction(action)
        if action.shortcut().toString() > "":
            action.setToolTip(action.text().replace("&", "") + "<br>" + action.shortcut().toString())
    def setIsMenuBar(self, isMenuBar):
        self._isMenuBar = bool(isMenuBar)
        self.repaint()
    def paintEvent(self, event):
        if self.isMenuBar():
            painter = QStylePainter(self)
            option = QStyleOptionToolBar()
            self.initStyleOption(option)
            style = self.style()
            style.drawControl(QStyle.CE_MenuBarEmptyArea, option, painter, self)
        else:
            QToolBar.paintEvent(self, event)

class MenuToolBar(QToolBar):
    pass

if not sys.platform.startswith("darwin"):
    MenuToolBar = _MenuToolBar

# Location bar.
class LocationBar(QLineEdit):
    def __init__(self, *args, icon=None, **kwargs):
        super(LocationBar, self).__init__(*args, **kwargs)
        self.icon = QToolButton(self)
        self._savedText = ""
        if type(icon) is QIcon:
            self.icon.setIcon(icon)
        self.icon.setFixedWidth(16)
        self.icon.setFixedHeight(16)
        self.icon.setStyleSheet("QToolButton { border: 0; background: transparent; width: 16px; height: 16px; }")
        sz = self.icon
        fw = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.s = False
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(), self.icon.sizeHint().height() + fw * 2 + 2), max(msz.height(), self.icon.sizeHint().height() + fw * 2 + 2))

    def savedText(self):
        return self._savedText

    def setSavedText(self, text):
        self._savedText = str(text)

    def resizeEvent(self, ev):
        super(LocationBar, self).resizeEvent(ev)
        sz = self.icon
        fw = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.icon.move(QPoint(self.rect().left() + (self.height() + 1 - sz.width())/2, (self.height() + 1 - sz.height())/2))
        if self.s == False:
            self.setStyleSheet("QLineEdit { background: transparent; padding-left: %spx; }" % str(sz.width() + (self.height() + 1 - sz.width())/2))
            self.s = True
            self.redefResizeEvent()

    def redefResizeEvent(self):
        self.resizeEvent = self.shortResizeEvent

    def shortResizeEvent(self, ev):
        super(LocationBar, self).resizeEvent(ev)
        sz = self.icon
        fw = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.icon.move(QPoint(self.rect().left() + (self.height() + 1 - sz.width())/2, (self.height() + 1 - sz.height())/2))

    def setIcon(self, icon):
        self.icon.setIcon(icon)

    # These are just here to maintain some level of compatibility with older extensions.

    def lineEdit(self):
        return self

    def setEditText(self, *args, **kwargs):
        self.setText(*args, **kwargs)

    def addItem(self, *args, **kwargs):
        pass

# Link action for dropdown menus.
class LinkAction(QAction):
    triggered2 = Signal([str], [QUrl])
    def __init__(self, url, *args, **kwargs):
        super(LinkAction, self).__init__(*args, **kwargs)
        self.url = url
        if type(self.url) is QUrl:
            self.triggered.connect(lambda: self.triggered2[QUrl].emit(self.url))
        else:
            self.triggered.connect(lambda: self.triggered2.emit(self.url))

# Action that emits a number.
class IndexAction(QAction):
    triggered2 = Signal(int)
    def __init__(self, index, *args, **kwargs):
        super(IndexAction, self).__init__(*args, **kwargs)
        self.setData(index)
        self.triggered.connect(lambda: self.triggered2.emit(self.data()))

# Action that emits a number.
class StringAction(QAction):
    triggered2 = Signal(str)
    def __init__(self, data, *args, **kwargs):
        super(StringAction, self).__init__(*args, **kwargs)
        self.setData(data)
        self.triggered.connect(lambda: self.triggered2.emit(self.data()))

# Web history action for dropdown menus.
class WebHistoryAction(IndexAction):
    pass

# License view class.
class ReadOnlyTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(ReadOnlyTextEdit, self).__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setFontFamily("monospace")

# Tab bar.
class TabBar(QTabBar):
    def minimumSizeHint(self):
        return QSize(0, 0)

# Tab widget.
class TabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(TabWidget, self).__init__(*args, **kwargs)
        tabbar = TabBar()
        self.setTabBar(tabbar)
    def minimumSizeHint(self):
        return QSize(0, 0)
    def resizeEvent(self, ev):
        size = self.tabBar().size()
        QTabWidget.resizeEvent(self, ev)
        self.tabBar().resize(size)

# Licensing dialog.
class LicenseDialog(QMainWindow):
    def __init__(self, parent=None):
        super(LicenseDialog, self).__init__(parent)
        self.resize(420, 320)
        self.setWindowTitle(tr("Credits & Licensing"))
        self.setWindowFlags(Qt.Dialog)
        self.readme = ""
        self.license = ""
        self.thanks = ""
        self.authors = ""
        self.tabWidget = QTabWidget(self)
        self.setCentralWidget(self.tabWidget)
        for folder in (app_folder, os.path.dirname(app_folder)):
            for fname in os.listdir(folder):
                if fname.startswith("LICENSE"):
                    try: f = open(os.path.join(folder, fname), "r")
                    except: pass
                    else:
                        self.license = f.read()
                        f.close()
                elif fname.startswith("THANKS"):
                    try: f = open(os.path.join(folder, fname), "r")
                    except: pass
                    else:
                        self.thanks = f.read()
                        f.close()
                elif fname.startswith("AUTHORS"):
                    try: f = open(os.path.join(folder, fname), "r")
                    except: pass
                    else:
                        self.authors = f.read()
                        f.close()
                elif fname.startswith("README"):
                    try: f = open(os.path.join(folder, fname), "r")
                    except: pass
                    else:
                        self.readme = f.read()
                        f.close()
        self.readmeView = ReadOnlyTextEdit(self)
        self.readmeView.setText(self.readme)
        self.tabWidget.addTab(self.readmeView, tr("&README"))
        self.authorsView = ReadOnlyTextEdit(self)
        self.authorsView.setText(self.authors)
        self.tabWidget.addTab(self.authorsView, tr("&Authors"))
        self.thanksView = ReadOnlyTextEdit(self)
        self.thanksView.setText(self.thanks)
        self.tabWidget.addTab(self.thanksView, tr("&Thanks"))
        self.licenseView = ReadOnlyTextEdit(self)
        self.licenseView.setText(self.license)
        self.tabWidget.addTab(self.licenseView, tr("&License"))
        closeAction = QAction(self)
        closeAction.setShortcuts(["Esc", "Ctrl+W"])
        closeAction.triggered.connect(self.hide)
        self.addAction(closeAction)
        self.toolBar = QToolBar(self)
        self.toolBar.setStyleSheet(blank_toolbar)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(Qt.BottomToolBarArea, self.toolBar)
        self.toolBar.addWidget(HorizontalExpander(self))
        self.closeButton = QPushButton(tr("&OK"), self)
        self.closeButton.clicked.connect(self.close)
        self.toolBar.addWidget(self.closeButton)
        self.closeButton.setFocus()
