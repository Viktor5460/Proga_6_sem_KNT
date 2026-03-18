list_length([], 0).
list_length([_ | T], Num) :-
	list_length(T, TNum),
	Num is TNum + 1.

% проверка, что длина списка чётная
even_length(List) :-
	list_length(List, Len),
	R is Len mod 2,
	R =:= 0.

% test: ?- even_length([5, g, gz5, ee]).
% test: ?- even_length([5, g, gz5, ee, l]).
