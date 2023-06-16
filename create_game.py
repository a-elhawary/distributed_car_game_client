from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
import ready_window 
import networking


class CreateGameScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        layout = QVBoxLayout()
        layout.addStretch(1)
        small = QWidget()
        small.setContentsMargins(300,0,300,0)
        small_layout = QVBoxLayout()
        title = QLabel("Let's Play!! Create a new Game")
        title.setStyleSheet(
            """
            color:#dbcd4b;
            font-size:20px;
            font-weight:bold;
            """
        )
        game_name_label = QLabel("GameName:")
        self.game_name = QLineEdit()
        self.game_name.setStyleSheet(
            """
            padding:10px;
            """
        )
        players_num_label = QLabel("Number of Players (max 6):")
        self.players_num = QLineEdit()
        self.players_num.setStyleSheet(
            """
            padding:10px;
            """
        )
        button = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        login = QPushButton("CreateGame")
        login.setStyleSheet(
            """
            background-color:#dbcd4b;
            color:#000;
            padding:10px;
            """
        )
        login.clicked.connect(self.onCreateGame)
        buttonLayout.addWidget(login)
        button.setLayout(buttonLayout)
        small_layout.addWidget(title)
        small_layout.addWidget(game_name_label)
        small_layout.addWidget(self.game_name)
        small_layout.addWidget(players_num_label)
        small_layout.addWidget(self.players_num)
        small_layout.addWidget(button)
        small.setLayout(small_layout)
        layout.addWidget(small)
        layout.addStretch(1)
        self.setLayout(layout)

    def onCreateGame(self):
        net = networking.ClientMiddleware()
        res = net.create_game(self.game_name.text(), self.players_num.text())
        net.joinGame(res[0], res[1])
        self.window.changeScreen(ready_window.ReadyScreen(net, self.window))

