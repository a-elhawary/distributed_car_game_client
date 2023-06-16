from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
import sys
import login_window


class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.screen = None
        self.setStyleSheet(
            """
            background-color:#202020;
            color:#eee;
            """
        )
        self.layout = QVBoxLayout()
        self.layout.addWidget(login_window.LoginWindow(self))
        self.setLayout(self.layout)
        self.resize(1200, 800)
        self.setWindowTitle("Game Window")
        self.show()

    def changeScreen(self, screen):
        self.screen = screen
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.layout.addWidget(screen)


def main():
    global chat
    app = QApplication([])
    main = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
