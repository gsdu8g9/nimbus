#!/usr/bin/env python3
from network import cookieJar, incognitoCookieJar
import json
try:
    from PyQt4.QtCore import QCoreApplication, QByteArray, QUrl, QSettings
    from PyQt4.QtNetwork import QNetworkCookie
except:
    from PySide.QtCore import QCoreApplication, QByteArray, QUrl, QSettings
    from PySide.QtNetwork import QNetworkCookie

# Global list to store history.
history = []

data = QSettings(QSettings.IniFormat, QSettings.UserScope, "nimbus", "data", QCoreApplication.instance())

# These store the geolocation whitelist and blacklist.
geolocation_whitelist = []
geolocation_blacklist = []

# This function loads the browser's settings.
def loadData():
    # Load history.
    global history
    global geolocation_whitelist
    global geolocation_blacklist
    raw_history = data.value("data/History")
    if type(raw_history) is str:
        history = json.loads(raw_history)

    # Load cookies.
    try: raw_cookies = json.loads(str(data.value("data/Cookies")))
    except: pass
    else:
        if type(raw_cookies) is list:
            cookies = [QNetworkCookie().parseCookies(QByteArray(cookie))[0] for cookie in raw_cookies]
            cookieJar.setAllCookies(cookies)

    try: wl = json.loads(str(data.value("data/GeolocationWhitelist")))
    except: pass
    else:
        if type(wl) is list:
            geolocation_whitelist = wl

    try: bl = json.loads(str(data.value("data/GeolocationBlacklist")))
    except: pass
    else:
        if type(bl) is list:
            geolocation_blacklist = bl

# This function saves the browser's settings.
def saveData():
    # Save history.
    global history
    history = [(item.partition("://")[-1] if "://" in item else item) for item in history]
    history = [item.replace(("www." if item.startswith("www.") else ""), "") for item in history]
    history = list(set(history))
    history.sort()
    data.setValue("data/History", json.dumps(history))

    # Save cookies.
    cookies = json.dumps([cookie.toRawForm().data().decode("utf-8") for cookie in cookieJar.allCookies()])
    data.setValue("data/Cookies", cookies)

    data.setValue("data/GeolocationWhitelist", json.dumps(geolocation_whitelist))
    data.setValue("data/GeolocationBlacklist", json.dumps(geolocation_blacklist))

    # Sync any unsaved settings.
    data.sync()

# Clear history.
def clearHistory():
    global history
    history = []
    saveData()

# Clear cookies.
def clearCookies():
    cookieJar.setAllCookies([])
    incognitoCookieJar.setAllCookies([])
    saveData()
