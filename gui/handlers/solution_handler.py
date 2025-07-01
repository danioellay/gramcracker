# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *
from clingo import Control
import time

class SolutionHandler:
    def __init__(self):
        self.given_nonogram: Nonogram | None = None
        self.solutions: List[NonogramSoln] = []
        self.curr_soln_idx: int = 0

    def give_nonogram(self, nonogram: Nonogram):
        """Give a reference to a nonogram that will be solved when run_solver is called"""
        self.given_nonogram = nonogram
        self.curr_soln_idx = 0
        self.solutions = []

    def get_curr_soln(self) -> NonogramSoln:
        return self.solutions[self.curr_soln_idx]

    def run_solver(self, solver_path: str, check_unique: bool = True, all_models: bool = False) -> str:
        """Run the logic program at the given path, assume it is a nonogram solver and try to find one/two models, depending on the check_unique flag"""
        if not self.given_nonogram:
            print("Error: No nonogram to solve")
            self.curr_soln_idx = 0
            self.solutions = []
            return "Error: No nonogram to solve"

        # Initialize the clingo control and give the dimensional constants
        ctl = Control([f"{0 if check_unique else 1}", 
                       "-c", f"w={self.given_nonogram.width}", 
                       "-c", f"h={self.given_nonogram.height}"])

        # Add the hint predicates to the base program
        for row_index, row in enumerate(self.given_nonogram.row_hints):
            for hint_index, hint_length in enumerate(row):
                ctl.add(f"row_hint({row_index+1},{hint_index+1},{hint_length}).")
        for col_index, col in enumerate(self.given_nonogram.col_hints):
            for hint_index, hint_length in enumerate(col):
                ctl.add(f"col_hint({col_index+1},{hint_index+1},{hint_length}).")
        
        # Load the solver file
        ctl.load("solvers/" + solver_path + ".lp")

        # Find the first model and track the computation times
        start_time = time.time()
        ctl.ground([("base", [])])
        ground_time = time.time()

        handler = ctl.solve(yield_=True)
        model1 = handler.model()
        end_time = time.time()

        if model1:
            soln = NonogramSoln(self.given_nonogram)
            soln.fill_from_model(model1)
            self.solutions = [soln]
            self.curr_soln_idx = 0

        model2 = None
        unique_time = end_time
        # If checking uniqueness, try to find a second model
        if model1 and check_unique:
            handler.resume()
            model2 = handler.model()
            unique_time = time.time()

            if model2:
                soln = NonogramSoln(self.given_nonogram)
                soln.fill_from_model(model1)
                self.solutions.append(soln)

        all_time = end_time
        # If trying to find all solutions, keep going
        if model2 and check_unique and all_models:
            while True:
                print(f"looking for model nr {len(self.solutions) + 1}...")
                handler.resume()
                next_model = handler.model()
                if next_model:
                    print(f"found model nr {len(self.solutions) + 1}!")
                    next_soln = NonogramSoln(self.given_nonogram)
                    next_soln.fill_from_model(next_model)
                    self.solutions.append(next_soln)
                else:
                    print(f"model nr {len(self.solutions) + 1} not found! Ending search...")
                    print()
                    break
                
            all_time = time.time()

        # Status bar output
        self.res = ""
        if not model1:
            self.res = f"Solver '{solver_path}' found no solutions after {format_time(end_time - start_time)}"

        elif not check_unique:
            self.res = f"Solver '{solver_path}' found a solution after {format_time(end_time - start_time)}"
        elif check_unique and not all_models:
            if not model2:
                self.res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find a unique solution"
            else:
                self.res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find at least two solutions"
        elif check_unique and all_models:
            if len(self.solutions) == 1:
                self.res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find a unique solution"
            else:
                self.res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find all {len(self.solutions)} solutions"

        print(self.res + ":")
        print(f"\tGrounding:  {format_time(ground_time - start_time)}")
        print(f"\tSolving:    {format_time(end_time - ground_time)}")
        if check_unique:
            print(f"\tUniqueness: {format_time(unique_time - end_time)}")
        if all_models and len(self.solutions) > 1:
            print(f"\tAll Solutions: {format_time(all_time - unique_time)}")
        
        return self.res
    
    def next_soln(self):
        if len(self.solutions) < 2:
            return
        self.curr_soln_idx += 1
        if self.curr_soln_idx >= len(self.solutions):
            self.curr_soln_idx = 0

    def prev_soln(self):
        if len(self.solutions) < 2:
            return
        self.curr_soln_idx -= 1
        if self.curr_soln_idx < 0:
            self.curr_soln_idx = len(self.solutions) - 1

    def solves_row(self, row: int) -> bool:
        """Does the current working solution match the hints in the specified row in the given nonogram?"""
        if not self.given_nonogram:
            print("Error: No nonogram to check rows for")
            return False
        if not self.solutions:
            print("Error: No solution to check rows in")
            return False
        
        hints = self.given_nonogram.row_hints[row]
        line = self.get_curr_soln().fill[row]
        return check_line(line, hints)
    
    def solves_col(self, col: int) -> bool:
        """Does the current working solution match the hints in the specified column in the given nonogram?"""
        if not self.given_nonogram:
            print("Error: No nonogram to check columns for")
            return False
        if not self.solutions:
            print("Error: No solution to check columns in")
            return False
        
        hints = self.given_nonogram.col_hints[col]
        line = [fill[col] for fill in self.get_curr_soln().fill]
        return check_line(line, hints)
