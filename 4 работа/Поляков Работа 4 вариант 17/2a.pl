concat_lists([], B, B).
concat_lists([H | T], B, [H | TRes]) :-
	concat_lists(T, B, TRes).

% удалить каждый третий элемент списка
remove_every_third([], []).
remove_every_third([X], [X]).
remove_every_third([X, Y], [X, Y]).
remove_every_third([X, Y, _ | Tail], Res) :-
	remove_every_third(Tail, RTail),
	concat_lists([X, Y], RTail, Res).

% test: ?- remove_every_third([1,2,3,4,5,6,7], Res).
% test: ?- remove_every_third([a,b,c,d,e], Res).
