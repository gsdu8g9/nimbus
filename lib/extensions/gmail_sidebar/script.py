name = "Gmail"
url = "http://m.gmail.com/"
clip = "mail.google"
ua = None
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, ua)
else:
    self.parentWindow().toggleSideBar(name)
