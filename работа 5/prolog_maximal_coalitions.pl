:- use_module(library(lists)).
:- use_module(library(http/json)).


% "A и B встречались в партии". Делаем связь двусторонней.
connected(A, B) :- played(A, B), A @< B.
connected(A, B) :- played(B, A), B @< A.


% Любой игрок, который есть в фактах played/2.
player(P) :- played(P, _).
player(P) :- played(_, P).


% Все игроки без повторов (setof сам сортирует).
all_players(Players) :-
    setof(P, player(P), Players),
    !.
all_players([]).


% Простое пересечение двух списков.
intersection_list(A, B, I) :-
    findall(X, (member(X, A), memberchk(X, B)), I0),
    sort(I0, I).


% Все соседи игрока V.
neighbors(V, Ns) :-
    setof(U, connected(V, U), Ns),
    !.
neighbors(_, []).


% R - текущая группа, P - кого еще можно добавить, X - кого уже проверили.
% Когда P и X пусты, R уже максимальная группа.
% Если кандидатов и обработанных нет, текущая группа R является готовым ответом.
bk(R, [], [], [R]) :- !.
% Шаг рекурсии: обрабатываем список кандидатов P.
bk(R, P, X, Groups) :-
    % Запускаем итератор по кандидатам и накапливаем найденные группы.
    bk_iter(P, X, R, [], GroupsRev),
    % Разворачиваем аккумулятор, чтобы сохранить ожидаемый порядок вывода.
    reverse(GroupsRev, Groups).


% Идем по кандидатам V из P.
% Nv - соседи V, P1/X1 - пересечения с Nv.
% Так мы оставляем только тех, кто совместим с текущей группой R.
% База итерации: если P пуст, возвращаем накопленные группы.
bk_iter([], _, _, Acc, Acc).
% Берем первого кандидата V и продолжаем с остальными Ps.
bk_iter([V | Ps], X, R, Acc, Groups) :-
    % Находим всех соседей кандидата V.
    neighbors(V, Nv),
    % Оставляем в P только тех, кто совместим с V.
    intersection_list([V | Ps], Nv, P1),
    % Оставляем в X только тех, кто совместим с V.
    intersection_list(X, Nv, X1),
    % Углубляемся: пробуем расширить группу, добавив V в R.
    bk([V | R], P1, X1, Found),
    % Добавляем найденные на этом шаге группы в аккумулятор.
    append(Found, Acc, Acc1),
    % Переходим к следующему кандидату: V удаляем из P и переносим в X.
    bk_iter(Ps, [V | X], R, Acc1, Groups).


% Все максимальные полносвязные группы игроков.
% Сортируем и сами группы, и общий список (стабильный вывод для Python).
maximal_coalitions(Coalitions) :-
    all_players(Players),
    bk([], Players, [], Raw),
    findall(S, (member(C, Raw), sort(C, S)), Sorted),
    sort(Sorted, Coalitions).


% Упаковка результата в JSON, чтобы Python легко прочитал ответ.
maximal_coalitions_json(JsonAtom) :-
    maximal_coalitions(Coalitions),
    atom_json_term(
        JsonAtom,
        _{
            coalitions: Coalitions
        },
        []
    ).
