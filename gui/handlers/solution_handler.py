# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *
from clingo import Control
import time
from copy import deepcopy
from typing import List, Tuple

class SolutionHandler:
    def __init__(self):
        """Init a handler that can be given nonograms to solve"""
        self.given_nonogram: Nonogram
        self.solutions: List[NonogramSoln] = []
        self.curr_soln_idx: int = -1 # == -1 if in working solution
        self.working_soln: NonogramSoln
        self.timeout: float = 1.0
        self.found_all = False

    def give_nonogram(self, nonogram: Nonogram) -> None:
        """Give a reference to a nonogram that will be solved when run_solver is called"""
        self.given_nonogram = nonogram
        self.curr_soln_idx = -1
        self.solutions = []
        self.working_soln = NonogramSoln(nonogram)

    def set_timeout(self, t: float) -> None:
        """Set the maximum time the solver can take before aborting"""
        self.timeout = t

    def get_curr_soln(self) -> NonogramSoln:
        """Get the currently selected solution; use use_working_soln, next_soln or prev_soln methods to switch between solution"""
        if self.curr_soln_idx < 0:
            return self.working_soln
        return self.solutions[self.curr_soln_idx]
    
    def use_working_soln(self):
        """Create a copy of the current solution to make it available for editing"""
        self.working_soln = deepcopy(self.get_curr_soln())
        self.curr_soln_idx = -1

    def next_soln(self):
        """Switch to the next solution the solver found (wraps around)"""
        if len(self.solutions) < 2:
            self.curr_soln_idx = 0
            return
        self.curr_soln_idx += 1
        if self.curr_soln_idx >= len(self.solutions):
            self.curr_soln_idx = 0

    def prev_soln(self):
        """Switch to the previous solution the solver found (wraps around)"""
        if len(self.solutions) < 2:
            self.curr_soln_idx = 0
            return
        self.curr_soln_idx -= 1
        if self.curr_soln_idx < 0:
            self.curr_soln_idx = len(self.solutions) - 1

    def get_cautious_pixels(self) -> np.ndarray:
        """Find all solutions if not done already and return the coordinates of the pixels that are filled in every solution"""
        if not self.found_all:
            # If we did not find all solutions previously, do it now
            self.run_solver_auto(True, True)

        grids = [solution.grid for solution in self.solutions]
        stacked_grids = np.stack(grids, axis=0)
        common_grid = np.logical_and.reduce(stacked_grids, axis=0)
        return common_grid
    
    def run_solver_auto(self, check_unique: bool = True, all_models: bool = False) -> str:
        """Auto-select the best solver and run it"""
        return self.run_solver("sbs-improved", check_unique, all_models)

    def run_solver(self, solver_path: str, check_unique: bool = True, all_models: bool = False) -> str:
        """Run the logic program at the given path, assume it is a nonogram solver and try to find one/two models, depending on the check_unique flag"""
        if not self.given_nonogram:
            print("Error: No nonogram to solve")
            self.curr_soln_idx = 0
            self.solutions = []
            return "Error: No nonogram to solve"

        # Initialize the clingo control and give the dimensional constants
        num = 1
        if check_unique:
            num = 2
        if all_models:
            num = 0
        ctl = Control([f"{num}", 
                       "-c", f"w={self.given_nonogram.width}", 
                       "-c", f"h={self.given_nonogram.height}"])

        # Add the hint predicates to the base program
        for row_index, row in enumerate(self.given_nonogram.row_hints):
            for hint_index, hint_length in enumerate(row):
                ctl.add(f"row_hint({row_index+1},{hint_index+1},{hint_length}).")
        for col_index, col in enumerate(self.given_nonogram.col_hints):
            for hint_index, hint_length in enumerate(col):
                ctl.add(f"col_hint({col_index+1},{hint_index+1},{hint_length}).")
        
        # Load the solver file and ground the program
        ctl.load("solvers/" + solver_path + ".lp")

        start_time = time.time()
        ctl.ground([("base", [])])
        ground_time = time.time()

        # Find the models and track the computation times
        self.solutions.clear()
        self.curr_soln_idx = -1
        timed_out = False

        with ctl.solve(async_=True, on_model=self._on_model) as handle:
            while not handle.wait(1.0):
                if time.time() - ground_time > self.timeout:
                    handle.cancel()
                    timed_out = True
                    break

        end_time = time.time()

        if self.solutions:
            self.curr_soln_idx = 0

        if all_models:
            self.found_all = True
        else:
            self.found_all = False

        # Status bar output
        form_time = format_time(end_time - start_time)
        self.res = ""

        if not self.solutions:
            self.res = f"Solver '{solver_path}' found no solutions after {form_time}"

        elif not check_unique:
            self.res = f"Solver '{solver_path}' found a solution after {form_time}"
        elif check_unique and not all_models:
            if len(self.solutions) == 1:
                self.res = f"Solver '{solver_path}' took {form_time} to find a unique solution"
            else:
                self.res = f"Solver '{solver_path}' took {form_time} to find two distinct solutions (more may exist)"
        elif check_unique and all_models:
            if len(self.solutions) == 1:
                self.res = f"Solver '{solver_path}' took {form_time} to find a unique solution"
            else:
                self.res = f"Solver '{solver_path}' took {form_time} to find {"all" if not timed_out else ""} {len(self.solutions)} solutions"

        if timed_out:
            self.res += " (timeout)"

        print(self.res + ":")
        print(f"\tGrounding:  {format_time(ground_time - start_time)}")
        print(f"\tSolving:    {format_time(end_time - ground_time)}")
        # if check_unique:
        #     print(f"\tUniqueness: {format_time(unique_time - end_time)}")
        # if all_models and len(self.solutions) > 1:
        #     print(f"\tAll Solutions: {format_time(all_time - unique_time)}")
        
        return self.res
    
    def _on_model(self, model: Model) -> None:
        """Clingo 'model found' callback to convert the model into a NonogramSoln and store it"""
        soln = NonogramSoln(self.given_nonogram)
        soln.fill_from_model(model)
        self.solutions.append(soln)

    def solves_row(self, row: int) -> bool:
        """Does the current working solution match the hints in the specified row in the given nonogram?"""
        if not self.given_nonogram:
            return False
        
        row_hint = self.given_nonogram.row_hints[row]
        return self.get_curr_soln().row_matches_hint(row, row_hint)

    def solves_col(self, col: int) -> bool:
        """Does the current working solution match the hints in the specified column in the given nonogram?"""
        if not self.given_nonogram:
            return False
        
        col_hint = self.given_nonogram.col_hints[col]
        return self.get_curr_soln().col_matches_hint(col, col_hint)
    
    def solves_row_partial(self, row: int) -> List[int]:
        """Which row hints are satisfied?"""
        if not self.given_nonogram:
            return []
        
        row_hint = self.given_nonogram.row_hints[row]
        return self.get_curr_soln().row_matches_hint_partial(row, row_hint)

    def solves_col_partial(self, col: int) -> List[int]:
        """Which column hints are satisfied?"""
        if not self.given_nonogram:
            return []
        
        col_hint = self.given_nonogram.col_hints[col]
        return self.get_curr_soln().col_matches_hint_partial(col, col_hint)