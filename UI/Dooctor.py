from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PIL import Image
import torch
import os
import sys
import Dooctor_UI


def LoadImages(path):
    imagesList = os.listdir(path)
    loadedImages = []
    for image in imagesList:
        if os.path.isdir(path + '/' + image):
            continue
        loadedImages.append(QtGui.QPixmap(path + '/' + image))

    return loadedImages


def ScaphoidDetection(imgs):
    model = torch.hub.load('ultralytics/yolov5', 'custom',
                           path='./models/batch8_epoch40_v5l_f1.pt')
    results = model(imgs)

    return results


class Dooctor(QtWidgets.QMainWindow, Dooctor_UI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Dooctor, self).__init__(parent)
        self.setupUi(self)
        self.OpenImageFolder.clicked.connect(self.GetDirectory)
        self.ImageSwitcher.valueChanged.connect(self.ChangeImage)

    def GetDirectory(self):
        # idk why there isn't file dialog in Qt designer
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)

        if dialog.exec_():
            dirPath = dialog.selectedFiles()
            self.imgs = LoadImages(dirPath[0])
            self.OriginalImage.setPixmap(self.imgs[self.ImageSwitcher.value()])
            self.ImageSwitcher.setMaximum(len(self.imgs) - 1)

    def ChangeImage(self):
        if self.ImageSwitcher.value() > len(self.imgs) - 1:
            return
        self.OriginalImage.setPixmap(self.imgs[self.ImageSwitcher.value()])


def main():
    app = QApplication(sys.argv)
    form = Dooctor()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
