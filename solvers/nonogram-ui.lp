%%% Nonogram UI with clinguin
%%% Author: Fabian Kraus
%%% Modified from clinguin sudoko example
%%% (https://clinguin.readthedocs.io/en/latest/clinguin/examples/sudoku.html)

elem(window,window,root).

    %%%%%%%%%%%%%%%%%%%%%%%%
    % Grid
    %%%%%%%%%%%%%%%%%%%%%%%%
    elem(image,container,window).
    attr(image,child_layout,grid).
    attr(image,width,100).
    attr(image,height,100).

        %%%%%%%%%%%%%%%%%%%%%%%%
        % Hint labels
        %%%%%%%%%%%%%%%%%%%%%%%%
        % Convert row hints to string form
        row_hint_str(Row, @stringify(Length), 1) :- row(Row), row_hint(Row, 1, Length).
        row_hint_str(Row, @concat("", LStr, ", ", @stringify(Length)), Index) :- row(Row), row_hint(Row, Index, Length), Index > 1, row_hint_str(Row, LStr, Index - 1).
        row_hint_str_nr(Row, Count) :- row(Row), Count = #count { Index : row_hint(Row, Index, Length) }.
        % Add row hint string to grid
        elem(row_hint_label(Row), label, image) :- row(Row).
        attr(row_hint_label(Row), width, 100):-row(Row).
        attr(row_hint_label(Row), label, Str) :- row(Row), row_hint_str_nr(Row, Count), row_hint_str(Row, Str, Count).
        attr(row_hint_label(Row), grid_row, Row) :- row(Row).
        
        % Convert column hints to string form
        col_hint_str(Col, @stringify(Length), 1) :- col(Col), col_hint(Col, 1, Length).
        col_hint_str(Col, @concat(" ", LStr, " , ", @stringify(Length), " "), Index) :- col(Col), col_hint(Col, Index, Length), Index > 1, col_hint_str(Col, LStr, Index - 1).
        col_hint_str_nr(Col, Count) :- col(Col), Count = #count { Index : col_hint(Col, Index, Length) }.
        % Add column hint string to grid
        elem(col_hint_label(Col), label, image) :- col(Col).
        attr(col_hint_label(Col), height, 100):-col(Col).
        attr(col_hint_label(Col), label, Str) :- col(Col), col_hint_str_nr(Col, Count), col_hint_str(Col, Str, Count).
        attr(col_hint_label(Col), grid_column, Col) :- col(Col).

        %%%%%%%%%%%%%%%%%%%%%%%%
        % Cell dropdown
        %%%%%%%%%%%%%%%%%%%%%%%%
        
        elem(pb(X,Y),container,image):-row(X), col(Y).
        attr(pb(X,Y),width,50):-row(X), col(Y).
        attr(pb(X,Y),height,50):-row(X), col(Y).
        attr(pb(X,Y),grid_column,Y):-row(X), col(Y).
        attr(pb(X,Y),grid_row,X):-row(X), col(Y).
        attr(pb(X,Y),class,("border-dark";"bg-primary")):-fill(X,Y).
        attr(pb(X,Y),class,("opacity-100";"disabled";"fw-bold";"text-dark")):-pixel(X,Y,1).
        attr(pb(X,Y),class,("opacity-40";"disabled";"fw-bold";"text-dark")):-pixel(X,Y,0).
        attr(pb(X,Y),class,("text-primary")):-_clinguin_assume(pixel(X,Y,V), true).
        attr(pb(X,Y),class,("text-info")):-_all(pixel(X,Y,V)), not _clinguin_assume(pixel(X,Y,V), true).
        attr(pb(X,Y),selected,V):-_all(pixel(X,Y,V)).
        attr(pb(X,Y),selected,V):-pixel(X,Y,V), _clinguin_browsing.

        attr(pb(X,Y), border_width, 1) :- row(X), col(Y).
        attr(pb(X,Y), border_color, "black") :- row(X), col(Y).


%%%%%%%%%%%%%%%%%%%%%%%%
% Menu bar
%%%%%%%%%%%%%%%%%%%%%%%%
elem(menu_bar, menu_bar, window).
attr(menu_bar, title, "Nonogram").
attr(menu_bar, icon, "fa-table-cells").

    elem(menu_bar_clear, button, menu_bar).
    attr(menu_bar_clear, label, "Clear").
    attr(menu_bar_clear, icon, "fa-trash").
    attr(menu_bar_clear, class, ("btn-outline-danger";"border-0")).
    when(menu_bar_clear, click, callback, clear_assumptions).

    elem(menu_bar_select, button, menu_bar).
    attr(menu_bar_select, label, "Select solution").
    attr(menu_bar_select, icon, "fa-hand-pointer").
    when(menu_bar_select, click, callback, select).

    elem(menu_bar_next, button, menu_bar).
    attr(menu_bar_next, label, "Next").
    attr(menu_bar_next, icon, "fa-forward-step").
    when(menu_bar_next, click, callback, next_solution).