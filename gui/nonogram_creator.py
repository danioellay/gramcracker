# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

import tkinter as tk
from tkinter import StringVar, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import random

import cv2
import numpy as np

def spinbox_int(master, title, callback, min_value, max_value, initial_value, step=1):
    tk.Label(master, text=title).pack(side=tk.LEFT, padx=5, pady=1)
    var = StringVar(master, value=str(initial_value))
    def pseudo_callback(*_):
        try:
            num = int(var.get())
        except:
            return
        if num > max_value or num < min_value:
            return
        return callback(num)
    var.trace_add("write", pseudo_callback)
    max_strlen = max(len(str(max_value)), len(str(min_value)))

    sb = tk.Spinbox(master,
                    from_=min_value,
                    to=max_value,
                    increment=step,
                    width = 2 * max_strlen + 2,
                    textvariable=var)
    sb.pack(side=tk.RIGHT, padx=5, pady=1)
    
    return sb

def spinbox_float(master, title, callback, min_value, max_value, initial_value, step=0.1):
    tk.Label(master, text=title).pack(side=tk.LEFT, padx=5, pady=1)
    var = StringVar(master, value=str(initial_value))
    def pseudo_callback(*_):
        try:
            num = float(var.get())
        except:
            return
        if num > max_value or num < min_value:
            return
        return callback(num)
    
    var.trace_add("write", pseudo_callback)
    max_strlen = max(len(str(max_value)), len(str(min_value)))

    sb = tk.Spinbox(master,
                    from_=min_value,
                    to=max_value,
                    increment=step,
                    width = 2 * max_strlen + 2,
                    textvariable=var)
    sb.pack(side=tk.RIGHT, padx=5, pady=1)
    
    return sb


