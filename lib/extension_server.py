#!/usr/bin/env python3

# -------------------
# extension_server.py
# -------------------
# Author:      Daniel Sim (foxhead128)
# License:     See LICENSE.md for more details.
# Description: This simple script launches a webserver, which hosts the
#              browser's extension files so they can be loaded into the DOM
#              without suffering from issues regarding origin policies.

# Import whatever we need to run.
import os
from http.server import SimpleHTTPRequestHandler
import http.server
import time
try:
    from PyQt5.QtCore import QThread
except ImportError:
    from PyQt4.QtCore import QThread
from settings import extensions_folder

class ExtensionServerThread(QThread):
    def __init__(self, *args, directory=extensions_folder, **kwargs):
        super(ExtensionServerThread, self).__init__(*args, **kwargs)
        self.directory = directory
        self.httpd = None
    def setDirectory(self, directory):
        self.directory = directory
        os.chdir(self.directory)
    def run(self):
        os.chdir(self.directory)
        HandlerClass = SimpleHTTPRequestHandler
        ServerClass  = http.server.HTTPServer
        Protocol     = "HTTP/1.0"

        port = 8133
        server_address = ('127.0.0.1', port)

        HandlerClass.protocol_version = Protocol
        counter = 5
        while 1:
            try: self.httpd = ServerClass(server_address, HandlerClass)
            except:
                print("Failed to start extension server! Retrying in %s seconds." % (counter,))
                time.sleep(counter)
                counter *= 2
            else:
                print("Extension server started successfully.")
                break

        sa = self.httpd.socket.getsockname()
        self.httpd.serve_forever()
