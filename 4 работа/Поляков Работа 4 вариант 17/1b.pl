% parent(child, parent)

parent(charlie, alice).
parent(diane, alice).
parent(charlie, bob).
parent(diane, bob).
parent(gregory, emily).
parent(harry, emily).
parent(gregory, fred).
parent(harry, fred).
parent(ian, diane).
parent(jack, diane).
parent(kevin, diane).
parent(ian, gregory).
parent(jack, gregory).
parent(kevin, gregory).
parent(michael, linda).
parent(norman, linda).
parent(michael, kevin).
parent(norman, kevin).
parent(oscar, fred).

woman(alice).
woman(diane).
woman(emily).
woman(linda).
man(bob).
man(charlie).
man(fred).
man(gregory).
man(harry).
man(ian).
man(jack).
man(kevin).
man(michael).
man(norman).
man(oscar).

% X имеет детей от двух разных людей
parent_with_two_partners(X) :-
	parent(Child1, X),
	parent(Child1, Partner1),
	X \= Partner1,
	parent(Child2, X),
	parent(Child2, Partner2),
	X \= Partner2,
	Partner1 \= Partner2,
	Child1 \= Child2.

% test: ?- setof(X, parent_with_two_partners(X), Res).
