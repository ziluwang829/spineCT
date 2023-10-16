from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QWidget, QGridLayout, QFileDialog, QHBoxLayout, QVBoxLayout, \
    QScrollArea, QScrollBar, QLabel, QSizePolicy, QStackedLayout
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QPixmap, QIcon, QImage
import pydicom as dicom
import numpy as np
import cv2
import sys
import os
from pdb import set_trace



class UninteractiveScrollArea(QScrollArea):
    def __init__(self):
        super().__init__()


    def keyPressEvent(self, event):
        event.ignore()


    def wheelEvent(self, event):
        event.ignore()



class Shape():
    # color could be 0: Red, 1: Green, 2: Blue, 3: Yellow
    def __init__(self, ndarray, color):
        self.ndarray = ndarray
        self.color = color

    # color could be 0: Red, 1: Green, 2: Blue, 3: Yellow
    def change_color(self, color):
        self.color = color


    def draw_on_array(self, ndarray):
        pass


    def on(self, x, y):
        pass


    def info(self):
        pass



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
        self.info.setStyleSheet("background : transparent; color: red; border: 1px double red")

        self.info_label = QLabel(self.info)
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_layout = QHBoxLayout(self.info)
        self.info_layout.addWidget(self.info_label)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(0)

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


    def update_images(self, ct_img):
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
    def display_image(self, folder_index, image_index, drawn = True):
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
        
        
    def refresh_image(self):
        self.display_image(self.current_image[0], self.current_image[1])


    def display_info(self, position):
        pass


    def change_control(self, control):
        self.current_control = control
        if self.current_control == 5 and self.current_image is not None:
            if self.current_image in self.drawn_shapes.keys():
                self.drawn_shapes.pop(self.current_image)
                self.refresh_image()


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
        if self.all_images is not None:
            self.refresh_images()
























