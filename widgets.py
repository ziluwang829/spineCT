from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QWidget, QGridLayout, QFileDialog, QHBoxLayout, QVBoxLayout, QScrollBar, QStackedLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QAction, QPixmap, QIcon
from PyQt6.QtCore import QSize, Qt
import numpy as np
import sys
import os

from widgets import *
from shapes import *
from ct import *

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
            # TODO Must change all colors back to blue before changing image


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
            # Get zoom factor, height, and width
            z = self.zoom_factors[self.current_image[0]][self.current_image[1]]
            h, w, _ = img.shape

            if z != 1:
                img = cv2.resize(img, (int(w * z), int(h * z)))

                w = min(img.shape[1], self.size().width())
                h = min(img.shape[0], self.size().height())

                img = img[img.shape[0] // 2 - h // 2 : img.shape[0] // 2 + h // 2, \
                              img.shape[1] // 2 - w // 2 : img.shape[1] // 2 + w // 2]
                
                h, w, _ = img.shape

            q_image = QImage(img.tobytes(), w, h, 3 * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.screen_label.setPixmap(pixmap)
        
        
    def refresh_image(self):
        self.display_image(self.current_image[0], self.current_image[1])
        

    def display_info(self):
        if self.current_image is not None:
            i, j = self.current_image
            self.info_label.show()
            self.info_label.setText(str(self.ct.get_CTImage(i, j)))


    def change_control(self, control):
        if self.current_control == 1 and control != 1:
            self.info_label.hide()
        self.current_control = control
        if self.current_control == 1 and self.current_image is not None:
            self.display_info()
        if self.current_control == 9 and self.current_image is not None:
            i, j = self.current_image
            ct_img = self.ct.get_CTImage(i, j)
            ct_img.empty()
            self.refresh_image()
            self.current_control = 0


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


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.current_control is not None:
            self.start_pos = event.position()
            if self.current_control == 0:
                self.display_info(event.position())
            elif self.current_control == 1:
                self.dragging = True
            elif self.current_control in [2, 3, 4]:
                self.dragging = True





    def mouseMoveEvent(self, event):
        if self.current_control is not None and self.current_control in [2, 3, 4] and self.dragging:
            w = self.size().width()
            h = self.size().height()

            p0 = (int(self.start_pos.x()), int(self.start_pos.y()))
            p1 = (int(event.position().x()), int(event.position().y()))
            draw = np.zeros((h, w, 3)).astype(np.uint8)
            if self.current_control == 2:
                draw = cv2.line(draw, p0, p1, (0, 255, 0), thickness = 1)
            elif self.current_control == 3:
                p0_np = np.array(p0)
                p1_np = np.array(p1)
                r = np.linalg.norm(p0_np - p1_np)
                draw = cv2.circle(draw, p0, int(r), (0, 255, 0), thickness = 1)
            elif self.current_control == 4:
                draw = cv2.rectangle(draw, p0, p1, (0, 255, 0), thickness = 1)
            else:
                return
            alpha = np.clip(draw.sum(axis = 2), 0, 255)
            alpha = alpha[..., np.newaxis]
            draw = np.dstack((draw, alpha))
            draw = np.squeeze(draw)
            draw = draw.astype(np.uint8)
            q_image = QImage(draw.tobytes(), w, h, 4 * w, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(q_image)
            self.board_label.setPixmap(pixmap)
            self.save_draw = np.clip(draw[:, :, :3].sum(axis = 2), 0, 255)


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.current_control is not None and self.current_control in [2, 3, 4]:
            self.dragging = False
            if self.save_draw is not None:
                w = self.size().width() // 2
                h = self.size().height() // 2
                w = w - (self.screen_label.pixmap().size().width() // 2)
                h = h - (self.screen_label.pixmap().size().height() // 2)
                try:
                    drawing = self.save_draw[h:h + self.screen_label.pixmap().size().height(), \
                                             w:w + self.screen_label.pixmap().size().width()]
                except:
                    set_trace()
                    return
                if self.current_image not in self.drawn_shapes.keys():
                    self.drawn_shapes[self.current_image] = [drawing]
                else:
                    drawn = self.drawn_shapes[self.current_image]
                    drawn.append(drawing)
                    self.drawn_shapes[self.current_image] = drawn
                self.board_label.setPixmap(QPixmap()) 
                self.refresh_image()


    def resizeEvent(self, event):
        if self.ct is not None:
            self.refresh_image()

