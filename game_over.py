from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
import games_list

class GameOver(QWidget):
    def __init__(self, chat, net, parent=None):
        QWidget.__init__(self,parent)
        self.window = parent
        self.chat = chat
        layout = QVBoxLayout()
        top = QWidget()
        top_layout = QVBoxLayout()
        top_layout.addStretch(1)
        btn = QPushButton("See Other Games")
        btn.setStyleSheet(
            """
            background-color:#dbcd4b;
            color:#000;
            padding:10px;
            """
        )
        btn.clicked.connect(self.home)
        top_layout.addWidget(btn)
        top.setLayout(top_layout)
        ranking = QWidget()
        ranking_layout = QVBoxLayout()
        
        players = []
        for player in net.getState()["Players_Info"]:
            players.append((player["ID"], int(player["Position_Y"])))

        players.sort(key=lambda a: a[1], reverse=True)

        i = 1
        for player in players:
            ranking_layout.addWidget(QLabel("%s. %s %s" % (i, player[0], player[1])))
            i+=1

        ranking.setLayout(ranking_layout)
        layout.addWidget(top)
        center = QWidget()
        center_layout = QHBoxLayout()
        center_layout.addWidget(ranking)
        center_layout.addWidget(chat)
        center.setLayout(center_layout)
        layout.addWidget(center)
        self.setLayout(layout)

    def home(self):
        self.chat.isRunning = False
        self.window.changeScreen(games_list.GameList(self.window))
