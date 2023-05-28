from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5 import QtCore
import ready_window

# dummy, TODO: send a request to get json response


class Game(QWidget):
    def __init__(self, name, num_players, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        layout = QHBoxLayout()
        self.setStyleSheet(
            """
            background-color:#404040;
            padding:20px;
            """
        )
        title = QLabel(name)
        title.setStyleSheet(
            """
            color:#dbcd4b;
            font-size:20px;
            font-weight:bold;
            """
        )
        player_count = QLabel(str(num_players) + "/6 players")
        join = QPushButton("Join")
        join.clicked.connect(self.onJoin)
        join.setStyleSheet(
            """
            background-color:#dbcd4b;
            color:#000;
            padding:20px;
            """
        )
        layout.addWidget(title)
        layout.addWidget(player_count)
        layout.addStretch(1)
        layout.addWidget(join)
        self.setLayout(layout)

    def onJoin(self):
        self.window.changeScreen(ready_window.ReadyScreen(self.window))


class GameList(QWidget):
    def __init__(self, parent=None):
        self.window = parent
        QWidget.__init__(self, parent)
        layout = QVBoxLayout()
        games = [{"name": "OsZoz", "num_players": 3},{"name": "Habd", "num_players": 1}]
        for game in games:
            layout.addWidget(Game(game["name"], game["num_players"], self.window))
        layout.addStretch(1);
        self.setLayout(layout)
