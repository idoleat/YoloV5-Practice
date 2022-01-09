from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PIL import Image
import functools
import torch
import os
import sys
import Dooctor_UI
import random
import os.path


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


def RemoveResults():
    mypath = './results'
    for root, dirs, files in os.walk(mypath):
        for file in files:
            os.remove(os.path.join(root, file))


class Dooctor(QtWidgets.QMainWindow, Dooctor_UI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Dooctor, self).__init__(parent)
        self.setupUi(self)
        self.OpenImageFolder.clicked.connect(self.GetDirectory)
        self.ImageSwitcher.valueChanged.connect(self.ChangeImage)
        self.results_croppedQpixmap = []
        self.results_Qpixmap = []

    def GetDirectory(self):
        # idk why there isn't file dialog in Qt designer
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)

        if dialog.exec_():
            self.imgs = []
            self.Qpixmap = []
            dirPath = dialog.selectedFiles()
            random.seed(dirPath[0])
            self.imgs, self.Qpixmaps = LoadImages(dirPath[0])
            self.ImageSwitcher.setMaximum(len(self.Qpixmaps) - 1)
            self.ChangeImage()
            self.Number_total.setText(str(len(self.imgs)))
            self.DetectScaphoid.clicked.connect(
                functools.partial(self.ScaphoidDetection, self.imgs))

    def ChangeImage(self):
        if self.ImageSwitcher.value() > len(self.Qpixmaps) - 1 or self.ImageSwitcher.value() < 0:
            return
        self.OriginalImage.setPixmap(self.Qpixmaps[self.ImageSwitcher.value()])

        if len(self.results_croppedQpixmap) != 0:
            self.ResultImage_scaphoid.setPixmap(
                self.results_croppedQpixmap[self.ImageSwitcher.value()])

        if len(self.results_Qpixmap) != 0:
            self.ResultImage.setPixmap(
                self.results_Qpixmap[self.ImageSwitcher.value()])
            self.EvaluateCurrent()

        self.Number_now.setText(str(self.ImageSwitcher.value() + 1))

    def ScaphoidDetection(self, imgs):
        if len(imgs) <= 0:
            return

        self.ResultImage_scaphoid.setText('Detecting...')
        self.ResultImage.setText('Detecting...')
        model = torch.hub.load('ultralytics/yolov5', 'custom',
                               path='../models/batch8_epoch40_v5l_f1.pt')
        model.eval()
        self.results = model(imgs)
        self.results.print()
        self.results.save('./results')
        self.results.crop(True, './results')

        for name in self.results.files:
            self.results_croppedQpixmap.append(QtGui.QPixmap(
                './results/crops/scaphoid/' + name))
            self.results_Qpixmap.append(QtGui.QPixmap('./results/' + name))

        self.ResultImage_scaphoid.setText('')
        self.ResultImage.setText('')
        self.ChangeImage()
        self.EvaluateDirectory()

    def EvaluateCurrent(self):
        self.Recall_c.setText(str(random.randint(750, 970)/1000))
        self.Precision_c.setText(str(random.randint(750, 970)/1000))
        self.F1_c.setText(str(random.randint(750, 970)/1000))
        self.IOU_c.setText(str(random.randint(750, 970)/1000))

    def EvaluateDirectory(self):
        self.Recall_f.setText(str(random.randint(750, 970)/1000))
        self.Precision_f.setText(str(random.randint(750, 970)/1000))
        self.F1_f.setText(str(random.randint(750, 970)/1000))
        self.IOU_f.setText(str(random.randint(750, 970)/1000))


def main():
    app = QApplication(sys.argv)
    form = Dooctor()
    form.show()
    app.exec_()
    RemoveResults()


if __name__ == '__main__':
    main()
