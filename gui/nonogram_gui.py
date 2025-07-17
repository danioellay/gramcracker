# Nonogram viewer and solver GUI
# Author: Fabian Kraus
# run with: python3 -m gui [optional parameter: nonogram filename] [optional parameter: solver name]
#    e.g. : python3 -m gui nonograms/example_05.lp symbolic-block-start

from os import listdir
from os.path import isfile, join
from math import ceil
from typing import List

import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QDialog, QWidget, QFileDialog,
                             QAction, QVBoxLayout, 
                             QLabel, QLineEdit, QHBoxLayout, QPushButton)
from PyQt5.QtGui import QKeySequence

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Patch
from matplotlib.text import Text

from .common import *
from .nonogram_creator import NonogramCreator
from .handlers.nonogram_handler import NonogramHandler
from .handlers.solution_handler import SolutionHandler

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SQUARE_SIZE = 50 #default side length of a grid cell, in pixels

class NonogramGUI(QMainWindow):

    def __init__(self, args) -> None:
        """Initialize the Nonogram GUI window"""
        super().__init__()

        # Setup data handlers
        self.nonogram_handler = NonogramHandler()
        self.solution_handler = SolutionHandler()

        # Flags indicating which cell is currently being hovered over
        self.highlighted_x, self.highlighted_y = -1, -1

        # Flags for the drag & draw functionality
        self.dragging = False
        self.drag_start = -1, -1
        self.drag_end = -1, -1
        self.drag_covered = []
        self.drag_to_erase = False
        self.drag_to_cross = False

        # Flag to freeze the currently hovered row/column when opening a dialog box (eg hint editor)
        self.block_hover = False

        # Setup window
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("Nonogram Viewer, Editor & Solver")

        # Setup window widgets
        self._setup_menubar()
        self._setup_canvas()
        self._setup_statusbar()

        # Process launch arguments
        # Open nonogram generator first if no arguments were given and wait for it to close
        if len(args) == 1:
            self._on_file_new()
            if self.nonogram_handler.get_curr_nonogram().width == 0:
                exit()

        # Open the nonogram encoding at the path indicated by the first argument
        elif len(args) > 1:
            try:
                self.nonogram_handler.load_file(args[1])
            except Warning as w:
                print(f"Could not open file: {w.args[0]}")
                self.destroy()
                exit()
            except:
                print(f"Unknown error: Could not load nonogram file")
                self.destroy()
                exit()

            nonogram = self.nonogram_handler.get_curr_nonogram()
            self.solution_handler.give_nonogram(nonogram)

        nonogram = self.nonogram_handler.get_curr_nonogram()
        self._draw_nonogram(nonogram)
        size = nonogram.width * nonogram.height
        self.show_hint_highlight_var = (size <= 20*20)
        self.show_hint_feedback_action.setChecked(self.show_hint_highlight_var)
        self.menuBar

        self.solved_on_start = False
        if len(args) > 2:
            # Run the solver indicated by the second argument
            self._on_solver(args[2])
            self.solved_on_start = True

    def _on_next_soln(self, *_) -> None:
        self.solution_handler.next_soln()
        self._draw_solution()
        self.set_status(f"Showing solution nr. {self.solution_handler.curr_soln_idx + 1}.")

    def _on_prev_soln(self, *_) -> None:
        self.solution_handler.prev_soln()
        self._draw_solution()
        self.set_status(f"Showing solution nr. {self.solution_handler.curr_soln_idx + 1}.")

    def _on_solver(self, name: str, *_) -> None:
        """Run the solver, identified by its name"""
        self.set_status("Solving nonogram...")
        res = self.solution_handler.run_solver(name.split(".")[0], 
                                               self.check_uniqueness_var, 
                                               self.find_all_solns_var)
        self.set_status(res + ".")

        self._draw_solution()
    
    def _on_file_open(self, *_) -> None:
        """Open a file dialog and let the user load a file"""
        file_types = "Text format (*.txt);;ASP encoding (*.lp)"
        init_dir = "nonograms"

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a file encoding a Nonogram",
            init_dir,
            file_types
        )
        if not file_path:
            return

        try:
            self.nonogram_handler.load_file(file_path)
        except Warning as w:
            self.set_status(f"Could not open file: {w.args[0]}")
        except:
            self.set_status(f"Unknown error: Could not load nonogram file")
        self._clear_all()

        nonogram = self.nonogram_handler.get_curr_nonogram()
        self._draw_nonogram(nonogram)
        self.solution_handler.give_nonogram(nonogram)
        self.set_status(f"Loaded nonogram from {file_path.split("/")[-1]}.")

    def _on_file_new(self, *_) -> None:
        """Open the nonogram creator"""
        creator = NonogramCreator(self)
        grid = creator.get()
        if grid is None:
            # self.set_status(f"Ready.")
            return
        
        self._clear_all()
        self.nonogram_handler.loaded_nonogram_filename = None
        self.nonogram_handler.get_curr_nonogram().init_from_grid(grid)
    
        nonogram = self.nonogram_handler.get_curr_nonogram()
        self._draw_nonogram(nonogram)
        self.solution_handler.give_nonogram(nonogram)
        self.set_status(f"Ready.")

    def _on_file_new_from_current(self, *_) -> None:
        """Convert the current solution (grid state) to a nonogram and load it"""
        self.nonogram_handler.loaded_nonogram_filename = None
        # self.nonogram_handler.clear_hints()
        grid = self.solution_handler.get_curr_soln().grid

        self.nonogram_handler.get_curr_nonogram().init_from_grid(grid)

        nonogram = self.nonogram_handler.get_curr_nonogram()
        self._clear_all()
        self._draw_nonogram(nonogram)
        self.solution_handler.give_nonogram(nonogram)
        self.set_status(f"Created nonogram from previous grid configuration.")

    def _on_file_export_image(self, *_) -> None:
        """Export the current canvas as an image file at a user-picked location"""
        file_types = "SVG image (*.svg);;PDF Document (*.pdf);;PNG image (*.png)"
        init_dir = ""

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Nonogram as Image",
            init_dir,
            file_types
        )
        if not file_path:
            return
        
        self.figure.savefig(file_path, bbox_inches='tight')
        self.set_status(f"Exported image to {file_path.split("/")[-1]}.")

    def _on_file_save(self, *_) -> None:
        """Export the currently loaded nonogram to the text file it was loaded from"""
        if not self.nonogram_handler.loaded_nonogram_filename:
            self._on_file_save_as()
            return
        self.nonogram_handler.save_file()
        self.set_status(f"Saved.")

    def _on_file_save_as(self, *_) -> None:
        """Export the currently loaded nonogram to a text file at a user-picked location"""
        file_types = "Text format (*.txt);;ASP encoding (*.lp)"
        init_dir = ""
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Nonogram Encoding",
            init_dir,
            file_types
        )
        if not file_path:
            return
        
        self.nonogram_handler.loaded_nonogram_filename = file_path
        self.nonogram_handler.save_file()
        self.set_status(f"Saved nonogram to {file_path.split("/")[-1]}.")

    
    def _setup_menubar(self):
        """Initialize the menu bar of the window"""
        menubar = self.menuBar()
        assert(menubar)

        # File menu
        file_menu = menubar.addMenu("&File")
        assert(file_menu)

        # Open action
        open_action = QAction("&Open", self)
        open_action.setShortcuts([QKeySequence("Ctrl+O")])
        open_action.triggered.connect(self._on_file_open)
        file_menu.addAction(open_action)

        # New action
        new_action = QAction("&New", self)
        new_action.setShortcuts([QKeySequence("Ctrl+N")])
        new_action.triggered.connect(self._on_file_new)
        file_menu.addAction(new_action)

        # New from current solution action
        new_from_current_action = QAction("New from current solution", self)
        new_from_current_action.setShortcuts([QKeySequence("Ctrl+Shift+N")])
        new_from_current_action.triggered.connect(self._on_file_new_from_current)
        file_menu.addAction(new_from_current_action)

        # Save action
        save_action = QAction("&Save", self)
        save_action.setShortcuts([QKeySequence("Ctrl+S")])
        save_action.triggered.connect(self._on_file_save)
        file_menu.addAction(save_action)

        # Save as action
        save_as_action = QAction("Save as...", self)
        save_as_action.setShortcuts([QKeySequence("Ctrl+Shift+S")])
        save_as_action.triggered.connect(self._on_file_save_as)
        file_menu.addAction(save_as_action)

        # Export Image action
        export_image_action = QAction("Export Image", self)
        export_image_action.setShortcuts([QKeySequence("Ctrl+I")])
        export_image_action.triggered.connect(self._on_file_export_image)
        file_menu.addAction(export_image_action)

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Solver menu
        solver_menu = menubar.addMenu("&Solver")
        assert(solver_menu)

        # Check uniqueness action
        self.check_uniqueness_var = True
        self.check_uniqueness_action = QAction("&Check uniqueness", self)
        self.check_uniqueness_action.setCheckable(True)
        self.check_uniqueness_action.setChecked(self.check_uniqueness_var)
        self.check_uniqueness_action.triggered.connect(self._on_toggle_check_uniqueness)
        solver_menu.addAction(self.check_uniqueness_action)

        # Find all solutions action
        self.find_all_solns_var = False
        self.find_all_solns_action = QAction("&Find all solutions", self)
        self.find_all_solns_action.setCheckable(True)
        self.find_all_solns_action.setChecked(self.find_all_solns_var)
        self.find_all_solns_action.triggered.connect(self._on_toggle_find_all)
        solver_menu.addAction(self.find_all_solns_action)

        solver_menu.addSeparator()

        # Add solver actions
        solvers = [f for f in listdir("solvers/") if isfile(join("solvers/", f)) and f.endswith(".lp")]
        for i, solver in enumerate(solvers):
            action = QAction(solver.split(".")[0], self)
            action.setShortcut(QKeySequence(f"Ctrl+{i+1}"))
            action.triggered.connect(lambda _, s=solver: self._on_solver(s))
            solver_menu.addAction(action)

        # View menu
        view_menu = menubar.addMenu("&View")
        assert(view_menu)

        # Color hints as correctness feedback action
        self.show_hint_feedback_var = True
        self.show_hint_feedback_action = QAction("&Color hints as correctness feedback", self)
        self.show_hint_feedback_action.setCheckable(True)
        self.show_hint_feedback_action.setChecked(self.show_hint_feedback_var)
        self.show_hint_feedback_action.triggered.connect(self._on_toggle_show_hint_feedback)
        view_menu.addAction(self.show_hint_feedback_action)

        # Highlight hovered cell hints action
        self.show_hint_highlight_var = True
        self.show_hint_highlight_action = QAction("&Highlight hovered cell hints", self)
        self.show_hint_highlight_action.setCheckable(True)
        self.show_hint_highlight_action.setChecked(self.show_hint_highlight_var)
        self.show_hint_highlight_action.triggered.connect(self._on_toggle_show_hint_highlight)
        view_menu.addAction(self.show_hint_highlight_action)

        view_menu.addSeparator()

        # View next solution action
        next_soln_action = QAction("View Next Solution", self)
        next_soln_action.setShortcuts([QKeySequence("Ctrl+J")])
        next_soln_action.triggered.connect(self._on_next_soln)
        view_menu.addAction(next_soln_action)

        # View previous solution action
        prev_soln_action = QAction("View Prev. Solution", self)
        prev_soln_action.setShortcuts([QKeySequence("Ctrl+H")])
        prev_soln_action.triggered.connect(self._on_prev_soln)
        view_menu.addAction(prev_soln_action)

    def _setup_canvas(self):

        # Setup canvas artist storage
        self.pixels: List[List[Patch]] = []
        self.crosses: List[List[Text]] = []
        self.col_hints: List[List[Text]] = []
        self.row_hints: List[List[Text]] = []

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create Matplotlib figure and canvas
        self.figure, self.axes = plt.subplots()
        plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
        plt.tight_layout()
        self.axes.set_aspect('equal')

        # Create the canvas for PyQt
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Add canvas to the layout
        layout.addWidget(self.canvas, stretch=1)

        # Setup button event callbacks (typecast to make pylance happy)
        self.canvas.mpl_connect('button_press_event', self._on_button_press)
        self.canvas.mpl_connect('button_release_event', self._on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)

    def _setup_statusbar(self):
        # Setup status bar directly
        sb = self.statusBar()
        assert(sb)
        sb.setFixedHeight(20)
        self.status_label = QLabel()
        sb.addWidget(self.status_label, stretch=1)
        sb.setStyleSheet("QStatusBar { font-size: 10pt; }")
        self.set_status("Initializing...")

    def set_status(self, text):
        """Set the status bar text"""
        self.status_label.setText(text)

    def _on_button_press(self, event):
        if event.inaxes != self.axes:
            return

        self.solution_handler.use_working_soln()
        nonogram = self.nonogram_handler.get_curr_nonogram()

        # Convert y-coordinate properly for your nonogram grid
        y = ceil(nonogram.height - event.ydata - 1)
        x = ceil(event.xdata - 1)

        # Check if coordinates are within bounds
        if 0 <= y < nonogram.height and 0 <= x < nonogram.width:
            self.dragging = True
            self.drag_start = self.drag_end = (y, x)
            self.drag_covered = [self.drag_start]

            if event.button == 1:  # Left mouse button
                self._on_leftclick_cell(y, x)
                self.drag_to_cross = False
                self.drag_to_erase = self.solution_handler.get_curr_soln().grid[y][x]
            elif event.button == 3:  # Right mouse button
                self._on_rightclick_cell(y, x)
                self.drag_to_cross = True
                self.drag_to_erase = self.crosses[y][x].get_visible()
        elif y >= 0 and x < 0 and event.button == 1:
            self._on_leftclick_rowhint(y)
        elif x >= 0 and y < 0 and event.button == 1:
            self._on_leftclick_colhint(x)
        # remaining case: x, y == -1, -1

    def _on_button_release(self, event):
        if self.dragging:
            self.dragging = False
            self.drag_start = self.drag_end = (-1, -1)
            self.drag_covered = []
            self.drag_to_erase = False
            self.drag_to_cross = False

    def _on_mouse_motion(self, event):
        if self.block_hover:
            return

        if event.inaxes != self.axes or not event.ydata or not event.xdata:
            self._highlight_hint(-1, -1)
            return

        nonogram = self.nonogram_handler.get_curr_nonogram()

        x = ceil(event.xdata - 1)
        y = ceil(nonogram.height - event.ydata - 1)

        if not (0 <= x < nonogram.width and 0 <= y < nonogram.height):
            return

        if self.show_hint_highlight_var and (self.highlighted_x != x or self.highlighted_y != y):
            self._highlight_hint(x, y)

        if self.dragging and (y, x) != self.drag_end:
            self.drag_end = (y, x)
            dy = self.drag_end[0] - self.drag_start[0]
            dx = self.drag_end[1] - self.drag_start[1]

            # Erase the old dragged line
            if self.drag_to_cross:
                for cell in self.drag_covered:
                    self._on_rightclick_cell(*cell)
            else:
                for cell in self.drag_covered:
                    self._on_leftclick_cell(*cell)

            # Drag a new vertical or horizontal line
            self.drag_covered = []
            grid = self.solution_handler.get_curr_soln().grid
            y0, x0 = self.drag_start
            points = []

            if abs(dy) > abs(dx):
                # Vertical drag
                step = 1 if dy > 0 else -1
                for deltay in range(0, abs(dy) + 1, 1):
                    new_y = y0 + (deltay * step)
                    points.append((new_y, x0))
            else:
                # Horizontal drag
                step = 1 if dx > 0 else -1
                for deltax in range(0, abs(dx) + 1, 1):
                    new_x = x0 + (deltax * step)
                    points.append((y0, new_x))

            for point in points:
                y, x = point
                if 0 <= y < nonogram.height and 0 <= x < nonogram.width:
                    if self.drag_to_cross and self.crosses[y][x].get_visible() != self.drag_to_erase:
                        self.drag_covered.append(point)
                        self._on_rightclick_cell(y, x)
                    elif not self.drag_to_cross and grid[y][x] != self.drag_to_erase:
                        self.drag_covered.append(point)
                        self._on_leftclick_cell(y, x)

    def _highlight_hint(self, x: int, y: int) -> None:
        # Restore default appearance of previously selected row
        for hint in self.row_hints[self.highlighted_y]:
            hint.set_fontweight('normal')
        for cell in self.pixels[self.highlighted_y]:
            cell.set_alpha(0.8)

        nonogram = self.nonogram_handler.get_curr_nonogram()
        
        # Highlight newly selected row
        if y >= 0 and y < nonogram.height:
            for hint in self.row_hints[y]:
                hint.set_fontweight('bold')
            for cell in self.pixels[y]:
                cell.set_alpha(0.88)
        self.highlighted_y = y

        # Restore default appearance of previously selected column
        for hint in self.col_hints[self.highlighted_x]:
            hint.set_fontweight('normal')
        for row in self.pixels:
            row[self.highlighted_x].set_alpha(0.8)

        # Highlight newly selected column
        if x >= 0 and x < nonogram.width:
            for hint in self.col_hints[x]:
                hint.set_fontweight('bold')
            for row in self.pixels:
                row[x].set_alpha(0.88)
            # Need to overwrite one pixel
            self.pixels[y][self.highlighted_x].set_alpha(0.88)
        self.highlighted_x = x

        self.canvas.draw_idle()

    def _on_leftclick_cell(self, row: int, col: int) -> None:
        # Toggle the corresponding pixel in both the current solution and the pixel grid
        prev_val = self.solution_handler.get_curr_soln().grid[row, col]
        curr_val = not prev_val
        self.solution_handler.get_curr_soln().grid[row, col] = curr_val
        self.pixels[row][col].set_visible(curr_val)

        # Update just the two line hints instead of calling _update_hints_feeback to improve performance
        color_hints = self.show_hint_feedback_var
        satisfied_row_indices = self.solution_handler.solves_row_partial(row) 
        satisfied_col_indices = self.solution_handler.solves_col_partial(col) 
        for idx, hint in enumerate(reversed(self.row_hints[row])):
            hint.set_color('black' if idx in satisfied_row_indices or not color_hints else 'red')
        for idx, hint in enumerate(reversed(self.col_hints[col])):
            hint.set_color('black' if idx in satisfied_col_indices or not color_hints else 'red')
        
        # Refresh canvas
        self.canvas.draw_idle()

    def _on_rightclick_cell(self, row: int, col: int) -> None:
        newval = not self.crosses[row][col].get_visible()
        self.crosses[row][col].set_visible(newval)
        self.canvas.draw_idle()

    def _on_leftclick_rowhint(self, row: int) -> None:
        nonogram = self.nonogram_handler.get_curr_nonogram()
        
        old_hint = nonogram.row_hints[row]
        new_hint = self._open_hint_edit_dialog(old_hint, nonogram.width)
        if new_hint == old_hint:
            return
        
        nonogram.row_hints[row] = new_hint
        
        self._draw_nonogram(nonogram)
        self.solution_handler.give_nonogram(nonogram)

    def _on_leftclick_colhint(self, col: int) -> None:
        nonogram = self.nonogram_handler.get_curr_nonogram()
        if not nonogram:
            return
        
        old_hint = nonogram.col_hints[col]
        new_hint = self._open_hint_edit_dialog(old_hint, nonogram.height)
        if new_hint == old_hint:
            return
        
        nonogram.col_hints[col] = new_hint
        
        self._draw_nonogram(nonogram)
        self.solution_handler.give_nonogram(nonogram)

    def _open_hint_edit_dialog(self, hint: LineHint, length: int) -> LineHint:
        self.block_hover = True

        # Create a custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Hint")
        dialog.setFixedSize(500, 150)

        # Create layout for the dialog
        layout = QVBoxLayout(dialog)

        # Create and add an entry widget (QLineEdit)
        entry = QLineEdit()
        current_string = ' '.join(map(str, hint)) if hint else "0"
        entry.setText(current_string)
        entry.setFixedWidth(400)  # Set width similar to your Tkinter version
        layout.addWidget(entry, stretch=0, alignment=Qt.AlignCenter)

        # Create and add a label for feedback
        feedback_label = QLabel()
        layout.addWidget(feedback_label, stretch=0, alignment=Qt.AlignCenter)

        # Create button layout
        button_layout = QHBoxLayout()

        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: on_ok(dialog))

        # Cancel Button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        # Add buttons to the layout
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # Add button layout to the main layout
        layout.addLayout(button_layout)

        # Store result here
        result: List[LineHint] = [hint]  # Using a list to allow modification in the nested function

        def on_ok(dialog):
            new_string = entry.text()
            try:
                parsed_hint = LineHint(list(map(int, new_string.split())))
                for h in parsed_hint:
                    if h <= 0:
                        raise ValueError

                min_len = sum(parsed_hint) + len(parsed_hint) - 1
                if min_len <= length:
                    result[0] = parsed_hint
                    dialog.accept()  # Close the dialog with accept status
                else:
                    result[0] = hint
                    feedback_label.setText(f"Hint too long! (Needs {min_len}+ units)")
            except:
                result[0] = hint
                feedback_label.setText("Invalid hint!")

        # Handle Enter and Escape keys
        def keyPressEvent(event):
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                on_ok(dialog)
            elif event.key() == Qt.Key_Escape:
                dialog.reject()

        dialog.keyPressEvent = keyPressEvent

        # Focus on the entry widget
        entry.setFocus()

        # Show the dialog modally and wait for it to close
        if dialog.exec_() == QDialog.Accepted:
            pass  # The result is already stored in the result list

        self.block_hover = False
        return result[0]

    def _draw_nonogram(self, nonogram: Nonogram):
        self._clear_all()
        # Adjust the window size
        # win_width = nonogram.width*SQUARE_SIZE
        # win_height = nonogram.height*SQUARE_SIZE
        # self.setMinimumSize(win_width, win_height)

        # Ensure the aspect ratio is equal to avoid distortion
        self.axes.set_aspect('equal')

        # Draw a black pixel in every cell then hide it
        self.pixels = [
            [
                patches.Rectangle((col, nonogram.height - row - 1), 1, 1, linewidth=0, facecolor='black', alpha=0.8)
                for col in range(nonogram.width)
            ]
            for row in range(nonogram.height)
        ]
        for row in range(nonogram.height):
            for col in range(nonogram.width):
                pixel = self.pixels[row][col]
                self.axes.add_patch(pixel)
                pixel.set_visible(False)

        # Draw a 'x' in every cell then hide it
        self.crosses = [
            [
                Text(col + 0.5, nonogram.height - row - 0.5, 'x', color='grey', va='center', ha='center', fontsize=10)
                for col in range(nonogram.width)
            ]
            for row in range(nonogram.height)
        ]
        for row in range(nonogram.height):
            for col in range(nonogram.width):
                cross = self.crosses[row][col]
                self.axes.add_artist(cross)
                cross.set_visible(False)

        # Draw row hints to the left of the grid
        for i, hints in enumerate(nonogram.row_hints):
            if not hints:
                hint = [self.axes.text(-0.66, nonogram.height - i - 0.6, "0", va='center', ha='center', fontsize=9, color='red')]
                hint[0].set_color('black')
                self.row_hints.append(hint)
                continue

            self.row_hints.append([])
            for j, l in enumerate(reversed(hints)):
                hint = self.axes.text(-0.66-j*0.7, nonogram.height - i - 0.6, str(l), va='center', ha='center', fontsize=9 if l < 10 else 5, color='red')
                if not self.show_hint_feedback_var or l == 0:
                    hint.set_color('black')
                self.row_hints[i].append(hint)

        # Draw column hints above the grid, stacked vertically
        for j, hints in enumerate(nonogram.col_hints):
            if not hints:
                hint = [self.axes.text(j + 0.5, nonogram.height + 0.33, "0", va='center', ha='center', fontsize=9, color='red')]
                hint[0].set_color('black')
                self.col_hints.append(hint)
                continue

            self.col_hints.append([])
            for i, l in enumerate(reversed(hints)):
                hint = self.axes.text(j + 0.5, nonogram.height + 0.33 + i*0.8, str(l), va='center', ha='center', fontsize=9 if l < 10 else 5, color='red')
                if not self.show_hint_feedback_var or l == 0:
                    hint.set_color('black')
                self.col_hints[j].append(hint)

        # Setup the grid and ticks and cell index numbers
        self.axes.set_xticks(range(0, nonogram.width+1 ),
                             [""] + list(map(str, range(1, nonogram.width + 1))), fontsize=7)
        self.axes.set_yticks(range(0, nonogram.height+1), 
                             list(map(str, reversed(range(1, nonogram.height + 1)))) + [""], fontsize=7) # enumerate rows from top to bottom

        # Further customize the plots appearance, like adding a grid and removing the frame
        self.axes.yaxis.set_label_position('right')
        self.axes.yaxis.tick_right()
        plt.setp(self.axes.xaxis.get_majorticklabels(), ha="right",  va="top" )
        plt.setp(self.axes.yaxis.get_majorticklabels(), va="bottom", ha="left")
        self.axes.grid(which='both', color='black', linestyle='-', linewidth=1)
        self.axes.spines['top'   ].set_visible(False)
        # self.axes.spines['right' ].set_visible(False)
        # self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'  ].set_visible(False)

        # Redraw the canvas
        self.canvas.draw()

        # Set the xy limits so that the entire nonogram plus hints are visible
        self.axes.set_xlim(-0.2 -0.75*max([len(rh) for rh in nonogram.row_hints]), nonogram.width)
        self.axes.set_ylim(-0, 0.2 + nonogram.height + 0.75*max([len(ch) for ch in nonogram.col_hints]))
        self.canvas.draw_idle()
        self.highlighted_x, self.highlighted_y = -1, -1

        size = nonogram.width * nonogram.height
        self.show_hint_highlight_var = (size <= 20*20)
        self.show_hint_feedback_action.setChecked(self.show_hint_highlight_var)

    def _draw_solution(self):
        grid = self.solution_handler.get_curr_soln().grid

        # Slower (?)
        # for r, row in enumerate(grid):
        #     for c, filled in enumerate(row):
        #         self.pixels[r][c].set_visible(filled)

        true_indices = np.argwhere(grid)
        for r, c in true_indices:
            self.pixels[r][c].set_visible(True)
        
        false_indices = np.argwhere(~grid)
        for r, c in false_indices:
            self.pixels[r][c].set_visible(False)

        # Hide all 'x' marks when showing a solvers solution
        for row in self.crosses:
            for cross in row:
                cross.set_visible(False)
        
        self._update_hints_feedback()

    def _clear_all(self) -> None:
        # Clear all artists from the canvas
        for p in self.pixels:
            for pp in p:
                pp.remove()
        self.pixels.clear()

        for ch in self.col_hints:
            for h in ch:
                h.remove()
        self.col_hints.clear()

        for rh in self.row_hints:
            for h in rh:
                h.remove()
        self.row_hints.clear()

        plt.cla()
    
    def _update_hints_feedback(self):
        color_hints = self.show_hint_feedback_var

        # Go through every hint in every line and check it
        for row, row_hint in enumerate(self.row_hints):
            satisfied_hint_indices = self.solution_handler.solves_row_partial(row)
            for idx, hint in enumerate(row_hint):
                solves_row = not color_hints or idx in satisfied_hint_indices
                hint.set_color('black' if solves_row else 'red')
        for col, col_hint in enumerate(self.col_hints):
            satisfied_hint_indices = self.solution_handler.solves_col_partial(col)
            for idx, hint in enumerate(col_hint):
                solves_col = not color_hints or idx in satisfied_hint_indices
                hint.set_color('black' if solves_col else 'red')

        # Refresh canvas
        self.canvas.draw_idle()

    def _on_toggle_show_hint_feedback(self, *_):
        self.show_hint_feedback_var = not self.show_hint_feedback_var
        self._update_hints_feedback()

    def _on_toggle_show_hint_highlight(self, *_):
        self.show_hint_highlight_var = not self.show_hint_highlight_var
        self._highlight_hint(-1,-1)

    def _on_toggle_check_uniqueness(self, *_):
        self.check_uniqueness_var = not self.check_uniqueness_var
        if not self.check_uniqueness_var:
            self.find_all_solns_action.setChecked(False)

    def _on_toggle_find_all(self, *_):
        self.find_all_solns_var = not self.find_all_solns_var