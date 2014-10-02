nimbus
======

Nimbus is a somewhat hacky Web browser coded in Python 3, using either Qt 5
via PyQt5, or Qt 4 via either PyQt4 or PySide. It is tailored specifically
for my use case, but I have open-sourced it due to 1) personal ideology, and
2) personal convenience. Maybe someone will find it useful for something. Be
warned that there are no claims of stability, security, or usability in
Nimbus, since it is being made for no one but myself.

Nimbus more or less covers the following use case:
* X11 user.
* Heavy use of keyboard shortcuts.
* Long periods of time spent in fullscreen mode.
* Limited use of bookmarks and history.
* Lots of forum browsing.
* General dislike of ads.
* Some basic desire to add features to the browser.
* Use of GitHub as an image hosting service.

Dependencies
======

Nimbus depends on Python >=3.2 and either PyQt5, PyQt4, or PySide, with
python3-dbus and feedparser as optional dependencies. It is possible that it
will work in versions of Python 3 below 3.2 as well, but this has not been
tested before.

Nimbus does not work in Python 2.x and I have no plans to support it.

You can install all of Nimbus's dependencies on Debian-based platforms
using the following command:

    sudo apt-get install python3 python3-pyqt5 python3-pyqt5.qtwebkit python3-dbus python3-dbus.mainloop.pyqt5 python3-feedparser

Running Nimbus on Linux
======

Simply run the following:

    ./nimbus

Alternatively, you can try the following:

    ./lib/nimbus.py

![Nimbus running on Debian](https://raw.githubusercontent.com/foxhead128/fh-images/master/nimbus-current.png)<br>
*Nimbus running on Debian*

Installing Nimbus on Linux
======

**Note:** You don't have to install Nimbus in order to run it; see previous
section.

If you want to install Nimbus system-wide, you will need setuptools. On
Debian-based platforms, you can install it with the following command:

    sudo apt-get install python3-setuptools

Once that's done, run the following:

    sudo python3 ./setup.py install
    
Uninstalling Nimbus on Linux
======

Simply run the following:

    ./uninstall.sh

Running Nimbus on Windows
======

Nimbus also works using [Portable Python](http://portablepython.com/); this is
currently the recommended way of running it on Windows. To start Nimbus, open
the /lib folder and run nimbus.py. Unfortunately, this is not a long-term 
solution unless Portable Python starts bundling PyQt5; see **The future of
Nimbus** for more details.

The compile_windows.py script is deprecated and has been broken for quite some
time now. It will likely be removed in the near future.

![Nimbus running on Windows 7](http://i.imgur.com/fGP5bkz.png)<br>
*Nimbus running on Windows 7*

Enabling portable mode
======

Portable Python makes it possible to run Nimbus off a flash drive. For true
portability, Nimbus also supports a portable mode in which settings are saved
to whatever folder Nimbus itself is contained in, as opposed to the user's
home folder on the local hard drive. To enable this mode, simply create a file
named portable.conf and insert it into the /lib folder.

Running Nimbus on OS X
======

First, install
[Python 3.2.3 for OS X](https://www.python.org/download/releases/3.2.3/).
After that, install PyQtX from
[here](http://sourceforge.net/projects/pyqtx/files/Complete/). Keep in mind to
download the Python 3 version, not the Python 2 version. Once that's done,
open a terminal emulator and enter the following:

    cd <insert path to /lib folder here>
    python3.2 ./nimbus.py

Nimbus will look terrible, and it probably won't work very well, but it should
be functional.

![Nimbus running on OS X](https://raw.githubusercontent.com/foxhead128/fh-images/master/nimbus-mac.png)<br>
*Nimbus running on OS X*

Translations
======

Nimbus supports translations by way of QTranslator. To write a new
translation for Nimbus, make a copy of translations/en_US.ts, rename it to the
ISO code for the desired locale, and edit away. Once you're done, run
compile_translations.py on Linux/OS X/Unix, or lrelease on Windows. You will
need lrelease to be installed. Do note that the translation files are badly
out of date.

The future of Nimbus
======

In the long run, PyQt5 will drop support for QtWebKit in favor of QtWebEngine.
Supporting both of them at once will be infeasible, meaning that Nimbus will
only support QtWebEngine in the future. This also means dropping support for
both PyQt4 and PySide, unless PySide actually picks up the slack and starts
supporting Qt 5.

Licensing information
======

See LICENSE.md for more details.
