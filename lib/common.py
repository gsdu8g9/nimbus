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
import stringfunctions
import paths
import settings
from PyQt5.QtCore import qVersion, QLocale, QUrl, QEvent, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebKit import qWebKitVersion, QWebSettings
pyqt4 = False

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

chop = stringfunctions.chop
rchop = stringfunctions.rchop
htmlToBase64 = stringfunctions.htmlToBase64
cssToBase64 = stringfunctions.cssToBase64

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

# App name info file
app_name_file = paths.app_name_file

# Version info file
app_version_file = paths.app_version_file

def applyWebSettings():
    websettings = QWebSettings.globalSettings()
    websettings.setAttribute(websettings.XSSAuditingEnabled, settings.setting_to_bool("network/XSSAuditingEnabled"))
    websettings.setAttribute(websettings.DnsPrefetchEnabled, settings.setting_to_bool("network/DnsPrefetchEnabled"))
    websettings.setAttribute(websettings.AutoLoadImages, settings.setting_to_bool("content/AutoLoadImages"))
    websettings.setAttribute(websettings.JavascriptCanOpenWindows, settings.setting_to_bool("content/JavascriptCanOpenWindows"))
    websettings.setAttribute(websettings.JavascriptCanCloseWindows, settings.setting_to_bool("content/JavascriptCanCloseWindows"))
    websettings.setAttribute(websettings.JavascriptCanAccessClipboard, settings.setting_to_bool("content/JavascriptCanAccessClipboard"))
    websettings.setAttribute(websettings.JavaEnabled, settings.setting_to_bool("content/JavaEnabled"))
    websettings.setAttribute(websettings.PrintElementBackgrounds, settings.setting_to_bool("content/PrintElementBackgrounds"))
    websettings.setAttribute(websettings.FrameFlatteningEnabled, settings.setting_to_bool("content/FrameFlatteningEnabled"))
    websettings.setAttribute(websettings.PluginsEnabled, settings.setting_to_bool("content/PluginsEnabled"))
    websettings.setAttribute(websettings.TiledBackingStoreEnabled, settings.setting_to_bool("content/TiledBackingStoreEnabled"))
    websettings.setAttribute(websettings.SiteSpecificQuirksEnabled, settings.setting_to_bool("content/SiteSpecificQuirksEnabled"))
    try: websettings.setAttribute(websettings.SpatialNavigationEnabled, settings.setting_to_bool("navigation/SpatialNavigationEnabled"))
    except: pass
    try: websettings.setAttribute(websettings.CaretBrowsingEnabled, settings.setting_to_bool("navigation/CaretBrowsingEnabled"))
    except: pass

# Application name. Change this to change the name of the program everywhere.
app_name = "Nimbus"
if os.path.isfile(app_name_file):
    try: f = open(app_name_file, "r")
    except: pass
    else:
        try: app_name = f.read().replace("\n", "")
        except: pass
        f.close()

# Application version
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

format_string = {"system": platform.system(), "machine": platform.machine(), "app_name": app_name, "qt_version": qt_version, "app_version": app_version, "webkit_version_m1": qWebKitVersion().split(".")[0], "webkit_version": qWebKitVersion(), "qt_version": qt_version, "locale": app_locale_h.lower(), "release": platform.release()}
defaultUserAgent = "Mozilla/5.0 (%(system)s %(machine)s; U; %(locale)s) AppleWebKit/%(webkit_version_m1)s+ (KHTML, like Gecko) Arora/%(qt_version)s Safari/%(webkit_version)s+ %(app_name)s/%(app_version)s" % format_string
mobileUserAgent = "Mozilla/5.0 (Linux; U; Android 2.3.5; %s) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1" % (app_locale_h,)
simpleUserAgent = "%(app_name)s/%(app_version)s (%(system)s; %(locale)s)" % format_string
chromeUserAgent = "Mozilla/5.0 (%(system)s %(machine)s; U; %(locale)s) AppleWebKit/%(webkit_version)s (KHTML, like Gecko) Chrome/24.%(qt_version)s Safari/%(webkit_version)s" % format_string
elinksUserAgent = "ELinks/%(qt_version)s (textmode; %(system)s %(release)s %(machine)s; 80x24)" % format_string
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
disconnected = []
