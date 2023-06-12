from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
import games_list
import login_window
import networking


class RegisterScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        layout = QVBoxLayout()
        layout.addStretch(1)
        small = QWidget()
        small.setContentsMargins(300,0,300,0)
        small_layout = QVBoxLayout()
        title = QLabel("Create a new Account!")
        self.errorMsg = QLabel("")
        self.errorMsg.setStyleSheet(
            """
            color:#ff0000;
            """
        )
        title.setStyleSheet(
            """
            color:#dbcd4b;
            font-size:20px;
            font-weight:bold;
            """
        )
        user_name_label = QLabel("Username:")
        self.user_name = QLineEdit()
        self.user_name.setStyleSheet(
            """
            padding:10px;
            """
        )
        password_label = QLabel("Password:")
        self.password = QLineEdit()
        self.password.setStyleSheet(
            """
            padding:10px;
            """
        )
        confirm_password_label = QLabel("Confirm Password:")
        self.confirm_password = QLineEdit()
        self.confirm_password.setStyleSheet(
            """
            padding:10px;
            """
        )
        button = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        register = QPushButton("Or Login")
        register.setStyleSheet(
            """
            color:#dbcd4b;
            padding:10px;
            """
        )
        register.clicked.connect(self.register)
        login = QPushButton("Register")
        login.setStyleSheet(
            """
            background-color:#dbcd4b;
            color:#000;
            padding:10px;
            """
        )
        login.clicked.connect(self.onLogin)
        buttonLayout.addWidget(register)
        buttonLayout.addWidget(login)
        button.setLayout(buttonLayout)
        small_layout.addWidget(title)
        small_layout.addWidget(self.errorMsg)
        small_layout.addWidget(user_name_label)
        small_layout.addWidget(self.user_name)
        small_layout.addWidget(password_label)
        small_layout.addWidget(self.password)
        small_layout.addWidget(confirm_password_label)
        small_layout.addWidget(self.confirm_password)
        small_layout.addWidget(button)
        small.setLayout(small_layout)
        layout.addWidget(small)
        layout.addStretch(1)
        self.setLayout(layout)

    def register(self):
        self.window.changeScreen(login_window.LoginWindow(self.window))

    def onLogin(self):
        if self.confirm_password.text() != self.password.text():
            self.errorMsg.setText("Passwords Don't Match!")
            return
        net = networking.ClientMiddleware()
        result = net.register(self.user_name.text(), self.password.text())
        if result == "user added":
            net.setUserID()
            self.window.changeScreen(games_list.GameList(self.window))
        else:
            self.errorMsg.setText(result)

        



