from PyQt5.QtWebEngineWidgets import QWebEnginePage

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if "Refused to load the script" in message or "Uncaught TypeError" in message or "Unexpected token" in message:
            print(f"Suppressed JS error: {message}")
        else:
            super().javaScriptConsoleMessage(level, message, lineNumber, sourceId)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if isMainFrame:
            print(f"Navigating to {url.toString()}")
        return super().acceptNavigationRequest(url, _type, isMainFrame)
