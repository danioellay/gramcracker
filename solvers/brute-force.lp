%%% ASP Nonogram solver
%%% "Brute force" problem encoding
%%% Author: Fabian Kraus
%%% run with: clinguin client-server --domain-files nonograms/example_02.lp solvers/brute-force.lp --ui-files solvers/nonogram-ui.lp
%%%       or: clingo nonograms/example_02.lp solvers/brute-force.lp

%%% PROBLEM ENCODING
% Pixel Grid: every pixel has to have exactly one color
color(0..1).
row(1..n).
col(1..n).
pos(X, Y) :- row(X), col(Y).
1 { pixel(X, Y, C) : color(C) } 1 :- pos(X, Y).

% Constraint 1: In every row the number of black pixels must match the sum of all hints
row_count(Row, Count) :- row(Row), Count = #count { Y : pixel(Row, Y, 1) }.
row_hint_count(Row, Count) :- row(Row), Count = #sum{ L : row_hint(Row, _, L) }.
:- row(Row), row_count(Row, RCount), row_hint_count(Row, HCount), RCount != HCount.

% Constraint 1': In every column the number of black pixels must match the sum of all hints
col_count(Col, Count) :- col(Col), Count = #count { X : pixel(X, Col, 1) }.
col_hint_count(Col, Count) :- col(Col), Count = #sum{ L : col_hint(Col, _, L) }.
:- col(Col), col_count(Col, RCount), col_hint_count(Col, HCount), RCount != HCount.

% Constraint 2: In every row, the first black pixel must be followed by exactly L-1 more black pixels
first_black_pixel_row(Row, Col) :- row(Row), Col = #min { Y : pixel(Row, Y, 1) }.
:- row_hint(Row, 1, L), first_black_pixel_row(Row, Col),
     #count { Y : pixel(Row, Y, 1), Y >= Col, Y - L < Col } != L.

% Constraint 2': In every column, the first black pixel must be followed by exactly L-1 more black pixels
first_black_pixel_col(Col, Row) :- col(Col), Row = #min { X : pixel(X, Col, 1) }.
:- col_hint(Col, 1, L), first_black_pixel_col(Col, Row),
     #count { X : pixel(X, Col, 1), X >= Row, X - L < Row } != L.

% Constraint 3: In every row, the first pixel after the first block of black pixels must be not black, or it is the right end of the image
:- row_hint(Row, 1, L), first_black_pixel_row(Row, Col), 
   #sum { 1 : pixel(Row, C, 1), C = Col + L } != 0, Col <= n - L.

% Constraint 3': In every column, the first pixel after the first block of black pixels must be not black, or it is the bottom end of the image
:- col_hint(Col, 1, L), first_black_pixel_col(Col, Row),
   #sum { 1 : pixel(R, Col, 1), R = Row + L } != 0, Row <= n - L.

% Constraint 4: In every row, for every further hint the next first black pixel must be followed by exactly L-1 more black pixels

% Constraint 4': In every column, for every further hint the next first black pixel must be followed by exactly L-1 more black pixels

% Constraint 5: In every row, the first pixel after every block of black pixels must be not black, or it is the right end of the image

% Constraint 5': In every column, the first pixel after every block of black pixels must be not black, or it is the bottom end of the image

% Constraint 6: In every row, the last block must be followed only by white pixels

% Constraint 6': In every column, the last block must be followed only by white pixels

% Output
#show pixel/3.