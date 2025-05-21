color(0..1).
row(1..h).
col(1..w).
pos(X, Y) :- row(X), col(Y).
1 { pixel(X, Y, C) : color(C) } 1 :- pos(X, Y).

% Constraint 1: Total black pixels must match hint sum in every column
black_count(Y, C) :- col(Y), C = #count{ X : pixel(X, Y, 1) }.
hint_sum(Y, S) :- col(Y), S = #sum{ L,I : col_hint(Y, I, L) }.
:- col(Y), black_count(Y, C), hint_sum(Y, S), C != S.

% first_black_col(Y, 1, P) :-
%     pos(Y), P = #min{ Pos : pixel_col(Y, Pos, 1) }.

% first_black_col(Y, I, P) :-
%     pos(Y), I > 1,
%     col_hint(Y, I-1, Lp),
%     first_black_col(Y, I-1, Pp),
%     P = #min{ Pos : pixel_col(Y, Pos, 1), Pos >= 1 + Pp + Lp }.

% :- first_black_col(Y, I, P), col_hint(Y, I, L),
%    { pixel_col(Y, PP, 1) : PP = P..P+L-1 } != L.

% :- first_black_col(Y, I, P), col_hint(Y, I, L),
%    pixel_col(Y, P + L, 1).

fill(X, Y) :- col(Y), pixel(X, Y, 1).

#show fill/2.