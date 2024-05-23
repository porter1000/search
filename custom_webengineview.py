from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class CustomWebEngineView(QWebEngineView):
    def __init__(self):
        super().__init__()

    def load_url(self, url):
        proxy_url = f"http://127.0.0.1:8080/proxy/{url}"
        self.setUrl(QUrl(proxy_url))
