name = "OpenStreetMap"
url = "http://www.openstreetmap.org/"
clip = "openstreetmap"
style1 = os.path.join(settings.extensions_folder, self.name, "style.css")
style = style1 if os.path.isfile(style1) else None
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, style=style)
else:
    self.parentWindow().toggleSideBar(name)
