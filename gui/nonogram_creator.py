# Nonogram creator dialog with image to nonogram converter and uniqueness check
# Author: Fabian Kraus

from PyQt5.QtWidgets import (QDialog,  QVBoxLayout, QHBoxLayout, QFrame,
                            QLabel, QPushButton, QRadioButton, QButtonGroup,
                            QSpinBox, QDoubleSpinBox, QFileDialog,
                            QSizePolicy)
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

import cv2

from .common import Nonogram
from .handlers.solution_handler import SolutionHandler

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

class NonogramCreator(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup default empty nonogram
        self.width_: int = 15
        self.height_: int = 15
        self.grid: np.ndarray = np.full((self.height_, self.width_), 255, dtype=np.uint8)
        
        # Setup default nonogram creation parameters
        self.bwratio: float = 0.6
        self.pxcorr: float = 0.8
        self.threshold: int = 100
        self.im_file_path: str = ""
        self.success: bool = True
        self.timeout: float = 1.0

        # Setup the window and layout
        self.setWindowTitle("gramcracker Nonogram Generator")
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout = QHBoxLayout(self)

        left_frame = QFrame()
        left_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        left_frame.setFixedWidth(300)

        right_frame = QFrame()
        right_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)

        # Set up the left frame layout
        left_layout = QVBoxLayout(left_frame)

        # Nonogram size section
        dimensions_label = QLabel("Nonogram Size")
        dimensions_label.setStyleSheet("font-size: 12pt;")
        left_layout.addWidget(dimensions_label)

        # Add frame for width
        width_frame = QFrame()
        width_layout = QHBoxLayout(width_frame)
        width_label = QLabel("Width:")
        self.width_sb = QSpinBox()
        self.width_sb.setRange(1, 1024)
        self.width_sb.setValue(self.width_)
        self.width_sb.setSingleStep(5)
        self.width_sb.valueChanged.connect(self._on_set_width)
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_sb)
        left_layout.addWidget(width_frame)

        # Add frame for height
        height_frame = QFrame()
        height_layout = QHBoxLayout(height_frame)
        height_label = QLabel("Height:")
        self.height_sb = QSpinBox()
        self.height_sb.setRange(1, 1024)
        self.height_sb.setValue(self.height_)
        self.height_sb.setSingleStep(5)
        self.height_sb.valueChanged.connect(self._on_set_height)
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_sb)
        left_layout.addWidget(height_frame)

        # Add separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(separator1)

        # Image selection section
        image_label = QLabel("What should the Nonogram show?")
        image_label.setStyleSheet("font-size: 12pt;")
        left_layout.addWidget(image_label)

        options = [
            ("Nothing (Empty)", "empty"),
            ("Random Noise", "random"),
            ("Load Image", "image")
        ]

        # Radio buttons for image source
        self.selected_option_var = "empty"  # Tracks the selected option

        radio_group = QButtonGroup()

        for text, value in options:
            radio = QRadioButton(text)
            radio.value = value

            radio_group.addButton(radio)
            left_layout.addWidget(radio)

            if value == "empty":
                radio.setChecked(True)

            if value == "random":
                # Add widgets for random noise generator parameters
                bwratio_frame = QFrame()
                bwratio_layout = QHBoxLayout(bwratio_frame)
                bwratio_label = QLabel("White ratio:")
                self.bwratio_sb = QDoubleSpinBox()
                self.bwratio_sb.setRange(0.0, 1.0)
                self.bwratio_sb.setValue(self.bwratio)
                self.bwratio_sb.setSingleStep(0.1)
                self.bwratio_sb.setDecimals(2)
                self.bwratio_sb.setEnabled(False)
                self.bwratio_sb.valueChanged.connect(self._on_set_bwratio)
                bwratio_layout.addWidget(bwratio_label)
                bwratio_layout.addWidget(self.bwratio_sb)
                left_layout.addWidget(bwratio_frame)

                pxcorr_frame = QFrame()
                pxcorr_layout = QHBoxLayout(pxcorr_frame)
                pxcorr_label = QLabel("Pixel correlation:")
                self.pxcorr_sb = QDoubleSpinBox()
                self.pxcorr_sb.setRange(0.0, 1.0)
                self.pxcorr_sb.setValue(self.pxcorr)
                self.pxcorr_sb.setSingleStep(0.1)
                self.pxcorr_sb.setDecimals(2)
                self.pxcorr_sb.setEnabled(False)
                self.pxcorr_sb.valueChanged.connect(self._on_set_pxcorr)
                pxcorr_layout.addWidget(pxcorr_label)
                pxcorr_layout.addWidget(self.pxcorr_sb)
                left_layout.addWidget(pxcorr_frame)

            if value == "image":
                # Add file selection button
                file_select_frame = QFrame()
                file_select_layout = QHBoxLayout(file_select_frame)
                self.file_select_bt = QPushButton("Select image file")
                self.file_select_bt.setEnabled(False)  # Initially disabled
                self.file_select_bt.clicked.connect(self._on_select_image_file)
                file_select_layout.addWidget(self.file_select_bt)
                left_layout.addWidget(file_select_frame)

                # Add threshold control
                threshold_frame = QFrame()
                threshold_layout = QHBoxLayout(threshold_frame)
                threshold_label = QLabel("Brightness Threshold:")
                self.threshold_sb = QSpinBox()
                self.threshold_sb.setRange(0, 255)
                self.threshold_sb.setValue(self.threshold)
                self.threshold_sb.setEnabled(False)  # Initially disabled
                self.threshold_sb.setSingleStep(10)
                self.threshold_sb.valueChanged.connect(self._on_set_threshold)
                threshold_layout.addWidget(threshold_label)
                threshold_layout.addWidget(self.threshold_sb)
                left_layout.addWidget(threshold_frame)

            # Connect radio button to update UI based on selection
            radio.toggled.connect(lambda checked, v=value: self._on_option_select(checked, v))

        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(separator2)

        # Uniqueness section
        uniqueness_label = QLabel("Nonogram Uniqueness")
        uniqueness_label.setStyleSheet("font-size: 12pt;")
        left_layout.addWidget(uniqueness_label)

        # Check uniqueness button and timeout
        check_frame = QFrame()
        check_layout = QHBoxLayout(check_frame)
        check_button = QPushButton("Check")
        check_button.clicked.connect(self._check_uniqueness)

        timeout_label = QLabel("Timeout [sec]:")
        self.timeout_sb = QSpinBox()
        self.timeout_sb.setRange(1, 10000)
        self.timeout_sb.setValue(1)
        self.timeout_sb.setSingleStep(10)
        self.timeout_sb.valueChanged.connect(self._on_set_timeout)
        check_layout.addWidget(check_button)
        check_layout.addWidget(timeout_label)
        check_layout.addWidget(self.timeout_sb)
        left_layout.addWidget(check_frame)

        # Uniqueness label (changed in _check_uniqueness to show output)
        self.uniqueness_label = QLabel("   ✓ Nonogram is unique")
        self.uniqueness_label.setStyleSheet("color: green; font-size: 11px;")
        left_layout.addWidget(self.uniqueness_label)

        # Add separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.HLine)
        separator3.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(separator3)

        # Buttons at the bottom
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)

        reload_button = QPushButton("Reload")
        reload_button.clicked.connect(self.reload)

        invert_button = QPushButton("Invert")
        invert_button.clicked.connect(self._invert)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._on_ok)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(reload_button)
        button_layout.addWidget(invert_button)
        button_layout.addWidget(self.ok_button)

        left_layout.addWidget(button_frame, stretch=0, alignment=Qt.AlignBottom)

        # Set up the right frame with the matplotlib canvas
        right_layout = QVBoxLayout(right_frame)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.figure.tight_layout()
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes.imshow(self.grid, 'gray', vmin=0, vmax=255)
        self.canvas = FigureCanvasQTAgg(self.figure)
        right_layout.addWidget(self.canvas)

        # Connect signals for key handling
        self.installEventFilter(self)

    def reload(self):
        """Re-generate the image, then draw it"""
        opt_str = self.selected_option_var
        if opt_str == "empty":
            # generate white image
            self.grid = np.full((self.height_, self.width_), 255, dtype=np.uint8)
        
        elif opt_str == "random":
            # generate random boolean matrix
            self.grid = np.random.choice([0, 255], size=(self.height_, self.width_), p=[1 - self.bwratio, self.bwratio]).astype(np.uint8)

            # correlate neighboring values in matrix
            for i in range(self.height_):
                for j in range(self.width_):
                    if np.random.rand() < self.pxcorr:
                        # Check neighboring cells
                        neighbors = []
                        if i > 0:
                            neighbors.append(self.grid[i-1, j])
                        if j > 0:
                            neighbors.append(self.grid[i, j-1])
                        if i < self.height_ - 1:
                            neighbors.append(self.grid[i+1, j])
                        if j < self.width_ - 1:
                            neighbors.append(self.grid[i, j+1])

                        # If there are any neighbors, set the current cell to the majority value
                        if neighbors:
                            self.grid[i, j] = max(set(neighbors), key=neighbors.count)

        elif opt_str == "image" and hasattr(self, 'im_original'):
            # Resize the image to a lower resolution
            im_scaled = cv2.resize(self.im_original, (self.width_, self.height_), interpolation=cv2.INTER_AREA)

            # Apply a binary threshold to the image
            _, self.grid = cv2.threshold(im_scaled, self.threshold, 255, cv2.THRESH_BINARY)

        self.update_plot()
        self.uniqueness_label.setText("")

    def update_plot(self):
        """Re-draw the preview image"""
        self.axes.clear()
        
        grid_width = self.grid.shape[1]
        grid_height = self.grid.shape[0]
        extent = (0.0, grid_width, grid_height, 0.0)

        # Draw background if available
        if self.selected_option_var == "image" and hasattr(self, 'im_original'):
            #Stretch background to match grid aspect ratio
            self.axes.imshow(self.im_original, cmap='gray', vmin=0, vmax=255,
                            aspect='auto', extent=extent, zorder=1)
            for i in range(self.grid.shape[0] + 1):
                self.axes.axhline(i, color='gray', linewidth=0.5)
            for j in range(self.grid.shape[1] + 1):
                self.axes.axvline(j, color='gray', linewidth=0.5)
            
        rgba_image = self._convert_to_rgba(self.grid,  self.selected_option_var == "image" and hasattr(self, 'im_original'))
        # Display the RGBA image
        self.axes.imshow(rgba_image, aspect='equal', zorder=2, extent=extent)
        self.axes.set_xlim(0, self.grid.shape[1])
        self.axes.set_ylim(self.grid.shape[0], 0)
        self.axes.set_aspect('equal')
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        plt.tight_layout()
        self.canvas.draw()

    def _convert_to_rgba(self, grid, bg):
        """Convert a binary grid to RGBA format where white pixels are transparent"""
        import numpy as np

        # Create an empty RGBA image (4 channels)
        height, width = grid.shape
        rgba = np.zeros((height, width, 4), dtype=np.uint8)

        # Set colors based on grid values
        black = np.array([150 if bg else 0, 0, 0, 140 if bg else 255])
        transparent = np.array([0, 0, 0, 0]) 

        # Create masks for black and white pixels
        black_mask = (grid == 0)
        white_mask = (grid == 255)

        # Apply colors
        rgba[black_mask] = black
        rgba[white_mask] = transparent

        return rgba
    
    def _check_uniqueness(self):
        """Run the nonogram solver and see if it would be unique"""
        # Convert grid to nonogram, then solve it to check uniqueness
        nonogram = Nonogram()
        nonogram.init_from_grid(self.grid != 255)
        soln_handler = SolutionHandler()
        soln_handler.give_nonogram(nonogram)
        soln_handler.set_timeout(self.timeout)
        _ = soln_handler.run_solver("sbs-improved", True, False)
        if not soln_handler.solutions:
            self.uniqueness_label.setText("   Uniqueness check timed out")
            self.uniqueness_label.setStyleSheet("color: default; font-size: 11px;")
        elif len(soln_handler.solutions) > 1:
            self.uniqueness_label.setText(f"   ✗ Nonogram is not unique! ({len(soln_handler.solutions)}+ Solutions)")
            self.uniqueness_label.setStyleSheet("color: red; font-size: 11px;")
        else:
            self.uniqueness_label.setText("   ✓ Nonogram is unique")
            self.uniqueness_label.setStyleSheet("color: green; font-size: 11px;")

    def get(self) -> np.ndarray | None:
        """Wait for dialog to close and return result (similar to Tkinter version)"""
        exec_result = self.exec_()

        if exec_result == QDialog.Accepted and self.success:
            if self.grid is not None:
                return (self.grid != 255).astype(np.uint8)
        return None

    def _on_ok(self):
        """Handle OK button click - store the result and close dialog"""
        self.success = True
        self.accept()

    def _on_cancel(self, *_):
        self.success = False
        self.reject()

    def _invert(self):
        """Invert the nonogram image (swap black and white)"""
        self.grid = 255 - self.grid
        self.update_plot()

    def eventFilter(self, a0, a1):
        """Handle key press events for the dialog"""
        if not a1:
            return super().eventFilter(a0, a1)
        
        if a1.type() == QtCore.QEvent.KeyPress:
            if a1.key() == Qt.Key_Return or a1.key() == Qt.Key_Enter:
                self._on_ok()  # Close dialog with Accepted status
                return True
            elif a1.key() == Qt.Key_Escape:
                self._on_cancel()
                return True
        return super().eventFilter(a0, a1)

    def _on_option_select(self, checked, value):
        """Handle selection of radio button options"""
        if checked:
            self.selected_option_var = value

            # Enable/disable controls based on selected option
            if value == "random":
                self.bwratio_sb.setEnabled(True)
                self.pxcorr_sb.setEnabled(True)
                self.file_select_bt.setEnabled(False)
                self.threshold_sb.setEnabled(False)
            elif value == "image":
                self.bwratio_sb.setEnabled(False)
                self.pxcorr_sb.setEnabled(False)
                self.file_select_bt.setEnabled(True)
                self.threshold_sb.setEnabled(True)
            else:  # "empty"
                self.bwratio_sb.setEnabled(False)
                self.pxcorr_sb.setEnabled(False)
                self.file_select_bt.setEnabled(False)
                self.threshold_sb.setEnabled(False)

            self.reload()

    def _on_set_timeout(self, input):
        self.timeout = float(input)
        
    def _on_set_width(self, input):
        if self.width_ == input:
            return
        self.width_ = input
        self.mat = np.zeros((self.height_, self.width_), dtype=np.uint8)
        self.reload()

    def _on_set_height(self, input):
        if self.height_ == input:
            return
        self.height_ = input
        self.mat = np.zeros((self.height_, self.width_), dtype=np.uint8)
        self.reload()

    def _on_set_bwratio(self, input):
        if self.bwratio == input:
            return
        self.bwratio = input
        self.reload()
        
    def _on_set_pxcorr(self, input):
        if self.pxcorr == input:
            return
        self.pxcorr = input
        self.reload()

    def _on_set_threshold(self, input):
        if self.threshold == input:
            return
        self.threshold = input
        self.reload()

    def _on_select_image_file(self, *_):
        """Open a filedialog to select an image and save it, then reload"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "images")
        
        if not file_path or self.im_file_path == file_path:
            return
        self.im_file_path = file_path
        self.im_original = cv2.imread(self.im_file_path, cv2.IMREAD_GRAYSCALE)
        try:
            _ = self.im_original.size
            _ = cv2.resize(self.im_original, (100, 100))
        except:
            self.im_original = None

        if self.im_original is None:
            print("Error: Could not read image at " + self.im_file_path)
            self.file_select_bt.setText("Error loading image")
            return
        
        # Get the dimensions of the image
        height, width = self.im_original.shape

        # Check if the image is very large and should to be resized
        if width > 1000 or height > 1000:
            # print("image is very large, rescaling...")
            # Calculate the scaling factor
            scaling_factor = min(1000.0 / width, 1000.0 / height)

            # Calculate new dimensions
            new_width = int(width * scaling_factor)
            new_height = int(height * scaling_factor)

            # Resize the image
            self.im_original = cv2.resize(self.im_original, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
        h, w = self.im_original.shape
        self.file_select_bt.setText(''.join(file_path.split("/")[-1].split(".")[:-1]) + f"({w}x{h})")

        self.reload()
