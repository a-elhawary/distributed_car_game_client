from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5 import QtCore
import ready_window
import create_game
import networking


class Game(QWidget):
    def __init__(self, name, num_players, tracker1_ip, tracker2_ip, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        self.trackers = [tracker1_ip, tracker2_ip]
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
        player_count = QLabel(str(num_players) + " players")
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
        games = networking.ClientMiddleware().list_games()
        gamesAdded = False
        for game in games:
            print(game)
            layout.addWidget(Game(game[1], game[2], game[3], game[4], self.window))
            gamesAdded = True
        if not gamesAdded:
            layout.addWidget(QLabel("No Games Yet! Create One..."))
        layout.addStretch(1);
        bottomBar = QWidget()
        bottomBarLayout = QHBoxLayout()
        bottomBarLayout.addWidget(QLabel("Or start a new Game!"))
        bottomBarLayout.addStretch(1)
        createGameBtn = QPushButton("Create Game!")
        createGameBtn.setStyleSheet(
            """
            background-color:#dbcd4b;
            color:#000;
            padding:10px;
            """
        )
        createGameBtn.clicked.connect(self.createGame)
        bottomBarLayout.addWidget(createGameBtn)
        bottomBar.setLayout(bottomBarLayout)
        layout.addWidget(bottomBar)
        self.setLayout(layout)

    def createGame(self):
        self.window.changeScreen(create_game.CreateGameScreen(self.window))
