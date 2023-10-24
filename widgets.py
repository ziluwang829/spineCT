from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QWidget, QGridLayout, QFileDialog, QHBoxLayout, QVBoxLayout, QScrollBar, QStackedLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QAction, QPixmap, QIcon
from PyQt6.QtCore import QSize, Qt
import numpy as np
import sys
import time

from widgets import *
from shapes import *
from ct import *
import copy

from pdb import set_trace



class UninteractiveScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()


    def keyPressEvent(self, event):
        event.ignore()


    def wheelEvent(self, event):
        event.ignore()



class DisplayWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(DisplayWidget, self).__init__(*args, **kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 

        # Set screen and screen label
        self.screen_ = QWidget()
        self.screen_.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.screen_.setStyleSheet("background : transparent;")

        self.screen_label = QLabel(self.screen_)
        self.screen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.screen_layout = QHBoxLayout(self.screen_)
        self.screen_layout.addWidget(self.screen_label)
        self.screen_layout.setContentsMargins(0, 0, 0, 0)
        self.screen_layout.setSpacing(0)

        # Set info panel
        self.info = QWidget()
        self.info.setFixedSize(QSize(200, 200))
        self.info.move(50, 50)
        self.info.setStyleSheet("background : transparent;")

        self.info_label = QLabel(self.info)
        self.info_label.setStyleSheet("color: red; border : 1px double red;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_layout = QHBoxLayout(self.info)
        self.info_layout.addWidget(self.info_label)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(0)

        self.info_label.hide()

        # Set stacking layout and add screen and board
        self.layout = QStackedLayout(self)
        self.layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.screen_)

        # No data available for now
        self.current_control = 0
        self.current_image = None
        self.current_shape = None
        self.zoom_factors = None
        self.ct = None
        

    def update_ct(self, ct):
        if ct is None or len(ct.sizes()) <= 0:
            return
        # Set current control to default
        self.current_control = 0
        # Set current displayed image
        self.current_image = (0, 0)
        # Set all zoom factors
        self.zoom_factors = [[1 for _ in range(cts)] for cts in ct.sizes()]
        # Set all ct images
        self.ct = ct
        # Redraw first image
        self.refresh_image()


    def display_image(self, folder_index, image_index):
        if self.ct is not None:

            # Must change all colors back to blue before changing image
            if folder_index != self.current_image[0] or image_index != self.current_image[1]:
                self.current_shape = None
                ct_img_past = self.ct.get_CTImage(self.current_image[0], self.current_image[1])
                for s in ct_img_past.shapes():
                    s.change_color((0, 0, 255))

            # switch info
            if self.current_control == 1 and self.current_image is not None:
                self.display_info()

            # Set current
            self.current_image = (folder_index, image_index)

            # get img with the shapes
            ct_img = self.ct.get_CTImage(folder_index, image_index)
            gray_img = ct_img.image()
            h, w = gray_img.shape

            # Get max height
            max_h = self.size().height()
            max_w = self.size().width()

            # crop to window size
            if max_h < h:
                if h % 2 == max_h % 2:
                    crop_top = (h - max_h) // 2
                else: 
                    crop_top = (h - max_h) // 2 if h % 2 != 0 else (h - max_h) // 2 + 1
                crop_bottom = crop_top + max_h
                gray_img = gray_img[crop_top:crop_bottom, :]
                assert (gray_img.shape[0] == max_h)
            if max_w < w:
                if w % 2 == max_w % 2:
                    crop_left = (w - max_w) // 2
                else: 
                    crop_left = (w - max_w) // 2 if w % 2 != 0 else (w - max_w) // 2 + 1
                crop_right = crop_left + max_w
                gray_img = gray_img[:, crop_left:crop_right]
                assert (gray_img.shape[1] == max_w)

            # pad to window size
            pad_h = max_h - h
            pad_w = max_w - w

            if pad_h > 0:
                if h % 2 == 0:
                    pad_top = pad_h // 2
                else:
                    pad_top = pad_h // 2 if pad_h % 2 == 0 else pad_h // 2 + 1
                pad_bottom = pad_h - pad_top
                gray_img = np.pad(gray_img, ((pad_top, pad_bottom), (0, 0)), mode='constant')

            if pad_w > 0:
                if h % 2 == 0:
                    pad_left = pad_w // 2 
                else:
                    pad_left = pad_w // 2 if pad_w % 2 == 0 else pad_w // 2 + 1
                pad_right = pad_w - pad_left
                gray_img = np.pad(gray_img, ((0, 0), (pad_left, pad_right)), mode='constant')

            img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2RGB)
            h, w, _ = img.shape

            self.h_save = h
            self.w_save = w
            # draw
            p1s = []
            for s in ct_img.shapes():
                if isinstance(s, Shape):
                    img = s.draw(img, w, h)
                if isinstance(s, Line):
                    p1s.append((s.get_left(), s))

            # Get zoom factor, height, and width, then resize
            z = self.zoom_factors[self.current_image[0]][self.current_image[1]]

            img = cv2.resize(img, (int(w * z), int(h * z)))
            h, w, _ = img.shape

            # crop after resize
            if max_h < h:
                if h % 2 == max_h % 2:
                    crop_top = (h - max_h) // 2
                else: 
                    crop_top = (h - max_h) // 2 if h % 2 != 0 else (h - max_h) // 2 + 1
                crop_bottom = crop_top + max_h
                img = img[crop_top:crop_bottom, :]
                assert (img.shape[0] == max_h)
            if max_w < w:
                if w % 2 == max_w % 2:
                    crop_left = (w - max_w) // 2
                else: 
                    crop_left = (w - max_w) // 2 if w % 2 != 0 else (w - max_w) // 2 + 1
                crop_right = crop_left + max_w
                img = img[:, crop_left:crop_right]
                assert (img.shape[1] == max_w)

            h, w, _ = img.shape

            # for labeling the length of the line
            # Lines only
            # scuffed
            for p1 in p1s:
                p, s = p1
                print(p)
                p, a = p
                x, y = self.inverse_adjusted_point(p)
                img2 = np.zeros_like(img)
                img2 = cv2.putText(img2, str(s), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  
                   (255, 0, 0), 1, cv2.LINE_AA) 
                print(np.degrees(a))
                M = cv2.getRotationMatrix2D((x, y), np.degrees(a) + 90, 1)
                img2 = cv2.warpAffine(img2, M, (img2.shape[1], img2.shape[0]))
                red_pixels_mask = (img2[:, :, 0] > 10)
                img[red_pixels_mask, 0] = img2[red_pixels_mask, 0]
                img[red_pixels_mask, 1] = 0
                img[red_pixels_mask, 2] = 0
                
            q_image = QImage(img.tobytes(), w, h, 3 * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.screen_label.setPixmap(pixmap)
        
        
    def refresh_image(self):
        self.display_image(self.current_image[0], self.current_image[1])
        

    # can only display file name for now.
    def display_info(self):
        if self.current_image is not None:
            i, j = self.current_image
            self.info_label.show()
            self.info_label.setText(str(self.ct.get_CTImage(i, j)))

    # when buttons on top are clicked
    def change_control(self, control):
        if self.current_control == 1 and control != 1:
            self.info_label.hide()
        self.current_control = control
        self.current_shape = None
        if self.current_control == 1 and self.current_image is not None:
            self.display_info()
        if self.current_control == 9 and self.current_image is not None:
            i, j = self.current_image
            ct_img = self.ct.get_CTImage(i, j)
            ct_img.empty()
            self.refresh_image()
            self.current_control = 0

    # zoom in/out
    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            delta = event.angleDelta().x()
            i, j = self.current_image
            z = self.zoom_factors[i][j]
            self.zoom_factors[i][j] = np.clip(z + np.sign(delta) * 0.05, 1, 3)
            self.refresh_image()
        else:
            event.ignore()

    # from (x,y) in plot coordinates from screen
    # to Cartesian coordinate with (0, 0) being center of ct image
    def adjusted_point(self, x, y):
        max_h = self.size().height()
        max_w = self.size().width()
        z = self.zoom_factors[self.current_image[0]][self.current_image[1]]
        p = (x - max_w // 2, y - max_h // 2)
        r = np.sqrt(p[0]**2 + p[1]**2)
        theta = -1 * np.arctan2(p[1], p[0]) 
        p = (int((r / z) * np.cos(theta)), -1 * int((r / z) * np.sin(theta)))
        return p

    # inverse of above
    # is the math correct? i can't confirm
    def inverse_adjusted_point(self, p):
        max_h = self.size().height()
        max_w = self.size().width()
        z = self.zoom_factors[self.current_image[0]][self.current_image[1]]
        r = np.sqrt(p[0] ** 2 + p[1] ** 2)
        theta = -1 * np.arctan2(p[1], p[0])
        x = int((r * z) * np.cos(theta) + max_w // 2)
        y = int((-1 * (r * z) * np.sin(theta)) + max_h // 2)
        return x, y

    # find the Shapethat is located in p
    def find_shape(self, p):
        if self.current_image is None:
            return None
        else:
            ct_img = self.ct.get_CTImage(self.current_image[0], self.current_image[1])
            shapes = ct_img.shapes()
            img = np.zeros((self.h_save, self.w_save, 3))
            h, w, _ = img.shape
            for s in shapes:
                if isinstance(s, Shape) and s.click(img, w, h, p):
                    return s
            return None

    # mouse press event to start drawing
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.current_control is not None:
            if self.current_control == 1:
                self.display_info()
            elif self.current_control in [4, 5, 6, 7]:
                self.start_pos = event.position()
                self.dragging = True
            elif self.current_control == 3:
                p = self.adjusted_point(event.position().x(), event.position().y())
                self.current_shape = self.find_shape(p)
                if self.current_shape is not None:
                    self.current_shape_copy = copy.deepcopy(self.current_shape)
                    self.start_pos = event.position()
                    self.dragging = True
            elif self.current_control == 8:
                if self.current_shape is None:
                    p = self.adjusted_point(event.position().x(), event.position().y())
                    self.current_shape = Polygon([p])
                    ct_img = self.ct.get_CTImage(self.current_image[0], self.current_image[1])
                    ct_img.attach(self.current_shape)
                else:
                    ps = self.current_shape.get_points()
                    p = self.adjusted_point(event.position().x(), event.position().y())
                    ps.append(p)
                    self.current_shape.change_points(ps)
                self.refresh_image()
        if event.button() == Qt.MouseButton.RightButton and self.current_control == 8 and self.current_shape is not None:
            self.current_shape.change_color((0, 0, 255))
            self.current_shape = None
            self.refresh_image()


    # handle drag when drawing
    def mouseMoveEvent(self, event):
        if self.current_control is None:
            return
        elif self.current_control in [4, 5, 6, 7] and self.dragging:

            p0 = self.adjusted_point(self.start_pos.x(), self.start_pos.y())
            p1 = self.adjusted_point(event.position().x(), event.position().y())

            if self.current_shape is None:
                if self.current_control == 4:
                    self.current_shape = Line(p0, p1)
                elif self.current_control == 5:
                    self.current_shape = Circle(p0, int(np.linalg.norm(np.array(p1) - np.array(p0))))
                elif self.current_control == 6:
                    self.current_shape = Rect(p0, p1)
                elif self.current_control == 7:
                    self.current_shape = Ellipse(p0, p1)
                ct_img = self.ct.get_CTImage(self.current_image[0], self.current_image[1])
                ct_img.attach(self.current_shape)
            else:
                if self.current_control == 4:
                    self.current_shape.change_points(p0, p1)
                elif self.current_control == 5:
                    self.current_shape.change_point_radius(p0, int(np.linalg.norm(np.array(p1) - np.array(p0))))
                elif self.current_control == 6:
                    self.current_shape.change_points(p0, p1)
                elif self.current_control == 7:
                    self.current_shape.change_points(p0, p1)
        elif self.current_control == 3 and self.dragging:
            # is a deep copy, not drawn on board
            # make adjust ment to current_shape
            p0 = self.adjusted_point(self.start_pos.x(), self.start_pos.y())
            p1 = self.adjusted_point(event.position().x(), event.position().y())
            p_dff = (p1[0] - p0[0], p1[1] - p0[1])
            
            if isinstance(self.current_shape, Line):
                p0, p1 = self.current_shape_copy.get_points()
                p0 = (p0[0] + p_dff[0], p0[1] + p_dff[1])
                p1 = (p1[0] + p_dff[0], p1[1] + p_dff[1])
                self.current_shape.change_points(p0, p1)
                self.current_shape.change_color((0, 255, 255))
            if isinstance(self.current_shape, Circle):
                p0, r = self.current_shape_copy.get_point_radius()
                p0 = (p0[0] + p_dff[0], p0[1] + p_dff[1])
                self.current_shape.change_point_radius(p0, r)
                self.current_shape.change_color((0, 255, 255))
            if isinstance(self.current_shape, Rect):
                p0, p1 = self.current_shape_copy.get_points()
                p0 = (p0[0] + p_dff[0], p0[1] + p_dff[1])
                p1 = (p1[0] + p_dff[0], p1[1] + p_dff[1])
                self.current_shape.change_points(p0, p1)
                self.current_shape.change_color((0, 255, 255))
            if isinstance(self.current_shape, Ellipse):
                p0, p1 = self.current_shape_copy.get_points()
                p0 = (p0[0] + p_dff[0], p0[1] + p_dff[1])
                p1 = (p1[0] + p_dff[0], p1[1] + p_dff[1])
                self.current_shape.change_points(p0, p1)
                self.current_shape.change_color((0, 255, 255))
            if isinstance(self.current_shape, Polygon):
                ps = self.current_shape_copy.get_points()
                ps = [[p[0] + p_dff[0], p[1] + p_dff[1]] for p in ps]
                self.current_shape.change_points(ps)
                self.current_shape.change_color((0, 255, 255))
        self.refresh_image()

    # finish drawing, change  to blue
    def mouseReleaseEvent(self, event):
        if self.current_control is None:
            return
        if event.button() == Qt.MouseButton.LeftButton and self.current_control in [4, 5, 6, 7]:
            self.dragging = False
            if self.current_shape is not None:
                self.current_shape.change_color((0, 0, 255))
                self.current_shape = None
                self.refresh_image()
        elif event.button() == Qt.MouseButton.LeftButton and self.current_control == 3:
            self.dragging = False
            if self.current_shape is not None:
                self.current_shape.change_color((0, 0, 255))
                self.current_shape = None
                self.refresh_image()


    def resizeEvent(self, event):
        if self.ct is not None:
            self.refresh_image()