class NonogramCreator(tk.Toplevel):
    width: int = 5
    height: int = 5
    bwratio: float = 0.5
    pxcorr: float = 0.8
    threshold: int = 127
    im_file_path: str = ""
    grid = np.full((height, width), 255, dtype=np.uint8)
    success: bool = True

    def reload(self):
        opt_str = self.selected_option_var.get()
        if opt_str == "empty":
            # print("reload->empty")
            self.grid = np.full((self.height, self.width), 255, dtype=np.uint8)
        
        elif opt_str == "random":
            # print("reload->random")
            # generate random boolean matrix
            initial = np.zeros((self.height, self.width), dtype=np.uint8)
            for row in range(self.height):
                for col in range(self.width):
                    initial[row][col] = 0 if random.random() < self.bwratio else 255

            # correlate neighboring values in matrix
            self.grid = np.zeros((self.height, self.width), dtype=np.uint8)
            for row in range(self.height):
                for col in range(self.width):
                    neighbour_count = 0
                    if row > 0 and initial[row-1][col]:
                        neighbour_count += 1
                    if row < self.height - 1 and initial[row+1][col]:
                        neighbour_count += 1
                    if col > 0 and initial[row][col-1]:
                        neighbour_count += 1
                    if col < self.width - 1 and initial[row][col+1]:
                        neighbour_count += 1
                    self.grid[row][col] = 0 if random.random() < neighbour_count*self.pxcorr/4 else 255

        elif opt_str == "image" and hasattr(self, 'im_original'):
            # print("reload->image")

            # Resize the image to a lower resolution
            im_scaled = cv2.resize(self.im_original, (self.width, self.height))

            # Apply a binary threshold to the image
            _, self.grid = cv2.threshold(im_scaled, self.threshold, 255, cv2.THRESH_BINARY)

        self.update()
        plt.imshow(self.grid, 'gray', vmin=0, vmax=255)
        self.canvas.draw()

        # self.redraw_grid()

    def invert(self):
        for row in range(self.height):
            for col in range(self.width):
                x = self.grid[row][col]
                self.grid[row][col] = 255 if x == 0 else 0
        plt.imshow(self.grid, 'gray', vmin=0, vmax=255)
        self.canvas.draw()

    def __init__(self, parent):
        # Create a custom dialog window
        tk.Toplevel.__init__(self, parent)
        self.title("Nonogram Generator")
        self.geometry("1050x650")
        self.minsize(1050, 650)

        leftframe = tk.Frame(self)
        leftframe.pack(side=tk.LEFT, fill=tk.X, expand=False)
        rightframe = tk.Frame(self)
        rightframe.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        bottomframe = tk.Frame(leftframe)
        bottomframe.pack(side=tk.BOTTOM, anchor="s")

        # Labels and Entry widgets for height and width
        frame = tk.Frame(leftframe)
        frame.pack(side=tk.TOP)
        tk.Label(frame, text="Dimensions: ", font=("", 12)).grid(row=0,column=0, columnspan=1, pady=1)

        frame = tk.Frame(leftframe)
        frame.pack(side=tk.TOP)
        spinbox_int(frame, "Width:", self._on_set_width, 1, 1024, self.width)

        frame = tk.Frame(leftframe)
        frame.pack(side=tk.TOP)
        spinbox_int(frame, "Height:", self._on_set_height, 1, 1024, self.height)
        
        # Variable to hold the selected option
        self.selected_option_var = StringVar(value="empty")
        self.selected_option_var.trace_add('write', self._on_option_select)

        frame = tk.Frame(leftframe)
        frame.pack(side=tk.TOP)
        tk.Label(frame).pack()
        tk.Label(frame, text="Nonogram contents:", font=("",12)).pack()

        # List of options
        options = [
            ("Empty Nonogram", "empty"),
            ("Random Nonogram", "random"),
            ("From Image", "image")
        ]

        # Create radio buttons
        frame = tk.Frame(leftframe)
        frame.pack(side=tk.TOP)
        
        for text, value in options:
            radio = tk.Radiobutton(frame, text=text, font=("",11), variable=self.selected_option_var, value=value)
            radio.pack(side=tk.TOP)
            if value == "random":
                frame2 = tk.Frame(frame)
                frame2.pack(side=tk.TOP)
                self.bwratio_sb = spinbox_float(frame2, "B/W ratio:", self._on_set_bwratio, 0.0, 1.0, self.bwratio)
                frame2 = tk.Frame(frame)
                frame2.pack(side=tk.TOP)
                self.pxcorr_sb = spinbox_float(frame2, "Pixel corr.:", self._on_set_pxcorr, 0.0, 1.0, self.pxcorr)
                self.bwratio_sb.configure(state=tk.DISABLED)
                self.pxcorr_sb.configure(state=tk.DISABLED)
            if value == "image":
                frame2 = tk.Frame(frame)
                frame2.pack(side=tk.TOP)
                self.file_select_bt = tk.Button(frame2, text="Select image file", command=self._on_select_image_file)
                self.file_select_bt.pack(side=tk.LEFT)
                frame2 = tk.Frame(frame)
                frame2.pack(side=tk.TOP)
                self.threshold_sb = spinbox_int(frame2, "Threshold:", self._on_set_threshold, 0, 255, self.threshold, 10)
                self.file_select_bt.configure(state=tk.DISABLED)
                self.threshold_sb.configure(state=tk.DISABLED)
        
        tk.Label(leftframe).pack()

        # Buttons for OK and Cancel
        tk.Button(bottomframe, text="Cancel", command=self._on_cancel).grid(row=0, column=0)
        tk.Button(bottomframe, text="Reload", command=self.reload).    grid(row=0, column=1)
        tk.Button(bottomframe, text="Invert", command=self.invert).    grid(row=0, column=2)
        tk.Button(bottomframe, text="OK",     command=self.destroy).   grid(row=0, column=3)

        # Create a Tkinter label to display the image
        self.figure, self.axes = plt.subplots()
        self.axes.set_aspect('equal')
        self.figure.tight_layout()
        plt.imshow(self.grid, 'gray', vmin=0, vmax=255)
        self.canvas = FigureCanvasTkAgg(self.figure, master=rightframe)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _on_cancel(self, *_):
        self.success = False
        self.destroy()
        
    def _on_set_width(self, input):
        if self.width == input:
            return
        self.width = input
        # print(f"width = {self.width}.. resizing mat")
        self.mat = np.zeros((self.height, self.width), dtype=np.uint8)
        self.reload()

    def _on_set_height(self, input):
        if self.height == input:
            return
        self.height = input
        # print(f"height = {self.height}.. resizing mat")
        self.mat = np.zeros((self.height, self.width), dtype=np.uint8)
        self.reload()

    def _on_set_bwratio(self, input):
        if self.bwratio == input:
            return
        self.bwratio = input
        # print(f"bwdist = {self.bwratio}")
        self.reload()
        
    def _on_set_pxcorr(self, input):
        if self.pxcorr == input:
            return
        self.pxcorr = input
        # print(f"pxcorr = {self.pxcorr}")
        self.reload()

    def _on_set_threshold(self, input):
        if self.threshold == input:
            return
        self.threshold = input
        # print(f"threshold = {self.threshold}")
        self.reload()

    def _on_option_select(self, *_):
        opt_str = self.selected_option_var.get()
        if opt_str == "empty":
            self.file_select_bt.configure(state=tk.DISABLED)
            self.threshold_sb.configure(state=tk.DISABLED)
            self.bwratio_sb.configure(state=tk.DISABLED)
            self.pxcorr_sb.configure(state=tk.DISABLED)
        if opt_str == "random":
            self.file_select_bt.configure(state=tk.DISABLED)
            self.threshold_sb.configure(state=tk.DISABLED)
            self.bwratio_sb.configure(state=tk.NORMAL)
            self.pxcorr_sb.configure(state=tk.NORMAL)
        if opt_str == "image":
            self.file_select_bt.configure(state=tk.NORMAL)
            self.threshold_sb.configure(state=tk.NORMAL)
            self.bwratio_sb.configure(state=tk.DISABLED)
            self.pxcorr_sb.configure(state=tk.DISABLED)
        if opt_str != "image":
            self.reload()

    def _on_select_image_file(self, *_):
        filetypes = [('All files', '*.*')]

        filename = filedialog.askopenfilename(
            title='Open a file',
            initialdir='images/',
            filetypes=filetypes)
        
        if not filename or self.im_file_path == filename:
            return
        self.im_file_path = filename
        self.im_original = cv2.imread(self.im_file_path, cv2.IMREAD_GRAYSCALE)

        self.file_select_bt.configure(font=("", 8))
        if self.im_original is None:
            print("Error: Could not read image at " + self.im_file_path)
            self.file_select_bt.configure(text="Error loading image")
        else:
            w, h = len(self.im_original), len(self.im_original[0])
            self.file_select_bt.configure(text=''.join(filename.split("/")[-1].split(".")[:-1]) + f"({w}x{h})")
        self.reload()

    def get(self):
        # Wait for the dialog to close
        self.wait_window()
        if self.success:
            return self.width, self.height, (self.grid != 255).tolist()
        else:
            return None, None, None
