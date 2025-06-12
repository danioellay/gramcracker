# ASP Nonogram viewer and solver GUI
# Author: Fabian Kraus

from gui.common import *
from clingo import Control
import time

class SolutionHandler:
    def __init__(self):
        self.working_solution: NonogramSoln | None
        self.given_nonogram: Nonogram | None = None

    def give_nonogram(self, nonogram: Nonogram):
        """Give a reference to a nonogram that will be solved when run_solver is called"""
        self.given_nonogram = nonogram
        self.working_solution = NonogramSoln(nonogram)

    def run_solver(self, solver_path: str, check_unique: bool = True) -> str:
        """Run the logic program at the given path, assume it is a nonogram solver and try to find one/two models, depending on the check_unique flag"""
        if not self.given_nonogram:
            print("Error: No nonogram to solve")
            return "Error: No nonogram to solve"

        # Initialize the clingo control specifying two models are required, and give the dimensional constants
        ctl = Control([f"{2 if check_unique else 1}", 
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
        model = handler.model()
        end_time = time.time()

        # If checking uniqueness, try to find a second model
        if check_unique:
            handler.resume()
            model2 = handler.model()
            unique_time = time.time()
        self.res = ""
        # Console output
        if not model:
            self.res = f"Solver '{solver_path}' found no solutions after {format_time(end_time - start_time)}"

        elif not check_unique:
            self.res = f"Solver '{solver_path}' found a solutions after {format_time(end_time - start_time)}"
        else:
            if not model2:
                self.res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find a unique solution"
            else:
                self.res = f"Solver '{solver_path}' took {format_time(unique_time - start_time)} to find at least two solutions"

        print(self.res + ":")
        print(f"\tGrounding:  {format_time(ground_time - start_time)}")
        print(f"\tSolving:    {format_time(end_time - ground_time)}")
        if check_unique:
            print(f"\tUniqueness: {format_time(unique_time - end_time)}")
        
        # Clear the working solution and only fill from the first model
        self.working_solution = NonogramSoln(self.given_nonogram)
        self.working_solution.fill_from_model(model)

        return self.res

    def solves_row(self, row: int) -> bool:
        """Does the current working solution match the hints in the specified row in the given nonogram?"""
        if not self.given_nonogram:
            print("Error: No nonogram to check rows for")
            return False
        if not self.working_solution:
            print("Error: No solution to check rows in")
            return False
        
        hints = self.given_nonogram.row_hints[row]
        line = self.working_solution.fill[row]
        return check_line(line, hints)
    
    def solves_col(self, col: int) -> bool:
        """Does the current working solution match the hints in the specified column in the given nonogram?"""
        if not self.given_nonogram:
            print("Error: No nonogram to check columns for")
            return False
        if not self.working_solution:
            print("Error: No solution to check columns in")
            return False
        
        hints = self.given_nonogram.col_hints[col]
        line = [fill[col] for fill in self.working_solution.fill]
        return check_line(line, hints)
