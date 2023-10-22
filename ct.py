from PyQt6.QtGui import QPixmap, QIcon, QImage
import pydicom as dicom
import numpy as np
import cv2
import os

from shapes import *



class CTImage:
    def __init__(self, abs_path):
        self.path = abs_path
        self.dir = os.path.dirname(abs_path)
        self.file = os.path.basename(abs_path)
        self.ds = dicom.dcmread(abs_path)
        self.matrix = cv2.normalize(self.ds.pixel_array, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        self.shapelist = list()


    def image(self) -> np.ndarray:
        return self.matrix

    def shapes(self) -> list[Shape]:
        return self.shapelist

    def attach(self, shape):
        self.shapelist.append(shape)

    def detach(self, shape):
        self.shapelist.remove(shape)

    def empty(self):
        self.shapelist = list()

    def __repr__(self) -> str:
        return self.dir + "\n" + self.file



class CTCases:
    def __init__(self, path):
        self.path = path
        self.cases = []


    # case is list of (non-zero) CTImages
    def add(self, case):
        self.cases.append(case)
    

    # return a list of sizes of cases
    def sizes(self):
        return [len(case) for case in self.cases]
    

    # return a QIcon of the CTImage object of case i, image j
    def get_QIcon(self, i, j) -> QIcon:
        img = self.cases[i][j].image()
        h, w = img.shape
        return QIcon(QPixmap(QImage(bytearray(img), w, h, QImage.Format.Format_Grayscale8)))
    

    # return the CTImage object of case i, image j 
    def get_CTImage(self, i, j) -> CTImage:
        try:
            x = self.cases[i][j]
        except:
            return None
        else:
            return self.cases[i][j]