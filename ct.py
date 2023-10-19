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


    def image(self, draw = True) -> np.ndarray:
        if not draw:
            return self.matrix
        
        matrix_h, matrix_w = self.matrix.shape
        expand_h, expand_w = (0, 0)
        for shape in self.shapelist:
            offset_h, offset_w = shape.offset()
            shape_h,  shape_w  = shape.matrix()

            if offset_h >= 0 and matrix_h + expand_h < offset_h + shape_h:
                expand_h = offset_h + shape_h - matrix_h
            if offset_h < 0 and -1 * expand_h > offset_h:
                expand_h = -1 * offset_h

            if offset_w >= 0 and matrix_w + expand_w < offset_w + shape_w:
                expand_w = offset_w + shape_w - matrix_w
            if offset_w < 0 and -1 * expand_w > offset_w:
                expand_w = -1 * offset_w
            
        img = np.pad(self.matrix, ((expand_h, expand_h), (expand_w, expand_w)), \
                     'constant', constant_values = 0)
        # TODO finish adding shapes to img, allows shapes to br anywhere
        return img


    def shapes(self) -> list[Shape]:
        return self.shapelist

    def attach(self, shape):
        self.shapelist.append(shape)

    def detach(self, shape):
        self.shapelist.remove(shape)

    def __repr__(self) -> str:
        pass




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
        img = self.cases[i][j].image(draw = False)
        h, w = img.shape
        return QIcon(QPixmap(QImage(bytearray(img), w, h, QImage.Format.Format_Grayscale8)))
    

    # return the CTImage object of case i, image j 
    def get_CTImage(self, i, j) -> CTImage:
        return self.cases[i][j]