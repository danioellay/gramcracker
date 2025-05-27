# use with python3 solvers/script.py nonograms/example_01.lp solvers/symbolic-block-start.lp

from clingo import Control, Function
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_solver.py <puzzle_file.lp> <solver_file.lp>")
        return

    puzzle_file = sys.argv[1]
    solver_file = sys.argv[2]

    ctl = Control()
    ctl.load(puzzle_file)
    ctl.load(solver_file)
    ctl.ground([("base", [])])

    fill_atoms = []

    def on_model(model):
        for atom in model.symbols(shown=True):
            if atom.name == "fill" and len(atom.arguments) == 2:
                fill_atoms.append(atom)

    ctl.solve(on_model=on_model)

    if not fill_atoms:
        print("No solution found.")
        return

    with ctl.backend() as backend:
        literals = []
        for atom in fill_atoms:
            sym = Function(atom.name, atom.arguments)
            lit = backend.add_atom(sym)
            literals.append(lit)
        backend.add_rule([], literals)

    with ctl.solve(yield_=True) as handle:
        for _ in handle:
            print("Uniqueness Check failed: Multiple solutions found")
            return

    print("Nonogram has a UNIQUE solution.")


if __name__ == "__main__":
    main()