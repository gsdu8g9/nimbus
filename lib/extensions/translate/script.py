currentTab = self.parentWindow().currentWidget()
currentTab.load(QUrl("http://translate.google.com/translate?u=" + currentTab.url().toString()))
