mainWindow = browser.activeWindow()
try: mainWindow.counter
except:
    mainWindow.counter = 0
url = mainWindow.tabWidget().currentWidget().url().toString()
title = mainWindow.tabWidget().currentWidget().windowTitle()
def bbCodify(text):
    mainWindow = browser.activeWindow()
    if mainWindow.locationBar.isVisible():
        mainWindow.locationBar.setEditText(text)
    else:
        common.copyToClipboard(text)
        common.trayIcon.showMessage("Now on clipboard", text)
if mainWindow.counter == 0:
    bbCodify("[URL=%s]%s[/URL]" % (url, title))
elif mainWindow.counter == 1:
    bbCodify("[IMG]%s[/IMG]" % (url,))
elif mainWindow.counter == 2:
    bbCodify("[URL=%s][IMG]%s[/IMG][/URL]" % (url, url))
mainWindow.counter += 1
if mainWindow.counter > 2:
    mainWindow.counter = 0
