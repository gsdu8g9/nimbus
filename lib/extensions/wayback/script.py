currentTab = self.parentWindow().currentWidget()
currentTab.load(QUrl("http://web.archive.org/web/*/" + currentTab.url().toString()))
