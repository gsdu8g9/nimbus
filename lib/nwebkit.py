#! /usr/bin/env python3

# ----------
# nwebkit.py
# ----------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module mainly contains stuff related to QtWebKit.

# Import everything we need.
import sys
import os
import re
import browser
import urllib.parse
import hashlib
import common
import traceback
import geolocation
import custom_widgets
import filtering
import translate
from translate import tr
import settings
import data
import network
import rss_parser
#import view_source_dialog

# Extremely specific imports from PyQt5/PySide.
# We give PyQt5 priority because it supports Qt5.
if not common.pyqt4:
    from PyQt5.QtCore import Qt, QSize, QObject, QCoreApplication, pyqtSignal, pyqtSlot, QUrl, QFile, QIODevice, QTimer, QByteArray, QDataStream, QDateTime, QPoint, QEventLoop
    from PyQt5.QtGui import QIcon, QImage, QClipboard, QCursor, QDesktopServices
    from PyQt5.QtWidgets import QApplication, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QAction, QToolBar, QLineEdit, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QDateTimeEdit, QDial, QPushButton, QMenu, QDesktopWidget, QWidgetAction, QToolTip, QWidget, QToolButton, QVBoxLayout
    from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
    from PyQt5.QtNetwork import QNetworkProxy, QNetworkRequest
    from PyQt5.QtWebKit import QWebHistory
    from PyQt5.QtWebKitWidgets import QWebView, QWebPage
    Signal = pyqtSignal
    Slot = pyqtSlot
else:
    from PyQt4.QtCore import Qt, QSize, QObject, QCoreApplication, pyqtSignal, pyqtSlot, QUrl, QFile, QIODevice, QTimer, QByteArray, QDataStream, QDateTime, QPoint, QEventLoop
    from PyQt4.QtGui import QApplication, QListWidget, QSpinBox, QListWidgetItem, QMessageBox, QIcon, QAction, QToolBar, QLineEdit, QPrinter, QPrintDialog, QPrintPreviewDialog, QInputDialog, QFileDialog, QProgressBar, QLabel, QCalendarWidget, QSlider, QFontComboBox, QLCDNumber, QImage, QDateTimeEdit, QDial, QPushButton, QMenu, QDesktopWidget, QClipboard, QWidgetAction, QToolTip, QCursor, QWidget, QToolButton, QVBoxLayout, QDesktopServices
    from PyQt4.QtNetwork import QNetworkProxy, QNetworkRequest
    from PyQt4.QtWebKit import QWebView, QWebPage, QWebHistory
    Signal = pyqtSignal
    Slot = pyqtSlot

# Add an item to the browser history.
def addHistoryItem(url, title=None):
    if settings.setting_to_bool("data/RememberHistory"):
        url = url.split("#")[0]
        if len(url) <= settings.setting_to_int("data/MaximumURLLength"):
            data.history[url] = {"title": title, "last_visited" : QDateTime.currentDateTime().toMSecsSinceEpoch()}

mtype_associations = (("python", "py"),
                      ("html", "html"),
                      ("xml", "xml"),
                      ("zip", "zip"),
                      ("ttf", "ttf"),
                      ("otf", "otf"),
                      ("ogg", "ogg"),
                      ("xcf", "xcf"),
                      ("x-rar", "rar"),
                      ("mpeg", "mpeg"),
                      ("plain", "txt"),
                      ("svg+xml", "svg"),
                      ("xml", "xml"),
                      ("pdf", "pdf"),
                      ("dosexec", "exe"),
                      ("debian", "deb"),
                      ("msword", "doc"),
                      ("tar", "tar"),
                      ("octet-stream", "iso"),
                      ("opendocument.presentation", "odp"),
                      ("java-archive", "jar"),
                      ("gzip", "gz"),
                      ("bzip", "bz"),
                      ("7zip", "7z"))

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

# Progress bar used for downloads.
# This was ripped off of Ryouko.
class DownloadProgressBar(QProgressBar):

    # Initialize class.
    def __init__(self, reply=False, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressBar, self).__init__(parent)
        self.setWindowTitle(reply.request().url().toString().split("/")[-1])
        self.networkReply = reply
        self.destination = destination
        self.progress = [0, 0]
        if self.networkReply:
            self.networkReply.downloadProgress.connect(self.updateProgress)
            self.networkReply.finished.connect(self.finishDownload)

    # Writes downloaded file to the disk.
    def finishDownload(self):
        if self.networkReply.isFinished():
            data = self.networkReply.readAll()
            f = QFile(self.destination)
            f.open(QIODevice.WriteOnly)
            f.write(data)
            f.flush()
            f.close()
            self.progress = [0, 0]
            common.trayIcon.showMessage(tr("Download complete"), os.path.split(self.destination)[1])
            

    # Updates the progress bar.
    def updateProgress(self, received, total):
        self.setMaximum(total)
        self.setValue(received)
        self.progress[0] = received
        self.progress[1] = total
        self.show()

    # Abort download.
    def abort(self):
        self.networkReply.abort()

# File download toolbar.
# These are displayed at the bottom of a MainWindow.
class DownloadBar(QToolBar):
    def __init__(self, reply, destination, parent=None):
        super(DownloadBar, self).__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(16, 16))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setStyleSheet(common.blank_toolbar)
        label = QLabel(self)
        self.addWidget(label)
        self.progressBar = DownloadProgressBar(reply, destination, self)
        #self.progressBar.networkReply.finished.connect(self.close)
        #self.progressBar.networkReply.finished.connect(self.deleteLater)
        self.addWidget(self.progressBar)
        label.setText(os.path.split(self.progressBar.destination)[1])
        openFileAction = QAction(common.complete_icon("media-playback-start"), tr("Open file"), self)
        openFileAction.triggered.connect(self.openFile)
        self.addAction(openFileAction)
        openFolderAction = QAction(common.complete_icon("document-open"), tr("Open containing folder"), self)
        openFolderAction.triggered.connect(self.openFolder)
        self.addAction(openFolderAction)
        abortAction = QAction(QIcon().fromTheme("process-stop", QIcon(common.icon("process-stop.png"))), tr("Abort/Remove"), self)
        abortAction.triggered.connect(self.progressBar.abort)
        abortAction.triggered.connect(self.deleteLater)
        self.addAction(abortAction)
    def openFile(self):
        QDesktopServices.openUrl(QUrl.fromUserInput(self.progressBar.destination))
    def openFolder(self):
        QDesktopServices.openUrl(QUrl.fromUserInput(os.path.split(self.progressBar.destination)[0]))

# Class for exposing fullscreen API to DOM.
class FullScreenRequester(QObject):
    fullScreenRequested = Signal(bool)
    @Slot(bool)
    def setFullScreen(self, fullscreen=False):
        self.fullScreenRequested.emit(fullscreen)

isOnlineTimer = QTimer()

