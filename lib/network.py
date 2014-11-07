#! /usr/bin/env python3

# ----------
# network.py
# ----------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains data related to networking, such as a
#              cookie jar, disk cache, and QNetworkAccessManager. It also
#              contains a function to detect whether the browser is online
#              or not.

import sys
import os
import common
import settings
import filtering
import random
import settings
from translate import tr
if not common.pyqt4:
    from PyQt5.QtCore import QCoreApplication, QUrl, QTimer
    from PyQt5.QtGui import QDesktopServices
    from PyQt5.QtWidgets import QInputDialog, QLineEdit
    from PyQt5.QtNetwork import QNetworkInterface, QNetworkCookieJar, QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest, QNetworkReply
else:
    from PyQt4.QtCore import QCoreApplication, QUrl, QTimer, SIGNAL
    from PyQt4.QtGui import QInputDialog, QLineEdit, QDesktopServices
    from PyQt4.QtNetwork import QNetworkInterface, QNetworkCookieJar, QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest, QNetworkReply

# Global cookiejar to store cookies.
# All nimbus.WebView instances use this.
cookie_jar = QNetworkCookieJar(QCoreApplication.instance())

# All incognito nimbus.WebView instances use this one instead.
incognito_cookie_jar = QNetworkCookieJar(QCoreApplication.instance())

# Subclass of QNetworkReply that loads a local folder.
class NetworkReply(QNetworkReply):
    def __init__(self, parent, url, operation, content=""):
        QNetworkReply.__init__(self, parent)
        self.content = content
        self.offset = 0
        self.setHeader(QNetworkRequest.ContentTypeHeader, "text/html; charset=UTF-8")
        self.setHeader(QNetworkRequest.ContentLengthHeader, len(self.content))
        try:
            QTimer.singleShot(0, self.readyRead)
            QTimer.singleShot(0, self.finished)
        except:
            QTimer.singleShot(0, self, SIGNAL("readyRead()"))
            QTimer.singleShot(0, self, SIGNAL("finished()"))
        self.open(self.ReadOnly | self.Unbuffered)
        self.setUrl(url)

    def abort(self):
        pass

    def bytesAvailable(self):
        return len(self.content) - self.offset
    
    def isSequential(self):
        return True

    def readData(self, maxSize):
        if self.offset < len(self.content):
            end = min(self.offset + maxSize, len(self.content))
            data = self.content[self.offset:end]
            data = data.encode("utf-8")
            self.offset = end
            return bytes(data)

# Error page generator.
def errorPage(url="about:blank", title="Whoops...", error="Nimbus could not load the requested page."):
    if type(url) is QUrl:
        url = url.toString()
    return "<!DOCTYPE html><html><title>%(title)s</title><style type='text/css'>html{font-family:sans-serif;}</style><body><h1>%(heading)s</h1><p>%(error)s</p><a href=\"%(url)s\">%(tryagain)s</a></body></html>" % {"title": tr("Problem loading page"), "heading": tr(title), "error": tr(error), "url": url, "tryagain": tr("Try again")}

directoryView = """<!DOCTYPE html>
<html>
    <head>
        <title>%(title)s</title>
    </head>
    <body>
        <h1 style="margin-bottom: 0;">%(heading)s</h1>
        <hr/>
        %(links)s
    </body>
</html>
"""

replacement_table = {}

