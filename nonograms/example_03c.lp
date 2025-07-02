%%% ASP Nonogram solver
%%% Problem Instance encoding example
%%% 10x10 Nonogram with unique solution (non-square version)
%%% Author: Fabian Kraus
#const w = 6.  % Size of the Nonogram (w x h bw image)
#const h = 9.

% Hints for rows
% Format: row_hint(Row, HintIndex, BlockLength)
%row_hint( 0, 1, 0).
row_hint( 1, 1, 4).
row_hint( 2, 1, 6).
row_hint( 3, 1, 2).
row_hint( 3, 2, 2).
row_hint( 4, 1, 2).
row_hint( 4, 2, 2).

row_hint( 5, 1, 6).
row_hint( 6, 1, 4).
row_hint( 7, 1, 2).
row_hint( 8, 1, 2).
row_hint( 9, 1, 2).

% Hints for columns
% Format: col_hint(Column, HintIndex, BlockLength)
%col_hint(-1, 1, 0).
%col_hint( 0, 1, 0).
col_hint( 1, 1, 9).
col_hint( 2, 1, 9).
col_hint( 3, 1, 2).
col_hint( 3, 2, 2).

col_hint( 4, 1, 2).
col_hint( 4, 2, 2).
col_hint( 5, 1, 4).
col_hint( 6, 1, 4).
%col_hint( 7, 1, 0).
%col_hint( 8, 1, 0).