# Custom WebPage class with support for filesystem.
class WebPage(QWebPage):
    plugins = (("qcalendarwidget", QCalendarWidget),
               ("qslider", QSlider),
               ("qprogressbar", QProgressBar),
               ("qfontcombobox", QFontComboBox),
               ("qlcdnumber", QLCDNumber),
               ("qimage", QImage),
               ("qdatetimeedit", QDateTimeEdit),
               ("qdial", QDial),
               ("qspinbox", QSpinBox))

    fullScreenRequested = Signal(bool)
    javaScriptBar = Signal(QWidget)
    
    def __init__(self, *args, **kwargs):
        super(WebPage, self).__init__(*args, **kwargs)

        # Connect this so that permissions for geolocation and stuff work.
        self.featurePermissionRequested.connect(self.permissionRequested)

        # This object is exposed to the DOM to allow geolocation.
        self.geolocation = geolocation.Geolocation(self)

        # This object is exposed to the DOM to allow full screen mode.
        self.fullScreenRequester = FullScreenRequester(self)
        self.fullScreenRequester.fullScreenRequested.connect(self.toggleFullScreen)

        self._userScriptsLoaded = False
        self.mainFrame().javaScriptWindowObjectCleared.connect(lambda: self.setUserScriptsLoaded(False))

        # Connect to self.tweakDOM, which carries out some hacks to
        # improve HTML5 support.
        self.mainFrame().javaScriptWindowObjectCleared.connect(self.tweakDOM)

        # Connect loadFinished to checkForNavigatorGeolocation and loadUserScripts.
        self.loadFinished.connect(self.onLoadFinished)
        self.loadStarted.connect(self.loadUserScriptsStart)
        self.jsConfirm = False

        # Custom userscript.
        self.userScript = ""

        # This stores the user agent.
        self._userAgent = ""

        # Start self.isOnlineTimer.
        isOnlineTimer.timeout.connect(self.setNavigatorOnline)
        if not isOnlineTimer.isActive():
            isOnlineTimer.start(5000)

        # Set user agent to default value.
        self.setUserAgent()

    def onLoadFinished(self, success=True):
        if success:
            self.doRedirectHack()
            self.loadUserScripts()
            self.checkForNavigatorGeolocation()
    
    # This is a half-assed implementation of error pages,
    # which doesn't work yet.
    def supportsExtension(self, extension):
        if extension == QWebPage.ErrorPageExtension:
            return True
        else:
            return QWebPage.supportsExtension(self, extension)

    def extension(self, extension, option=None, output=None):
        if extension == QWebPage.ErrorPageExtension and option != None:
            try: url = option.url
            except: url = QUrl("about:blank")
            if network.isConnectedToNetwork():
                output.content = QByteArray(network.errorPage(url))
            else:
                output.content = QByteArray(network.errorPage(url, "No Internet connection.", "Your computer is not connected to the Internet.", suggestions=["Check your computer's network settings.", "If you have access to a wired Ethernet connection, make sure the cable is plugged in.", "If the problem persists, contact your network administrator."]))
            return True
        else:
            return QWebPage.extension(self, extension, option, output)

    def deleteLater(self):
        try: isOnlineTimer.timeout.disconnect(self.setNavigatorOnline)
        except: pass
        QWebPage.deleteLater(self)

    def setNavigatorOnline(self):
        online = bool(network.isConnectedToNetwork(self.mainFrame().url().toString()))
        script = "window.navigator.onLine = " + str(online).lower() + ";"
        self.mainFrame().evaluateJavaScript(script)
        if online:
            try: self.mainFrame().evaluateJavaScript("document.dispatchEvent(window.nimbus.onLineEvent);")
            except: pass
        else:
            try: self.mainFrame().evaluateJavaScript("document.dispatchEvent(window.nimbus.offLineEvent);")
            except: pass

    def javaScriptAlert(self, frame, msg, title="JavaScript Alert:"):
        pause = QEventLoop()
        tb = QToolBar(parent=self.parent(), movable=False)
        toolBar = QWidget(parent=tb)
        layout = QVBoxLayout(toolBar)
        toolBar.setLayout(layout)
        w1 = custom_widgets.Expander(parent=toolBar)
        layout.addWidget(w1)
        title = QLabel(parent=toolBar, text="<b>%s</b>" % title,)
        layout.addWidget(title)
        tb.label = QLabel(parent=toolBar, text=msg)
        layout.addWidget(tb.label)
        tb.no = QToolButton(toolBar, text=tr("&OK"))
        tb.no.clicked.connect(tb.deleteLater)
        tb.no.clicked.connect(pause.quit)
        layout.addWidget(tb.no)
        tb.no.setFocusPolicy(Qt.StrongFocus)
        w2 = custom_widgets.Expander(parent=toolBar)
        layout.addWidget(w2)
        tb.addWidget(toolBar)
        self.javaScriptBar.emit(tb)
        pause.exec_()

    def setJSConfirm(self, jsc):
        self.jsConfirm = jsc

    def javaScriptConfirm(self, frame, msg, title="JavaScript Confirm:"):
        pause = QEventLoop()
        tb = QToolBar(parent=self.parent(), movable=False)
        toolBar = QWidget(parent=self.parent())
        layout = QVBoxLayout(toolBar)
        toolBar.setLayout(layout)
        w1 = custom_widgets.Expander(parent=toolBar)
        layout.addWidget(w1)
        title = QLabel(parent=toolBar, text="<b>%s</b>" % title,)
        layout.addWidget(title)
        tb.label = QLabel(parent=toolBar, text=msg)
        layout.addWidget(tb.label)
        yes = QToolButton(toolBar, text=tr("&OK"))
        yes.clicked.connect(tb.deleteLater)
        yes.clicked.connect(pause.quit)
        yes.clicked.connect(lambda: self.setJSConfirm(True))
        layout.addWidget(yes)
        yes.setFocusPolicy(Qt.StrongFocus)
        tb.no = QToolButton(toolBar, text=tr("&Cancel"))
        tb.no.clicked.connect(tb.deleteLater)
        tb.no.clicked.connect(pause.quit)
        tb.no.clicked.connect(lambda: self.setJSConfirm(False))
        layout.addWidget(tb.no)
        tb.no.setFocusPolicy(Qt.StrongFocus)
        w2 = custom_widgets.Expander(parent=toolBar)
        layout.addWidget(w2)
        tb.addWidget(toolBar)
        self.javaScriptBar.emit(tb)
        pause.exec_()
        return self.jsConfirm

    if (common.qt_version_info[0] == 5 and common.qt_version_info[1] > 2 and common.qt_version_info[2] > 0) or common.qt_version_info[0] != 5:
        def javaScriptPrompt(self, frame, msg, defaultValue, result=None, title="JavaScript Prompt:"):
            pause = QEventLoop()
            tb = QToolBar(parent=self.parent(), movable=False)
            toolBar = QWidget(parent=self.parent())
            layout = QVBoxLayout(toolBar)
            toolBar.setLayout(layout)
            w1 = custom_widgets.Expander(parent=toolBar)
            layout.addWidget(w1)
            title = QLabel(parent=toolBar, text="<b>%s</b>" % title,)
            layout.addWidget(title)
            tb.label = QLabel(parent=toolBar, text=msg)
            layout.addWidget(tb.label)
            tb.lineEdit = QLineEdit(toolBar)
            tb.lineEdit.setText(defaultValue)
            tb.lineEdit.returnPressed.connect(tb.deleteLater)
            tb.lineEdit.returnPressed.connect(pause.quit)
            tb.lineEdit.returnPressed.connect(lambda: self.setJSConfirm(True))
            layout.addWidget(tb.lineEdit)
            yes = QToolButton(toolBar, text=tr("&OK"))
            yes.clicked.connect(tb.deleteLater)
            yes.clicked.connect(pause.quit)
            yes.clicked.connect(lambda: self.setJSConfirm(True))
            layout.addWidget(yes)
            yes.setFocusPolicy(Qt.StrongFocus)
            tb.no = QToolButton(toolBar, text=tr("&Cancel"))
            tb.no.clicked.connect(tb.deleteLater)
            tb.no.clicked.connect(pause.quit)
            tb.no.clicked.connect(lambda: self.setJSConfirm(False))
            layout.addWidget(tb.no)
            tb.no.setFocusPolicy(Qt.StrongFocus)
            w2 = custom_widgets.Expander(parent=toolBar)
            layout.addWidget(w2)
            tb.addWidget(toolBar)
            self.javaScriptBar.emit(tb)
            pause.exec_()
            return self.jsConfirm, tb.lineEdit.text()

    def setUserScript(self, script):
        if script:
            self.userScript = script

    # Performs a hack on Google pages to change their URLs.
    def doRedirectHack(self):
        links = self.mainFrame().findAllElements("a")
        for link in links:
            try: href = link.attribute("href")
            except: pass
            else:
                for gurl in ("/url?q=", "?redirect="):
                    if href.startswith(gurl):
                        url = href.replace(gurl, "").split("&")[0]
                        url = urllib.parse.unquote(url)
                        link.setAttribute("href", url)
                    elif gurl in href:
                        url = href.split(gurl)[-1]
                        url = urllib.parse.unquote(url)
                        link.setAttribute("href", url)

    # Loads history.
    def loadHistory(self, history):
        out = QDataStream(history, QIODevice.ReadOnly)
        out.__rshift__(self.history())

    def saveHistory(self):
        byteArray = QByteArray()
        out = QDataStream(byteArray, QIODevice.WriteOnly)
        out.__lshift__(self.history())
        return byteArray

    # Sends a request to become fullscreen.
    def toggleFullScreen(self, value):
        if (value == True and settings.setting_to_bool("content/JavascriptCanEnterFullscreenMode")) or\
           (value == False and settings.setting_to_bool("content/JavascriptCanExitFullscreenMode")):
            self.fullScreenRequested.emit(value)

    def setUserScriptsLoaded(self, loaded=False):
        self._userScriptsLoaded = loaded

    # Load userscripts of document-start.
    def loadUserScriptsStart(self):
        if not self._userScriptsLoaded:
            for userscript in settings.userscripts:
                if userscript["start"] == False:
                    continue
                for match in userscript["match"]:
                    try:
                        if match == "*":
                            r = True
                        else:
                            r = re.match(match, self.mainFrame().url().toString())
                        if r:
                            self.mainFrame().evaluateJavaScript(userscript["content"])
                            break
                    except:
                        pass

    # Load userscripts.
    def loadUserScripts(self):
        if not self._userScriptsLoaded:
            self._userScriptsLoaded = True
            if settings.setting_to_bool("content/HostFilterEnabled") or settings.setting_to_bool("content/AdblockEnabled"):
                self.mainFrame().evaluateJavaScript("""var __NimbusAdRemoverQueries = %s;
for (var i=0; i<__NimbusAdRemoverQueries.length; i++) {
    var cl = document.querySelectorAll(__NimbusAdRemoverQueries[i]);
    for (var j=0; j<cl.length; j++) {
        cl[j].style.display = "none";
    }
}
delete __NimbusAdRemoverQueries;""" % (settings.adremover_filters,))
            self.mainFrame().evaluateJavaScript(self.userScript)
            for userscript in settings.userscripts:
                if userscript["start"] == True:
                    continue
                for match in userscript["match"]:
                    try:
                        if match == "*":
                            r = True
                        else:
                            r = re.match(match, self.mainFrame().url().toString())
                        if r:
                            self.mainFrame().evaluateJavaScript(userscript["content"])
                            break
                    except:
                        pass

    # Returns user agent string.
    def userAgentForUrl(self, url):
        override = data.userAgentForUrl(url.authority())
        if override == "nimbus_generic" and not self._userAgent:
            return QWebPage.userAgentForUrl(self, url)
        elif override and not self._userAgent:
            return override
        elif self._userAgent:
            return self._userAgent
        else:
            return common.defaultUserAgent

    # Convenience function.
    def setUserAgent(self, ua=None):
        self._userAgent = ua

    # This is a hacky way of checking whether a website wants to use
    # geolocation. It checks the page source for navigator.geolocation,
    # and if it is present, it assumes that the website wants to use it.
    def checkForNavigatorGeolocation(self):
        if "navigator.geolocation" in self.mainFrame().toHtml() and not self.mainFrame().url().authority() in data.geolocation_whitelist:
            self.allowGeolocation()

    # Prompts the user to enable or block geolocation, and reloads the page if the
    # user said yes.
    def allowGeolocation(self):
        reload_ = self.permissionRequested(self.mainFrame(), self.Geolocation)
        if reload_:
            self.action(self.Reload).trigger()

    # Sets permissions for features.
    # Currently supports geolocation.
    def permissionRequested(self, frame, feature):
        authority = frame.url().authority()
        if feature == self.Notifications and frame == self.mainFrame():
            self.setFeaturePermission(frame, feature, self.PermissionGrantedByUser)
        elif feature == self.Geolocation and frame == self.mainFrame() and settings.setting_to_bool("network/GeolocationEnabled") and not authority in data.geolocation_blacklist:
            confirm = True
            if not authority in data.geolocation_whitelist:
                confirm = QMessageBox.question(None, common.app_name, tr("This website would like to track your location."), QMessageBox.Ok | QMessageBox.No | QMessageBox.NoToAll, QMessageBox.Ok)
            if confirm == QMessageBox.Ok:
                if not authority in data.geolocation_whitelist:
                    data.geolocation_whitelist.append(authority)
                    data.saveData()
                self.setFeaturePermission(frame, feature, self.PermissionGrantedByUser)
            elif confirm == QMessageBox.NoToAll:
                if not authority in data.geolocation_blacklist:
                    data.geolocation_blacklist.append(authority)
                    data.saveData()
                self.setFeaturePermission(frame, feature, self.PermissionDeniedByUser)
            return confirm == QMessageBox.Ok
        return False

    # This loads a bunch of hacks to improve HTML5 support.
    def tweakDOM(self):
        authority = self.mainFrame().url().authority()
        self.mainFrame().addToJavaScriptWindowObject("nimbusFullScreenRequester", self.fullScreenRequester)
        self.mainFrame().evaluateJavaScript("window.nimbus = new Object();")
        self.mainFrame().evaluateJavaScript("window.nimbus.fullScreenRequester = nimbusFullScreenRequester; delete nimbusFullScreenRequester;")
        if settings.setting_to_bool("network/GeolocationEnabled") and authority in data.geolocation_whitelist:
            self.mainFrame().addToJavaScriptWindowObject("nimbusGeolocation", self.geolocation)
            script = "window.nimbus.geolocation = nimbusGeolocation;\n" + \
                     "delete nimbusGeolocation;\n" + \
                     "window.navigator.geolocation = {};\n" + \
                     "window.navigator.geolocation.getCurrentPosition = function(success, error, options) { var getCurrentPosition = eval('(' + window.nimbus.geolocation.getCurrentPosition() + ')'); success(getCurrentPosition); return getCurrentPosition; };"
            self.mainFrame().evaluateJavaScript(script)
        self.mainFrame().evaluateJavaScript("HTMLElement.prototype.requestFullScreen = function() { window.nimbus.fullScreenRequester.setFullScreen(true); var style = ''; if (this.hasAttribute('style')) { style = this.getAttribute('style'); }; this.setAttribute('oldstyle', style); this.setAttribute('style', style + ' position: fixed; top: 0; left: 0; padding: 0; margin: 0; width: 100%; height: 100%; z-index: 9001 !important;'); document.fullScreen = true; }")
        self.mainFrame().evaluateJavaScript("HTMLElement.prototype.webkitRequestFullScreen = HTMLElement.prototype.requestFullScreen")
        self.mainFrame().evaluateJavaScript("document.cancelFullScreen = function() { window.nimbus.fullScreenRequester.setFullScreen(false); document.fullScreen = false; var allElements = document.getElementsByTagName('*'); for (var i=0;i<allElements.length;i++) { var element = allElements[i]; if (element.hasAttribute('oldstyle')) { element.setAttribute('style', element.getAttribute('oldstyle')); } } }")
        self.mainFrame().evaluateJavaScript("document.webkitCancelFullScreen = document.cancelFullScreen")
        self.mainFrame().evaluateJavaScript("document.fullScreen = false;")
        self.mainFrame().evaluateJavaScript("document.exitFullscreen = document.cancelFullScreen")
        self.mainFrame().evaluateJavaScript("window.nimbus.onLineEvent = document.createEvent('Event');\n" + \
                                            "window.nimbus.onLineEvent.initEvent('online',true,false);")
        self.mainFrame().evaluateJavaScript("window.nimbus.offLineEvent = document.createEvent('Event');\n" + \
                                            "window.nimbus.offLineEvent.initEvent('offline',true,false);")

    # Creates Qt-based plugins.
    # One plugin pertains to the settings dialog,
    # while another pertains to local directory views.
    def createPlugin(self, classid, url, paramNames, paramValues):
        for name, widgetclass in self.plugins:
            if classid.lower() == name:
                widget = widgetclass(self.view())
                widgetid = classid
                pnames = [name.lower() for name in paramNames]
                if "id" in pnames:
                    widgetid = paramValues[pnames.index("id")]
                self.mainFrame().addToJavaScriptWindowObject(widgetid, widget)
                return widget
        return

