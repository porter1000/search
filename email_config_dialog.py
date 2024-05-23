from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout

class EmailConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Configuration")

        self.form_layout = QFormLayout()
        self.mail_server_input = QLineEdit()
        self.mail_port_input = QLineEdit()
        self.mail_username_input = QLineEdit()
        self.mail_password_input = QLineEdit()
        self.mail_password_input.setEchoMode(QLineEdit.Password)
        
        self.form_layout.addRow("Mail Server:", self.mail_server_input)
        self.form_layout.addRow("Mail Port:", self.mail_port_input)
        self.form_layout.addRow("Mail Username:", self.mail_username_input)
        self.form_layout.addRow("Mail Password:", self.mail_password_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.button_box)
        
        self.setLayout(self.layout)

    def get_data(self):
        return {
            'mail_server': self.mail_server_input.text(),
            'mail_port': int(self.mail_port_input.text()),
            'mail_username': self.mail_username_input.text(),
            'mail_password': self.mail_password_input.text()
        }
