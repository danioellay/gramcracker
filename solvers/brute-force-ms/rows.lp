color(0..1).
row(1..h).
col(1..w).
pos(X, Y) :- row(X), col(Y).
1 { pixel(X, Y, C) : color(C) } 1 :- pos(X, Y).

% Constraint 1: Total black pixels must match hint sum in every row
black_count(X, C) :- row(X), C = #count{ Y : pixel(X, Y, 1) }.
hint_sum(X, S) :- row(X), S = #sum{ L,I : row_hint(X, I, L) }.
:- row(X), black_count(X, C), hint_sum(X, S), C != S.

% first_black_row(X, 1, P) :-
%     pos(X), P = #min{ Pos : pixel_row(X, Pos, 1) }.

% first_black_row(X, I, P) :-
%     pos(X), I > 1,
%     row_hint(X, I-1, Lp),
%     first_black_row(X, I-1, Pp),
%     P = #min{ Pos : pixel_row(X, Pos, 1), Pos >= 1 + Pp + Lp }.

% :- first_black_row(X, I, P), row_hint(X, I, L),
%    { pixel_row(X, PP, 1) : PP = P..P+L-1 } != L.

% :- first_black_row(X, I, P), row_hint(X, I, L),
%    pixel_row(X, P + L, 1).

fill(X, Y) :- row(X), pixel(X, Y, 1).

#show fill/2.