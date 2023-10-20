from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QWidget, QGridLayout, QFileDialog, QHBoxLayout, QVBoxLayout, QScrollBar
from PyQt6.QtGui import QAction, QPixmap, QIcon
from PyQt6.QtCore import QSize, Qt
import numpy as np
import sys
import os



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

        # Set drawing board and drawing board label
        self.board = QWidget()
        self.board.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.board.setStyleSheet("background : transparent;")

        self.board_label = QLabel(self.board)
        self.board_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.board_layout = QHBoxLayout(self.board)
        self.board_layout.addWidget(self.board_label)
        self.board_layout.setContentsMargins(0, 0, 0, 0)
        self.board_layout.setSpacing(0)

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
        self.layout.addWidget(self.board)
        self.layout.addWidget(self.screen_)

        # No data available for now
        self.current_control = None
        self.current_image = None
        self.all_images = None
        self.zoom_factors = None
        self.drawn_shapes = None
        self.save_draw = None


    def update_ct(self, ct):
        if ct_img is None or len(ct_img) <= 0:
            return
        # Set current displayed image
        self.current_image = (0, 0)
        # Set all ct images
        self.all_images = ct_img
        # Set all zoom factors
        self.zoom_factors = [[1 for ct in ct_group] for ct_group in ct_img]
        # Set empty dict, key is (int, int) to get a list 
        # of drawn shapes. 
        self.drawn_shapes = {}
        # Redraw first image
        self.refresh_image()
        # A reference to a Shape object that will be saved
        self.save_draw = None


    # TODO
    def display_image(self, folder_index, image_index, reset_color = True):
        if self.all_images is not None:
            # Set current
            self.current_image = (folder_index, image_index)

            # convert image from gray to rbg
            img = self.all_images[folder_index][image_index]
            rgb_image = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

            # Get zoom factor, height, and width
            z = self.zoom_factors[self.current_image[0]][self.current_image[1]]
            h, w, _ = rgb_image.shape

            if self.current_image in self.drawn_shapes.keys() and self.drawn_shapes[self.current_image] is not None:
                drawn = self.drawn_shapes[self.current_image]
                for d in drawn:
                    rgb_image[np.where(d > 0)] = np.array([0, 0, 255])

            if z != 1:
                rgb_image = cv2.resize(rgb_image, (int(w * z), int(h * z)))

                w = min(rgb_image.shape[1], self.size().width())
                h = min(rgb_image.shape[0], self.size().height())

                rgb_image = rgb_image[rgb_image.shape[0] // 2 - h // 2 : rgb_image.shape[0] // 2 + h // 2, \
                              rgb_image.shape[1] // 2 - w // 2 : rgb_image.shape[1] // 2 + w // 2]
                
                h, w, _ = rgb_image.shape

            q_image = QImage(rgb_image.tobytes(), w, h, 3 * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.screen_label.setPixmap(pixmap)
        
        
    def refresh_image(self, reset_color = True):
        self.display_image(self.current_image[0], self.current_image[1], reset_color = reset_color)


    def display_info(self, position):
        if self.current_image is not None:
            if self.current_image in self.drawn_shapes.keys():
                for s in self.drawn_shapes[self.current_image]:
                    if s.on(position):
                        s.change_color(0)
                        self.info_label.show()
                        self.info_label.setText(s.info())
                        break
                self.refresh_image(reset_color = False)


    def change_control(self, control):
        if self.current_control == 0 and control != 0:
            self.info_label.hide()
        self.current_control = control
        if self.current_control == 5 and self.current_image is not None:
            if self.current_image in self.drawn_shapes.keys():
                self.drawn_shapes.pop(self.current_image)
                self.refresh_image()
            self.current_control = 0
            # make sure that when clear is entered, control returns to 0 at end.


    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            delta = event.angleDelta().x()
            i, j = self.current_image
            z = self.zoom_factors[i][j]
            self.zoom_factors[i][j] = np.clip(z + np.sign(delta) * 0.05, 1, 3)
            self.refresh_image(reset_color = False)
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
        if self.all_images is not None:
            self.refresh_image(reset_color = False)

