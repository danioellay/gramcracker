# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus
# run with: python3 -m gui [optional parameter: nonogram filename] [optional parameter: solver name]
#    e.g. : python3 -m gui nonograms/example_05.lp symbolic-block-start

import tkinter as tk
from tkinter import filedialog, Event, BooleanVar
import os
from os import listdir
from os.path import isfile, join

from math import ceil

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.text import Text

from .common import *
from .nonogram_creator import NonogramCreator
from .handlers.nonogram_handler import NonogramHandler
from .handlers.solution_handler import SolutionHandler

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
SQUARE_SIZE = 50 #default side length of a grid cell, pixels


class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, height=50)
        self.label = tk.Label(self)
        self.label.pack(side=tk.LEFT)
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def set(self, newText):
        self.label.config(text=newText)
    
    def clear(self):
        self.label.config(text="")


class NonogramGUI(tk.Tk):

    def __init__(self, args) -> None:
        tk.Tk.__init__(self)
        # Setup data handlers
        self.nonogram_handler = NonogramHandler()
        self.solution_handler = SolutionHandler()

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

        self.solver_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(menu=self.solver_menu, label="Solver")
        self.check_uniqueness_var = BooleanVar(value=True)
        self.solver_menu.add_checkbutton(label="Also check uniqueness", variable=self.check_uniqueness_var)

        solvers = [f for f in listdir("solvers/") if isfile(join("solvers/", f)) and f.endswith(".lp")]
        for i, solver in enumerate(solvers):
            # Create a lambda function that calls _on_solver with the correct solver
            self.solver_menu.add_command(label=solver.split(".")[0], accelerator=f"Ctrl+{i+1}", command=lambda s=solver: self._on_solver(s))
            self.bind_all(f"<Control-Key-{i+1}>", lambda e, s=solver: self._on_solver(s))

        self.view_menu = tk.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(menu=self.view_menu, label="View")
        self.show_hint_feedback_var = BooleanVar(value=True)
        self.show_hint_feedback_var.trace_add('write', self._on_toggle_show_hint_feedback)
        self.view_menu.add_checkbutton(label="Color hints as correctness feedback", variable=self.show_hint_feedback_var)
        self.show_hint_highlight_var = BooleanVar(value=True)
        self.show_hint_highlight_var.trace_add('write', self._on_toggle_show_hint_highlight)
        self.view_menu.add_checkbutton(label="Highlight hovered cell hints", variable=self.show_hint_highlight_var)

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
        self.status.set("halsd")

        # Setup button event callbacks
        self.canvas.mpl_connect('button_press_event', self._on_button_press)
        # self.canvas.mpl_connect('button_release_event', self._on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)
        # self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.block_hover = False

        # Process launch arguments
        if len(args) > 1:
            self.nonogram_handler.load_file(args[1])
            self.solution_handler.give_nonogram(self.nonogram_handler.get_nonogram())

        self.draw_nonogram(self.nonogram_handler.get_nonogram())

        if len(args) > 2:
            self._on_solver(args[2])

    def run(self) -> None:
        # Finish setting up the GUI and enter mainloop
        self.update()
        self.update_idletasks()
        self.focus_force()
        return self.mainloop()
    
    def _clear_all(self):
        if hasattr(self, "pixels"):
            for r in self.pixels:
                for c in r:
                    c.remove()
            self.pixels.clear()
            self.pixels = None

        if hasattr(self, "col_hints"):
            for h in self.col_hints:
                h.remove()
            self.col_hints.clear()
            self.col_hints = None

        if hasattr(self, "row_hints"):
            for h in self.row_hints:
                h.remove()
            self.row_hints.clear()
            self.row_hints = None

        plt.cla()

    def _on_solver(self, name: str, *_):
        res = self.solution_handler.run_solver(name.split(".")[0], self.check_uniqueness_var.get())
        self.status.set(res)
        self.draw_solution(self.solution_handler.working_solution)
    
    def _on_file_open(self, *_):
        file_types = [('ASP encoding', '*.lp'), ('Raw format (UNIMPLEMENTED)', '*.txt')]
        init_dir = "nonograms"
        file_path = filedialog.askopenfilename(title="Select a file encoding a Nonogram", initialdir=init_dir, filetypes=file_types)
        if not file_path:
            return
        self.nonogram_handler.load_file(file_path)
        nonogram = self.nonogram_handler.get_nonogram()
        self._clear_all()
        self.draw_nonogram(nonogram)
        self.solution_handler.give_nonogram(nonogram)

    def _on_file_new(self, *_):
        creator = NonogramCreator(self)
        width, height, grid = creator.get()
        if not width or not height:
            return
        
        self._clear_all()
        self.nonogram_handler.loaded_nonogram_filename = None
        
        if grid:
            self.nonogram_handler.hints_from_grid(grid)
        else:
            self.nonogram_handler.resize(width, height)
        
        nonogram = self.nonogram_handler.get_nonogram()
        self.solution_handler.give_nonogram(nonogram)
        if hasattr(self, "axes"):
            self.draw_nonogram(nonogram)

    def _on_file_new_from_current(self, *_):
        self.nonogram_handler.loaded_nonogram_filename = None
        self.nonogram_handler.clear_hints()
        grid = self.solution_handler.working_solution.fill

        self.nonogram_handler.hints_from_grid(grid)

        nonogram = self.nonogram_handler.get_nonogram()
        self.solution_handler.give_nonogram(nonogram)
        self._clear_all()
        self.draw_nonogram(nonogram)

    def _on_file_export_image(self, *_):
        file_types = [('SVG image', '*.svg'), ('PDF Document', '*.pdf'), ('PNG image', '*.png'), ('JPG image', '*.jpg')]
        init_dir = ""
        file_path = filedialog.asksaveasfilename(title="Export image", initialdir=init_dir, filetypes=file_types)
        if not file_path:
            return
        self.figure.savefig(file_path, bbox_inches='tight')

    def _on_file_save(self, *_):
        if not self.nonogram_handler.loaded_nonogram_filename:
            return self._on_file_save_as()
        self.nonogram_handler.save_file()

    def _on_file_save_as(self, *_):
        file_types = [('Logic Program', '*.lp')]
        init_dir = ""
        file_path = filedialog.asksaveasfilename(title="Export Nonogram Encoding", initialdir=init_dir, filetypes=file_types)
        if not file_path:
            return
        self.nonogram_handler.loaded_nonogram_filename = file_path
        self.nonogram_handler.save_file()

    def _on_button_press(self, event: Event):
        if event.inaxes != self.axes:
            return
        if not hasattr(self.solution_handler, "working_solution"):
            return
        
        if event.button == 1: #(left mouse button)
            nonogram = self.nonogram_handler.get_nonogram()
            y = ceil(nonogram.height - event.ydata - 1)
            x = ceil(event.xdata - 1)
            if y >= 0 and y < nonogram.height and x >= 0 and x < nonogram.width:
                self._on_leftclick_cell(y, x)
            elif y >= 0 and x < 0:
                self._on_leftclick_rowhint(y)
            elif x >= 0 and y < 0:
                self._on_leftclick_colhint(x)

    def _on_mouse_motion(self, event: Event):
        if self.block_hover:
            return
        
        if event.inaxes != self.axes or not hasattr(self.solution_handler, "working_solution") or not self.show_hint_highlight_var.get():
            self._highlight_hint(-1, -1)
            return
        
        nonogram = self.nonogram_handler.get_nonogram()
        y = ceil(nonogram.height - event.ydata - 1)
        x = ceil(event.xdata - 1)
        if self.highlighted_x != x or self.highlighted_y != y:
            self._highlight_hint(x, y)

    def _highlight_hint(self, x: int, y: int):
        # Restore default appearance of previously selected row
        self.row_hints[self.highlighted_y].set_fontweight('normal')
        for cell in self.pixels[self.highlighted_y]:
            cell.set_alpha(0.8)

        nonogram = self.nonogram_handler.get_nonogram()
        # Highlight newly selected row
        if y >= 0 and y < nonogram.height:
            self.row_hints[y].set_fontweight('bold')
            for cell in self.pixels[y]:
                cell.set_alpha(0.88)
        self.highlighted_y = y

        # Restore default appearance of previously selected column
        self.col_hints[self.highlighted_x].set_fontweight('normal')
        for row in self.pixels:
            row[self.highlighted_x].set_alpha(0.8)

        # Highlight newly selected column
        if x >= 0 and x < nonogram.width:
            self.col_hints[x].set_fontweight('bold')
            for row in self.pixels:
                row[x].set_alpha(0.88)
            # Need to overwrite one pixel
            self.pixels[y][self.highlighted_x].set_alpha(0.88)
        self.highlighted_x = x

        self.canvas.draw_idle()

    def _on_leftclick_cell(self, row: int, col: int):
        color_hints = self.show_hint_feedback_var.get()

        self.solution_handler.working_solution.fill[row][col] = not self.solution_handler.working_solution.fill[row][col]
        self.pixels[row][col].set_visible(self.solution_handler.working_solution.fill[row][col])
        self.row_hints[row].set_color('black' if not color_hints or self.solution_handler.solves_row(row) else 'red')
        self.col_hints[col].set_color('black' if not color_hints or self.solution_handler.solves_col(col) else 'red')
        self.canvas.draw_idle()

    def _on_leftclick_rowhint(self, row: int):
        nonogram = self.nonogram_handler.get_nonogram()
        if not nonogram:
            return
        
        old_hint = nonogram.row_hints[row]
        new_hint = self._open_hint_edit_dialog(old_hint, nonogram.width)
        if new_hint != None:
            nonogram.row_hints[row] = new_hint
            self.row_hints[row].set_text(' '.join(map(str, nonogram.row_hints[row])) if nonogram.row_hints[row] else "0")
            self.row_hints[row].set_color('black' if not self.show_hint_highlight_var.get() or self.solution_handler.solves_row(row) else 'red')
            self.canvas.draw_idle()

    def _on_leftclick_colhint(self, col: int):
        nonogram = self.nonogram_handler.get_nonogram()
        if not nonogram:
            return
        
        old_hint = nonogram.col_hints[col]
        new_hint = self._open_hint_edit_dialog(old_hint, nonogram.height)
        if new_hint != None:
            nonogram.col_hints[col] = new_hint
            self.col_hints[col].set_text('\n'.join(map(str, nonogram.col_hints[col])) if nonogram.col_hints[col] else "0")
            self.col_hints[col].set_color('black' if not self.show_hint_highlight_var.get() or self.solution_handler.solves_col(col) else 'red')
            self.canvas.draw_idle()

    def _open_hint_edit_dialog(self, hint: list[int], length: int):
        self.block_hover = True
        # Load the current string
        current_string = ' '.join(map(str, hint)) if hint else "0"

        # Create a custom dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Hint")
        dialog.geometry("400x150")

        # Add an entry widget
        entry = tk.Entry(dialog, width=40)
        entry.insert(0, current_string)
        entry.pack(pady=20)
        self.result = None

        # Function to handle OK button click
        def on_ok():
            new_string = entry.get()
            try:
                self.result = list(map(int, new_string.split()))
                dialog.destroy()
            except:
                print(f"invalid hint: {new_string}")

        # Add OK and Cancel buttons
        ok_button = tk.Button(dialog, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(dialog, text="Cancel", command=dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)

        # Bind the Enter key to the OK button command
        dialog.bind('<Return>', lambda event: on_ok())

        # Bind the Escape key to the Cancel button command
        dialog.bind('<Escape>', lambda event: dialog.destroy())

        # Focus on the entry widget so the user can start typing immediately
        entry.focus_set()

        dialog.wait_window()

        self.block_hover = False

        return self.result

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
        self.pixels: list[list[patches.Patch]] = [[None for _ in range(nonogram.width)] for _ in range(nonogram.height)]
        for x in range(nonogram.width):
            col = x
            for y in range(nonogram.height):
                row = nonogram.height - y - 1
                # self.axes.text(x,y,f"{row}|{col}", fontsize=8)
                pixel = patches.Rectangle((x, y), 1, 1, linewidth=0, facecolor='black', alpha=0.8)
                self.axes.add_patch(pixel)
                self.pixels[row][col] = pixel
                pixel.set_visible(False)

        # Draw row hints to the left of the grid
        self.row_hints: list[Text] = []
        for i, hints in enumerate(nonogram.row_hints):
            hint_text = ' '.join(map(str, hints)) if hints else "0"
            hint = self.axes.text(-0.5, nonogram.height - i - 0.5, hint_text, va='center', ha='right', fontsize=18, color='red')
            if (not hints or len(hints) == 1 and hints[0] == 0) or not self.show_hint_feedback_var.get():
                hint.set_color('black')
            self.row_hints.append(hint)

        # Draw column hints above the grid, stacked vertically
        self.col_hints: list[Text] = []
        for j, hints in enumerate(nonogram.col_hints):
            hint_text = '\n'.join(map(str, hints)) if hints else "0"
            hint = self.axes.text(j + 0.5, nonogram.height + 0.5, hint_text, va='bottom', ha='center', fontsize=18, color='red')
            if (not hints or len(hints) == 1 and hints[0] == 0) or not self.show_hint_feedback_var.get():
                hint.set_color('black')
            self.col_hints.append(hint)

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
        self.axes.set_xlim(-0.75*max([len(rh) for rh in nonogram.row_hints]), nonogram.width)
        self.axes.set_ylim(-0, nonogram.height + 0.9*max([len(ch) for ch in nonogram.col_hints]))
        self.canvas.draw_idle()
        self.highlighted_x, self.highlighted_y = -1, -1

    def draw_solution(self, solution: NonogramSoln):
        color_hints = self.show_hint_feedback_var.get()
        for r, row in enumerate(solution.fill):
            self.row_hints[r].set_color('black' if not color_hints or self.solution_handler.solves_row(r) else 'red')
            for c, filled in enumerate(row):
                self.col_hints[c].set_color('black' if not color_hints or self.solution_handler.solves_col(c) else 'red')
                self.pixels[r][c].set_visible(filled)
        self.canvas.draw_idle()

    def _on_toggle_show_hint_feedback(self, *_):
        self.draw_solution(self.solution_handler.working_solution)

    def _on_toggle_show_hint_highlight(self, *_):
        self._highlight_hint(-1,-1)
