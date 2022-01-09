from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PIL import Image
import functools
import torch
import os
import sys
import Dooctor_UI


def LoadImages(path):
    imagesList = os.listdir(path)
    loadedImages = []
    loadedQPixmap = []
    for image in imagesList:
        if os.path.isdir(path + '/' + image):
            continue
        img = Image.open(path + '/' + image)
        loadedImages.append(img)
        loadedQPixmap.append(QtGui.QPixmap(path + '/' + image))

    return loadedImages, loadedQPixmap


class Dooctor(QtWidgets.QMainWindow, Dooctor_UI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Dooctor, self).__init__(parent)
        self.setupUi(self)
        self.OpenImageFolder.clicked.connect(self.GetDirectory)
        self.ImageSwitcher.valueChanged.connect(self.ChangeImage)
        self.results_croppedQpixmap = []

    def GetDirectory(self):
        # idk why there isn't file dialog in Qt designer
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)

        if dialog.exec_():
            self.imgs = []
            self.Qpixmap = []
            dirPath = dialog.selectedFiles()
            self.imgs, self.Qpixmaps = LoadImages(dirPath[0])
            self.ImageSwitcher.setMaximum(len(self.Qpixmaps) - 1)
            self.ChangeImage()
            self.ClassifyNDetectFracture.clicked.connect(
                functools.partial(self.ScaphoidDetection, self.imgs))

    def ChangeImage(self):
        if self.ImageSwitcher.value() > len(self.Qpixmaps) - 1 or self.ImageSwitcher.value() < 0:
            return
        self.OriginalImage.setPixmap(self.Qpixmaps[self.ImageSwitcher.value()])

        if len(self.results_croppedQpixmap) != 0:
            self.ResultImage_scaphoid.setPixmap(
                self.results_croppedQpixmap[self.ImageSwitcher.value()])

    def ScaphoidDetection(self, imgs):
        if len(imgs) < 0:
            return

        self.ResultImage_scaphoid.setText('Detecting...')
        model = torch.hub.load('ultralytics/yolov5', 'custom',
                               path='../models/batch8_epoch40_v5l_f1.pt')
        self.results = model(imgs)
        self.results.print()
        self.results.save('./results')

        loadedQPixmap = []
        imagesList = os.listdir('./results')
        for image in imagesList:
            if os.path.isdir('./results/' + image):
                continue
            loadedQPixmap.append(QtGui.QPixmap('./results/' + image))

        index = 0
        for img in loadedQPixmap:
            ax = self.results.pandas().xyxy[index].xmin[0]
            ay = self.results.pandas().xyxy[index].ymin[0]
            awidth = self.results.pandas(
            ).xyxy[index].xmax[0] - self.results.pandas().xyxy[index].xmin[0]
            aheight = self.results.pandas(
            ).xyxy[index].ymax[0] - self.results.pandas().xyxy[index].ymax[0]

            cropped = img.copy(ax, ay, awidth, aheight)
            self.results_croppedQpixmap.append(cropped)
            index += 1
            print('yoooo--')
        self.ResultImage_scaphoid.setText('')
        self.ChangeImage()


def main():
    app = QApplication(sys.argv)
    form = Dooctor()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
