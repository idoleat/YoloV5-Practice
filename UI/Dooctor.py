from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PIL import Image
import os
import sys
import Dooctor_UI


def loadImages(path):
    imagesList = os.listdir(path)
    loadedImages = []
    for image in imagesList:
        if os.path.isdir(path + '/' + image):
            continue
        img = Image.open(path + '/' + image)
        loadedImages.append(img)

    return loadedImages


class Dooctor(QtWidgets.QMainWindow, Dooctor_UI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Dooctor, self).__init__(parent)
        self.setupUi(self)
        self.OpenImageFolder.clicked.connect(self.getDirectory)

    def getDirectory(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)

        if dialog.exec_():
            dirPath = dialog.selectedFiles()
            self.imgs = loadImages(dirPath[0])


def main():
    app = QApplication(sys.argv)
    form = Dooctor()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
