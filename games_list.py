from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5 import QtCore
import ready_window
import create_game
import networking


class Game(QWidget):
    def __init__(self, game_id, name, num_players, tracker1_ip, tracker2_ip, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        self.trackers = [tracker1_ip, tracker2_ip]
        self.game_id = game_id
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
        join.setStyleSheet(
            """
            background-color:#dbcd4b;
            """
        )
        join.clicked.connect(self.onJoin)
        layout.addWidget(title)
        layout.addWidget(player_count)
        layout.addStretch(1)
        layout.addWidget(join)
        self.setLayout(layout)

    def onJoin(self):
        net = networking.ClientMiddleware()
        net.joinGame(self.game_id, self.trackers)
        self.window.changeScreen(ready_window.ReadyScreen(net, self.window))


class GameList(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.window = parent
        self.setStyleSheet(
            """
            QPushButton{
                background-color:#dbcd4b;
                color:#000;
                padding:20px;
            }
            """
        )
        layout = QVBoxLayout()
        games_widget = QWidget()
        self.games_layout = QVBoxLayout()
        games_widget.setLayout(self.games_layout)
        layout.addWidget(games_widget)
        self.refresh()
        layout.addStretch(1);
        bottomBar = QWidget()
        bottomBarLayout = QHBoxLayout()
        bottomBarLayout.addWidget(QLabel("Or start a new Game!"))
        bottomBarLayout.addStretch(1)
        createGameBtn = QPushButton("Create Game!")
        createGameBtn.clicked.connect(self.createGame)
        refreshBtn = QPushButton("Refresh")
        refreshBtn.clicked.connect(self.refresh)
        bottomBarLayout.addWidget(createGameBtn)
        bottomBarLayout.addWidget(refreshBtn)
        bottomBar.setLayout(bottomBarLayout)
        layout.addWidget(bottomBar)
        self.setLayout(layout)

    def refresh(self):
        games = networking.ClientMiddleware().list_games()
        for i in reversed(range(self.games_layout.count())):
            self.games_layout.itemAt(i).widget().setParent(None)
        gamesAdded = False
        for game in games:
            self.games_layout.addWidget(Game(game[0], game[1], game[2], game[3], game[4], self.window))
            gamesAdded = True
        if not gamesAdded:
            self.games_layout.addWidget(QLabel("No Games Yet! Create One..."))


    def createGame(self):
        self.window.changeScreen(create_game.CreateGameScreen(self.window))
