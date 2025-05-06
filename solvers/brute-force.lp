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

%%% Generalized line handling
line_type(row; col).
line(row, N) :- row(N).
line(col, N) :- col(N).

line_hint(row, R, I, L) :- row_hint(R, I, L).
line_hint(col, C, I, L) :- col_hint(C, I, L).

pixel_in_line(row, N, Y, C) :- pixel(N, Y, C).
pixel_in_line(col, N, X, C) :- pixel(X, N, C).

%%% Combined constraints for lines
% Constraint 1: Total black pixels must match hint sum
line_black_count(T, N, C) :- line(T, N), C = #count{ P : pixel_in_line(T, N, P, 1) }.
line_hint_sum(T, N, S) :- line(T, N), S = #sum{ L,I : line_hint(T, N, I, L) }.  
:- line_type(T), line(T,N), line_black_count(T,N,C), line_hint_sum(T,N,S), C != S.

% Helper predicate to find the first black pixel for each block
first_black(T, N, 1, P) :-
    line_hint(T, N, 1, L), L > 0,
    P = #min{ Pos : pixel_in_line(T, N, Pos, 1) }.
first_black(T, N, I, P) :-
    line_hint(T, N, I, L), L > 0, I > 1,
    line_hint(T, N, I-1, Lp),
    first_black(T, N, I-1, Pp),
    line(T, N),
    P = #min{ Pos : pixel_in_line(T, N, Pos, 1), Pos >= Pp + Lp + 1 }.

% Constraint 2: Blocks of black pixels must be correct length
:- first_black(T, N, I, P), line_hint(T, N, I, L),
   { pixel_in_line(T, N, PP, 1) : PP = P..P+L-1 } != L.

% Constraint 3: There must be a space after every block
:- first_black(T, N, I, P), line_hint(T, N, I, L),
   P + L <= n,
   pixel_in_line(T, N, P + L, 1).
   
% Output
#show pixel/3.