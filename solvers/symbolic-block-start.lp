% https://link.springer.com/chapter/10.1007/978-3-031-86585-5_11
% tl;dr: separating the problem into row/column constraints and one board constraint showed good efficiency
% https://github.com/v4hn/nonogram_asp
% tl;dr: encode only the block start. This should reduce grounding size

% run with clingo nonograms/example_01.lp solvers/symbolic-block-start.lp
%     or with: clinguin client-server --domain-files nonograms/example_01.lp solvers/symbolic-block-start.lp --ui-files solvers/nonogram-ui.lp



row(1..n).
col(1..n).
pos(1..n). % starting position of a block


% ---------------------------------------------
% Row Fills
% ---------------------------------------------

% Guess block start positions
1 { start_r(R,I,S) : pos(S) } 1 :- row_hint(R, I, L), L > 0.

% Clues with a later index, must start after the last index + 1
:- start_r(R,I1,S1), start_r(R,I2,S2), I1 < I2,
   row_hint(R,I1,L1), S2 < S1 + L1 + 1.

% A cell is filled if it's within the span of some block that starts at column S with length L
fill_r(R,C) :- start_r(R,I,S), row_hint(R,I,L), pos(C), C >= S, C < S + L.

% Row length constraint
:- start_r(R,I,S), row_hint(R,I,L), S + L - 1 > n.

% ---------------------------------------------
% Column Fills (analogically)
% ---------------------------------------------

1 { start_c(C,I,S) : pos(S) } 1 :- col_hint(C,I, L), L > 0.

:- start_c(C,I1,S1), start_c(C,I2,S2), I1 < I2,
   col_hint(C,I1,L1), S2 < S1 + L1 + 1.

fill_c(R,C) :- start_c(C,I,S), col_hint(C,I,L), pos(R), R >= S, R < S + L.

:- start_c(C,I,S), col_hint(C,I,L), S + L - 1 > n.

% ---------------------------------------------
% Agreement Between Row and Column Fills
% ---------------------------------------------

% A pixel is filled only if it's filled in both the row set and the column set
fill(R,C) :- fill_r(R,C), fill_c(R,C).
:- fill_r(R,C), not fill_c(R,C).
:- fill_c(R,C), not fill_r(R,C).

#show fill/2.
