# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *
from clingo import Control
import time

def format_time(t: float) -> str:
    if t > 60.0*60.0:
        return f"{t/(60.0*60.0):.2f}h"
    if t > 60.0:
        return f"{t/60.0:.2f}min"
    if t > 1.0:
        return f"{t:.2f}s"
    if t > 0.001:
        return f"{t*1.0e3:.2f}ms"
    return f"{t*1.0e6:.2f}ns"

class SolutionHandler:
    def __init__(self):
        pass

    def give_nonogram(self, nonogram: Nonogram):
        self.given_nonogram = nonogram
        self.working_solution = NonogramSoln(nonogram)

    def run_solver(self, encoding: str, solver: str):
        # Clear the solution and only fill from the model
        self.working_solution = NonogramSoln(self.given_nonogram)

        ctl = Control(["0"])
        ctl.load(encoding)
        ctl.load("solvers/" + solver + ".lp")
        start_time = time.time()
        ctl.ground([("base", [])])
        ground_time = time.time()
        result = ctl.solve(yield_=True)
        model = result.model()
        end_time = time.time()
        result.resume()
        model2 = result.model()
        unique_time = time.time()
        if not model:
            print(f"Solver {solver}' found no model after {format_time(end_time - start_time)}:")
        elif not model2:
            print(f"Solver '{solver}' took {format_time(unique_time - start_time)} to find a unique model:")
        else:
            print(f"Solver '{solver}' took {format_time(unique_time - start_time)} to find at least two models:")
        print(f"\tGrounding:  {format_time(ground_time - start_time)}")
        print(f"\tSolving:    {format_time(end_time - ground_time)}")
        print(f"\tUniqueness: {format_time(unique_time - end_time)}")
        
        # Clear the solution and only fill from the model
        if model:
            for symbol in model.symbols(atoms=True):
                if symbol.name == 'fill':
                    self.working_solution.fill[symbol.arguments[0].number - 1][symbol.arguments[1].number - 1] = True

    def solves_row(self, row: int) -> bool:
        hints = self.given_nonogram.row_hints[row]
        line = self.working_solution.fill[row]
        return self._check_line(line, hints)
            
    def solves_col(self, col: int) -> bool:
        hints = self.given_nonogram.col_hints[col]
        line = [fill[col] for fill in self.working_solution.fill]
        return self._check_line(line, hints)

    def _check_line(self, line: List[bool], hints: List[int]) -> bool:
        hint_index = 0
        i = 0
        n = len(line)

        while i < n and hint_index < len(hints):
            # Skip unfilled cells
            while i < n and not line[i]:
                i += 1

            # Check if there are enough cells left for the current hint
            if i + hints[hint_index] > n:
                return False

            # Check if the next cells are filled to match the hint
            for j in range(hints[hint_index]):
                if not line[i + j]:
                    return False

            # Move past the current block
            i += hints[hint_index]

            # Check if the block is followed by at least one unfilled cell
            if i < n and line[i]:
                return False

            # Move to the next hint
            hint_index += 1

        # Ensure there are no remaining filled cells
        while i < n:
            if line[i]:
                return False
            i += 1

        # Ensure all hints have been processed
        return hint_index == len(hints)
