% an attempt to get close to a traditional nonogram layout

elem(window, window, root).

% Grid container
elem(grid, container, window).
attr(grid, child_layout, grid).
attr(grid, width, 200).
attr(grid, height, 200).

% Define grid cells
elem(cell(R,C), container, grid) :- row(R), col(C).
attr(cell(R,C), grid_row, R) :- row(R), col(C).
attr(cell(R,C), grid_column, C) :- row(R), col(C).
attr(cell(R,C), width, 50) :- row(R), col(C).
attr(cell(R,C), height, 50) :- row(R), col(C).

% Set border
attr(cell(R,C), border_width, 1) :- row(R), col(C).
attr(cell(R,C), border_color, "black") :- row(R), col(C).

% Background color: filled or empty
attr(cell(R,C), background, "white") :- row(R), col(C), not fill(R,C).
attr(cell(R,C), background, "black") :- fill(R,C).

% Row Hint Grid
elem(row_hint_cell(R), container, grid) :- row(R).
attr(row_hint_cell(R), grid_row, R) :- row(R).
attr(row_hint_cell(R), width, 100) :- row(R).
attr(row_hint_cell(R), height, 50) :- row(R).
attr(row_hint_cell(R), border_width, 1) :- row(R).
attr(row_hint_cell(R), border_color, "black") :- row(R).

% Column Hint Grid
elem(col_hint_cell(C), container, grid) :- col(C).
attr(col_hint_cell(C), grid_column, C) :- col(C).
attr(col_hint_cell(C), width, 50) :- col(C).
attr(col_hint_cell(C), height, 85) :- col(C).
attr(col_hint_cell(C), border_width, 1) :- col(C).
attr(col_hint_cell(C), border_color, "black") :- col(C).


row_hint_label(R, @stringify(L), 1) :- row_hint(R, 1, L).
row_hint_label(R, @concat(LPrev, " ", @stringify(L)), I) :- I > 1, row_hint(R, I, L), I1 = I - 1, row_hint_label(R, LPrev, I1).


col_hint_label(C, @stringify(L), 1) :- col_hint(C, 1, L).
col_hint_label(C, @concat(LPrev, "<br/>", @stringify(L)), I) :- I > 1, col_hint(C, I, L), I1 = I - 1, col_hint_label(C, LPrev, I1).


elem(row_hint_label(R), label, row_hint_cell(R)) :- row(R).
attr(row_hint_label(R), label, L) :- N = #count { I : row_hint(R, I, _) }, row_hint_label(R, L, N).


elem(col_hint_label(C), label, col_hint_cell(C)) :- col(C).
attr(col_hint_label(C), label, L) :- N = #count { I : col_hint(C, I, _) }, col_hint_label(C, L, N).











