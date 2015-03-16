#! /usr/bin/env python3

# ---------------------
# view_source_dialog.py
# ---------------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains a simple text dialog for viewing a page's
#              source code. It was ported over from Ryouko
#              (http://github.com/foxhead128/ryouko).

from __future__ import print_function

from common import pyqt4
import os.path, sys
if not pyqt4:
    from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, QObject, QSize
    Signal = pyqtSignal
    from PyQt5.QtGui import QTextDocument
    from PyQt5.QtWidgets import QMainWindow, QMenuBar, QMenu, QAction, QTextEdit, QFileDialog, QInputDialog, QLineEdit, QTabWidget
else:
    try:
        from PyQt4.QtCore import Qt, QCoreApplication, pyqtSignal, QObject, QSize
        Signal = pyqtSignal
        from PyQt4.QtGui import QMainWindow, QMenuBar, QMenu, QAction, QTextEdit, QTextDocument, QFileDialog, QInputDialog, QLineEdit, QTabWidget
    except ImportError:
        from PySide.QtCore import Qt, QCoreApplication, Signal, QObject, QSize
        from PySide.QtGui import QMainWindow, QMenuBar, QMenu, QAction, QTextEdit, QTextDocument, QFileDialog, QInputDialog, QLineEdit, QTabWidget
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)
from translate import tr

class SourceView(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(SourceView, self).__init__(*args, **kwargs)
    def wheelEvent(self, e):
        if QCoreApplication.instance().keyboardModifiers() != Qt.NoModifier:
            return
        else:
            QTextEdit.wheelEvent(self, e)

class ViewSourceDialogTabber(QMainWindow):
    def __init__(self, parent=None, title="Source"):
        super(ViewSourceDialogTabber, self).__init__(parent)
        self.setWindowTitle(title)
        self.tabs = QTabWidget(self)
        self.tabs.setElideMode(Qt.ElideRight)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.removeTab)
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self.updateWindowTitle)
    def sizeHint(self):
        return QSize(640, 480)
    def removeTab(self):
        self.tabWidget().removeTab(index)
    def addTab(self, title="New Tab", data=""):
        vsd = ViewSourceDialog(self, str(title))
        vsd.setPlainText(data)
        self.tabs.addTab(vsd, tr("Source of %s") % (title,))
        self.tabs.setCurrentIndex(self.tabs.count()-1)
        self.raise_()
        self.activateWindow()
    def updateWindowTitle(self):
        try: self.setWindowTitle(tr("Source of %s") % (self.tabs.currentWidget().windowTitle(),))
        except: pass
        if self.tabs.count() == 0:
            self.hide()

class ViewSourceDialog(QMainWindow):
    closed = pyqtSignal(QObject)
    def __init__(self, parent=None, title="Source"):
        super(ViewSourceDialog, self).__init__()
        self.setParent(parent)
        self.menuBar = QMenuBar(self)
        self.menuBar.setStyleSheet("""QMenuBar { background: transparent; border: 0; }
                                      QMenuBar::item { background: transparent;
                                                       color: palette(window-text); }
                                      QMenuBar::item:pressed { background: palette(highlight);
                                                               color: palette(highlighted-text); }""")
        self.setMenuBar(self.menuBar)

        self.text = ""
        self.findFlag = None

        self.fileMenu = QMenu(tr("&File"), self.menuBar)
        self.menuBar.addMenu(self.fileMenu)

        self.saveAsAction = QAction(tr("&Save As..."), self)
        self.saveAsAction.setShortcut("Ctrl+S")
        self.saveAsAction.triggered.connect(self.saveAs)
        self.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.saveAsAction)

        self.viewMenu = QMenu(tr("&View"), self.menuBar)
        self.menuBar.addMenu(self.viewMenu)

        self.findAction = QAction(tr("&Find..."), self)
        self.findAction.setShortcut("Ctrl+F")
        self.findAction.triggered.connect(self.find)
        self.addAction(self.findAction)
        self.viewMenu.addAction(self.findAction)

        self.findNextAction = QAction(tr("Find Ne&xt"), self)
        self.findNextAction.setShortcut("Ctrl+G")
        self.findNextAction.triggered.connect(self.findNext)
        self.addAction(self.findNextAction)
        self.viewMenu.addAction(self.findNextAction)

        self.findPreviousAction = QAction(tr("Find Pre&vious"), self)
        self.findPreviousAction.setShortcut("Ctrl+Shift+G")
        self.findPreviousAction.triggered.connect(self.findPrevious)
        self.addAction(self.findPreviousAction)
        self.viewMenu.addAction(self.findPreviousAction)

        self.sourceView = SourceView(self)
        self.sourceView.setReadOnly(True)
        self.sourceView.setFontFamily("monospace")
        self.setCentralWidget(self.sourceView)
        closeWindowAction = QAction(self)
        closeWindowAction.setShortcut("Ctrl+W")
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)
        self.setWindowTitle(title)

        self.resize(640, 480)

    def closeEvent(self, ev):
        super(ViewSourceDialog, self).closeEvent(ev)
        self.deleteLater()

    def saveAs(self):
        fname = QFileDialog.getSaveFileName(None, tr("Save As..."), self.windowTitle() + ".txt", tr("Text files (*.txt)"))
        if type(fname) is tuple:
            fname = fname[0]
        if fname:
            g = str(self.sourceView.toPlainText())
            f = open(fname, "w")
            f.write(g)
            f.close()

    def find(self):
        find = QInputDialog.getText(self, tr("Find"), tr("Search for:"), QLineEdit.Normal, self.text)
        if find[1]:
            self.text = find[0]
        else:
            self.text = ""
        if self.findFlag:
            self.sourceView.find(self.text, self.findFlag)
        else:
            self.sourceView.find(self.text)

    def findNext(self, findFlag=None):
        if not self.text:
            self.find()
        else:
            self.findFlag = findFlag
            if self.findFlag:
                self.sourceView.find(self.text, self.findFlag)
            else:
                self.sourceView.find(self.text)

    def findPrevious(self):
        self.findNext(QTextDocument.FindBackward)

    def setFindFlag(self):
        if self.findReverseAction.isChecked():
            self.findFlag = QTextDocument.FindBackward
        else:
            self.findFlag = None

    def setPlainText(self, *args, **kwargs):
        self.sourceView.setPlainText(*args, **kwargs)

    def doNothing(self):
        pass

    def closeEvent(self, ev):
        self.closed.emit(self)
        self.deleteLater()
        ev.accept()
