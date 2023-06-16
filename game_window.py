from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal
import time
import cv2
import numpy as np
import live_chat
import copy
import game_over

class ActualGame(QWidget):

    def __init__(self, chat, net, parent=None):
        QWidget.__init__(self, parent)
        self.isRunning = True
        self.window = parent
        self.chat = chat
        layout = QVBoxLayout()
        self.background_im = cv2.imread('assets/background.png')
        self.car = cv2.imread("assets/car.png")
        self.enemy_car = cv2.imread("assets/enemy_car.png")
        self.lanes = [80,  190, 320, 450, 580, 680]
        image = QImage(self.background_im.data, self.background_im.shape[1], self.background_im.shape[0], QImage.Format_RGB888).rgbSwapped()
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap.fromImage(image))
        self.ranking = QLabel(self)
        layout.addWidget(self.ranking)
        layout.addWidget(self.label)

        self.net = net
        self.current_state = copy.deepcopy(self.net.getState())
        self.prev_y = None
        self.gameLoop = GameLoop(self.net, self)
        self.gameLoop.msg.connect(self.updateState)
        self.gameLoop.start()
        self.updateState()

        self.setLayout(layout)
        self.setFocus()


    def mousePressEvent(self, event):
        if QApplication.focusWidget() is not None:
            QApplication.focusWidget().clearFocus()
        self.setFocus()

    def keyPressEvent(self, e):
        if e.key() == 87: # w in ascii
            self.net.move("UP")
        elif e.key() == 65: # a in ascii
            self.net.move("LEFT")
        elif e.key() == 68: # d in ascii
            self.net.move("RIGHT")
        else:
            print(e.key())

    def getMyXY(self):
        for player in self.current_state["Players_Info"]:
            if self.net.isMine(player["ID"]):
                return self.lanes[int(player["Position_X"])], int(player["Position_Y"])
        return None, None

    def updateState(self):
        if self.current_state["Status"] == "Done":
            self.isRunning = False
            self.window.changeScreen(game_over.GameOver(self.chat, self.net, self.window))
            return
        _, self.prev_y = self.getMyXY()
        self.current_state = copy.deepcopy(self.net.getState())

        players = []
        for player in self.current_state["Players_Info"]:
            players.append((player["ID"], int(player["Position_Y"])))

        players.sort(key=lambda a: a[1], reverse=True)

        s = ""
        i = 1
        for player in players:
            s +=  str(i) + ". " + player[0] + " " + str(player[1]) + "% "
            i += 1
        self.ranking.setText(s)

        self.updateImage()

    def scrollImage(self, offset):
        new_im = self.background_im.copy()
        new_im[:offset][:][:] = self.background_im[self.background_im.shape[0]-offset:][:][:]
        new_im[offset:][:][:] = self.background_im[:self.background_im.shape[0]-offset][:][:]

        self.background_im = new_im

    def updateImage(self):
        offset = 40
        my_x, my_y = self.getMyXY()

        # scroll background if I moved up
        if my_y > self.prev_y:
            self.scrollImage(offset * (my_y - self.prev_y))

        rendered_im = self.background_im.copy()

        # render me
        im = self.car 
        rendered_im[530:530+im.shape[0], my_x:my_x+im.shape[1], :] = im

        # render rest
        for player in self.current_state["Players_Info"]:
            if not self.net.isMine(player["ID"]):
                this_y = int(player["Position_Y"])
                if this_y >= my_y:
                    im = self.enemy_car
                    x = self.lanes[int(player["Position_X"])]
                    y = 530 - offset * (this_y - my_y)
                    if y >= 0 and y <= 530:
                        rendered_im[y:y+im.shape[0], x:x+im.shape[1], :] = im

        image = QImage(rendered_im.data, rendered_im.shape[1], rendered_im.shape[0], QImage.Format_RGB888).rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(image))


class GameLoop(QThread):
    msg = pyqtSignal(int)

    def __init__(self, net,  parent=None):
        QThread.__init__(self, parent)
        self.net = net
        self.parent = parent

    def run(self):
        while self.parent.isRunning:
            if self.net.isStateChanged():
                self.msg.emit(0)


class GameWindow(QWidget):
    def __init__(self,chat, net, parent=None):
        QWidget.__init__(self, parent)

        self.window = parent
        self.net = net 

        self.actual_game = ActualGame(chat, self.net, self.window)

        layout = QHBoxLayout()
        layout.addWidget(self.actual_game)
        layout.addWidget(chat)
        self.setLayout(layout)
