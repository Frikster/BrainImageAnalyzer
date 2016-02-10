import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QApplication
import showGui
from pdb import set_trace


class QMainWindow(QMainWindow, showGui.Ui_MainWindow):

    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.showMessageBox)

    def showMessageBox(self):
        QMessageBox.information(self, "Hello!", "Hello there, " + self.nameEdit.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = QMainWindow()
    form.show()
    app.exec_()