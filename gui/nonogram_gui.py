# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus
# run with: python3 -m gui [optional parameter: nonogram filename]

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from .handlers.nonogram_handler import NonogramHandler

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
SQUARE_SIZE = 50 #default side length of a grid cell, pixels

class NonogramGUI(tk.Tk):

    def __init__(self, args) -> None:
        tk.Tk.__init__(self)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.title("Nonogram GUI")
        self.protocol("WM_DELETE_WINDOW", self._on_del_window)
        self.protocol("tk::mac::Quit", self._on_del_window)

        self.nonogram_handler = NonogramHandler()

        self.figure_frame = tk.Frame(self)
        self.figure_frame.pack(fill=tk.BOTH, expand=True)
        self.figure, self.axes = plt.subplots()
        self.axes.set_aspect('equal')
        plt.subplots_adjust(left=0.05, right=0.9, top=1.0, bottom=0.0)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_frame)
        # self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # self.canvas.mpl_connect('button_press_event', self._on_button_press)
        # self.canvas.mpl_connect('button_release_event', self._on_button_release)
        # self.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)
        # self.canvas.mpl_connect('scroll_event', self._on_scroll)
        if len(args) > 1:
            self.nonogram_handler.load_file(args[1])
            self.draw_nonogram()

    def run(self) -> None:
        self.update()
        self.update_idletasks()
        self.focus_force()
        return self.mainloop()
    
    def _on_del_window(self) -> None:
        self.quit()

    def draw_nonogram(self):
        # Get the current nonogram from the handler
        nonogram = self.nonogram_handler.get_nonogram()  # Assuming this method exists

        # Adjust the window size
        win_width = nonogram.width*SQUARE_SIZE
        win_height = nonogram.height*SQUARE_SIZE
        self.geometry(f"{win_width}x{win_height}")
        # self.minsize(win_width, win_height)

        # Draw the nonogram fully filled and save each pixel as a separate object, then hide them
        # The pixels are indexed by [row][column], starting at index 1!
        self.pixels: list[list[patches.Patch]] = [[None for _ in range(nonogram.width + 1)] for _ in range(nonogram.height + 1)]
        for x in range(nonogram.width):
            col = x + 1
            for y in range(nonogram.height):
                row = nonogram.height - y
                # self.axes.text(x,y,f"{row}|{col}", fontsize=8)
                pixel = patches.Rectangle((x, y), 1, 1, linewidth=0, facecolor='black', alpha=0.667)
                self.axes.add_patch(pixel)
                self.pixels[row][col] = pixel
                # pixel.set_visible(False)

        # Draw row hints to the left of the grid
        for i, hints in enumerate(nonogram.row_hints):
            hint_text = ' '.join(map(str, hints))
            self.axes.text(-0.5, nonogram.height - i - 0.5, hint_text, va='center', ha='right', fontsize=18)

        # Draw column hints above the grid, stacked vertically
        for j, hints in enumerate(nonogram.col_hints):
            hint_text = '\n'.join(map(str, hints))
            self.axes.text(j + 0.5, nonogram.height + 0.5, hint_text, va='bottom', ha='center', fontsize=18) 

        # Setup the grid and ticks and cell index numbers
        self.axes.set_xticks(range(0, nonogram.width+1 ),
                             ["column: "] + list(map(str, range(1, nonogram.width + 1))))
        self.axes.set_yticks(range(0, nonogram.height+1), 
                             list(map(str, reversed(range(1, nonogram.height + 1)))) + ["row:"]) # enumerate rows from top to bottom

        # Further customize the plots appearance, like adding a grid and removing the frame
        self.axes.yaxis.set_label_position('right')
        self.axes.yaxis.tick_right()
        plt.setp(self.axes.xaxis.get_majorticklabels(), ha="right",  va="top" )
        plt.setp(self.axes.yaxis.get_majorticklabels(), va="bottom", ha="left")
        self.axes.grid(which='both', color='black', linestyle='-', linewidth=1)
        self.axes.spines['top'   ].set_visible(False)
        self.axes.spines['right' ].set_visible(False)
        self.axes.spines['bottom'].set_visible(False)
        self.axes.spines['left'  ].set_visible(False)

        # Redraw the canvas
        self.canvas.draw()

        # Set the xy limits so that the entire nonogram plus hints are visible
        self.axes.set_xlim(-0.75*max([len(rh) for rh in nonogram.row_hints]), nonogram.width)
        self.axes.set_ylim(-0, nonogram.height + 0.9*max([len(ch) for ch in nonogram.col_hints]))

