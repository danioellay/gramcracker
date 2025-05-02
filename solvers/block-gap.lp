%%% ASP Nonogram solver
%%% Author: Fabian Kraus
%%% run with: clinguin client-server --domain-files instance.lp block-gap.lp --ui-files nonogram-ui.lp


row(1..n).
col(1..n).

% Possible offset lengths in front of first block
offset_value(0..n-1).
% Possible gap lengths between two separate blocks
gap_value(1..n-1).

% Guess possible offsets between left/top border and blocks of black pixels in rows/columns
% (first hint can have zero offset, all other hints have offset >= 1)
1 { row_gap(Row, 1, O) : offset_value(O) } 1 :- row_hint(Row, 1, _).
1 { col_gap(Col, 1, O) : offset_value(O) } 1 :- col_hint(Col, 1, _).
1 { row_gap(Row, Index, G) : gap_value(G) } 1 :- row_hint(Row, Index, _), Index > 1.
1 { col_gap(Col, Index, G) : gap_value(G) } 1 :- col_hint(Col, Index, _), Index > 1.

% Constraint: Sum of gap lengths plus block lengths cannot exceed n for any row
:- row(Row), #sum { G, RowHint : row_gap(Row, Index, G), row_hint(Row, Index, RowHint) } > n.

% Constraint: Sum of gap lengths plus block lengths cannot exceed n for any column
:- col(Col), #sum { G, ColHint : col_gap(Col, Index, G), col_hint(Col, Index, ColHint) } > n.

% Grid representation
pixel(Row, Col, 0..1) :- row(Row), col(Col).

% Define blocks in rows with correct gaps
block_row(Row, Index, Start) :-
    row_hint(Row, Index, Length),
    row_gap(Row, Index, Offset),
    Start = Offset + 1,
    #count { C : pixel(Row, C, 1), C >= Start, C < Start + Length } = Length.

% Ensure gap before next block in rows if exists
:- row_hint(Row, Index, Length), row_hint(Row, Index + 1, NextLength),
   row_gap(Row, Index, Gap), row_gap(Row, Index + 1, NextOffset),
   Length + Gap + NextOffset + NextLength > n.

% Define blocks in columns with correct gaps
block_col(Col, Index, Start) :-
    col_hint(Col, Index, Length),
    col_gap(Col, Index, Offset),
    Start = Offset + 1,
    #count { R : pixel(R, Col, 1), R >= Start, R < Start + Length } = Length.

% Ensure gap before next block in columns if exists
:- col_hint(Col, Index, Length), col_hint(Col, Index + 1, NextLength),
   col_gap(Col, Index, Gap), col_gap(Col, Index + 1, NextOffset),
   Length + Gap + NextOffset + NextLength > n.

% Consistency between rows and columns
:- pixel(Row, Col, 1), not block_row(Row, _, _).
:- pixel(Row, Col, 1), not block_col(Col, _, _).

% Show only interesting atoms
%#show pixel/3.
%#show row_gap/3.
%#show col_gap/3.
