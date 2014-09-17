mainWindow = browser.activeWindow()
try: mainWindow.counter
except:
    mainWindow.counter = 0
url = mainWindow.tabWidget().currentWidget().url().toString()
title = mainWindow.tabWidget().currentWidget().windowTitle()
if mainWindow.counter == 0:
    mainWindow.locationBar.setEditText("[url=%s]%s[/url]" % (url, title))
elif mainWindow.counter == 1:
    mainWindow.locationBar.setEditText("[img]%s[/img]" % (url,))
elif mainWindow.counter == 2:
    mainWindow.locationBar.setEditText("[url=%s][img]%s[/img][/url]" % (url, url))
mainWindow.counter += 1
if mainWindow.counter > 2:
    mainWindow.counter = 0