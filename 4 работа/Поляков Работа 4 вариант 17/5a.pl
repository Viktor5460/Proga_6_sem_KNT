concat_lists([], B, B).
concat_lists([H | T], B, [H | TRes]) :-
	concat_lists(T, B, TRes).

% склеить список списков в один список (без удаления внутренних вложенностей)
concat_sublists([], []).
concat_sublists([H | T], Res) :-
	concat_sublists(T, RTail),
	concat_lists(H, RTail, Res).

% test: ?- concat_sublists([[a,b], [1,2,3], [c,d,[e,f]], [], [4]], Res).
