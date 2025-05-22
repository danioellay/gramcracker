# use from root with:
# python3 nonograms/survey_by_numbers_dataset/parse_nonogram.py nonograms/survey_by_numbers_dataset/cat6.txt

import sys
import os

def parse_nonogram_file_to_asp(filepath):
    with open(filepath, 'r') as f:
        lines = [line.strip('\n') for line in f]

    try:
        split_index = lines.index('')
    except ValueError:
        raise ValueError("Expected a blank line separating column and row clues.")

    row_hint_lines = [line.strip() for line in lines[:split_index] if line.strip()]
    col_hint_lines = [line.strip() for line in lines[split_index + 1:] if line.strip()]

    out_lines = [f"#const h = {len(row_hint_lines)}.", f"#const w = {len(col_hint_lines)}.\n", "% Row Hints"]

    for row_index, line in enumerate(row_hint_lines, start=1):
        hints = list(map(int, line.split()))
        for hint_index, length in enumerate(hints, start=1):
            out_lines.append(f"row_hint({row_index}, {hint_index}, {length}).")

    out_lines.append("\n% Column Hints")
    for col_index, line in enumerate(col_hint_lines, start=1):
        hints = list(map(int, line.split()))
        for hint_index, length in enumerate(hints, start=1):
            out_lines.append(f"col_hint({col_index}, {hint_index}, {length}).")

    output = "\n".join(out_lines)

    output_dir = "nonograms/survey_by_numbers_dataset/generated"
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.splitext(os.path.basename(filepath))[0]
    with open(os.path.join(output_dir, f"{filename}.lp"), 'w') as out:
        out.write(output)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    input_file = sys.argv[1]
    parse_nonogram_file_to_asp(input_file)
