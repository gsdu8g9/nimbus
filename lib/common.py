#! /usr/bin/env python3

# ---------
# common.py
# ---------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains global variables and objects used by the
#              rest of Nimbus' components.

# Import everything we need.
import sys
import platform
import os
import subprocess
import locale
import base64
import paths
import settings
pyqt4 = settings.pyqt4
if not settings.pyqt4:
    try:
        from PyQt5.QtCore import qVersion, QLocale, QUrl, QEvent, QCoreApplication
        from PyQt5.QtGui import QIcon
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtWebKit import qWebKitVersion
    except ImportError:
        try:
            from PyQt4.QtCore import qVersion, QLocale, QUrl, QEvent, QCoreApplication
            from PyQt4.QtGui import QIcon, QApplication
            from PyQt4.QtWebKit import qWebKitVersion
        except ImportError:
            from PySide.QtCore import qVersion, QLocale, QUrl, QEvent, QCoreApplication
            from PySide.QtGui import QIcon, QApplication
            from PySide.QtWebKit import qWebKitVersion
        pyqt4 = True
else:
    try:
        from PyQt4.QtCore import qVersion, QLocale, QUrl, QEvent, QCoreApplication
        from PyQt4.QtGui import QIcon, QApplication
        from PyQt4.QtWebKit import qWebKitVersion
    except:
        from PySide.QtCore import qVersion, QLocale, QUrl, QEvent, QCoreApplication
        from PySide.QtGui import QIcon, QApplication
        from PySide.QtWebKit import qWebKitVersion
    pyqt4 = True

def rm(fname):
    subprocess.Popen(["rm", fname])

if sys.platform.startswith("win"):
    import shutil
    def rmr(fname):
        shutil.rmtree(fname)
    def cp(fname, dest):
        shutil.copy2(fname, dest)
    def cpr(fname, dest):
        shutil.copytree(fname, dest)
else:
    def rmr(fname):
        os.system("rm -rf \"%s\"" % (fname,))
    def cp(fname, dest):
        subprocess.Popen(["cp", fname, dest])
    def cpr(fname, dest):
        subprocess.Popen(["cp", "-r", fname, dest])

def htmlToBase64(html):
    return "data:text/html;charset=utf-8;base64," + base64.b64encode((html.replace('\n', '')).encode('utf-8')).decode('utf-8')

def cssToBase64(css):
    return "data:text/css;charset=utf-8;base64," + base64.b64encode((css.replace('\n', '')).encode('utf-8')).decode('utf-8')

# Copy to clipboard.
# http://stackoverflow.com/questions/1073550/pyqt-clipboard-doesnt-copy-to-system-clipboard
def copyToClipboard(text):
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    event = QEvent(QEvent.Clipboard)
    QCoreApplication.instance().sendEvent(clipboard, event)

# Folder that Nimbus is stored in.
app_folder = paths.app_folder

portable = paths.portable

# Start page
startpage = paths.startpage

# Extensions folder
extensions_folder = paths.extensions_folder

# Icons folder
app_icons_folder = paths.app_icons_folder

# Version info file
app_version_file = paths.app_version_file

# Nimbus version
app_name = "Nimbus"
app_version = "0.0.0pre"
if os.path.isfile(app_version_file):
    try: f = open(app_version_file, "r")
    except: pass
    else:
        try: app_version = f.read().replace("\n", "")
        except: pass
        f.close()

# Valid top-level domains.
tlds_file = os.path.join(app_folder, "tlds.txt")
tlds = []
if os.path.isfile(tlds_file):
    try: f = open(tlds_file, "r")
    except: pass
    else:
        try: tlds = ["." + dom for dom in f.read().split("\n") if dom != ""]
        except: pass
        f.close()

def topLevelDomains():
    return tlds

# Qt version.
qt_version = qVersion()
try:
    qt_version_info = [int(seg) for seg in qt_version.split(".")]
except:
    qt_version_info = [5, 3, 1]

