%%% ASP Nonogram solver
%%% Problem Instance encoding example
%%% 20x20 Nonogram with unique solution
%%% Author: Fabian Kraus
#const n = 20.  % Size of the Nonogram (n x n bw image)

% Hints for rows
% Format: row_hint(Row, HintIndex, BlockLength)
row_hint( 1, 1, 3).
row_hint( 2, 1, 5).
row_hint( 3, 1, 3).
row_hint( 3, 2, 1).
row_hint( 4, 1, 2).
row_hint( 4, 2, 1).
row_hint( 5, 1, 3).
row_hint( 5, 2, 3).
row_hint( 5, 3, 4).

row_hint( 6, 1, 2).
row_hint( 6, 2, 2).
row_hint( 6, 3, 7).
row_hint( 7, 1, 6).
row_hint( 7, 2, 1).
row_hint( 7, 3, 1).
row_hint( 8, 1, 4).
row_hint( 8, 2, 2).
row_hint( 8, 3, 2).
row_hint( 9, 1, 1).
row_hint( 9, 2, 1).

row_hint(10, 1, 3).
row_hint(10, 2, 1).
row_hint(11, 1, 6).
row_hint(12, 1, 2).
row_hint(12, 2, 7).
row_hint(13, 1, 6).
row_hint(13, 2, 3).
row_hint(13, 3, 1).
row_hint(14, 1, 1).
row_hint(14, 2, 2).
row_hint(14, 3, 2).
row_hint(14, 4, 1).
row_hint(14, 5, 1).
row_hint(15, 1, 4).
row_hint(15, 2, 1).
row_hint(15, 3, 1).
row_hint(15, 4, 3).

row_hint(16, 1, 4).
row_hint(16, 2, 2).
row_hint(16, 3, 2).
row_hint(17, 1, 3).
row_hint(17, 2, 3).
row_hint(17, 3, 1).
row_hint(18, 1, 3).
row_hint(18, 2, 3).
row_hint(19, 1, 3).
row_hint(20, 1, 2).
row_hint(20, 2, 1).

% Hints for columns
% Format: col_hint(Column, HintIndex, BlockLength)
col_hint( 1, 1, 2).
col_hint( 2, 1, 1).
col_hint( 2, 2, 2).
col_hint( 3, 1, 2).
col_hint( 3, 2, 3).
col_hint( 4, 1, 2).
col_hint( 4, 2, 3).
col_hint( 5, 1, 3).
col_hint( 5, 2, 1).
col_hint( 5, 3, 1).

col_hint( 6, 1, 2).
col_hint( 6, 2, 1).
col_hint( 6, 3, 1).
col_hint( 7, 1, 1).
col_hint( 7, 2, 1).
col_hint( 7, 3, 1).
col_hint( 7, 4, 2).
col_hint( 7, 5, 2).
col_hint( 8, 1, 1).
col_hint( 8, 2, 1).
col_hint( 8, 3, 3).
col_hint( 8, 4, 1).
col_hint( 8, 5, 3).
col_hint( 9, 1, 2).
col_hint( 9, 2, 6).
col_hint( 9, 3, 4).
col_hint(10, 1, 3).
col_hint(10, 2, 3).
col_hint(10, 3, 9).
col_hint(10, 4, 1).

col_hint(11, 1, 5).
col_hint(11, 2, 3).
col_hint(11, 3, 2).
col_hint(12, 1, 3).
col_hint(12, 2, 1).
col_hint(12, 3, 2).
col_hint(12, 4, 2).
col_hint(13, 1, 2).
col_hint(13, 2, 1).
col_hint(13, 3, 7).
col_hint(14, 1, 3).
col_hint(14, 2, 3).
col_hint(14, 3, 2).
col_hint(15, 1, 2).
col_hint(15, 2, 4).

col_hint(16, 1, 2).
col_hint(16, 2, 1).
col_hint(16, 3, 2).
col_hint(17, 1, 2).
col_hint(17, 2, 2).
col_hint(17, 3, 1).
col_hint(18, 1, 2).
col_hint(18, 2, 2).
col_hint(19, 1, 1).
col_hint(20, 1, 1).
