# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *
from io import TextIOWrapper

class NonogramHandler:
    def __init__(self):
        self.loaded_nonogram: Nonogram = Nonogram()
        self.loaded_nonogram_filename: str | None = None
    
    def get_curr_nonogram(self) -> Nonogram:
        """Get a reference to the currently loaded nonogram"""
        return self.loaded_nonogram
    
    def load_file(self, path: str) -> None:
        """Open the logic program file at the specified path and load the encoded nonogram"""
        with open(path, 'r') as file:
            lines = file.readlines()
        # check which file ending the filename has and switch between parsers
        lpfile = path.split('.')[-1] == 'lp'
        if not lpfile and path.split('.')[-1] != 'txt':
            raise Warning("File Format not supported")
        
        self.loaded_nonogram = self._load_lp_format(lines) if lpfile else self._load_txt_format(lines)
        self.loaded_nonogram_filename = path

    def _load_lp_format(self, lines: list[str]) -> Nonogram:
        nonogram = Nonogram()

        for line in lines:
            line = line.strip()
            if line.startswith('#const w ='):
                try:
                    nonogram.width = int(line.split('=')[1].strip().split('.', 1)[0])
                    assert(nonogram.width > 0)
                except:
                    raise Warning("Nonogram width must be a positive integer")

            elif line.startswith('#const h ='):
                try:
                    nonogram.height = int(line.split('=')[1].strip().split('.', 1)[0])
                    assert(nonogram.height > 0)
                except:
                    raise Warning("Nonogram height must be a positive integer")

            elif line.startswith('row_hint('):
                try:
                    parts = line.split('(')[1].split(')')[0].split(',')
                    row, hint_index, block_length = map(int, parts)
                    assert(row > 0 and row <= nonogram.height)
                    assert(hint_index > 0)
                    assert(block_length >= 0)
                except:
                    raise Warning(f"Invalid row hint: {line}")
                while len(nonogram.row_hints) < nonogram.height:
                    nonogram.row_hints.append(cast(LineHint, []))
                while len(nonogram.row_hints[row - 1]) <= hint_index - 1:
                    nonogram.row_hints[row - 1].append(0)
                nonogram.row_hints[row - 1][hint_index - 1] = block_length

            elif line.startswith('col_hint('):
                try:
                    parts = line.split('(')[1].split(')')[0].split(',')
                    col, hint_index, block_length = map(int, parts)
                    assert(col > 0 and col <= nonogram.width)
                    assert(hint_index > 0)
                    assert(block_length >= 0)
                except:
                    raise Warning(f"Invalid column hint: {line}")
                while len(nonogram.col_hints) < nonogram.width:
                    nonogram.col_hints.append(cast(LineHint, []))
                while len(nonogram.col_hints[col - 1]) <= hint_index - 1:
                    nonogram.col_hints[col - 1].append(0)
                nonogram.col_hints[col - 1][hint_index - 1] = block_length

        if nonogram.width == 0 or nonogram.height == 0:
            raise Warning(f"Nonogram dimensions are missing")
        
        return nonogram
    
    def _load_txt_format(self, lines: list[str]) -> Nonogram:
        nonogram = Nonogram()

        try:
            split_index = lines.index('\n')
        except:
            raise Warning("Expected a blank line separating column and row hints")

        row_hint_lines = [line.strip() for line in lines[:split_index] if line.strip()]
        col_hint_lines = [line.strip() for line in lines[split_index + 1:] if line.strip()]
        if not row_hint_lines:
            raise Warning("Expected at least one row hint")
        if not col_hint_lines:
            raise Warning("Expected at least one column hint")

        nonogram.height, nonogram.width = len(row_hint_lines), len(col_hint_lines)

        for row_index, line in enumerate(row_hint_lines, start=1):
            try:
                hints = list(map(int, line.split()))
                for hint in hints:
                    assert(hint > 0)
            except:
                raise Warning(f"Invalid hint in row {row_index}: {line}")
            nonogram.row_hints.append(cast(LineHint, hints))

        for col_index, line in enumerate(col_hint_lines, start=1):
            try:
                hints = list(map(int, line.split()))
                for hint in hints:
                    assert(hint > 0)
            except:
                raise Warning(f"Invalid hint in column {col_index}: {line}")
            nonogram.col_hints.append(cast(LineHint, hints))

        return nonogram

    def save_file(self, path: str = "") -> None:
        """Write a logic program encoding the loaded nonogram to the path specified, or to the original path it was loaded from"""
        if path == "" and self.loaded_nonogram_filename:
            path = self.loaded_nonogram_filename
        elif path == "":
            print("Error: No path to save the file to")
            return
        
        nonogram = self.get_curr_nonogram()
        if not nonogram:
            print("Error: No nonogram to save")
            return
        
        filetype = path.split('.')[-1]
        
        with open(path, 'w') as f:
            if filetype == 'lp':
                self._write_lp_format(nonogram, f)
            elif filetype == 'txt':
                self._write_txt_format(nonogram, f)
            else:
                print(f"unsupported file format: '.{filetype}'")

    def _write_lp_format(self, nonogram: Nonogram, f: TextIOWrapper) -> None:
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

    def _write_txt_format(self, nonogram: Nonogram, f: TextIOWrapper) -> None:
        for hints in nonogram.row_hints:
            for len in hints:
                f.write(str(len) + ' ')
            f.write("\n")
        f.write("\n")
        for hints in nonogram.col_hints:
            for len in hints:
                f.write(str(len) + ' ')
            f.write("\n")
