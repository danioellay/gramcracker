from gui.common import *

class NonogramHandler:
    def load_file(self, filename: str) -> None:
        self.loaded_nonogram_filename = filename
        with open(filename, 'r') as file:
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

    def clear_hints(self):
        self.loaded_nonogram.col_hints = [[0] for _ in range(self.loaded_nonogram.width)]
        self.loaded_nonogram.row_hints = [[0] for _ in range(self.loaded_nonogram.height)]

    def resize(self, width: int, height: int):
        self.loaded_nonogram.width = width
        self.loaded_nonogram.height = height

    def save_file(self):
        pass
        #TODO

    def get_nonogram(self):
        return self.loaded_nonogram

    def solve(self):
        pass
        #TODO