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

% Constraint 1: In every row the number of black pixels must match 
%    the sum of all hints' lengths
row_count(Row, Count) :- row(Row), Count = #count { Y : pixel(Row, Y, 1) }.
row_hint_count(Row, 0) :- row(Row), not row_hint(Row, _, _).
row_hint_count(Row, 0) :- row(Row), row_hint(Row, 1, 0).
row_hint_count(Row, Count) :- row(Row), row_hint(Row, _, L), L != 0, 
     Count = #sum{ L', Index : row_hint(Row, Index, L') }.
:- row(Row), row_count(Row, RCount), row_hint_count(Row, HCount), 
     RCount != HCount.

% Constraint 1': In every column the number of black pixels must match
%    the sum of all hints' lengths
col_count(Col, Count) :- col(Col), Count = #count { X : pixel(X, Col, 1) }.
col_hint_count(Col, 0) :- col(Col), not col_hint(Col, _, _).
col_hint_count(Col, 0) :- col(Col), col_hint(Col, 1, 0).
col_hint_count(Col, Count) :- col(Col), col_hint(Col, _, L), L != 0, 
     Count = #sum{ L', Index : col_hint(Col, Index, L') }.
:- col(Col), col_count(Col, RCount), col_hint_count(Col, HCount), 
     RCount != HCount.

% Constraint 2: In every row with at least one hint, the first black pixel
%    must be followed by exactly L-1 more black pixels
first_black_pixel_row(Row, Col, 1) :- row(Row), row_hint(Row, 1, L), L != 0, 
     Col = #min { Y : pixel(Row, Y, 1) }.
:- row(Row), row_hint(Row, 1, L), L != 0, first_black_pixel_row(Row, Col, 1),
     #count { Y : pixel(Row, Y, 1), Y > Col, Y - L < Col } != L - 1.

% Constraint 2': In every column with at least one hint, the first black pixel
%    must be followed by exactly L-1 more black pixels
first_black_pixel_col(Col, Row, 1) :- col(Col), col_hint(Col, 1, L), L != 0, 
     Row = #min { X : pixel(X, Col, 1) }.
:- col(Col), col_hint(Col, 1, L), L != 0, first_black_pixel_col(Col, Row, 1),
     #count { X : pixel(X, Col, 1), X > Row, X - L < Row } != L - 1.

% Constraint 3: In every row, for every further hint the next first 
%    black pixel must be followed by exactly L-1 more black pixels
first_black_pixel_row(Row, Col, Index) :- row(Row), row_hint(Row, Index, L), L != 0, 
     row_hint(Row, Index - 1, L'), first_black_pixel_row(Row, Col', Index - 1), Index > 1, 
     Col = #min { Y : pixel(Row, Y, 1), Y - L' >= Col' }.
:- row(Row), row_hint(Row, Index, L), Index > 1, L != 0, first_black_pixel_row(Row, Col, Index),
     #count{ Y : pixel(Row, Y, 1), Y > Col, Y - L < Col } != L - 1.

% Constraint 3': In every column, for every further hint the next first 
%    black pixel must be followed by exactly L-1 more black pixels
first_black_pixel_col(Col, Row, Index) :- col(Col), col_hint(Col, Index, L), L != 0, 
     col_hint(Col, Index - 1, L'), first_black_pixel_col(Col, Row', Index - 1), Index > 1, 
     Row = #min { X : pixel(X, Col, 1), X - L' >= Row' }.
:- col(Col), col_hint(Col, Index, L), Index > 1, L != 0, first_black_pixel_col(Col, Row, Index),
     #count{ X : pixel(X, Col, 1), X > Row, X - L < Row} != L - 1.

% helper predicate because adding two numbers is too much for clingo
end_block(Begin, Length, End) :- row(Begin), row(Length), row(End), End = Begin + Length.

% Constraint 4: In every row, the first pixel after every block of 
%    black pixels must be not black, or it is the right end of the image
:- row(Row), row_hint(Row, Index, L), L != 0, first_black_pixel_row(Row, Col, Index), 
    end_block(Col, L, End), pixel(Row, End, 1), pos(Row, End).

% Constraint 4': In every column, the first pixel after every block of
%    black pixels must be not black, or it is the bottom end of the image
:- col(Col), col_hint(Col, Index, L), L != 0, first_black_pixel_col(Col, Row, Index), 
     end_block(Row, L, End), pixel(End, Col, 1), pos(End, Col).

% Output
#show pixel/3.