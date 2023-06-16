from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import game_window
import live_chat

class Player(QWidget):
    def __init__(self, name, ready, parent=None):
        QWidget.__init__(self, parent)
        self.screen = parent
        self.name = name
        self.ready = ready
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
        layout.addWidget(title)
        layout.addWidget(num_players)
        self.setLayout(layout)
        layout.addStretch(1)
        if self.screen.net.isMine(name) and ready == 0:
            join = QPushButton("Ready")
            join.clicked.connect(self.onReady)
            join.setStyleSheet(
                """
                background-color:#dbcd4b;
                color:#000;
                padding:20px;
                """
            )
            layout.addWidget(join)
        elif ready == 0:
            join = QLabel("Not Ready!")
            join.setStyleSheet(
                """
                color:#ff0000;
                """
            )
            layout.addWidget(join)
        elif ready == 1:
            join = QLabel("Ready!")
            join.setStyleSheet(
                """
                color:#dbcd4b;
                """
            )
            layout.addWidget(join)

    def onReady(self):
        self.screen.net.makeReady()


class ReadyScreen(QWidget):
    def __init__(self,net, parent=None):
        QWidget.__init__(self, parent)
        self.net = net 
        self.window = parent
        self.players = []
        self.isRunning = True
        worker = NetworkWorker(self)
        worker.redraw_msg.connect(self.redraw)
        worker.change_window_msg.connect(self.start_game)
        worker.start()
        window_layout = QHBoxLayout()
        left = QWidget()
        self.chat = live_chat.LiveChat(self.net)
        self.layout = QHBoxLayout()
        left.setLayout(self.layout)
        window_layout.addWidget(left)
        window_layout.addStretch(1)
        window_layout.addWidget(self.chat)
        self.setLayout(window_layout)

    def redraw(self, idx):
        print("REDRAWING")
        for i in reversed(range(self.layout.count())):
            print("REMOVED WIDGET")
            self.layout.itemAt(i).widget().setParent(None)
        for p in self.players:
            print("ADDED WIDGET")
            player = Player(p["ID"], p["Ready"], self)
            self.layout.addWidget(player)

    def start_game(self):
        self.window.changeScreen(game_window.GameWindow(self.chat, self.net, self.window))


class NetworkWorker(QThread):
    redraw_msg = pyqtSignal(int)
    change_window_msg = pyqtSignal(int)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.screen = parent

    def run(self):
        print("Checking for changes...")
        while self.screen.isRunning:
            if self.screen.net.isStateChanged():
                print("Something Changed!")
                if self.screen.net.isStartGame():
                    self.change_window_msg.emit(0)
                else:
                    newState = self.screen.net.getState()
                    self.screen.players = newState["Players_Info"]
                    self.redraw_msg.emit(0)
