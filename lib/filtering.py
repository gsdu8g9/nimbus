#! /usr/bin/env python3

# ------------
# filtering.py
# ------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: Loads URL filtering rules to be used by network.py.

import os.path
import abpy
import common
import settings
import urllib.request
if not common.pyqt4:
    from PyQt5.QtCore import QThread
else:
    try: from PyQt4.QtCore import QThread
    except: from PySide.QtCore import QThread

# Dummy adblock filter class.
class Filter(object):
    def __init__(self, rules):
        super(Filter, self).__init__()
        self.index = {}
    def match(self, url):
        return None

# Global stuff.
adblock_folder = os.path.join(settings.settings_folder, "Adblock")
hosts_folder = os.path.join(settings.settings_folder, "Hosts")
adblock_filter = Filter([])
shelved_filter = None
adblock_rules = []

# URLs for lists of rules.
adblock_urls = ["https://easylist-downloads.adblockplus.org/easylist.txt"]
hosts_urls = ["http://www.malwaredomainlist.com/hostslist/hosts.txt", "http://someonewhocares.org/hosts/hosts"]

# Update everything.
def download_rules():
    for folder, urls in ((adblock_folder, adblock_urls), (hosts_folder, hosts_urls)):
        if not os.path.isdir(folder):
            os.makedirs(folder)
        for url in urls:
            urllib.request.urlretrieve(url, os.path.join(folder, url.split("/")[-1]))

# Load adblock rules.
def load_adblock_rules():
    global adblock_filter
    global adblock_rules
    global shelved_filter

    if len(adblock_rules) < 1:
        if os.path.isdir(adblock_folder):
            for fname in os.listdir(adblock_folder):
                try:
                    f = open(os.path.join(adblock_folder, fname))
                    try: adblock_rules += [rule.rstrip("\n") for rule in f.readlines()]
                    except: pass
                    f.close()
                except:
                    pass

    # Create instance of abpy.Filter.
    if shelved_filter:
        adblock_filter = shelved_filter
    else:
        adblock_filter = abpy.Filter(adblock_rules)
        shelved_filter = adblock_filter

# Thread to load Adblock filters.
class AdblockFilterLoader(QThread):
    def __init__(self, parent=None):
        super(AdblockFilterLoader, self).__init__(parent)
    def run(self):
        if settings.setting_to_bool("content/AdblockEnabled"):
            load_adblock_rules()
        else:
            global adblock_filter
            global shelved_filter
            if len(adblock_filter.index.keys()) > 0:
                shelved_filter = adblock_filter
            adblock_filter = abpy.Filter([])
        self.quit()

# Create thread to load adblock filters.
adblock_filter_loader = AdblockFilterLoader()

# Host filter.
hosts_file = os.path.join(common.app_folder, "hosts")
host_rules = []

def load_host_rules():
    global host_rules
    host_rules = []
    if os.path.isdir(hosts_folder):
        for fname in os.listdir(hosts_folder):
            try: f = open(os.path.join(hosts_folder, fname), "r")
            except: pass
            else:
                # This is a big hacky way of parsing the rules.
                try:
                    host_rules += [line for line in [line.split(" ")[1].replace("\n", "") for line in f.readlines() if len(line.split(" ")) > 1 and not line.startswith("#") and len(line) > 1] if line != ""]
                except:
                    pass
                f.close()
