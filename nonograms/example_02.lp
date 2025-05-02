%%% ASP Nonogram solver
%%% Problem Instance encoding example
%%% 5x5 Nonogram with multiple solutions
%%% Author: Fabian Kraus
#const n = 5.  % Size of the Nonogram (n x n bw image)

% Hints for rows
% Format: row_hint(Row, HintIndex, BlockLength)
row_hint(1, 1, 1). % first block in first row has length two
row_hint(2, 1, 1).
row_hint(3, 1, 1).
row_hint(4, 1, 1).
row_hint(5, 1, 1).

% Hints for columns
% Format: col_hint(Column, HintIndex, BlockLength)
col_hint(1, 1, 1).
col_hint(2, 1, 1).
col_hint(3, 1, 1).
col_hint(4, 1, 1).
col_hint(5, 1, 1).
