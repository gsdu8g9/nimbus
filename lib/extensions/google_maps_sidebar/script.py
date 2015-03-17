name = "Google Maps"
url = "data:text/html;base64,PGh0bWw+PGJvZHk+R29vZ2xlIE1hcHMgbm8gbG9uZ2VyIHdvcmtzIGFzIGRlc2lyZWQgaW4gdGhlIE5pbWJ1cyBzaWRlYmFyLiBZb3UgY2FuIHRyeSB0aGUgT3BlblN0cmVldE1hcCBzaWRlYmFyIGluc3RlYWQuPC9ib2R5PjwvaHRtbD4K"
clip = "data:text/html"
ua = "Mozilla/5.0 (Linux; U; Android 2.3.5; en-us) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
style1 = os.path.join(settings.extensions_folder, self.name, "style.css")
style = style1 if os.path.isfile(style1) else None
if not self.isCheckable():
    self.setCheckable(True)
    self.setChecked(True)
if not self.parentWindow().hasSideBar(name):
    self.parentWindow().addSideBar(name, url, clip, ua, style=style)
else:
    self.parentWindow().toggleSideBar(name)