# Custom WebView class with support for ad-blocking, new tabs, downloads,
# recording history, and more.
class WebView(QWebView):

    # This stores the directory you last saved a file in.
    saveDirectory = os.path.expanduser("~")

    # This is used to store references to webViews so that they don't
    # automatically get cleaned up.
    webViews = []

    # Downloads
    downloads = []

    sourceDialogs = []

    # This is a signal used to inform everyone a new window was created.
    windowCreated = Signal(QWebView)
    
    # Requests tab
    tabRequested = Signal(QWebView)

    # This is a signal used to tell everyone a download has started.
    downloadStarted = Signal(QToolBar)
    urlChanged2 = Signal(QUrl)

    nextExpressions = ("start=", "offset=", "page=", "first=", "pn=", "=",)
    
    baseStyleSheet = "QWebView > QToolBar { background: transparent; padding: 0; margin: 0; } QWebView > QToolBar, QWebView > QToolBar > QWidget { min-width: %spx; max-width: %spx; min-height: %spx; max-height: %spx; padding: 2px; background: palette(window); }"

    # Initialize class.
    def __init__(self, *args, incognito=False, sizeHint=None, minimumSizeHint=None, forceBlankPage=False, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)

        self._sizeHint = sizeHint
        self._minimumSizeHint = minimumSizeHint

        # Add this webview to the list of webviews.
        self.setStyleSheet(self.baseStyleSheet % (self.size().width(), self.size().width(), self.size().height(), self.size().height()))

        # These are used to store the current url.
        self._url = ""
        self._urlText = ""
        self._oldURL = ""

        #self.disconnected = False

        self.isLoading = False

        self._html = ""

        self._changeCanGoNext = False

        self._cacheLoaded = False

        # Private browsing.
        self.incognito = incognito

        # Stores the mime type of the current page.
        self._contentType = None

        # This is used to store the text entered in using WebView.find(),
        # so that WebView.findNext() and WebView.findPrevious() work.
        self._findText = False

        # This is used to store the current status message.
        self._statusBarMessage = ""
        self.statusMessageDisplay = QLabel(self)
        self.statusMessageDisplay.setStyleSheet("QLabel { border-radius: 4px; padding: 2px; background: palette(highlight); color: palette(highlighted-text); }")
        self.statusMessageDisplay.hide()

        # This is used to store the current page loading progress.
        self._loadProgress = 0

        # Stores if window was maximized.
        self._wasMaximized = False

        # Stores next page.
        self._canGoNext = False

        # This stores the link last hovered over.
        self._hoveredLink = ""

        # Stores history to be loaded.
        self._historyToBeLoaded = None

        # Temporary title.
        self._tempTitle = None
        self.javaScriptBars = []

        self.setPage(WebPage(self))
        self.page().javaScriptBar.connect(self.addJavaScriptBar)

        # Create a NetworkAccessmanager that supports ad-blocking and set it.
        if not self.incognito:
            self.nAM = network.network_access_manager
        else:
            self.nAM = network.incognito_network_access_manager
        self.page().setNetworkAccessManager(self.nAM)
        self.nAM.setParent(QCoreApplication.instance())

        #self.updateProxy()
        
        self.toggleCaretBrowsingAction = QAction(self)
        self.toggleCaretBrowsingAction.setShortcut("F7")
        self.toggleCaretBrowsingAction.triggered.connect(self.toggleCaretBrowsing)
        self.addAction(self.toggleCaretBrowsingAction)
        
        self.toggleSpatialNavigationAction = QAction(self)
        self.toggleSpatialNavigationAction.setShortcut("F8")
        self.toggleSpatialNavigationAction.triggered.connect(self.toggleSpatialNavigation)
        self.addAction(self.toggleSpatialNavigationAction)

        # What to do if private browsing is not enabled.
        if self.incognito:
            # Global incognito cookie jar, so that logins are preserved
            # between incognito tabs.
            network.incognito_cookie_jar.setParent(QCoreApplication.instance())

            # Enable private browsing for QWebSettings.
            websettings = self.settings()
            websettings.setAttribute(websettings.PrivateBrowsingEnabled, True)
            websettings.setAttribute(websettings.JavaEnabled, False)
            websettings.setAttribute(websettings.PluginsEnabled, False)
            websettings.setAttribute(websettings.XSSAuditingEnabled, True)
            websettings.setAttribute(websettings.DnsPrefetchEnabled, False)

        # Handle unsupported content.
        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.handleUnsupportedContent)

        # This is what Nimbus should do when faced with a file to download.
        self.page().downloadRequested.connect(self.downloadFile)

        # Connect signals.
        self.page().linkHovered.connect(self.setStatusBarMessage)

        # PyQt5 doesn't support <audio> and <video> tags on Windows.
        # This is a little hack to work around it.
        self.page().networkAccessManager().finished.connect(self.ready)
        #self.loadFinished.connect(lambda: print("\n".join(self.rssFeeds()) + "\n"))

        # Check if content viewer.
        self._isUsingContentViewer = False

        self.setWindowTitle("")

        self.clippingsMenu = QMenu(self)

        self.init()

        if os.path.exists(settings.new_tab_page) and not forceBlankPage:
            if sys.platform.startswith("win"):
                self.load(QUrl.fromUserInput(settings.new_tab_page))
            else:
                self.load(QUrl.fromUserInput(settings.new_tab_page_short))

    def toggleCaretBrowsing(self):
        websettings = self.settings().globalSettings()
        try: book = websettings.testAttribute(websettings.CaretBrowsingEnabled)
        except: return
        websettings.setAttribute(websettings.CaretBrowsingEnabled, not book)
        settings.settings.setValue("navigation/CaretBrowsingEnabled", not book)
        settings.settings.sync()
        if book:
            common.trayIcon.showMessage(tr("Caret browsing disabled."), tr("Press F7 to toggle."))
        else:
            common.trayIcon.showMessage(tr("Caret browsing enabled."), tr("Press F7 to toggle."))

    def toggleSpatialNavigation(self):
        websettings = self.settings().globalSettings()
        try: book = websettings.testAttribute(websettings.SpatialNavigationEnabled)
        except: return
        websettings.setAttribute(websettings.SpatialNavigationEnabled, not book)
        settings.settings.setValue("navigation/SpatialNavigationEnabled", not book)
        settings.settings.sync()
        if book:
            common.trayIcon.showMessage(tr("Spatial navigation disabled."), tr("Press F8 to toggle."))
        else:
            common.trayIcon.showMessage(tr("Spatial navigation enabled."), tr("Press F8 to toggle."))

    def addJavaScriptBar(self, toolBar):
        self.javaScriptBars.append(toolBar)
        toolBar.show()
        try:
            toolBar.lineEdit.setFocus()
            toolBar.lineEdit.selectAll()
        except:
            pass

    def clearJavaScriptBars(self):
        for f in self.javaScriptBars:
            try: f.deleteLater()
            except: pass
        for i in range(0, len(self.javaScriptBars), -1):
            del self.javaScriptBars[i]

    def reload(self):
        super(WebView, self).reload()
        self.clearJavaScriptBars()

    def resizeEvent(self, *args, **kwargs):
        super(WebView, self).resizeEvent(*args, **kwargs)
        self.setStyleSheet(self.baseStyleSheet % (self.size().width(), self.size().width(), self.size().height(), self.size().height()))

    def wheelEvent(self, *args, **kwargs):
        super(WebView, self).wheelEvent(*args, **kwargs)
        self.statusMessageDisplay.hide()

    def disconnect(self, *args, **kwargs):
        super(WebView, self).disconnect(*args, **kwargs)
        self.init()
        #self.disconnected = True
        common.disconnected.append(self)

    def init(self):
        self.urlChanged.connect(self.setUrlText)
        self.urlChanged.connect(self.setJavaScriptEnabled)
        self.urlChanged.connect(self.clearJavaScriptBars)
        if not self.incognito:
            self.urlChanged.connect(self.addHistoryItem)
            self.urlChanged.connect(lambda: self.setChangeCanGoNext(True))
        self.titleChanged.connect(self.setWindowTitle2)
        self.titleChanged.connect(self.updateHistoryTitle)
        self.titleChanged.connect(self.setWindowTitle2)
        self.titleChanged.connect(self.updateHistoryTitle)
        self.statusBarMessage.connect(self.setStatusBarMessage)
        self.loadProgress.connect(self.setLoadProgress)
        self.loadStarted.connect(self.setLoading)
        self.loadFinished.connect(self.unsetLoading)
        self.loadStarted.connect(self.resetContentType)
        self.loadFinished.connect(self.replaceAVTags)
        self.loadFinished.connect(self.setCanGoNext)
        self.loadStarted.connect(self.checkIfUsingContentViewer)
        #self.loadFinished.connect(self.finishLoad)

    def killTempTitle(self):
        self._tempTitle = None

    def setJavaScriptEnabled(self):
        if not self.url().authority() in settings.js_exceptions and not self.url().authority().replace("www.", "") in settings.js_exceptions:
            self.settings().setAttribute(self.settings().JavascriptEnabled, settings.setting_to_bool("content/JavascriptEnabled"))
        else:
            self.settings().setAttribute(self.settings().JavascriptEnabled, not settings.setting_to_bool("content/JavascriptEnabled"))

    def requestTab(self):
        self.tabRequested.emit(self)

    def minimumSizeHint(self):
        if not type(self._minimumSizeHint) is QSize:
            return super(WebView, self).minimumSizeHint()
        return self._minimumSizeHint

    def sizeHint(self):
        if not type(self._sizeHint) is QSize:
            return super(WebView, self).sizeHint()
        return self._sizeHint

    def updateHistoryTitle(self, title):
        url = self.url().toString().split("#")[0]
        if url in data.history.keys():
            data.history[url]["title"] = (title if len(title) > 0 else tr("(Untitled)"))

    def setUrlText(self, text, emit=True):
        if type(text) is QUrl:
            text = text.toString()
        self._urlText = str(text)
        if emit:
            self.urlChanged2.emit(QUrl(self._urlText))

    def setLoading(self):
        self.isLoading = True
        self.iconChanged.emit()

    def unsetLoading(self):
        self.isLoading = False
        self.iconChanged.emit()

    def setWindowTitle2(self, text):
        if text == "" and self.url().toString() not in ("", "about:blank"):
            pass
        else:
            self.setWindowTitle(text)

    def contextMenuEvent(self, ev):
        if QCoreApplication.instance().keyboardModifiers() in (Qt.ControlModifier, Qt.ShiftModifier, Qt.AltModifier) and len(data.clippings) > 0:
            menu = self.clippingsMenu
            menu.clear()
            openInDefaultBrowserAction = QAction(tr("Open in Default Browser"), menu)
            openInDefaultBrowserAction.triggered.connect(self.openInDefaultBrowser)
            menu.addAction(openInDefaultBrowserAction)
            if self._statusBarMessage == "":
                openInDefaultBrowserAction.setEnabled(False)
            menu.addSeparator()
            row = custom_widgets.RowAction(menu)
            menu.addAction(row)
            array = sorted(list(data.clippings.items()), key=lambda x: x[0])
            for i in range(0, len(array), 20):
                chunk = array[i:i+20]
                submenu = QToolBar(row.row(), orientation=Qt.Vertical)
                row.addWidget(submenu)
                for clipping in chunk:
                    a = custom_widgets.LinkAction(clipping[1], clipping[0], menu)
                    a.triggered2.connect(common.copyToClipboard)
                    a.triggered2.connect(lambda: self.page().action(QWebPage.Paste).trigger())
                    submenu.addAction(a)
            menu.show()
            y = QDesktopWidget()
            menu.move(min(ev.globalX(), y.width()-menu.width()), min(ev.globalY(), y.height()-menu.height()))
            y.deleteLater()
        else:
            super(WebView, self).contextMenuEvent(ev)

    def shortTitle(self):
        title = self.title()
        return title[:24] + '...' if len(title) > 24 else title

    def shortWindowTitle(self):
        title = self.windowTitle()
        return title[:24] + '...' if len(title) > 24 else title

    def shortTempTitle(self):
        if not self._tempTitle:
            return None
        title = self._tempTitle
        return title[:24] + '...' if len(title) > 24 else title

    def viewSource(self):
        sview = self.createWindow(QWebPage.WebBrowserWindow)
        sview.setHtml("""<!DOCTYPE html>
<html>
    <head>
        <title>""" + (tr("Source of %s") % self.url().toString()) + """</title>
        <link rel="stylesheet" href="http://127.0.0.1:8133/highlight-style.css">
        <script src="http://127.0.0.1:8133/highlight.pack.js"></script>
    </head>
    <body>
        <pre>
            <code style="position: fixed; top: 0; left: 0; bottom: 0; right: 0; width: auto; height: auto; overflow-x: auto; overflow-y: auto;">""" + self.page().mainFrame().toHtml().replace("<", "&lt;").replace(">", "&gt;") + """</code>
        </pre>
        <script>hljs.initHighlightingOnLoad();</script>
    </body>
</html>""", QUrl("nimbus://view-source"))
        #sourceDialog = view_source_dialog.ViewSourceDialog(None)
        #for sd in self.sourceDialogs:
            #try: sd.doNothing()
            #except: self.sourceDialogs.remove(sd)
        #self.sourceDialogs.append(sourceDialog)
        #sourceDialog.setPlainText(self.page().mainFrame().toHtml())
        #sourceDialog.show()

    # Enables fullscreen in web app mode.
    def enableWebAppMode(self):
        self.isWebApp = True
        fullScreenAction = QAction(self)
        fullScreenAction.setShortcut("F11")
        fullScreenAction.triggered.connect(self.toggleFullScreen)
        self.addAction(fullScreenAction)

    # Sends a request to become fullscreen.
    def toggleFullScreen(self):
        if not self.isFullScreen():
            self._wasMaximized = self.isMaximized()
            self.showFullScreen()
        else:
            if not self._wasMaximized:
                self.showNormal()
            else:
                self.showNormal()
                self.showMaximized()

    def saveHtml(self):
        self._html = self.page().mainFrame().toHtml()

    def restoreHtml(self):
        self.setHtml(self._html)

    def deleteLater(self):
        try: self.page().networkAccessManager().finished.disconnect(self.ready)
        except: pass
        self.page().deleteLater()
        QWebView.deleteLater(self)

    def paintEvent(self, ev):
        if self._historyToBeLoaded:
            self.page().loadHistory(self._historyToBeLoaded)
            self._historyToBeLoaded = None
            self._tempTitle = None
        QWebView.paintEvent(self, ev)
        self.paintEvent = self.shortPaintEvent

    def shortPaintEvent(self, *args, **kwargs):
        QWebView.paintEvent(self, *args, **kwargs)

    def loadHistory(self, history, title=None):
        self._historyToBeLoaded = history
        out = QDataStream(history, QIODevice.ReadOnly)
        if title:
            self._tempTitle = title
        else:
            page = QWebPage(None)
            history = page.history()
            out.__rshift__(history)
            self._tempTitle = history.currentItem().title()
        self.titleChanged.emit(str(self._tempTitle))
        try: page.deleteLater()
        except: pass

    def title(self):
        if not self._tempTitle:
            return QWebView.title(self)
        else:
            return self._tempTitle

    def saveHistory(self):
        if self._historyToBeLoaded:
            return self._historyToBeLoaded
        return self.page().saveHistory()

    def setChangeCanGoNext(self, true=False):
        self._changeCanGoNext = true

    # Can it go up?
    def canGoUp(self):
        components = self.url().toString().split("/")
        urlString = self.url().toString()
        if len(components) < 2 or (urlString.count("/") < 4 and not "///" in urlString and urlString.startswith("file://")) or (len(components) < 5 and not urlString.startswith("file://") and components[-1] == ""):
            return False
        return True

    # Go up.
    def up(self):
        components = self.url().toString().split("/")
        urlString = self.url().toString()
        if urlString.count("/") < 4 and "///" in urlString:
            self.load(QUrl("file:///"))
            return
        self.load(QUrl.fromUserInput("/".join(components[:(-1 if components[-1] != "" else -2)])))

    # Get RSS.
    def rssFeeds(self):
        feed_urls = []
        links = self.page().mainFrame().findAllElements("[type=\"application/rss+xml\"], [type=\"application/atom+xml\"]")
        for element in links:
            if element.hasAttribute("title") and element.hasAttribute("href"):
                feed_urls.append((element.attribute("title"), element.attribute("href")))
            elif element.hasAttribute("href"):
                feed_urls.append((element.attribute("href"), element.attribute("href")))
        return feed_urls

    # This is awful and needs to be fixed.
    def setCanGoNext(self):
        if not self._changeCanGoNext:
            return
        else:
            self._changeCanGoNext = False
        url_parts = self.url().toString().split("/")
        fail = []
        for part in range(len(url_parts)):
            try: int(url_parts[part])
            except: pass
            else:
                fail.append(part)
        if len(fail) == 1:
            url_parts[fail[0]] = str(int(url_parts[fail[0]]) + 1)
            self._canGoNext = "/".join(url_parts)
            return
        anchors = self.page().mainFrame().findAllElements("a")
        for anchor in anchors:
            for attribute in anchor.attributeNames():
                try:
                    if attribute.lower() == "rel" and anchor.attribute(attribute).lower() == "next":
                        try:
                            self._canGoNext = anchor.attribute("href")
                            return
                        except:
                            pass
                except:
                    pass
        success = False
        for rstring in self.nextExpressions[:-1]:
            for times in reversed(range(1, 11)):
                try: thisPageNumber = int(re.search("%s%s" % (rstring, "[\d]" * times), self.url().toString().lower()).group().replace(rstring, ""))
                except: pass
                else:
                    success = True
                    break
        if not success:
            thisPageNumber = 0
        for rstring in self.nextExpressions:
            for anchor in anchors:
                for attribute in anchor.attributeNames():
                    try:
                        for times in reversed(range(1, 11)):
                            try: thatPageNumber = int(re.search("%s%s" % (rstring, "[\d]" * times), anchor.attribute(attribute).lower()).group().replace(rstring, ""))
                            except: pass
                            else: break
                        if thatPageNumber > thisPageNumber:
                            try:
                                self._canGoNext = anchor.attribute("href")
                                return
                            except:
                                pass
                    except:
                        pass
        for rstring in ("start=", "offset=", "page=", "="):
            for anchor in anchors:
                for attribute in anchor.attributeNames():
                    if re.search("%s[\d*]" % (rstring,), anchor.attribute(attribute).lower()):
                        try:
                            self._canGoNext = anchor.attribute("href")
                            return
                        except:
                            pass
        for anchor in anchors:
            for attribute in anchor.attributeNames():
                try:
                    if attribute.lower() in ("class", "rel", "id") and "next" in anchor.attribute(attribute).lower():
                        try:
                            self._canGoNext = anchor.attribute("href")
                            return
                        except:
                            pass
                except:
                    pass
        for anchor in anchors:
            if "next" in anchor.toPlainText().lower() or "older" in anchor.toPlainText().lower():
                try:
                    self._canGoNext = anchor.attribute("href")
                    return
                except:
                    pass
        self._canGoNext = False

    def canGoNext(self):
        return self._canGoNext

    def next(self):
        href = self.canGoNext()
        if href:
            self.page().mainFrame().evaluateJavaScript("window.location.href = \"%s\";" % (href,))

    # Convenience function.
    def setUserAgent(self, ua=None):
        self.page().setUserAgent(ua)

    # Returns whether the browser has loaded a content viewer.
    def isUsingContentViewer(self):
        return self._isUsingContentViewer

    # Checks whether the browser has loaded a content viewer.
    # This is necessary so that downloading the original file from
    # Google Docs Viewer doesn't loop back to Google Docs Viewer.
    def checkIfUsingContentViewer(self):
        for viewer in common.content_viewers:
            if viewer[0].replace("%s", "") in self.url().toString():
                self._isUsingContentViewer = True
                return
        self._isUsingContentViewer = False

    # Resets recorded content type.
    def resetContentType(self):
        self._contentType = None
        if self._oldURL != self._url:
            self._oldURL = self._url

    # If a request has finished and the request's URL is the current URL,
    # then set self._contentType.
    def ready(self, response):
        try:
            if self._contentType == None and response.url() == self.url():
                try: contentType = response.header(QNetworkRequest.ContentTypeHeader)
                except: contentType = None
                if contentType != None:
                    self._contentType = contentType
                html = self.page().mainFrame().toHtml()
                if "xml" in str(self._contentType) and ("<rss" in html or ("<feed" in html and "atom" in html)):
                    try: self.setHtml(rss_parser.feedToHtml(html), self.url())
                    except: pass
        except:
            pass

    # This is a custom implementation of mousePressEvent.
    # It allows the user to Ctrl-click or middle-click links to open them in
    # new tabs.
    def mousePressEvent(self, ev):
        if self._statusBarMessage != "" and (((QCoreApplication.instance().keyboardModifiers() == Qt.ControlModifier) and not ev.button() == Qt.RightButton) or ev.button() == Qt.MidButton or ev.button() == Qt.MiddleButton):
            url = self._statusBarMessage
            ev.ignore()
            newWindow = self.createWindow(QWebPage.WebBrowserWindow)
            newWindow.load(QUrl.fromUserInput(url))
        elif self._statusBarMessage != "" and (((QCoreApplication.instance().keyboardModifiers() == Qt.ShiftModifier) and not ev.button() == Qt.RightButton)):
            self.openInDefaultBrowser(urllib.parse.unquote(self._statusBarMessage))
        else:
            return QWebView.mousePressEvent(self, ev)

    def openInDefaultBrowser(self, url=None):
        if type(url) is QUrl:
            url = url.toString()
        elif not url:
            url = self._statusBarMessage
        QDesktopServies.openUrl(QUrl(url))

    def load2(self, url):
        self.page().mainFrame().evaluateJavaScript("window.location.href = \"%s\"" % (url,))

    # Method to replace all <audio> and <video> tags with <embed> tags.
    # This is mainly a hack for Windows, where <audio> and <video> tags are not
    # properly supported under PyQt5.
    def replaceAVTags(self):
        if not settings.setting_to_bool("content/ReplaceHTML5MediaTagsWithEmbedTags"):
            return
        audioVideo = self.page().mainFrame().findAllElements("audio, video")
        for element in audioVideo:
            attributes = []
            if not "width" in element.attributeNames():
                attributes.append("width=352")
            if not "height" in element.attributeNames():
                attributes.append("height=240")
            if not "autostart" in element.attributeNames():
                attributes.append("autostart=false")
            attributes += ["%s=\"%s\"" % (attribute, element.attribute(attribute),) for attribute in element.attributeNames()]
            if element.firstChild() != None:
                attributes += ["%s=\"%s\"" % (attribute, element.firstChild().attribute(attribute),) for attribute in element.firstChild().attributeNames()]
            embed = "<embed %s></embed>" % (" ".join(attributes),)
            element.replace(embed)

    # Set status bar message.
    def setStatusBarMessage(self, link="", title="", content=""):
        self._statusBarMessage = link
        if not settings.setting_to_bool("general/StatusBarVisible") and len(self._statusBarMessage) > 0:
            self.statusMessageDisplay.hide()
            self.statusMessageDisplay.setText(urllib.parse.unquote(self._statusBarMessage))
            self.statusMessageDisplay.show()
            self.statusMessageDisplay.move(QPoint(0, self.height()-self.statusMessageDisplay.height()))
            opposite = QCursor.pos().x() in tuple(range(self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).x(), self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).x() + self.statusMessageDisplay.width())) and QCursor.pos().y() in tuple(range(self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).y(), self.statusMessageDisplay.mapToGlobal(QPoint(0,0)).y() + self.statusMessageDisplay.height()))
            self.statusMessageDisplay.move(QPoint(0 if not opposite else self.width()-self.statusMessageDisplay.width(), self.height()-self.statusMessageDisplay.height()))
            self.repaint()
        elif len(self._statusBarMessage) == 0:
            self.statusMessageDisplay.hide()
            self.repaint()

    # Set load progress.
    def setLoadProgress(self, progress):
        self._loadProgress = progress

    # Set the window title. If the title is an empty string,
    # set it to "New Tab".
    def setWindowTitle(self, title):
        if len(title) == 0:
            title = tr("New Tab")
        QWebView.setWindowTitle(self, title)

    # Returns a devilish face if in incognito mode;
    # else page icon.
    def icon(self):
        if self.isLoading:
            return common.complete_icon("image-loading")
        elif self.incognito:
            return common.complete_icon("face-devilish")
        icon = QWebView.icon(self)
        if icon.pixmap(QSize(16, 16)).width() == 0:
            return common.complete_icon("text-html")
        else:
            return icon

    # Handler for unsupported content.
    # This is where the content viewers are loaded.
    def handleUnsupportedContent(self, reply):
        url2 = reply.url()
        url = url2.toString()

        # Make sure the file isn't local, that content viewers are
        # enabled, and private browsing isn't enabled.
        content_type = reply.header(QNetworkRequest.ContentTypeHeader)
        print(content_type)
        if "pdf" in str(content_type):
            if not common.pyqt4:
                self.load(QUrl("qrc:///pdf.js/viewer.html?file=%s#disableWorker=true" % url,))
                reply.deleteLater()
            else:
                self.load(QUrl("about:blank"))
                stream = QFile(':/pdf.js/viewer.html')
                stream.open(QIODevice.ReadOnly)
                data = stream.readAll().data().decode("utf-8")
                self.setHtml(data, QUrl("qrc:///pdf.js/viewer.html?file=%s#disableWorker=true" % url,))
                stream.close()
                reply.deleteLater()
            return
        elif "opendocument" in str(content_type) and not common.pyqt4:
            self.load(QUrl("qrc:///ViewerJS/index.html#%s" % url,))
            reply.deleteLater()
            return
        if not url2.scheme() == "file" and settings.setting_to_bool("content/UseOnlineContentViewers") and not self.incognito and not self.isUsingContentViewer():
            for viewer in common.content_viewers:
                try:
                    for extension in viewer[1]:
                        if url.lower().endswith(extension):
                            QWebView.load(self, QUrl(viewer[0] % (url,)))
                            reply.deleteLater()
                            return
                except:
                    pass

        self.downloadFile(reply.request(), content_type)
        reply.deleteLater()

    # Downloads a file.
    def downloadFile(self, request, contentType=None):
        if request.url() == self.url():

            # If the file type can be converted to plain text, use savePage
            # method instead.
            for mimeType in ("text", "svg", "html", "xml", "xhtml",):
                if mimeType in str(self._contentType):
                    self.savePage()
                    return

        # Get file name for destination.
        fnameList = request.url().toString().split("#")[0].split("?")[0].split("/")
        counter = -1
        fileName = ""
        while fileName == "":
            try:
                fileName = fnameList[counter]
                counter -= 1
            except:
                fileName = "omgus"
        upperFileName = fileName.upper()
        for extension in common.tlds:
            if upperFileName.endswith(extension):
                fileName = fileName + ".html"
        if contentType:
            mtype = contentType
            ext = ""
            if mtype.startswith("image"):
                ext = mtype.split("/")[-1]
            elif mtype.startswith("text") or mtype.startswith("application"):
                for association in mtype_associations:
                    if association[0] in mtype:
                        ext = association[1]
                        break
            if ext == "":
                ext = mtype.split("/")[-1]
            ext = "." + ext
        else:
            try: ext = "." + request.url().toString().split(".")[-1].split("#")[0].split("?")[0]
            except: ext = ".html"
        fname = QFileDialog.getSaveFileName(None, tr("Save As..."), os.path.join(self.saveDirectory, fileName + (ext if not "." in fileName else "")), tr("All files (*)"))
        if type(fname) is tuple:
            fname = fname[0]
        if fname:
            self.saveDirectory = os.path.split(fname)[0]
            reply = self.page().networkAccessManager().get(request)
            
            # Create a DownloadBar instance and append it to list of
            # downloads.
            downloadDialog = DownloadBar(reply, fname, None)
            self.downloads.append(downloadDialog)

            # Emit signal.
            self.downloadStarted.emit(downloadDialog)

    # Saves the current page.
    # It partially supports saving edits to a page,
    # but this is pretty hacky and doesn't work all the time.
    def savePage(self):
        content = self.page().mainFrame().toHtml()
        url = self.url().toString()
        #print(url)
        if url in ("about:blank", "", QUrl.fromUserInput(settings.new_tab_page).toString(), settings.new_tab_page_short,):
            fname = settings.new_tab_page
            content = content.replace("&lt;", "<").replace("&gt;", ">").replace("<body contenteditable=\"true\">", "<body>")
        else:
            fileName = self.windowTitle().lower()
            for r in (" ", "/", "\\", "_", "!", "?", "|"):
                fileName = fileName.replace(r, "-")
            fileName += ".html"
            upperFileName = fileName.upper()
            fname = QFileDialog.getSaveFileName(None, tr("Save As..."), os.path.join(self.saveDirectory, fileName + (ext if not "." in fileName else "")), tr("All files (*)"))
        if type(fname) is tuple:
            fname = fname[0]
        if fname:
            self.saveDirectory = os.path.split(fname)[0]
            try: f = open(fname, "w")
            except: pass
            else:
                try: f.write(content)
                except: pass
                f.close()
                common.trayIcon.showMessage(tr("Download complete"), os.path.split(fname)[1])

    # Adds a QUrl to the browser history.
    def addHistoryItem(self, url):
        addHistoryItem(url.toString(), self.windowTitle())

    # Redefine createWindow. Emits windowCreated signal so that others
    # can utilize the newly-created WebView instance.
    def createWindow(self, type):
        webview = WebView(incognito=self.incognito)
        self.webViews.append(webview)
        #webview.show()
        self.windowCreated.emit(webview)
        return webview

    # Convenience function.
    # Sets the zoom factor.
    def zoom(self):
        zoom = QInputDialog.getDouble(self, tr("Zoom"), tr("Set zoom factor:"), self.zoomFactor())
        if zoom[1]:
            self.setZoomFactor(zoom[0])

    # Convenience function.
    # Opens a very simple find text dialog.
    def find(self):
        if type(self._findText) is not str:
            self._findText = ""
        find = QInputDialog.getText(self, tr("Find"), tr("Search for:"), QLineEdit.Normal, self._findText)
        if find[1]:
            self._findText = find[0]
        else:
            self._findText = ""
        self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Convenience function.
    # Find next instance of text.
    def findNext(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Convenience function.
    # Find previous instance of text.
    def findPrevious(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument | QWebPage.FindBackward)

    # Opens a print dialog to print page.
    def printPage(self):
        printer = QPrinter()
        self.page().mainFrame().render(printer.paintEngine().painter())
        printDialog = QPrintDialog(printer)
        printDialog.open()
        printDialog.accepted.connect(lambda: self.print(printer))
        printDialog.exec_()

    # Opens a print preview dialog.
    def printPreview(self):
        printer = QPrinter()
        self.page().mainFrame().render(printer.paintEngine().painter())
        printDialog = QPrintPreviewDialog(printer, self)
        printDialog.paintRequested.connect(lambda: self.print(printer))
        printDialog.exec_()
        printDialog.deleteLater()

class WebViewAction(QWidgetAction):
    def __init__(self, *args, incognito=False, **kwargs):
        super(WebViewAction, self).__init__(*args, **kwargs)
        self.webView = WebView(incognito=incognito, sizeHint=QSize(1, 320), minimumSizeHint=QSize(0,0))
        self.webView.setUserAgent(common.mobileUserAgent)
        self.setDefaultWidget(self.webView)
    def load(self, *args, **kwargs):
        self.webView.load(*args, **kwargs)
    def back(self, *args, **kwargs):
        self.webView.back(*args, **kwargs)
    def forward(self, *args, **kwargs):
        self.webView.forward(*args, **kwargs)
    def reload(self, *args, **kwargs):
        self.webView.reload(*args, **kwargs)
    def stop(self, *args, **kwargs):
        self.webView.stop(*args, **kwargs)
