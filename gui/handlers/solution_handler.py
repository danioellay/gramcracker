from gui.common import *
from clingo import Control

class SolutionHandler:
    def __init__(self):
        pass

    def give_nonogram(self, nonogram: Nonogram):
        self.given_nonogram = nonogram
        self.working_solution = NonogramSoln(nonogram)

    def run_solver(self, encoding: str, solver: str):
        ctl = Control()
        ctl.load(encoding)
        ctl.load("solvers/" + solver + ".lp")
        ctl.ground([("base", [])])
        model = ctl.solve(yield_=True)
        
        # Clear the solution and only fill from the model
        self.working_solution = NonogramSoln(self.given_nonogram)
        for symbol in model.model().symbols(atoms=True):
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


