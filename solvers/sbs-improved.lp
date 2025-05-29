% https://link.springer.com/chapter/10.1007/978-3-031-86585-5_11
% tl;dr: separating the problem into row/column constraints and one board constraint showed good efficiency
% https://github.com/v4hn/nonogram_asp
% tl;dr: encode only the block start. This should reduce grounding size

% run with clingo nonograms/example_01.lp solvers/symbolic-block-start.lp
%     or with: clinguin client-server --domain-files nonograms/example_01.lp solvers/symbolic-block-start.lp --ui-files solvers/nonogram-ui.lp


row(1..h).
col(1..w).
pos_r(1..w). % starting position of a block
pos_c(1..h).

% ---------------------------------------------
% Determine empty columns and rows
% ---------------------------------------------

% Columns with no positive hints are zero columns
empty_col(C) :- col(C), not has_positive_col_hint(C).
has_positive_col_hint(C) :- col(C), col_hint(C, _, L), L > 0.

% Rows with no positive hints are zero rows
empty_row(R) :- row(R), not has_positive_row_hint(R).
has_positive_row_hint(R) :- row(R), row_hint(R, _, L), L > 0.


% ---------------------------------------------
% Precompute S_min and S_max for rows
% ---------------------------------------------

% Max hint index per row
max_hint_index_r(R,Max) :- row(R), Max = #max { I : row_hint(R,I,_) }.

% Sum of lengths from current hint to last in row
sum_remaining_r(R,I,Sum) :- row_hint(R,I,_), Sum = #sum { L : row_hint(R,J,L), J >= I }, row(R).

% Number of gaps after current hint
gaps_after_r(R,I,Gaps) :- row_hint(R,I,_), max_hint_index_r(R, Max), Gaps = Max - I.

% Latest possible start for current hint
s_max_r(R,I,SMax) :- row_hint(R,I,_), sum_remaining_r(R,I,Sum), gaps_after_r(R,I, Gaps), SMax = w - (Sum + Gaps) + 1.

% Earliest possible start for current hint (recursive)
s_min_r(R,1,1) :- row_hint(R,1,_).
s_min_r(R,I,SMin) :- row_hint(R,I,_), I > 1, row_hint(R,I-1,L_prev), s_min_r(R,I-1,SMin_prev), SMin = SMin_prev + L_prev + 1.

% Check if row block span includes any zero columns
has_empty_col_in_row_span(R, S, L) :- row_hint(R,_,L), pos_r(S), empty_col(C), C >= S, C < S + L.


% ---------------------------------------------
% Precompute S_min and S_max for columns
% ---------------------------------------------

% Max hint index per column
max_hint_index_c(C,Max) :- col(C), Max = #max { I : col_hint(C,I,_) }.

% Sum of lengths from current hint to last in column
sum_remaining_c(C,I,Sum) :- col_hint(C,I,_), Sum = #sum { L : col_hint(C,J,L), J >= I }, col(C).

% Number of gaps after current hint
gaps_after_c(C,I,Gaps) :- col_hint(C,I,_), max_hint_index_c(C, Max), Gaps = Max - I.

% Latest possible start for current hint
s_max_c(C,I,SMax) :- col_hint(C,I,_), sum_remaining_c(C,I,Sum), gaps_after_c(C,I, Gaps), SMax = h - (Sum + Gaps) + 1.

% Earliest possible start for current hint (recursive)
s_min_c(C,1,1) :- col_hint(C,1,_).
s_min_c(C,I,SMin) :- col_hint(C,I,_), I > 1, col_hint(C,I-1,L_prev), s_min_c(C,I-1,SMin_prev), SMin = SMin_prev + L_prev + 1.

% Check if column block span includes any zero rows
has_empty_row_in_col_span(C, S, L) :- col_hint(C,_,L), pos_c(S), empty_row(R), R >= S, R < S + L.


% ---------------------------------------------
% Row Fills with constrained start positions
% ---------------------------------------------

% Guess block start positions within the computed constraints
1 { start_r(R,I,S) : S = SMin..SMax, not has_empty_col_in_row_span(R,S,L) } 1 :- row_hint(R,I,L), L > 0, s_min_r(R,I,SMin), s_max_r(R,I,SMax).

% Blocks with a later index, must start after the last index + 1
:- start_r(R,I1,S1), start_r(R,I2,S2), I1 < I2, row_hint(R,I1,L1), S2 < S1 + L1 + 1.

% A cell is filled if it's within the span of some block that starts at column S with length L
fill_r(R,C) :- start_r(R,I,S), row_hint(R,I,L), pos_r(C), C >= S, C < S + L.

% ---------------------------------------------
% Column Fills with constrained start positions 
%               (analogous)
% ---------------------------------------------

% Guess block start positions within the computed constraints
1 { start_c(C,I,S) : S = SMin..SMax, not has_empty_row_in_col_span(C,S,L) } 1 :- col_hint(C,I,L), L > 0, s_min_c(C,I,SMin), s_max_c(C,I,SMax).

% Blocks with a later index, must start after the last index + 1
:- start_c(C,I1,S1), start_c(C,I2,S2), I1 < I2, col_hint(C,I1,L1), S2 < S1 + L1 + 1.

% A cell is filled if it's within the span of some block that starts at column S with length L
fill_c(R,C) :- start_c(C,I,S), col_hint(C,I,L), pos_c(R), R >= S, R < S + L.

% ---------------------------------------------
% Agreement Between Row and Column Fills
% ---------------------------------------------

% A pixel is filled only if it's filled in both the row set and the column set
fill(R,C) :- fill_r(R,C), fill_c(R,C).
:- fill_r(R,C), not fill_c(R,C).
:- fill_c(R,C), not fill_r(R,C).

#show fill/2.