# Default user agent.
def createUserAgent():
    pass

# Python locale
try: app_locale = str(locale.getlocale()[0])
except: app_locale = str(QLocale.system().name())
app_locale_h = app_locale.replace("_", "-")

defaultUserAgent = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; %(locale)s) AppleWebKit/%(webkit_version_m1)s+ (KHTML, like Gecko) Version/5.0 Safari/%(webkit_version)s+ %(app_name)s/%(app_version)s" % {"app_name": app_name, "app_version": app_version, "webkit_version_m1": qWebKitVersion().split(".")[0], "webkit_version": qWebKitVersion(), "qt_version": qt_version, "locale": app_locale_h}
mobileUserAgent = "Mozilla/5.0 (Linux; U; Android 2.3.5; %s) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1" % (app_locale_h,)
simpleUserAgent = "%(app_name)s/%(app_version)s (%(system)s; %(locale)s)" % {"app_name": app_name, "app_version": app_version, "system": platform.system(), "locale": app_locale_h}
chromeUserAgent = "Mozilla/5.0 (%(system)s %(machine)s; U; %(locale)s) AppleWebKit/%(webkit_version)s (KHTML, like Gecko) Chrome/24.%(qt_version)s Safari/%(webkit_version)s" % {"system": platform.system(), "webkit_version": qWebKitVersion(), "qt_version": qt_version, "locale": app_locale_h, "machine": platform.machine()}
elinksUserAgent = "ELinks/%(qt_version)s (textmode; %(system)s %(release)s %(machine)s; 80x24)" % {"system": platform.system(), "qt_version": qt_version, "machine": platform.machine(), "release": platform.release()}
dilloUserAgent = "Dillo/%s" % (qt_version,)

user_agents = {"&Simplified": simpleUserAgent, "&Chromium": chromeUserAgent, "&Nimbus": defaultUserAgent, "&Qt": "nimbus_generic", "&Android": mobileUserAgent, "&ELinks": elinksUserAgent, "&Dillo": dilloUserAgent}

# WIDGET RELATED #

# This is a global store for the settings dialog.
settingsDialog = None

#####################
# DIRECTORY-RELATED #
#####################

###################
# ADBLOCK-RELATED #
###################

# Content viewers
content_viewers = (("http://view.samurajdata.se/ps.php?url=%s", (".pdf", ".ps.gz", ".ps", ".doc")),
                   ("https://docs.google.com/viewer?url=%s", (".pps", ".odt", ".sxw", ".ppt", ".pptx", ".docx", ".xls", ".xlsx", ".pages", ".ai", ".psd", ".tif", ".tiff", ".dxf", ".svg", ".eps", ".ttf", ".xps", ".zip", ".rar")),
                   ("http://viewdocsonline.com/view.php?url=", (".ods", ".odp", ".odg", ".sxc", ".sxi", ".sxd")),
                   ("http://vuzit.com/view?url=", (".bmp", ".ppm", ".xpm")))

# Get an application icon.
def icon(name, size=22):
    return os.path.join(app_icons_folder, str(size), name)

complete_icons = {}

# Returns a QIcon
def complete_icon(name):
    global complete_icons
    try: return complete_icons[name]
    except:
        nnic = QIcon()
        for size in (12, 16, 22, 24, 32, 48, 64, 72, 80, 128, 256, "scalable"):
            ic = icon(name + (".png" if size != "scalable" else ".svg"), size)
            try: nnic.addFile(ic)
            except: pass
        try: nic = QIcon().fromTheme(name, nnic)
        except: nic = nnic
        complete_icons[name] = nic
        return complete_icons[name]

def shortenURL(url):
    return QUrl(url).authority().replace("www.", "")

# This stylesheet is applied to toolbars that are blank.
blank_toolbar = "QToolBar { border: 0; background: transparent; }"

# Stores WebView instances.
webviews = []

# Stores WebView instances.
disconnected = []