class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # initial directory
        self.folder = "./1444306"

        # Configure Window sizes
        self.setWindowTitle("Spine CT")
        self.resize(QSize(1280, 720))
        self.setMinimumSize(QSize(1280, 750))
        self.setMaximumSize(QSize(1920, 1080))       

        # Menu bar option for changing folders
        menubar = self.menuBar()
        action = QAction('Open New Folder', self)
        action.triggered.connect(self.new_dir)
        file_menu = menubar.addMenu('File')
        file_menu.addAction(action)

        # Overall layout of the application
        main_widget = QWidget()
        main_layout = QGridLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Control options and buttons
        self.control = QWidget()
        self.control.setFixedHeight(100)
        control_layout = QHBoxLayout(self.control)
        control_layout.setDirection(QVBoxLayout.Direction.LeftToRight)
        # Draw line, draw circle, draw box, get info, 
        # move drawings, and clear display
        self.control_current = None
        self.control_buttons = []
        asset_files = ["info", "move", "line", "circle", "box", "clear"]
        for asset in asset_files:
            button = QPushButton()
            button.setIcon(QIcon("assets/" + asset + ".png"))
            button.setIconSize(QSize(70,70))
            button.setFixedSize(80, 80)
            button.clicked.connect(self.change_control)
            self.control_buttons.append(button)
            control_layout.addWidget(button)
        control_layout.addStretch(1)

        # Selecting and moving between sub folders
        self.select = UninteractiveScrollArea()
        self.select.setFixedWidth(150)
        self.select.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.select.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # A display widget for showing CT images and drawings
        self.display = QWidget()
        self.display.setStyleSheet("background-color: black;")
        self.display.setMinimumWidth(1000)
        self.display.setMinimumHeight(600)
        self.display_layout = QVBoxLayout(self.display)
        self.display_layout.setDirection(QVBoxLayout.Direction.RightToLeft)
        self.display_layout.setContentsMargins(0, 0, 0, 0)
        self.display_layout.setSpacing(0)
        self.display_scrollbar = QScrollBar()
        self.display_scrollbar.setValue(0)
        self.display_scrollbar.setMinimum(0)
        self.display_scrollbar.setFixedWidth(20)
        self.display_scrollbar.setPageStep(1)
        self.display_scrollbar.valueChanged.connect(self.change_scrollvalue)
        self.display_layout.addWidget(self.display_scrollbar)
        self.display_screen = DisplayWidget()
        ct_img = self.extract_ct_and_update()
        self.display_screen.update_images(ct_img)
        self.display_layout.addWidget(self.display_screen)

        # set the main layout
        main_layout.addWidget(self.control, 0, 0, 1, 10)
        main_layout.addWidget(self.select, 1, 0, 9, 1)
        main_layout.addWidget(self.display, 1, 1, 9, 9)
    
 
    def new_dir(self):
        # Open a dialog and open a new directory to analyze
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.folder)
        if folder and os.path.abspath(self.folder) != os.path.abspath(folder):
            self.folder = folder
            print("Selected folder:", os.path.abspath(self.folder))
            ct_img = self.extract_ct_and_update()
            self.display_screen.update_images(ct_img)


    def change_control(self):
        # Update control option and signal display screen
        if self.control_current is not None:
            self.control_current.setStyleSheet("")
        if self.control_current != self.sender():
            self.control_current = self.sender()
            self.sender().setStyleSheet("background-color: gray;")
        else:
            self.control_current = None

        if self.control_current is not None:
            self.display_screen.change_control(self.control_buttons.index(self.control_current))
        else:
            self.display_screen.change_control(None)

    def extract_ct_and_update(self):
        # remove all widgets from self.select
        child_widgets = self.select.findChildren(QWidget)
        for widget in child_widgets:
            if widget.layout() is QVBoxLayout:
                widget.deleteLater()

        # From the selected directory, gather all folders
        pth = os.path.abspath(self.folder)
        dir = os.listdir(pth)
        dir = [os.path.abspath(os.path.join(pth, item))
                    for item in dir if os.path.isdir(os.path.join(pth, item))]
        dir.sort()

        # Open folders and find CT. If folder is empty, omit.
        ct_img = []
        for d in dir:
            sub_d = []
            for f in os.listdir(d):
                try:
                    ds = dicom.dcmread(os.path.join(d, f))
                except:
                    pass
                else:
                    array = ds.pixel_array.astype(np.int16)
                    array = cv2.normalize(array, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
                    sub_d.append(array)
            if len(sub_d) > 0:
                ct_img.append(sub_d)

        # Create a widget and layout for select
        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        widget_layout.setSpacing(1)
        widget_layout.setContentsMargins(7, 0, 0, 0)

        # Add buttons to select to switch between folders
        self.select_buttons = []
        for ct_group in ct_img:
            if len(ct_group) == 0:
                continue
            h, w = ct_group[0].shape
            image = QImage(bytearray(ct_group[0]), w, h, QImage.Format.Format_Grayscale8)
            button = QPushButton()
            button.setFixedWidth(120)
            button.setFixedHeight(90)
            button.setIconSize(QSize(80, 80))
            button.setIcon(QIcon(QPixmap(image)))
            button.clicked.connect(self.change_select)
            widget_layout.addWidget(button)
            self.select_buttons.append(button)
        self.select.setWidget(widget)

        # An array to remember where last displayed image
        self.select_history  = np.array([0] * len(ct_img))
        self.select_max = [len(ct_group) for ct_group in ct_img]
        if len(ct_img) == 0:
            self.select_current = None
        else: 
            self.select_current = -1
            self.change_select()
                
        return ct_img
    

    def change_select(self):
        # -1 is for initializing
        if self.select_current < 0 :
            self.select_buttons[0].setStyleSheet("border: 1px solid yellow;")
            self.select_current = 0
            self.display_scrollbar.setMaximum(self.select_max[self.select_current] - 1)
            self.display_scrollbar.setValue(self.select_history[self.select_current])
            self.change_display()
        # In the case that a button triggers this function
        elif self.select_buttons[self.select_current] != self.sender():
            self.select_buttons[self.select_current].setStyleSheet("")
            self.select_current = self.select_buttons.index(self.sender())
            self.sender().setStyleSheet("border: 1px solid yellow;")
            self.display_scrollbar.setMaximum(self.select_max[self.select_current] - 1)
            self.display_scrollbar.setValue(self.select_history[self.select_current])
            self.change_display()


    def change_scrollvalue(self):
        # Triggers when scroll wheel value is changed
        self.select_history[self.select_current] = self.display_scrollbar.value()
        self.change_display()


    def change_display(self):
        # Calls a function in DisplayWidget to change the display
        self.display_screen.display_image(self.select_current, self.display_scrollbar.value())


    def keyPressEvent(self, event):
        # Handles even when UP or DOWN keys are pressed
        if event.key() == Qt.Key.Key_Up:
            v = np.clip(self.display_scrollbar.value() - 1, 0, \
                        self.display_scrollbar.maximum())
            self.display_scrollbar.setValue(v)
            self.change_scrollvalue()
        elif event.key() == Qt.Key.Key_Down:
            v = np.clip(self.display_scrollbar.value() + 1, 0, \
                        self.display_scrollbar.maximum())
            self.display_scrollbar.setValue(v)
            self.change_scrollvalue()


    def wheelEvent(self, event):
        # Handles mouse wheel events
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ShiftModifier:
            event.ignore()
        else:
            delta = event.angleDelta().y()
            v = np.clip(self.display_scrollbar.value() - np.sign(delta), 0, \
                        self.display_scrollbar.maximum())
            self.display_scrollbar.setValue(v)
            self.change_scrollvalue()



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())