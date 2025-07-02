# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus
# run with: python3 -m gui [optional parameter: nonogram filename] [optional parameter: solver name]
#    e.g. : python3 -m gui nonograms/example_05.lp symbolic-block-start

from os import listdir
from os.path import isfile, join
from math import ceil

import tkinter as tk
from tkinter import filedialog, BooleanVar
from matplotlib.backend_bases import MouseEvent

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.text import Text

from .common import *
from .nonogram_creator import NonogramCreator
from .handlers.nonogram_handler import NonogramHandler
from .handlers.solution_handler import SolutionHandler

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SQUARE_SIZE = 50 #default side length of a grid cell, pixels


class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, height=50)
        self.label = tk.Label(self)
        self.label.pack(side=tk.LEFT)
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def set(self, newText) -> None:
        self.label.config(text=newText)
    
    def clear(self) -> None:
        self.label.config(text="")


class NonogramGUI(tk.Tk):

    def __init__(self, args) -> None:
        tk.Tk.__init__(self)

        # Setup data handlers
        self.nonogram_handler = NonogramHandler()
        self.solution_handler = SolutionHandler()

        # Open nonogram generator first if no arguments and wait for this to close
        if len(args) == 1:
            self.withdraw()
            self._on_file_new()
            if not self.nonogram_handler.get_nonogram() or not hasattr(self.solution_handler, "given_nonogram"):
                exit()
            self.deiconify()

        # Setup window
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.title("Nonogram GUI")
        self.protocol("WM_DELETE_WINDOW", self._on_del_window)
        self.protocol("tk::mac::Quit", self._on_del_window)

        # Setup window menubar
        self.menubar = tk.Menu(self, type='menubar')
        self.configure(menu=self.menubar)

        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self._on_file_open)
        self.bind_all("<Control-o>", self._on_file_open)
        self.bind_all("<Control-O>", self._on_file_open)
        self.file_menu.add_command(label="New", accelerator="Ctrl+N", command=self._on_file_new)
        self.bind_all("<Control-n>", self._on_file_new)
        self.bind_all("<Control-N>", self._on_file_new)
        self.file_menu.add_command(label="New from current solution", accelerator="Ctrl+Shift+N", command=self._on_file_new_from_current)
        self.bind_all("<Control-Shift-n>", self._on_file_new_from_current)
        self.bind_all("<Control-Shift-N>", self._on_file_new_from_current)
        self.file_menu.add_command(label="Save",  accelerator="Ctrl+S", command=self._on_file_save)
        self.bind_all("<Control-s>", self._on_file_save)
        self.bind_all("<Control-S>", self._on_file_save)
        self.file_menu.add_command(label="Save as ... ",  accelerator="Ctrl+Shift+S", command=self._on_file_save_as)
        self.bind_all("<Control-Shift-s>", self._on_file_save_as)
        self.bind_all("<Control-Shift-S>", self._on_file_save_as)
        self.file_menu.add_command(label="Export Image", accelerator="Ctrl+I", command=self._on_file_export_image)
        self.bind_all("<Control-i>", self._on_file_export_image)
        self.bind_all("<Control-I>", self._on_file_export_image)
        self.file_menu.add_command(label="Exit", command=self._on_del_window)

        # Solver menu
        self.solver_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(menu=self.solver_menu, label="Solver")

        self.check_uniqueness_var = BooleanVar(value=True)
        self.solver_menu.add_checkbutton(label="Check uniqueness", variable=self.check_uniqueness_var)
        self.check_uniqueness_var.trace_add('write', self._on_toggle_check_uniqueness)

        self.find_all_solns_var = BooleanVar(value=False)
        self.solver_menu.add_checkbutton(label="Find all solutions", variable=self.find_all_solns_var)
        self.find_all_solns_var.trace_add('write', self._on_toggle_check_uniqueness)

        self.solver_menu.add_separator()

        solvers = [f for f in listdir("solvers/") if isfile(join("solvers/", f)) and f.endswith(".lp")]
        for i, solver in enumerate(solvers):
            # Create a lambda function that calls _on_solver with the correct solver
            self.solver_menu.add_command(label=solver.split(".")[0], accelerator=f"Ctrl+{i+1}", command=lambda s=solver: self._on_solver(s))
            self.bind_all(f"<Control-Key-{i+1}>", lambda e, s=solver: self._on_solver(s))

        # View menu
        self.view_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(menu=self.view_menu, label="View")

        self.show_hint_feedback_var = BooleanVar(value=True)
        self.show_hint_feedback_var.trace_add('write', self._on_toggle_show_hint_feedback)
        self.view_menu.add_checkbutton(label="Color hints as correctness feedback", variable=self.show_hint_feedback_var)

        self.show_hint_highlight_var = BooleanVar(value=True)
        self.show_hint_highlight_var.trace_add('write', self._on_toggle_show_hint_highlight)
        self.view_menu.add_checkbutton(label="Highlight hovered cell hints", variable=self.show_hint_highlight_var)

        self.view_menu.add_separator()

        self.view_menu.add_command(label="View Next Solution", accelerator="Ctrl+J", command=self._on_next_soln)
        self.bind_all("<Control-j>", self._on_next_soln)
        self.bind_all("<Control-J>", self._on_next_soln)

        self.view_menu.add_command(label="View Prev. Solution", accelerator="Ctrl+H", command=self._on_prev_soln)
        self.bind_all("<Control-H>", self._on_prev_soln)
        self.bind_all("<Control-h>", self._on_prev_soln)

        # Setup nonogram drawing canvas and add to window
        self.figure_frame = tk.Frame(self)
        self.figure_frame.pack(fill=tk.BOTH, expand=True)
        self.figure, self.axes = plt.subplots()
        plt.subplots_adjust(left=0.05, right=0.9, top=1.0, bottom=0.05)
        self.axes.set_aspect('equal')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Setup status bar
        self.status = StatusBar(self)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status.set("Initializing...")

        # Setup button event callbacks
        self.canvas.mpl_connect('button_press_event', self._on_button_press)
        # self.canvas.mpl_connect('button_release_event', self._on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)
        # self.canvas.mpl_connect('scroll_event', self._on_scroll)

        # Flag to freeze the currently hovered row/column when opening a dialog box (eg hint editor)
        self.block_hover = False

        # Process launch arguments
        if len(args) > 1:
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

            nonogram = self.nonogram_handler.get_nonogram()
            if nonogram:
                self.solution_handler.give_nonogram(nonogram)

        nonogram = self.nonogram_handler.get_nonogram()
        if nonogram:
            self.draw_nonogram(nonogram)
            size = nonogram.width * nonogram.height
            self.show_hint_highlight_var.set(size <= 20*20)

        if len(args) > 2:
            self._on_solver(args[2])

    def run(self) -> None:
        # Finish setting up the GUI and enter mainloop
        self.update()
        self.update_idletasks()
        self.focus_force()
        self.status.set("Ready.")
        return self.mainloop()
    
    def _on_next_soln(self, *_) -> None:
        self.solution_handler.next_soln()
        self.draw_solution(self.solution_handler.get_curr_soln())
        self.status.set(f"Showing solution nr. {self.solution_handler.curr_soln_idx + 1}.")

    def _on_prev_soln(self, *_) -> None:
        self.solution_handler.prev_soln()
        self.draw_solution(self.solution_handler.get_curr_soln())
        self.status.set(f"Showing solution nr. {self.solution_handler.curr_soln_idx + 1}.")

    def _clear_all(self) -> None:
        if hasattr(self, "pixels"):
            for r in self.pixels:
                for c in r:
                    c.remove()
            self.pixels.clear()
            self.pixels = []

        if hasattr(self, "col_hints"):
            for h in self.col_hints:
                for hh in h:
                    hh.remove()
            self.col_hints.clear()
            self.col_hints = []

        if hasattr(self, "row_hints"):
            for h in self.row_hints:
                for hh in h:
                    hh.remove()
            self.row_hints.clear()
            self.row_hints = []

        plt.cla()

    def _on_solver(self, name: str, *_) -> None:
        self.status.set("Solving nonogram...")
        self.update_idletasks()
        res = self.solution_handler.run_solver(name.split(".")[0], 
                                               self.check_uniqueness_var.get(), 
                                               self.find_all_solns_var.get())
        self.status.set(res + ".")

        self.draw_solution(self.solution_handler.get_curr_soln())
    
    def _on_file_open(self, *_) -> None:
        file_types = [('Text format', '*.txt'), ('ASP encoding', '*.lp')]
        init_dir = "nonograms"
        file_path = filedialog.askopenfilename(title="Select a file encoding a Nonogram", initialdir=init_dir, filetypes=file_types)
        if not file_path:
            return

        try:
            self.nonogram_handler.load_file(file_path)
        except Warning as w:
            self.status.set(f"Could not open file: {w.args[0]}")
        except:
            self.status.set(f"Unknown error: Could not load nonogram file")
        self._clear_all()

        nonogram = self.nonogram_handler.get_nonogram()
        if nonogram:
            self.draw_nonogram(nonogram)
            if hasattr(self, "show_hint_highlight_var"):
                size = nonogram.width * nonogram.height
                self.show_hint_highlight_var.set(size <= 20*20)

            self.solution_handler.give_nonogram(nonogram)
            self.status.set(f"Loaded nonogram from {file_path.split("/")[-1]}.")

    def _on_file_new(self, *_) -> None:
        creator = NonogramCreator(self)
        result = creator.get()
        if not result:
            # self.status.set(f"Ready.")
            return
        width, height, grid = result
        
        self._clear_all()
        self.nonogram_handler.loaded_nonogram_filename = None
        
        if grid:
            self.nonogram_handler.hints_from_grid(grid)
        else:
            self.nonogram_handler.resize(width, height)
    
        nonogram = self.nonogram_handler.get_nonogram()
        if nonogram:
            self.solution_handler.give_nonogram(nonogram)
            if hasattr(self, "axes"):
                self.draw_nonogram(nonogram)
            
            if hasattr(self, "show_hint_highlight_var"):
                size = nonogram.width * nonogram.height
                self.show_hint_highlight_var.set(size <= 20*20)
            if hasattr(self, 'status'):
                self.status.set(f"Ready.")

    def _on_file_new_from_current(self, *_) -> None:
        self.nonogram_handler.loaded_nonogram_filename = None
        self.nonogram_handler.clear_hints()
        grid = self.solution_handler.get_curr_soln().fill

        self.nonogram_handler.hints_from_grid(grid)

        nonogram = self.nonogram_handler.get_nonogram()
        if nonogram:
            self.solution_handler.give_nonogram(nonogram)
            self._clear_all()
            self.draw_nonogram(nonogram)
            self.status.set(f"Ready.")

    def _on_file_export_image(self, *_) -> None:
        file_types = [('SVG image', '*.svg'), ('PDF Document', '*.pdf'), ('PNG image', '*.png'), ('JPG image', '*.jpg')]
        init_dir = ""
        file_path = filedialog.asksaveasfilename(title="Export image", initialdir=init_dir, filetypes=file_types)
        if not file_path:
            return
        self.figure.savefig(file_path, bbox_inches='tight')
        self.status.set(f"Exported image to {file_path.split("/")[-1]}.")

    def _on_file_save(self, *_) -> None:
        if not self.nonogram_handler.loaded_nonogram_filename:
            self._on_file_save_as()
            return
        self.nonogram_handler.save_file()
        self.status.set(f"Saved.")

    def _on_file_save_as(self, *_) -> None:
        file_types = [('Text format', '*.txt'), ('ASP encoding', '*.lp')]
        init_dir = ""
        file_path = filedialog.asksaveasfilename(title="Export Nonogram Encoding", initialdir=init_dir, filetypes=file_types)
        if not file_path:
            return
        self.nonogram_handler.loaded_nonogram_filename = file_path
        self.nonogram_handler.save_file()
        self.status.set(f"Saved nonogram to {file_path.split("/")[-1]}.")

    def _on_button_press(self, event: MouseEvent) -> None:
        if event.inaxes != self.axes:
            return
        self.solution_handler.use_working_soln()

        if event.button == 1 and event.ydata and event.xdata: #(left mouse button)
            nonogram = self.nonogram_handler.get_nonogram()
            assert(nonogram)
            y = ceil(nonogram.height - event.ydata - 1)
            x = ceil(event.xdata - 1)
            if y >= 0 and y < nonogram.height and x >= 0 and x < nonogram.width:
                self._on_leftclick_cell(y, x)
            elif y >= 0 and x < 0:
                self._on_leftclick_rowhint(y)
            elif x >= 0 and y < 0:
                self._on_leftclick_colhint(x)

    def _on_mouse_motion(self, event: MouseEvent) -> None:
        if self.block_hover:
            return
        
        self.block_hover = True
        self.after(100, self._unblock_mouse_motion)
    
        if event.inaxes != self.axes or not self.show_hint_highlight_var.get() or not event.ydata or not event.xdata:
            self._highlight_hint(-1, -1)
            return
        
        nonogram = self.nonogram_handler.get_nonogram()
        if not nonogram:
            return
        
        y = ceil(nonogram.height - event.ydata - 1)
        x = ceil(event.xdata - 1)
        if self.highlighted_x != x or self.highlighted_y != y:
            self._highlight_hint(x, y)

    def _unblock_mouse_motion(self):
            self.block_hover = False
            
    def _highlight_hint(self, x: int, y: int) -> None:
        # Restore default appearance of previously selected row
        for hint in self.row_hints[self.highlighted_y]:
            hint.set_fontweight('normal')
        for cell in self.pixels[self.highlighted_y]:
            cell.set_alpha(0.8)

        nonogram = self.nonogram_handler.get_nonogram()
        if not nonogram:
            return
        
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
        color_hints = self.show_hint_feedback_var.get()

        self.solution_handler.get_curr_soln().fill[row][col] = not self.solution_handler.get_curr_soln().fill[row][col]
        self.pixels[row][col].set_visible(self.solution_handler.get_curr_soln().fill[row][col])
        for hint in self.row_hints[row]:
            hint.set_color('black' if not color_hints or self.solution_handler.solves_row(row) else 'red')
        for hint in self.col_hints[col]:
            hint.set_color('black' if not color_hints or self.solution_handler.solves_col(col) else 'red')
        self.canvas.draw_idle()

    def _on_leftclick_rowhint(self, row: int) -> None:
        nonogram = self.nonogram_handler.get_nonogram()
        if not nonogram:
            return
        
        old_hint = nonogram.row_hints[row]
        new_hint = self._open_hint_edit_dialog(old_hint, nonogram.width)
        if new_hint == old_hint:
            return
        
        nonogram.row_hints[row] = new_hint
        
        for hint in self.row_hints[row]:
            hint.remove()
        
        self.row_hints[row] = []
        if not new_hint:
            hint = [self.axes.text(-0.66, nonogram.height - row - 0.6, "0", va='center', ha='center', fontsize=18, color='red')]
            if not self.show_hint_feedback_var.get() or self.solution_handler.solves_row(row):
                hint[0].set_color('black')
            self.row_hints[row] = hint
        else:
            for j, l in enumerate(reversed(new_hint)):
                hint = self.axes.text(-0.66-j*0.7, nonogram.height - row - 0.6, str(l), va='center', ha='center', fontsize=18 if l < 10 else 13, color='red')
                if not self.show_hint_feedback_var.get() or self.solution_handler.solves_row(row):
                    hint.set_color('black')
                self.row_hints[row].append(hint)
        self.canvas.draw_idle()

    def _on_leftclick_colhint(self, col: int) -> None:
        nonogram = self.nonogram_handler.get_nonogram()
        if not nonogram:
            return
        
        old_hint = nonogram.col_hints[col]
        new_hint = self._open_hint_edit_dialog(old_hint, nonogram.height)
        if new_hint == old_hint:
            return
        
        nonogram.col_hints[col] = new_hint
        
        for hint in self.col_hints[col]:
            hint.remove()
        
        self.col_hints[col] = []
        if not new_hint:
            hint = [self.axes.text(col + 0.5, nonogram.height + 0.33, "0", va='center', ha='center', fontsize=18, color='red')]
            if not self.show_hint_feedback_var.get() or self.solution_handler.solves_col(col):
                hint[0].set_color('black')
            self.col_hints[col] = hint
        else:
            for i, l in enumerate(reversed(new_hint)):
                hint = self.axes.text(col + 0.5, nonogram.height + 0.33 + i*0.8, str(l), va='center', ha='center', fontsize=18 if l < 10 else 13, color='red')
                if not self.show_hint_feedback_var.get() or self.solution_handler.solves_col(col):
                    hint.set_color('black')
                self.col_hints[col].append(hint)
        self.canvas.draw_idle()

    def _open_hint_edit_dialog(self, hint: list[int], length: int) -> List[int]:
        self.block_hover = True
        # Load the current string
        current_string = ' '.join(map(str, hint)) if hint else "0"

        # Create a custom dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Hint")
        dialog.geometry("500x150")

        # Add an entry widget
        entry = tk.Entry(dialog, width=40)
        entry.insert(0, current_string)
        entry.pack(pady=20)
        result: List[List[int]] = [hint]

        # Add a label widget for feedback
        feedback = [tk.Label(dialog, text="")]
        feedback[0].pack(pady=20)

        # Function to handle OK button click
        def on_ok():
            new_string = entry.get()
            try:
                result[0] = list(map(int, new_string.split()))
                for h in result[0]:
                    if h <= 0:
                        raise ValueError
                    
                min_len = sum(result[0]) + len(result[0]) - 1
                if min_len <= length:
                    dialog.destroy()
                else:
                    result[0] = hint
                    feedback[0].configure(text=f"Hint too long! (Needs {min_len}+ units)")
            except:
                result[0] = hint
                feedback[0].configure(text=f"Invalid hint!")

        # Add OK and Cancel buttons
        ok_button = tk.Button(dialog, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(dialog, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)

        # Bind the Enter key to the OK button command
        dialog.bind('<Return>', lambda _: on_ok())

        # Bind the Escape key to the Cancel button command
        dialog.bind('<Escape>', lambda _: dialog.destroy())

        # Focus on the entry widget so the user can start typing immediately
        entry.focus_set()

        dialog.wait_window()

        self.block_hover = False

        return result[0]

    def _on_del_window(self) -> None:
        self.quit()

    def draw_nonogram(self, nonogram: Nonogram):
        # Adjust the window size
        win_width = nonogram.width*SQUARE_SIZE
        win_height = nonogram.height*SQUARE_SIZE
        self.geometry(f"{win_width}x{win_height}")
        # self.minsize(win_width, win_height)

        # Draw the nonogram fully filled and save each pixel as a separate object, then hide them
        # The pixels are indexed by [row][column], starting at index 0!
        self.pixels: list[list[patches.Patch]] = [
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

        # Draw row hints to the left of the grid
        self.row_hints: list[list[Text]] = []
        for i, hints in enumerate(nonogram.row_hints):
            if not hints:
                hint = [self.axes.text(-0.66, nonogram.height - i - 0.6, "0", va='center', ha='center', fontsize=18, color='red')]
                if not self.show_hint_feedback_var.get() or self.solution_handler.solves_row(i):
                    hint[0].set_color('black')
                self.row_hints.append(hint)
                continue

            self.row_hints.append([])
            for j, l in enumerate(reversed(hints)):
                hint = self.axes.text(-0.66-j*0.7, nonogram.height - i - 0.6, str(l), va='center', ha='center', fontsize=18 if l < 10 else 13, color='red')
                if not self.show_hint_feedback_var.get() or self.solution_handler.solves_row(i):
                    hint.set_color('black')
                self.row_hints[-1].append(hint)

        # Draw column hints above the grid, stacked vertically
        self.col_hints: list[list[Text]] = []
        for j, hints in enumerate(nonogram.col_hints):
            if not hints:
                hint = [self.axes.text(j + 0.5, nonogram.height + 0.33, "0", va='center', ha='center', fontsize=18, color='red')]
                if not self.show_hint_feedback_var.get() or self.solution_handler.solves_col(j):
                    hint[0].set_color('black')
                self.col_hints.append(hint)
                continue

            self.col_hints.append([])
            for i, l in enumerate(reversed(hints)):
                hint = self.axes.text(j + 0.5, nonogram.height + 0.33 + i*0.8, str(l), va='center', ha='center', fontsize=18 if l < 10 else 13, color='red')
                if not self.show_hint_feedback_var.get() or self.solution_handler.solves_col(j):
                    hint.set_color('black')
                self.col_hints[-1].append(hint)

        # Setup the grid and ticks and cell index numbers
        self.axes.set_xticks(range(0, nonogram.width+1 ),
                             [""] + list(map(str, range(1, nonogram.width + 1))))
        self.axes.set_yticks(range(0, nonogram.height+1), 
                             list(map(str, reversed(range(1, nonogram.height + 1)))) + [""]) # enumerate rows from top to bottom

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

    def draw_solution(self, solution: NonogramSoln):
        color_hints = self.show_hint_feedback_var.get()
        for r, row in enumerate(solution.fill):
            for c, filled in enumerate(row):
                self.pixels[r][c].set_visible(filled)

        for r, _ in enumerate(solution.fill):
            for hint in self.row_hints[r]:
                hint.set_color('black' if not color_hints or self.solution_handler.solves_row(r) else 'red')
        for c, _ in enumerate(solution.fill[0]):
            for hint in self.col_hints[c]:
                hint.set_color('black' if not color_hints or self.solution_handler.solves_col(c) else 'red')
        self.canvas.draw_idle()

    def _on_toggle_show_hint_feedback(self, *_):
        self.draw_solution(self.solution_handler.get_curr_soln())

    def _on_toggle_show_hint_highlight(self, *_):
        self._highlight_hint(-1,-1)

    def _on_toggle_check_uniqueness(self, *_):
        if not self.check_uniqueness_var.get():
            self.find_all_solns_var.set(False)
