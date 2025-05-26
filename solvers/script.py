from clingo import Control, Function

def main():

    ctl = Control()
    ctl.load("symbolic-block-start.lp")
    ctl.load("../nonograms/example_01.lp")
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