# Custom NetworkAccessManager class with support for ad-blocking.
class NetworkAccessManager(QNetworkAccessManager):
    #diskCache = diskCache
    def __init__(self, *args, nocache=False, **kwargs):
        super(NetworkAccessManager, self).__init__(*args, **kwargs)
        self.authenticationRequired.connect(self.provideAuthentication)
    def provideAuthentication(self, reply, auth):
        username = QInputDialog.getText(None, "Authentication", "Enter your username:", QLineEdit.Normal)
        if username[1]:
            auth.setUser(username[0])
            password = QInputDialog.getText(None, "Authentication", "Enter your password:", QLineEdit.Password)
            if password[1]:
                auth.setPassword(password[0])
    def createRequest(self, op, request, device=None):
        url = request.url()
        ctype = str(request.header(QNetworkRequest.ContentTypeHeader))
        urlString = url.toString()
        lurlString = urlString.lower()
        x = filtering.adblock_filter.match(urlString)
        y = url.authority() in filtering.host_rules if settings.setting_to_bool("content/HostFilterEnabled") and url.authority() != "" else False
        z = (lurlString.endswith(".swf") or "flash" in ctype) and not settings.setting_to_bool("content/FlashEnabled")
        aa = (lurlString.endswith(".gif") or "image/gif" in ctype) and not settings.setting_to_bool("content/GIFsEnabled")
        if x != None or y or z or aa:
            return QNetworkAccessManager.createRequest(self, self.GetOperation, QNetworkRequest(QUrl(random.choice(("http://www.randomkittengenerator.com/images/cats/rotator.php", "http://thecatapi.com/api/images/get?format=src&type=png&size=small")) if settings.setting_to_bool("content/KittensEnabled") else "data:image/gif;base64,R0lGODlhAQABAHAAACH5BAUAAAAALAAAAAABAAEAAAICRAEAOw==")))
        if urlString in tuple(replacement_table.keys()):
            return QNetworkAccessManager.createRequest(self, op, QNetworkRequest(QUrl(replacement_table[urlString])), device)
        if url.scheme() == "file" and os.path.isdir(os.path.abspath(url.path())):
            try:
                html = directoryView % {"title": urlString, "heading": url.path(), "links": "".join(["<a href=\"%s\">%s</a><br/>" % (QUrl.fromUserInput(os.path.join(urlString, path)).toString(), path,) for path in [".."] + sorted(os.listdir(os.path.abspath(url.path())))])}
            except:
                html = directoryView % {"title": urlString, "heading": url.path(), "links": tr("The contents of this directory could not be loaded.")}
            return NetworkReply(self, url, self.GetOperation, html)
        if url.scheme() == "nimbus-extension":
            request.setUrl(QUrl("http://127.0.0.1:8133/" + common.chop(url.toString(QUrl.RemoveScheme), "//")))
            return QNetworkAccessManager.createRequest(self, op, request, device)
        if url.scheme() == "nimbus":
            request.setUrl(QUrl("file://%s/" % (common.app_folder,) + common.chop(url.toString(QUrl.RemoveScheme), "//")))
            return self.createRequest(op, request, device)
        if url.scheme() == "nimbus-settings":
            request.setUrl(QUrl("file://%s/" % (settings.settings_folder,) + common.chop(url.toString(QUrl.RemoveScheme), "//")))
            return self.createRequest(op, request, device)
        if url.scheme() == "apt":
            os.system("xterm -e \"sudo apt-get install %s\" &" % (common.chop(url.toString(QUrl.RemoveScheme), "//").split("&")[0],))
            return QNetworkAccessManager.createRequest(self, self.GetOperation, QNetworkRequest(QUrl("")))
        if url.scheme() == "mailto":
            QDesktopServices.openUrl(url)
            return QNetworkAccessManager.createRequest(self, self.GetOperation, QNetworkRequest(QUrl("")))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)

# Create global instance of NetworkAccessManager.
network_access_manager = NetworkAccessManager()
network_access_manager.setCookieJar(cookie_jar)
incognito_network_access_manager = NetworkAccessManager(nocache=True)
incognito_network_access_manager.setCookieJar(incognito_cookie_jar)

def apply_proxy():
    proxyType = str(settings.settings.value("proxy/Type"))
    if proxyType == "None":
        proxyType = "No"
    port = settings.settings.value("proxy/Port")
    if port == None:
        port = common.default_port
    user = str(settings.settings.value("proxy/User"))
    if user == "":
        user = None
    password = str(settings.settings.value("proxy/Password"))
    if password == "":
        password = None
    for manager in (incognito_network_access_manager, network_access_manager):
        manager.setProxy(QNetworkProxy(eval("QNetworkProxy." + proxyType + "Proxy"), str(settings.settings.value("proxy/Hostname")), int(port), user, password))

# Clear cache.
def clear_cache():
    common.trayIcon.showMessage("What cache?", "%s doesn't have a cache." % (common.app_name,))

# This function checks whether the system is connected to a network interface.
# It is used by Nimbus to determine whether the system is connected to the
# Internet, though this is technically a misuse of it.
# Ported from http://stackoverflow.com/questions/2475266/verfiying-the-network-connection-using-qt-4-4
# and http://stackoverflow.com/questions/13533710/pyqt-convert-enum-value-to-key
# and http://stackoverflow.com/questions/3764291/checking-network-connection
def isConnectedToNetwork(reference=None):
    ifaces = QNetworkInterface.allInterfaces()
    result = False
    for iface in ifaces:
        if (iface.flags() & QNetworkInterface.IsUp) and not (iface.flags() & QNetworkInterface.IsLoopBack):
            for entry in iface.addressEntries():
                result = True
                break
    return result
