#!/usr/bin/env python3

##################
## translate.py ##
##################

# Description:
# This module contains objects and functions pertaining to
# internationalization

import traceback
import os.path
from common import app_folder, app_locale

try: from PySide.QtCore import QCoreApplication, QLocale, QTranslator, QObject
except: from PyQt4.QtCore import QCoreApplication, QLocale, QTranslator, QObject

# Translation.
translations_folder = os.path.join(app_folder, "translations")
translator = QTranslator(QCoreApplication.instance())
translator.load(app_locale, translations_folder)

_translator = QObject()

def tr(string):
    translation = QCoreApplication.translate("General", string)
    return translation

def translate(string):
    return tr(string)
