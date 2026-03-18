% A является окончанием списка B (suffix)
is_suffix([], _).
is_suffix(A, A).
is_suffix(A, [_ | T]) :-
	is_suffix(A, T).

% test: ?- is_suffix([1,2,3], [a,b,4,1,2,3]).
% test: ?- is_suffix([1,2,4,3], [a,b,1,2,3,0]).
