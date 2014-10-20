#!/usr/bin/env python3

# -----------------
# settings.py
# -----------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This module contains a global QSettings object that stores
#              the browser's settings. It also contains some convenience
#              functions.

import sys
import os
import json
import paths
from qsettings import QSettings

pyqt4 = False
for arg in ("-4", "--pyqt4"):
    if arg in sys.argv:
        pyqt4 = True

settings = QSettings("nimbus", "config", portable=paths.portable)
settings_folder = os.path.dirname(settings.fileName())

crash_file = os.path.join(settings_folder, ".browsercrash")

# This is a global variable that gets the settings folder on any platform.

# This stores the cache.
network_cache_folder = os.path.join(settings_folder, "Cache")
offline_cache_folder = os.path.join(settings_folder, "OfflineCache")

# Start page.
startpage = os.path.join(settings_folder, "start.html")
startpage_short = "nimbus-settings://start.html"

# Session file.
session_file = os.path.join(settings_folder, "session.pkl")

# User CSS
user_css = os.path.join(settings_folder, "user.css")

session_folder = os.path.join(settings_folder, "Sessions")

# Default settings.
default_settings = {"proxy/Type": "None",
                    "proxy/Hostname": "",
                    "proxy/Port": 8080,
                    "proxy/User": "",
                    "proxy/Password": "",
                    "network/DnsPrefetchEnabled": False,
                    "network/XSSAuditingEnabled": False,
                    "content/AutoLoadImages": True,
                    "network/GeolocationEnabled": True,
                    "content/JavascriptEnabled": True,
                    "content/JavascriptCanOpenWindows": False,
                    "content/JavascriptCanCloseWindows": False,
                    "content/JavascriptCanAccessClipboard": False,
                    "content/JavascriptCanEnterFullscreenMode": True,
                    "content/JavascriptCanExitFullscreenMode": False,
                    "content/JavaEnabled": False,
                    "content/PrintElementBackgrounds": True,
                    "content/FrameFlatteningEnabled": False,
                    "content/PluginsEnabled": True,
                    "content/AdblockEnabled": False,
                    "content/AdremoverFilters": """["#guser > nobr > #gbe", "#HOME_TOP_RIGHT_BOXAD", "#TOP_RIGHT_BOXAD", "#WikiaTopAds", ".headerads", ".home-top-right-ads", ".home_right_column", ".SelfServeUrl", ".adcode_container", ".ad-blocking-makes-fella-confused", "div[id*='adcode']", "div[id*='div-gpt-ad']", "div[class*='sleekadbubble']", "div[class*='gr-adcast']", "div[class*='textbanner-ad']", "div[class*='dp-ad-visible']", "div[class*='partial-ad']", "iframe[src*='/ads/']", "div[style='text-align: center; margin: 0px auto; width:160px; height:600px; position:relative;']", "div[id*='pw_adbox']", "#headerad"]""",
                    "content/HostFilterEnabled": True,
                    "content/ReplaceHTML5MediaTagsWithEmbedTags": (True if "win" in sys.platform else False),
                    "content/UseOnlineContentViewers": True,
                    "content/TiledBackingStoreEnabled": False,
                    "content/FlashEnabled": True,
                    "content/GIFsEnabled": True,
                    "content/SiteSpecificQuirksEnabled": True,
                    "general/Homepage": startpage_short,
                    "general/Search": "%s",
                    "general/CloseWindowWithLastTab": True,
                    "general/TabsOnTop": True,
                    "data/RememberHistory": True,
                    "data/MaximumURLLength": 96,
                    "general/ForcePyQt4": pyqt4,
                    "data/MaximumCacheSize": 50,
                    "general/OpenSettingsInTab": False,
                    "general/PinnedTabCount": 0,
                    "general/UpButtonVisible": False,
                    "general/TabHotkeysVisible": False,
                    "general/HomeButtonVisible": False,
                    "general/FeedButtonVisible": False,
                    "extensions/Whitelist": [],
                    "general/ReopenableTabCount": 10,
                    "general/ReopenableWindowCount": 10,
                    "general/NavigationToolBarVisible": True,
                    "general/StatusBarVisible": False,
                    "content/JavaScriptExceptions": []}

default_port = default_settings["proxy/Port"]

# New tab page.
new_tab_page = os.path.join(settings_folder, "newtab.html")
new_tab_page_short = "nimbus-settings://newtab.html"

# Set up default values.
for setting, value in default_settings.items():
    if settings.value(setting) == None:
        settings.setValue(setting, value)

settings.hardSync()

def setting_to_bool(value=""):
    try: return bool(eval(str(settings.value(value)).title()))
    except: return False

def setting_to_int(value=""):
    try: return int(settings.value(value))
    except: return 0

def setting_to_list(value=""):
    if type(settings.value(value)) is list:
        return settings.value(value)
    else:
        try: return json.loads(settings.value(value))
        except: return []

pyqt4 = setting_to_bool("general/ForcePyQt4")

js_exceptions = setting_to_list("content/JavaScriptExceptions")

# List of extensions.
extensions_folder = os.path.join(settings_folder, "Extensions")
extensions = []

# Stores all extension buttons.
extension_buttons = []

# List of extensions to load.
extensions_whitelist = []

# List of extensions not to load.
extensions_blacklist = []

# Ad Remover filters.
adremover_filters = []

# Load Ad Remover filters.
def load_adremover_filters():
    global adremover_filters
    try: adremover_filters = json.loads(settings.value("content/AdremoverFilters"))
    except: pass

# Load Ad Remover filters.
def save_adremover_filters():
    try: settings.setValue("content/AdremoverFilters", json.dumps(adremover_filters))
    except: pass

load_adremover_filters()

# Userscripts
userscripts = []

def reload_userscripts():
    global userscripts
    while len(userscripts) > 0:
        userscripts.pop()
    for extension in extensions:
        if extension not in extensions_whitelist:
            continue
        extension_path = os.path.join(extensions_folder, extension)
        if os.path.isfile(extension_path):
            extension_data = {"match": [], "content": "", "start": False}
            try: f = open(extension_path, "r")
            except: pass
            else:
                try: content = f.read()
                except: content = ""
                extension_data["content"] = content
                f.close()
                lines = content.split("\n")
                for line in lines:
                    for r in ("@match", "@include"):
                        if r in line:
                            extension_data["match"].append(line.split(r)[-1].strip("\n\t ").replace("?", "\?").replace("#", "\#").replace("+", "\+").replace("|", "\|"))
                            break
                    if "@run-at" in line:
                        extension_data["start"] = True if "document-start" in line else False
                userscripts.append(extension_data)

reload_userscripts()

# Reloads extension blacklist.
def reload_extensions2():
    global extensions_blacklist
    global extensions_whitelist
    try:
        extensions_blacklist = [extension for extension in extensions if extension not in json.loads(settings.value("extensions/Whitelist"))]
        extensions_whitelist = [extension for extension in extensions if extension in json.loads(settings.value("extensions/Whitelist"))]
    except:
        extensions_blacklist = [extension for extension in extensions]
        extensions_whitelist = []

# Reloads extensions.
def reload_extensions():
    global extensions
    if os.path.isdir(extensions_folder):
        extensions = sorted(os.listdir(extensions_folder))
    else:
        extensions = []
    reload_extensions2()

reload_extensions()

# Clear extensions.
def reset_extensions():
    global extension_buttons
    for extension in extension_buttons:
        try: extension.deleteLater()
        except: pass
    while len(extension_buttons) > 0:
        extension_buttons.pop()
