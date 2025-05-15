%%% ASP Nonogram solver
%%% "Brute force" problem encoding
%%% Author: Fabian Kraus
%%% run with: clinguin client-server --domain-files nonograms/example_05.lp solvers/brute-force.lp --ui-files solvers/nonogram-ui.lp
%%%       or: clingo nonograms/example_05.lp solvers/brute-force.lp

%%% PROBLEM ENCODING
% Pixel Grid: every pixel has to have exactly one color
color(0..1).
row(1..n).
col(1..n).
pos(X, Y) :- row(X), col(Y).
1 { pixel(X, Y, C) : color(C) } 1 :- pos(X, Y).

%%% Generalized line handling
line_type(row; col).
line(row, N) :- row(N).
line(col, N) :- col(N).

line_hint(row, R, I, L) :- row_hint(R, I, L).
line_hint(col, C, I, L) :- col_hint(C, I, L).

pos_in_line(row, X) :- row(X).
pos_in_line(col, Y) :- col(Y).

pixel(row, N, Y, C) :- pixel(N, Y, C).
pixel(col, N, X, C) :- pixel(X, N, C).

%%% Combined constraints for lines
% Constraint 1: Total black pixels must match hint sum in every line
black_count(T, N, C) :- line(T, N), C = #count{ P : pixel(T, N, P, 1) }.
hint_sum(T, N, S) :- line(T, N), S = #sum{ L,I : line_hint(T, N, I, L) }.  
:- line_type(T), line(T,N), black_count(T,N,C), hint_sum(T,N,S), C != S.

% Helper predicate to find the first black pixel in every block in every line
% Format: first_black(line type, number, block index, position)
% base case: 1st block
first_black(T, N, 1, P) :-
    pos_in_line(T, P),
    line_hint(T, N, 1, L), L > 0,
    P = #min{ Pos : pixel(T, N, Pos, 1) }.
% inductive definition for 2nd, 3rd, ... blocks
first_black(T, N, I, P) :-
    pos_in_line(T, P),
    line_hint(T, N, I, L), L > 0, I > 1,
    line_hint(T, N, I-1, Lp),
    first_black(T, N, I-1, Pp),
    line(T, N), pos_in_line(T, Pp), pos_in_line(T, Lp),
    pos_in_line(T, Start),
    P = #min{ Pos : pixel(T, N, Pos, 1), Pos >= 1 + Pp + Lp }.

% Constraint 2: Blocks of black pixels in every line must be correct length
:- first_black(T, N, I, P), line_hint(T, N, I, L),
   { pixel(T, N, PP, 1) : PP = P..P+L-1 } != L.

% Constraint 3: There must be a space after every block in every line
:- first_black(T, N, I, P), line_hint(T, N, I, L),
   pixel(T, N, P + L, 1).
   
% Output
#show pixel/3.
fill(R,C) :- row(R), col(C), pixel(R,C,1).