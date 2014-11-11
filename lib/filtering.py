#! /usr/bin/env python3

# ------------
# filtering.py
# ------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: Loads URL filtering rules to be used by network.py.

import os.path
import abpy
import paths
import settings
import traceback
import urllib.request
from PyQt5.QtCore import QThread, QCoreApplication

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
adblock_urls = ["https://easylist-downloads.adblockplus.org/easylist.txt",
                "https://easylist-downloads.adblockplus.org/easyprivacy.txt"]
hosts_urls = ["http://www.malwaredomainlist.com/hostslist/hosts.txt",
              "http://someonewhocares.org/hosts/hosts",
              "http://winhelp2002.mvps.org/hosts.txt",
              "http://malwaredomains.lehigh.edu/files/justdomains"]

# Update everything.
def download_rules():
    for folder, urls in ((adblock_folder, adblock_urls), (hosts_folder, hosts_urls)):
        print("Updating filters for %s..." % folder.split("/")[-1],)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        for i in range(len(urls)):
            fname = str(i) + ".txt"
            print("Updating %s (using %s)..." % (fname, urls[i]))
            urllib.request.urlretrieve(urls[i], os.path.join(folder, fname))
            print("Done.")
        print("Filters for %s updated." % folder.split("/")[-1],)

# Update thread.
class FilterUpdater(QThread):
    def __init__(self, *args, **kwargs):
        super(FilterUpdater, self).__init__(*args, **kwargs)
    def run(self):
        print("Updating content filters...")
        download_rules()
        load_host_rules()
        print("All filters are up to date.")

filter_updater = FilterUpdater(QCoreApplication.instance())

# Convenience function.
def update_filters():
    if not filter_updater.isRunning():
        filter_updater.start()
    else:
        print("Already updating filters.")

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
                    try: adblock_rules += f.read().split("\n")
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
adblock_filter_loader = AdblockFilterLoader(QCoreApplication.instance())

# Host filter.
hosts_file = os.path.join(paths.app_folder, "hosts")
host_rules = []

def load_host_rules():
    global host_rules
    host_rules = []
    if os.path.isdir(hosts_folder):
        for fname in os.listdir(hosts_folder):
            try: f = open(os.path.join(hosts_folder, fname), "r")
            except: traceback.print_exc()
            else:
                # This is a big hacky way of parsing the rules.
                try:
                    new_file = [line for line in [line.split(" ")[-1].replace("\n", "") for line in f.readlines() if not line.startswith("#") and len(line) > 1] if line != ""]
                    host_rules += new_file
                except:
                    traceback.print_exc()
                f.close()
