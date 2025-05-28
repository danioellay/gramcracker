# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *

class NonogramHandler:
    def __init__(self):
        self.loaded_nonogram: Nonogram | None = None
        self.loaded_nonogram_filename: str | None = None

    def load_file(self, path: str) -> None:
        """Open the logic program file at the specified path and load the encoded nonogram"""
        with open(path, 'r') as file:
            lines = file.readlines()
        
        #TODO: check which file ending the filename has and switch between parsers

        width, height = 0, 0
        row_hints = [[] for _ in range(height)]
        col_hints = [[] for _ in range(width)]

        for line in lines:
            line = line.strip()
            if line.startswith('#const w ='):
                width = int(line.split('=')[1].strip().split('.', 1)[0])
                row_hints = [[] for _ in range(height if height else width)]
            elif line.startswith('#const h ='):
                height = int(line.split('=')[1].strip().split('.', 1)[0])
                row_hints = [[] for _ in range(height)]
                col_hints = [[] for _ in range(width)]
            elif line.startswith('row_hint('):
                parts = line.split('(')[1].split(')')[0].split(',')
                row, hint_index, block_length = map(int, parts)
                while len(row_hints) <= row - 1:
                    row_hints.append([])
                while len(row_hints[row - 1]) <= hint_index - 1:
                    row_hints[row - 1].append(0)
                row_hints[row - 1][hint_index - 1] = block_length
            elif line.startswith('col_hint('):
                parts = line.split('(')[1].split(')')[0].split(',')
                col, hint_index, block_length = map(int, parts)
                while len(col_hints) <= col - 1:
                    col_hints.append([])
                while len(col_hints[col - 1]) <= hint_index - 1:
                    col_hints[col - 1].append(0)
                col_hints[col - 1][hint_index - 1] = block_length

        self.loaded_nonogram = Nonogram(width, height, row_hints, col_hints)
        self.loaded_nonogram_filename = path

    def hints_from_grid(self, grid: List[List[bool]]):
        """Take a rectangular grid of booleans and convert it to a nonogram, then use it as loaded nonogram"""
        width = len(grid)
        height = len(grid[0])
        
        def get_hints(line):
            hints = []
            current = 0
            for cell in line:
                if cell:
                    current += 1
                else:
                    if current > 0:
                        hints.append(current)
                        current = 0
            if current > 0:
                hints.append(current)

            return hints if hints else [0]
        
        # Compute row hints
        row_hints = []
        for i in range(height):
            hints = get_hints(grid[i])
            row_hints.append(hints)
            
        # Compute column hints
        col_hints = []
        for j in range(width):
            column = [grid[i][j] for i in range(height)]
            hints = get_hints(column)
            col_hints.append(hints)

        # Create the nonogram and save it
        self.loaded_nonogram = Nonogram(width, height, row_hints, col_hints)
        self.loaded_nonogram_filename = None

    def clear_hints(self):
        """Remove all row and column hints from the loaded nonogram"""
        if not self.loaded_nonogram:
            print("Error: No nonogram loaded to clear hints in")
            return
        
        self.loaded_nonogram.col_hints = [[0] for _ in range(self.loaded_nonogram.width)]
        self.loaded_nonogram.row_hints = [[0] for _ in range(self.loaded_nonogram.height)]
        self.loaded_nonogram_filename = None

    def resize(self, width: int, height: int):
        """Adjust the dimensions of the loaded nonogram and remove all hints (calls clear_hints)"""        
        self.loaded_nonogram_filename = None
        self.loaded_nonogram = Nonogram(width, height, [], [])
        self.clear_hints()

    def save_file(self, path: str = ""):
        """Write a logic program encoding the loaded nonogram to the path specified, or to the original path it was loaded from"""
        if path == "":
            if self.loaded_nonogram_filename:
                path = self.loaded_nonogram_filename
            else:
                print("Error: No path to save the file to")
                return
        
        nonogram = self.get_nonogram()
        if not nonogram:
            print("Error: No nonogram to save")
            return
        
        with open(path, 'w') as f:
            f.write(f"%%% ASP Nonogram solver\n")
            f.write(f"%%% Problem Instance encoding\n")
            f.write(f"%%% {nonogram.width}x{nonogram.height} Nonogram\n")
            f.write(f"#const w = {nonogram.width}.  % Size of the Nonogram (w x h bw image)\n")
            f.write(f"#const h = {nonogram.height}.\n\n")
            f.write(f"% Hints for rows\n")
            f.write(f"% Format: row_hint(Row, HintIndex, BlockLength)\n")
            for row_num, hints in enumerate(nonogram.row_hints, start=1):
                for idx, length in enumerate(hints, start=1):
                    f.write(f"row_hint({row_num}, {idx}, {length}).\n")
            f.write("\n% Hints for columns\n")
            f.write("% Format: col_hint(Column, HintIndex, BlockLength)\n")
            for col_num, hints in enumerate(nonogram.col_hints, start=1):
                for idx, length in enumerate(hints, start=1):
                    f.write(f"col_hint({col_num}, {idx}, {length}).\n")

    def get_nonogram(self) -> Nonogram | None:
        """Get a reference to the currently loaded nonogram"""
        return self.loaded_nonogram
