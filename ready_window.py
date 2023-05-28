from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5 import QtCore
import game_window


class Player(QWidget):
    def __init__(self, name, ready, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout()
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
        num_players = QLabel("Ready" if ready else "Waiting...")
        join = QPushButton("Ready")
        join.clicked.connect(self.onJoin)
        join.setStyleSheet(
            """
            background-color:#dbcd4b;
            color:#000;
            padding:20px;
            """
        )
        layout.addWidget(title)
        layout.addWidget(num_players)
        layout.addStretch(1)
        layout.addWidget(join)
        self.setLayout(layout)

    def onJoin(self):
        self.window.changeScreen(game_window.GameWindow(self.window))


class ReadyScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        players = [{"name":"osos", "ready":False}, {"name":"osos", "ready":True}, {"name":"hawary", "ready":False}]
        layout = QHBoxLayout()
        for player in players:
            layout.addWidget(Player(player["name"], player["ready"], self.window))
        self.setLayout(layout)
