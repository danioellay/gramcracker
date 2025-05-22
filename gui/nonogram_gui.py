import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
        if len(args) > 1:
            self.nonogram_handler.load_file(args[1])

        self.figure_frame = tk.Frame(self)
        self.figure_frame.pack(fill=tk.BOTH, expand=True)
        self.figure, self.axes = plt.subplots()
        self.axes.set_aspect('equal')
        plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_frame)
        # self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # self.canvas.mpl_connect('button_press_event', self._on_button_press)
        # self.canvas.mpl_connect('button_release_event', self._on_button_release)
        # self.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)
        # self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.zoom_scale = 1.0
        self.panning = False
        self.cur_xlim = self.axes.get_xlim()
        self.cur_ylim = self.axes.get_ylim()
        self.x0 = None
        self.y0 = None
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
        self.minsize(win_width, win_height)
        # Draw the nonogram based on its properties
        for x in range(nonogram.width):
            for y in range(nonogram.height):
                if x % 2 and not y % 2 or not x % 2 and y % 2:
                    self.axes.fill_between([x, x+1], y, y+1, color='black')

        # Draw row hints to the left of the grid
        for i, hints in enumerate(nonogram.row_hints):
            hint_text = ' '.join(map(str, hints))
            self.axes.text(-0.5, nonogram.height - i - 0.5, hint_text, va='center', ha='right', fontsize=18)

        # Draw column hints above the grid, stacked vertically
        for j, hints in enumerate(nonogram.col_hints):
            hint_text = '\n'.join(map(str, hints))
            self.axes.text(j + 0.5, nonogram.height + 0.5, hint_text, va='bottom', ha='center', fontsize=18)  # Adjust vertical position


        # Set the limits and grid
        self.axes.set_xticks(range(0, nonogram.width+1))  # Start from 0 to avoid cutting row hints
        self.axes.set_yticks(range(0, nonogram.height+1))  # Start from 0 to avoid cutting column hints
        self.axes.yaxis.set_label_position('right')
        # self.axes.axis('equal')
        self.axes.yaxis.tick_right()
        self.axes.grid(which='both', color='black', linestyle='-', linewidth=1)

        # Redraw the canvas
        self.canvas.draw()
        self.axes.set_xlim(-max([len(rh) for rh in nonogram.row_hints])*0.75, nonogram.width + 0.5)  # Extend left
        self.axes.set_ylim(-0.5, nonogram.height + max([len(ch) for ch in nonogram.col_hints])*0.85)  # Extend top
