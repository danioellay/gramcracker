%%% ASP Nonogram solver
%%% Problem Instance encoding
%%% 20x18 Nonogram
#const w = 20.  % Size of the Nonogram (w x h bw image)
#const h = 18.

% Hints for rows
% Format: row_hint(Row, HintIndex, BlockLength)
row_hint(1, 1, 2).
row_hint(2, 1, 4).
row_hint(3, 1, 1).
row_hint(3, 2, 2).
row_hint(4, 1, 2).
row_hint(5, 1, 3).
row_hint(6, 1, 3).
row_hint(6, 2, 4).
row_hint(7, 1, 3).
row_hint(7, 2, 10).
row_hint(8, 1, 8).
row_hint(9, 1, 3).
row_hint(10, 1, 2).
row_hint(11, 1, 2).
row_hint(12, 1, 2).
row_hint(13, 1, 3).
row_hint(14, 1, 2).
row_hint(15, 1, 2).
row_hint(16, 1, 2).
row_hint(17, 1, 2).
row_hint(18, 1, 2).

% Hints for columns
% Format: col_hint(Column, HintIndex, BlockLength)
col_hint(1, 1, 2).
col_hint(2, 1, 2).
col_hint(3, 1, 1).
col_hint(4, 1, 2).
col_hint(5, 1, 2).
col_hint(6, 1, 2).
col_hint(7, 1, 2).
col_hint(8, 1, 2).
col_hint(9, 1, 2).
col_hint(10, 1, 3).
col_hint(11, 1, 2).
col_hint(11, 2, 2).
col_hint(12, 1, 2).
col_hint(12, 2, 2).
col_hint(13, 1, 2).
col_hint(13, 2, 2).
col_hint(14, 1, 2).
col_hint(14, 2, 1).
col_hint(15, 1, 1).
col_hint(15, 2, 2).
col_hint(16, 1, 1).
col_hint(16, 2, 1).
col_hint(16, 3, 2).
col_hint(17, 1, 2).
col_hint(17, 2, 2).
col_hint(17, 3, 2).
col_hint(18, 1, 1).
col_hint(18, 2, 2).
col_hint(18, 3, 2).
col_hint(19, 1, 2).
col_hint(19, 2, 2).
col_hint(19, 3, 2).
col_hint(20, 1, 2).
col_hint(20, 2, 2).
col_hint(20, 3, 1).
