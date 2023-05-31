from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal
import time
import cv2
from networking import ClientMiddleware


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
        layout = QVBoxLayout()
        messages = QWidget()
        self.messagesLayout = QVBoxLayout()
        messages.setLayout(self.messagesLayout)
        layout.addWidget(messages)
        layout.addStretch(1)

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
        self.net = net
        self.current = 0

    def run(self):
        while True:
            myLen = len(self.net.getMessages())
            if myLen != self.current:
                self.current = myLen
                if myLen > 0:
                    self.msg_signal.emit(0)


class ActualGame(QWidget):
    current_state = {}

    def __init__(self, net, parent=None):
        QWidget.__init__(self, parent)
        self.net = net
        layout = QVBoxLayout()
        self.im = cv2.imread('assets/background.png')
        image = QImage(self.im.data, self.im.shape[1], self.im.shape[0], QImage.Format_RGB888).rgbSwapped()
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap.fromImage(image))
        layout.addWidget(self.label)

        gameLoop = GameLoop(self)
        gameLoop.msg_signal.connect(self.scrollImage)
        gameLoop.start()

        updateLoop = UpdateLoop(self.net, self)
        updateLoop.msg_signal.connect(self.updateCar)
        updateLoop.start()

        self.setLayout(layout)
        self.setFocus()

    def mousePressEvent(self, event):
        if QApplication.focusWidget() is not None:
            QApplication.focusWidget().clearFocus()
        self.setFocus()

    def keyPressEvent(self, e):
        if e.key() == 87: # w in ascii
            print("UP")
            self.net.move("UP")
        elif e.key() == 65: # a in ascii
            print("LEFT")
            self.net.move("LEFT")
        elif e.key() == 68: # d in ascii
            print("RIGHT")
            self.net.move("RIGHT")
        else:
            print(e.key())

    def updateCar(self, idx):
        self.current_state = self.net.getState()

    def scrollImage(self):
        offset = 40
        new_im = self.im.copy()
        new_im[:offset][:][:] = self.im[self.im.shape[0]-offset:][:][:]
        new_im[offset:][:][:] = self.im[:self.im.shape[0]-offset][:][:]

        # draw car on top of next rendered image


        self.im = new_im

        image = QImage(self.im.data, self.im.shape[1], self.im.shape[0], QImage.Format_RGB888).rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(image))


class UpdateLoop(QThread):
    msg_signal = pyqtSignal(int)

    def __init__(self, net, parent=None):
        QThread.__init__(self, parent)
        self.net = net
        self.currSize = 0

    def run(self):
        while True:
            if self.net.isStateChanged():
                self.msg_signal.emit(0)

class GameLoop(QThread):
    msg_signal = pyqtSignal(int)

    def __init__(self,  parent=None):
        QThread.__init__(self, parent)
        self.currSize = 0

    def run(self):
        start_time = time.time() * 1000
        while True:
            current_time = time.time() * 1000
            if current_time - start_time > 100:
                self.msg_signal.emit(1)
                start_time = current_time


class GameWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # initialize server
        self.net = ClientMiddleware()
        self.net.start()

        layout = QHBoxLayout()
        layout.addWidget(ActualGame(self.net))
        layout.addWidget(LiveChat(self.net))
        self.setLayout(layout)
