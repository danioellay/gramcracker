from clingo import Control, Function
import sys

def main(filename):
    # Solve row problem
    ctl = Control()
    ctl.load(filename)
    ctl.load('solvers/brute-force-ms/rows.lp')
    ctl.ground([("base", [])])
    all_rows = []
    for model in ctl.solve(yield_=True):
        row_pixels = set()
        for symbol in model.symbols(atoms=True):
            if symbol.name == 'fill':
                row_pixels.add((symbol.arguments[0].number, symbol.arguments[1].number))
        all_rows.append(row_pixels)

    certain_rows = set()
    if all_rows:
        certain_rows = set.intersection(*all_rows)

    # Solve column problem
    ctl = Control()
    ctl.load(filename)
    ctl.load('solvers/brute-force-ms/cols.lp')
    ctl.ground([("base", [])])
    all_cols = []
    for model in ctl.solve(yield_=True):
        col_pixels = set()
        for symbol in model.symbols(atoms=True):
            if symbol.name == 'fill':
                col_pixels.add((symbol.arguments[1].number, symbol.arguments[0].number))
        all_cols.append(col_pixels)

    certain_cols = set()
    if all_cols:
        certain_cols = set.intersection(*all_cols)

    print(f"certain cols: {certain_cols}")
    print(f"certain rows: {certain_rows}")
    return
    # Combine certain pixels and solve main problem
    ctl = Control()
    ctl.load(filename)
    ctl.load('solvers/brute-force-ms/base.lp')
    ctl.ground([("base", []), ("problem", [])])
    assumptions = [(Function("certain_pixel_row", [x, y]), True) for (x, y) in certain_rows] + [(Function("certain_pixel_col", [x, y]), True) for (x, y) in certain_cols]
    ctl.solve(assumptions=assumptions)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python nonogram.py <filename>")
    else:
        main(sys.argv[1])