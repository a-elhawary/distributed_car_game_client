from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
import games_list


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        layout = QVBoxLayout()
        layout.addStretch(1)
        small = QWidget()
        small.setContentsMargins(300,0,300,0)
        small_layout = QVBoxLayout()
        title = QLabel("Welcome Back! Login to Your Account")
        title.setStyleSheet(
            """
            color:#dbcd4b;
            font-size:20px;
            font-weight:bold;
            """
        )
        user_name_label = QLabel("Username:")
        user_name = QLineEdit()
        user_name.setStyleSheet(
            """
            padding:10px;
            """
        )
        password_label = QLabel("Password:")
        password = QLineEdit()
        password.setStyleSheet(
            """
            padding:10px;
            """
        )
        button = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        login = QPushButton("Login")
        login.setStyleSheet(
            """
            background-color:#dbcd4b;
            color:#000;
            padding:10px;
            """
        )
        login.clicked.connect(self.onLogin)
        buttonLayout.addWidget(login)
        button.setLayout(buttonLayout)
        small_layout.addWidget(title)
        small_layout.addWidget(user_name_label)
        small_layout.addWidget(user_name)
        small_layout.addWidget(password_label)
        small_layout.addWidget(password)
        small_layout.addWidget(button)
        small.setLayout(small_layout)
        layout.addWidget(small)
        layout.addStretch(1)
        self.setLayout(layout)

    def onLogin(self):
        self.window.changeScreen(games_list.GameList(self.window))
