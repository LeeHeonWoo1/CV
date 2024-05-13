import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class FirstUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('First UI')
        layout = QVBoxLayout()
        self.btn1 = QPushButton('Show Second UI')
        self.btn1.clicked.connect(self.showSecondUI)
        layout.addWidget(self.btn1)
        self.setGeometry(400, 100, 1200, 800)
        self.setLayout(layout)

    def showSecondUI(self):
        self.second_ui = SecondUI()
        self.second_ui.show()
        self.hide()

class SecondUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Second UI')
        layout = QVBoxLayout()
        self.btn2 = QPushButton('Show First UI')
        self.btn2.clicked.connect(self.showFirstUI)
        layout.addWidget(self.btn2)
        self.setGeometry(400, 100, 1200, 800)
        self.setLayout(layout)

    def showFirstUI(self):
        self.first_ui = FirstUI()
        self.first_ui.show()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    first_ui = FirstUI()
    first_ui.show()
    sys.exit(app.exec_())