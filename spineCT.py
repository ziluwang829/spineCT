from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QWidget, QGridLayout, QFileDialog, QHBoxLayout, QVBoxLayout, QScrollBar
from PyQt6.QtGui import QAction, QPixmap, QIcon
from PyQt6.QtCore import QSize, Qt
import numpy as np
import sys
import os

from widgets import *
from shapes import *
from ct import *

from pdb import set_trace



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # initial directory
        self.folder = "./1444796"

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

        # options: info, edit, move
        # shapes: line, circle, rect, ellipse, polygon 
        # remove: clear all shape
        self.control_current = 0
        self.control_buttons = [None]
        asset_options = ["info", "edit", "move"]
        asset_shapes = ["line", "circle", "rect", "ellipse", "polygon"]
        asset_remove = ["clear"]
        for asset in asset_options + asset_shapes + asset_remove:
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
        self.ct = self.extract_ct_and_update()
        self.display_screen.update_ct(self.ct)
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
            self.ct = self.extract_ct_and_update()
            self.display_screen.update_ct(self.ct)


    def change_control(self):
        # Update control option and signal display screen
        sender = self.control_buttons.index(self.sender())

        # If a control is selcted, un-select control
        if self.control_current != 0:
            self.control_buttons[self.control_current].setStyleSheet("")

        # If the button is same as selected, un-select control
        if self.control_current != sender:
            self.control_current = sender
            self.sender().setStyleSheet("background-color: gray;")
        else:
            self.control_current = 0

        # Send the control to the display screen
        self.display_screen.change_control(self.control_current)

        # If the sender is "clear", then un-select control
        self.control_current = 0 if self.control_current == 9 else self.control_current 

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
        ct = CTCases(pth)
        for i, d in enumerate(dir):
            ct_group = []
            for f in os.listdir(d):
                try:
                    img = CTImage(os.path.join(d, f))
                except:
                    pass
                else:
                    ct_group.append(img)
            if len(ct_group) > 0:
                ct.add(ct_group)

        # Create a widget and layout for select
        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        widget_layout.setSpacing(1)
        widget_layout.setContentsMargins(7, 0, 0, 0)

        # Add buttons to select to switch between folders
        self.select_buttons = []
        ct_sizes = ct.sizes()
        for i in range(len(ct_sizes)) :
            if ct_sizes[i] == 0:
                continue
            button = QPushButton()
            button.setFixedWidth(120)
            button.setFixedHeight(90)
            button.setIconSize(QSize(80, 80))
            button.setIcon(ct.get_QIcon(i, 0))
            button.clicked.connect(self.change_select)
            widget_layout.addWidget(button)
            self.select_buttons.append(button)
        self.select.setWidget(widget)

        # An array to remember where last displayed image
        self.select_history  = np.zeros(len(ct_sizes))
        self.select_max = ct_sizes

        # initialize display
        if len(ct_sizes) == 0:
            self.select_current = None
        else: 
            self.select_buttons[0].setStyleSheet("border: 1px solid yellow;")
            self.select_current = 0
            self.display_scrollbar.setMaximum(self.select_max[self.select_current] - 1)
            self.display_scrollbar.setValue(self.select_history[self.select_current])
            self.change_display()
                
        return ct
    

    def change_select(self):
        # if select_current is None, folder has no CT
        if self.select_current is None:
            return
        
        # Change select when button is pushed
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
        # Change the icon for select
        button = self.select_buttons[self.select_current]
        icon = self.ct.get_QIcon(self.select_current, self.display_scrollbar.value())
        button.setIcon(icon)
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