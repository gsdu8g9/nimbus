#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication
import mainwindow

def main():
    app = QApplication(sys.argv)
    win = mainwindow.MainWindow()
    win.show()
    sys.exit(app.exec_())

main()
