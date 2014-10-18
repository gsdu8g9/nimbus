import random
number = random.randint(0, 10)
webView = self.parentWindow().currentWidget()
mainFrame = webView.page().mainFrame()
webView.page().javaScriptAlert(mainFrame, str(number), title="You rolled:")
