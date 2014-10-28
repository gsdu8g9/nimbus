nimbus
======

Nimbus is a somewhat hacky Web browser coded in Python 3, using either Qt 5
via PyQt5 or Qt 4 via PyQt4. It is tailored specifically for my use case, but
I have open-sourced it due to 1) personal ideology, and 2) personal
convenience. Maybe someone will find it useful for something. Be warned that
there are no claims of stability, security, or usability in Nimbus, since it
is being made for no one but myself.

Nimbus more or less covers the following use case:
* X11 user.
* Heavy use of keyboard shortcuts.
* Long periods of time spent in fullscreen mode.
* Limited use of bookmarks and history.
* Lots of forum browsing.
* General dislike of ads.
* Some basic desire to add features to the browser.
* Use of GitHub as an image hosting service.

[The wiki](https://github.com/foxhead128/nimbus/wiki) contains information
on security advisories, extensions, and some questions and statements you
may have.

Dependencies
======

Nimbus depends on Python >=3.2 and either PyQt5 or PyQt4, with python3-dbus
and feedparser as optional dependencies. It is possible that it will work in
versions of Python 3 below 3.2 as well, but this has not been tested before.

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

![Nimbus running on Debian](https://raw.githubusercontent.com/foxhead128/fh-images/master/nimbus-296bf74460-debian.png)<br>
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

Running Nimbus on other platforms
======
[The wiki](https://github.com/foxhead128/nimbus/wiki) contains instructions on
getting Nimbus to run on Windows and OS X.

Licensing information
======

See LICENSE.md for more details.
