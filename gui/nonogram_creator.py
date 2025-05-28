# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

import tkinter as tk
from tkinter import StringVar, filedialog
import matplotlib.pyplot as plt
import random
import cv2
import numpy as np

def create_new_nonogram(parent):
    # Create a custom dialog window
    dialog = tk.Toplevel(parent)
    dialog.title("Nonogram")
    dialog.geometry("400x700")
    
    # Labels and Entry widgets for height and width
    frame = tk.Frame(dialog)
    frame.pack(side=tk.TOP)
    tk.Label(frame, text="Dimensions:", font=(None,11)).pack(side=tk.TOP)
    frame = tk.Frame(dialog)
    frame.pack(side=tk.TOP)
    tk.Label(frame, text="Width:  ").pack(side=tk.LEFT)
    width_entry = tk.Entry(frame, textvariable=StringVar(dialog, "24"), width=10)
    width_entry.pack(side=tk.RIGHT)

    frame = tk.Frame(dialog)
    frame.pack(side=tk.TOP)
    tk.Label(frame, text="Height: ").pack(side=tk.LEFT)
    height_entry = tk.Entry(frame, textvariable=StringVar(dialog, "24"), width=10)
    height_entry.pack(side=tk.RIGHT)

    # Variable to hold the selected option
    selected_option = tk.StringVar(value="empty")

    frame = tk.Frame(dialog)
    frame.pack(side=tk.TOP)
    tk.Label(frame).pack()
    tk.Label(frame, text="Nonogram contents:", font=(None,11)).pack()
    # List of options
    options = [
        ("Empty Nonogram", "empty"),
        ("Random Nonogram", "random"),
        ("From Image", "image")
    ]

    image_filename = [None]
    filename_label = [None]

    def select_image_file():
        filetypes = [
            ('All files', '*.*')
        ]

        filename = filedialog.askopenfilename(
            title='Open a file',
            initialdir='',
            filetypes=filetypes)
        
        image_filename[0] = filename
        filename_label[0].configure(text=image_filename[0].split("/")[-1])


    # Create radio buttons
    frame = tk.Frame(dialog)
    frame.pack(side=tk.TOP)
    for text, value in options:
        radio = tk.Radiobutton(frame, text=text, variable=selected_option, value=value)
        radio.pack(anchor=tk.W)
        if value == "random":
            tk.Label(frame, text="Black/White ratio:").pack()
            bw_entry = tk.Entry(frame, textvariable=StringVar(dialog, "0.42"))
            bw_entry.pack()
            tk.Label(frame, text="Pixel correlation:").pack()
            corr_entry = tk.Entry(frame, textvariable=StringVar(dialog, "1.0"))
            corr_entry.pack()
        if value == "image":
            filename_label[0] = tk.Label(frame, text="")
            filename_label[0].pack()
            tk.Button(frame, text="Select image", command=select_image_file).pack()

    dimensions = [None, None]
    probabilities = [None, None]

    def on_ok():
        try:
            dimensions[0] = int(width_entry.get())
            dimensions[1] = int(height_entry.get())
            if selected_option.get() == "random":
                probabilities[0] = float(bw_entry.get())
                probabilities[1] = float(corr_entry.get())
            dialog.destroy()
        except ValueError:
            tk.messagebox.showerror("Invalid input", "Please enter valid numbers.")

    def on_cancel():
        dialog.destroy()

    # Buttons for OK and Cancel
    cancel_button = tk.Button(dialog, text="Cancel", command=on_cancel)
    cancel_button.pack(side="left")
    ok_button = tk.Button(dialog, text="OK", command=on_ok)
    ok_button.pack(side="right")


    # Wait for the dialog to close
    dialog.wait_window()

    # Process results
    if dimensions == [None, None]:
        return (None, None), None
    
    if selected_option.get() == "empty":
        return tuple(dimensions), None
    
    if selected_option.get() == "random":
        # generate pixel grid
        grid = []
        for _ in range(dimensions[1]): 
            row = [True if random.random() < probabilities[0] else False for _ in range(dimensions[0])] 
            grid.append(row)

        new_grid = []
        for r, row in enumerate(grid):
            new_grid.append(row)
            for c, fill in enumerate(row):
                neighbour_count = 0
                if r > 0 and grid[r-1][c]:
                    neighbour_count += 1
                if r < dimensions[1] - 1 and grid[r+1][c]:
                    neighbour_count += 1
                if c > 0 and grid[r][c-1]:
                    neighbour_count += 1
                if c < dimensions[0] - 1 and grid[r][c+1]:
                    neighbour_count += 1
                new_grid[r][c] = random.random() < neighbour_count*probabilities[1]/4

        return tuple(dimensions), new_grid

    if selected_option.get() == "image":
        # Load the image
        image = cv2.imread(image_filename[0], cv2.IMREAD_GRAYSCALE)
        
        # Get image dimensions
        height, width = image.shape
        brightness_threshold = 120

        # Calculate grid cell dimensions
        grid_width, grid_height = tuple(dimensions)
        cell_height = height // grid_height
        cell_width = width // grid_width

        # Create an empty grid
        grid = np.zeros((grid_height, grid_width), dtype=np.uint8)

        # Calculate average brightness for each grid cell
        for i in range(grid_height):
            for j in range(grid_width):
                # Define the cell boundaries
                y1 = i * cell_height
                y2 = (i + 1) * cell_height
                x1 = j * cell_width
                x2 = (j + 1) * cell_width

                # Extract the cell from the image
                cell = image[y1:y2, x1:x2]

                # Calculate the average brightness
                average_brightness = np.mean(cell)

                # Apply the brightness threshold
                grid[i, j] = 255 if average_brightness > brightness_threshold else 0
                
        # Scale the grid to original image size for display
        # scaled_grid = cv2.resize(grid, (width, height), interpolation=cv2.INTER_NEAREST)

        # Display the original and rasterized images using Matplotlib
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.title('Original Image')
        plt.imshow(image, cmap='gray')
        plt.subplot(1, 2, 2)
        plt.title('Rasterized Image')
        plt.imshow(grid, cmap='gray')
        plt.show()
        return tuple(dimensions), (grid != 255).tolist()
