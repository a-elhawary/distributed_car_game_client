from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class Message(QWidget):
    def __init__(self, msg, isMine, parent=None):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        if isMine:
            layout.addStretch(1)
        label = QLabel(msg)
        label.setStyleSheet("""
            padding:20px;
            border-radius:20px;
            background-color:#dbcd4b;
            color:#000;
        """)
        layout.addWidget(label)
        if not isMine:
            layout.addStretch(1)
        self.setLayout(layout)

class LiveChat(QWidget):
    def __init__(self,net, parent=None):
        QWidget.__init__(self, parent)
        self.net = net
        self.isRunning = True
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        messages = QWidget()
        scroll.setWidget(messages)
        self.messagesLayout = QVBoxLayout()
        self.messagesLayout.addStretch(1)
        messages.setLayout(self.messagesLayout)
        layout.addWidget(scroll)
        layout.setStretch(0,1)

        bottomBar = QWidget()
        bottomLayout = QHBoxLayout()
        self.chatText = QLineEdit()
        sendBtn = QPushButton()
        sendBtn.setText("Send")
        sendBtn.clicked.connect(self.sendMessage)
        bottomLayout.addWidget(self.chatText)
        bottomLayout.addWidget(sendBtn)
        bottomBar.setLayout(bottomLayout)

        layout.addWidget(bottomBar)
        self.setLayout(layout)

        myWorker = NetworkWoker(self.net, self)
        myWorker.msg_signal.connect(self.onDataRecieved)
        myWorker.start()

    def sendMessage(self, event):
        msg = self.chatText.text()
        self.net.sendChatMessage(msg)

    def onDataRecieved(self, indx):
        self.addMessage(self.net.getOneMessage(), False)

    def addMessage(self, data, isMine):
        self.messagesLayout.addWidget(Message(data[1], self.net.isMine(data[0])))


class NetworkWoker(QThread):
    msg_signal = pyqtSignal(int)

    def __init__(self, net, parent=None):
        QThread.__init__(self, parent)
        self.parent = parent
        self.net = net
        self.current = 0

    def run(self):
        while self.parent.isRunning:
            myLen = len(self.net.getMessages())
            if myLen != self.current:
                self.current = myLen
                if myLen > 0:
                    self.msg_signal.emit(0)
