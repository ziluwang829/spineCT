import typing
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QWidget, QGridLayout, QLineEdit, QFileDialog, QFormLayout, QLabel, \
    QLCDNumber, QMessageBox, QHBoxLayout, QComboBox, QRadioButton, QCheckBox, QVBoxLayout, QScrollArea, QScrollBar
from PyQt6.QtCore import pyqtSignal, QObject, QSize, QRunnable, pyqtSlot, QThreadPool, Qt
from PyQt6.QtGui import QAction, QPixmap, QIcon, QImage
from PyQt6.QtGui import QPalette, QColor
import numpy as np
import sys
import pdb
import os
import pydicom as dicom
import cv2


class MyScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        # Ignore key events to disable keyboard interaction
        event.ignore()

    def wheelEvent(self, event):
        event.ignore()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.folder = "./1444306"

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Spine CT")
        self.resize(QSize(1280, 720))
        self.setMinimumSize(QSize(780, 700))
        self.setMaximumSize(QSize(1920, 1080))


        # Menu Bar for changing folders.
        menubar = self.menuBar()
        new_folder_action = QAction('Open New Folder', self)
        new_folder_action.triggered.connect(self.new_folder_dialog)
        file_menu = menubar.addMenu('File')
        file_menu.addAction(new_folder_action)


        # Overall Layouts
        layout = QGridLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.control = QWidget()
        self.control.setMinimumHeight(100)
        self.control.setMaximumHeight(100)
        self.select = MyScrollArea()
        self.select.setMinimumWidth(150)
        self.select.setMaximumWidth(150)
        self.display = QWidget()
        # self.display.setStyleSheet("border: 1px solid blue;")
        self.display.setStyleSheet("background-color: black;")
        self.display.setMinimumWidth(590)
        self.display.setMinimumHeight(560)
        self.scrollbar = QScrollBar()
        self.scrollbar.setValue(0)
        self.scrollbar.setMinimum(0)
        self.scrollbar.setFixedWidth(20)
        self.scrollbar.setPageStep(1)
        # self.scrollbar.setStyleSheet("border: 1px solid yellow;")
        self.scrollbar.valueChanged.connect(self.change_slides)
        self.display_layout = QVBoxLayout(self.display)
        self.display_layout.setDirection(QVBoxLayout.Direction.RightToLeft)
        self.display_layout.addWidget(self.scrollbar)
        self.display_layout.setContentsMargins(0,0,0,0)
        self.display_layout.setSpacing(0)
        layout.addWidget(self.control, 0, 0, 1, 10)
        layout.addWidget(self.select, 1, 0, 9, 1)
        layout.addWidget(self.display, 1, 1, 9, 9)


        # self.control/Drawing Layout
        control_layout = QHBoxLayout(self.control)
        button1 = QPushButton()
        button1.setIcon(QIcon("assets/line.png"))
        button1.setIconSize(QSize(70,70))
        button1.setFixedSize(80, 80)
        button2 = QPushButton()
        button2.setIcon(QIcon("assets/circle.png"))
        button2.setIconSize(QSize(70,70))
        button2.setFixedSize(80, 80)
        button3 = QPushButton(self.control)
        button3.setIcon(QIcon("assets/square.png"))
        button3.setFixedSize(80, 80)
        button3.setIconSize(QSize(70,70))
        button1.clicked.connect(self.change_control)
        button2.clicked.connect(self.change_control)
        button3.clicked.connect(self.change_control)
        self.control_buttons = [button1, button2, button3]
        self.control_current = None
        control_layout.addWidget(button1)
        control_layout.addWidget(button2)
        control_layout.addWidget(button3)
        control_layout.addStretch(1)

        self.drawing_board = QWidget(self)
        self.drawing_board.setGeometry(self.display.pos().x(), self.display.pos().y(), \
                                       self.display.width() - 20, self.display.height())
        self.drawing_layout = QVBoxLayout(self.drawing_board)
        self.drawing_layout.setContentsMargins(0,0,0,0)
        self.drawing_layout.setSpacing(0)
        self.drawing_board.setStyleSheet("border: 1px solid yellow;")
        # self.drawing_board.hide()

        # Show Preview Img on side
        self.update_selection()


    def new_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.folder)
        if folder and os.path.abspath(self.folder) != os.path.abspath(folder):
            self.folder = folder
            print("Selected folder:", os.path.abspath(self.folder))
            self.update_selection()


    def change_control(self):
        # print(self.size())
        if self.control_current:
            self.control_current.setStyleSheet("")
        if self.control_current != self.sender():
            self.control_current = self.sender()
            self.sender().setStyleSheet("background-color: gray;")
        else:
            self.control_current = None
        
    def change_select(self):
        if self.select_current is None:
            self.select_buttons[0].setStyleSheet("border: 1px solid yellow;")
            self.select_current = 0
            self.change_display()
            return 
        elif self.select_current < 0:
            return
        else:
            if self.select_buttons[self.select_current] != self.sender():
                self.select_buttons[self.select_current].setStyleSheet("")
                self.select_current = self.select_buttons.index(self.sender())
                self.sender().setStyleSheet("border: 1px solid yellow;")
                self.change_display()

    def change_display(self):


        self.scrollbar.setMaximum(len(self.ctimg[self.select_current]) - 1)
        self.scrollbar.setValue(self.display_slides[self.select_current])
        self.update_display()

    def change_slides(self):

        self.display_slides[self.select_current] = self.scrollbar.value()
        self.update_display()

    def update_display(self):
        if self.display_layout is not None:
            while self.display_layout.count() > 1:
                item = self.display_layout.takeAt(1)
                widget = item.widget()
                if widget and widget != self.scrollbar:
                    widget.deleteLater()
        img = self.ctimg[self.select_current][self.display_slides[self.select_current]]
        z = self.zoom_factor[self.select_current][self.display_slides[self.select_current]]
        if z == 1:
            h, w = img.shape
            q_image = QImage(img, w, h, QImage.Format.Format_Grayscale16)
        else:

            h, w = img.shape[0] * z, img.shape[1] * z
            new_img = cv2.resize(img, (int(w), int(h)))

            w = self.display.size().width() - 50
            h = self.display.size().height() - 50

            w = min(new_img.shape[1], w)
            h = min(new_img.shape[0], h)
            new_img = new_img[new_img.shape[0] // 2 - h // 2 : new_img.shape[0] // 2 + h // 2, \
                              new_img.shape[1] // 2 - w // 2 : new_img.shape[1] // 2 + w // 2]
            q_image = QImage(new_img.tobytes(), new_img.shape[1], new_img.shape[0], QImage.Format.Format_Grayscale16)

        pixmap = QPixmap.fromImage(q_image)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # print(pixmap.pos())
        self.display_layout.addWidget(image_label)
        # image_label.setStyleSheet("border: 1px solid red;")
        self.display_layout.update()
        self.resizeEvent(None)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            v = np.clip(self.scrollbar.value() - 1, 0, self.scrollbar.maximum())
            self.scrollbar.setValue(v)
            self.change_slides()
        elif event.key() == Qt.Key.Key_Down:
            v = np.clip(self.scrollbar.value() + 1, 0, self.scrollbar.maximum())
            self.scrollbar.setValue(v)
            self.change_slides()

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            print("Shift + Scroll detected")
            # print(self.select_current)
            # print(self.display_slides[self.select_current])
            delta = event.angleDelta().x()
            z = self.zoom_factor[self.select_current][self.display_slides[self.select_current]]
            self.zoom_factor[self.select_current][self.display_slides[self.select_current]] = np.clip(z + np.sign(delta) * 0.05, 1, 3)
            # print(self.zoom_factor[self.select_current][self.display_slides[self.select_current]])
            self.update_display()
        else:
            delta = event.angleDelta().y()  # Get the vertical scrolling delta
            # print(delta)
            v = np.clip(self.scrollbar.value() - (delta // 120), 0, self.scrollbar.maximum())
            self.scrollbar.setValue(v)
            self.change_slides()
        # if delta > 0:
        #     v = np.clip(self.scrollbar.value() - delta, 0, self.scrollbar.maximum())
        #     self.scrollbar.setValue(v)
        #     self.change_slides()
        # elif delta < 0:
            

    def update_selection(self):
        pth = os.path.abspath(self.folder)
        dir = os.listdir(pth)

        dir = [os.path.abspath(os.path.join(pth, item))
                    for item in dir if os.path.isdir(os.path.join(pth, item))]
        dir.sort()

        self.ctimg = []

        for d in dir:
            temp = []
            for f in os.listdir(d):
                try:
                    ds = dicom.dcmread(os.path.join(d, f))
                except:
                    pass
                else:
                    pixel_array = ds.pixel_array.astype(np.int16)
                    temp.append(1 - pixel_array)
            self.ctimg.append(temp)


        child_widgets = self.select.findChildren(QWidget)
        for widget in child_widgets:
            if widget.layout() is QVBoxLayout:
                widget.deleteLater()

        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        widget_layout.setSpacing(1)  
        widget_layout.setContentsMargins(7, 0, 0, 0) 

        self.select_buttons = []

        for ct_group in self.ctimg:
            if len(ct_group) <= 0:
                continue
            h, w = ct_group[0].shape
            image = QImage(bytearray(ct_group[0]), w, h, QImage.Format.Format_Grayscale16)

            button = QPushButton()
            button.setFixedWidth(120)
            button.setFixedHeight(90)
            button.setIconSize(QSize(80, 80))
            button.setIcon(QIcon(QPixmap(image)))
            widget_layout.addWidget(button)
            self.select_buttons.append(button)
            button.clicked.connect(self.change_select)


        self.select.setWidget(widget)
        self.select.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.select.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.display_slides = np.array([0] * len(self.ctimg))

        self.zoom_factor = []
        for i, ct_group in enumerate(self.ctimg):
            self.zoom_factor.append([])
            for _ in ct_group:
                self.zoom_factor[i].append(1)

        if len(self.ctimg) == 0:
            self.select_current = -1
        else: 
            self.select_current = None
            self.change_select()


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.control_current is not None:
            self.drawing_board.show()
            self.dragging = True
            self.start_pos = event.position()

    def draw_line(self, x, y):
        if self.control_current is not None and self.dragging:
            if self.drawing_layout is not None:
                print(self.drawing_layout.count())
                while self.drawing_layout.count() > 0:
                    self.drawing_layout.takeAt(0)

            w = self.drawing_board.size().width()
            h = self.drawing_board.size().height()
            drawn = np.zeros((w, h, 4)).astype(np.uint8)

            bl = bresenham_line(self.start_pos.x() - self.drawing_board.pos().x(), \
                                self.start_pos.y() - self.drawing_board.pos().y(), \
                                x - self.drawing_board.pos().x(), \
                                y - self.drawing_board.pos().y())
            # print(self.start_pos.x() - self.drawing_board.pos().x())
            # print(self.start_pos.y() - self.drawing_board.pos().y())
            # print(x - self.drawing_board.pos().x())
            # print(y - self.drawing_board.pos().y())
            for x, y in bl:
                drawn[round(x), round(y), 2] = 255
                drawn[round(x), round(y), 3] = 255

            q_image = QImage(drawn, w, h, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(q_image)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.drawing_layout.addWidget(image_label)
            self.drawing_layout.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.control_current is not None:
            # self.draw_line(event.position().x(), event.position().y())
            self.dragging = False
            self.drawing_board.show()
    
    def mouseMoveEvent(self, event):
        if self.control_current is not None and self.dragging :
            # pass
            self.draw_line(event.position().x(), event.position().y())
        else:
            print("-------------------")
            print(self.drawing_board.size())
            print(event.position())
            print(self.drawing_board.pos())

    def resizeEvent(self, event):
        if self.drawing_board is not None:
            self.drawing_board.setGeometry(self.display.pos().x(), self.display.pos().y(), \
                                       self.display.width() - 20, self.display.height())


def bresenham_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    line = []

    while True:
        line.append((x1, y1))

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return line


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


