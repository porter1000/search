import sys
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTextBrowser, QWidget, QLabel, QPushButton, QHBoxLayout, QFormLayout, QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt, QUrl
from custom_webengineview import CustomWebEngineView
from email_config_dialog import EmailConfigDialog  # Import the new dialog
import requests
from backend.routes import app as flask_app

class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")

        self.form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Password:", self.password_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.button_box)
        
        self.setLayout(self.layout)

    def get_data(self):
        return {
            'username': self.username_input.text(),
            'email': self.email_input.text(),
            'password': self.password_input.text()
        }

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        self.form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.button_box)
        
        self.setLayout(self.layout)

    def get_data(self):
        return {
            'username': self.username_input.text(),
            'password': self.password_input.text()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced Web Browser")
        self.setGeometry(100, 100, 800, 600)

        self.browser = CustomWebEngineView()

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL")
        self.url_bar.returnPressed.connect(self.load_url)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.returnPressed.connect(self.search_content)

        self.search_results = QTextBrowser()
        self.search_results.setOpenExternalLinks(False)
        self.search_results.anchorClicked.connect(self.load_link_from_search_results)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_user)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_user)

        self.email_config_button = QPushButton("Configure Email")
        self.email_config_button.clicked.connect(self.configure_email)

        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)

        auth_layout = QHBoxLayout()
        auth_layout.addWidget(self.register_button)
        auth_layout.addWidget(self.login_button)
        auth_layout.addWidget(self.email_config_button)

        layout = QVBoxLayout()
        layout.addWidget(self.url_bar)
        layout.addWidget(self.browser)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.search_results)
        layout.addWidget(self.status_label)
        layout.addLayout(pagination_layout)
        layout.addLayout(auth_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.current_page = 1
        self.per_page = 10
        self.current_query = ""

        self.fetch_and_display_default_results()

    def load_url(self):
        url = self.url_bar.text()
        self.browser.load_url(url)
        self.status_label.setText(f"Loading {url}...")

    def search_content(self):
        self.current_page = 1
        self.current_query = self.search_bar.text()
        if self.current_query:
            self.fetch_search_results()

    def fetch_search_results(self):
        response = requests.get(f'http://127.0.0.1:5000/api/search?q={self.current_query}&page={self.current_page}&per_page={self.per_page}')
        if response.status_code == 200:
            results = response.json()
            self.display_search_results(results)
            self.update_pagination_controls(results)
        else:
            self.display_search_results([])
            self.update_pagination_controls([])

    def fetch_and_display_default_results(self):
        predefined_queries = ['technology', 'science', 'sports', 'news']
        results = []
        for query in predefined_queries:
            response = requests.get(f'http://127.0.0.1:5000/api/search?q={query}&page=1&per_page=5')
            if response.status_code == 200:
                query_results = response.json()
                results.extend(query_results)
        self.display_search_results(results)

    def display_search_results(self, results):
        self.search_results.clear()
        for url, title, content in results:
            self.search_results.append(f'<b>{title}</b>\n<a href="{url}">{url}</a>\n<p>{content[:200]}...</p>\n\n')

    def update_pagination_controls(self, results):
        if self.current_page > 1:
            self.prev_button.setEnabled(True)
        else:
            self.prev_button.setEnabled(False)

        if len(results) == self.per_page:
            self.next_button.setEnabled(True)
        else:
            self.next_button.setEnabled(False)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.fetch_search_results()

    def next_page(self):
        self.current_page += 1
        self.fetch_search_results()

    def register_user(self):
        dialog = RegisterDialog()
        if dialog.exec_():
            data = dialog.get_data()
            response = requests.post('http://127.0.0.1:5000/api/register', json=data)
            if response.status_code == 201:
                self.status_label.setText("User registered successfully.")
            else:
                self.status_label.setText("Registration failed.")

    def login_user(self):
        dialog = LoginDialog()
        if dialog.exec_():
            data = dialog.get_data()
            response = requests.post('http://127.0.0.1:5000/api/login', json=data)
            if response.status_code == 200:
                self.status_label.setText("Login successful.")
            else:
                self.status_label.setText("Login failed.")

    def configure_email(self):
        dialog = EmailConfigDialog()
        if dialog.exec_():
            data = dialog.get_data()
            response = requests.post('http://127.0.0.1:5000/api/configure_email', json=data)
            if response.status_code == 200:
                self.status_label.setText("Email configured successfully.")
            else:
                self.status_label.setText("Email configuration failed.")

    def load_link_from_search_results(self, url):
        self.browser.load_url(url.toString())
        self.status_label.setText(f"Loading content from {url.toString()}...")

def run_flask():
    flask_app.run(debug=False)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
