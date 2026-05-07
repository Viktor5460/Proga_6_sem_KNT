import ctypes
from ctypes import c_char_p, c_int, c_void_p, create_string_buffer


#
# Пример работы с библиотекой board_game_lib.dll через ctypes
# (по образцу слайдов: libmonster.so, create_monster, get_health и т.п.).
#

# Загружаем DLL, лежащую в той же папке, что и этот скрипт.
lib = ctypes.CDLL("./board_game_lib.dll")

# Тип "ручки" на игру: в C это BoardGame*, в Python — void*.
BoardGameHandle = c_void_p
GameDatabaseHandle = c_void_p
MatchHandle = c_void_p

# === Описание сигнатур C-функций ===

lib.bg_create.argtypes = [c_char_p, c_char_p, c_int, c_int, c_char_p]
lib.bg_create.restype = BoardGameHandle

lib.bg_dispose.argtypes = [BoardGameHandle]
lib.bg_dispose.restype = None

lib.bg_get_name.argtypes = [BoardGameHandle, ctypes.c_char_p, c_int]
lib.bg_get_name.restype = None

lib.bg_get_description.argtypes = [BoardGameHandle, ctypes.c_char_p, c_int]
lib.bg_get_description.restype = None

lib.bg_get_min_players.argtypes = [BoardGameHandle]
lib.bg_get_min_players.restype = c_int

lib.bg_get_max_players.argtypes = [BoardGameHandle]
lib.bg_get_max_players.restype = c_int

lib.bg_set_complexity.argtypes = [BoardGameHandle, c_char_p]
lib.bg_set_complexity.restype = None

lib.bg_get_complexity.argtypes = [BoardGameHandle, ctypes.c_char_p, c_int]
lib.bg_get_complexity.restype = None

lib.bg_set_duration.argtypes = [BoardGameHandle, c_int]
lib.bg_set_duration.restype = None

lib.bg_get_duration.argtypes = [BoardGameHandle]
lib.bg_get_duration.restype = c_int

lib.bg_add_feature.argtypes = [BoardGameHandle, c_char_p, c_char_p]
lib.bg_add_feature.restype = c_int

lib.bg_get_feature.argtypes = [BoardGameHandle, c_char_p, ctypes.c_char_p, c_int]
lib.bg_get_feature.restype = None

lib.bg_has_feature.argtypes = [BoardGameHandle, c_char_p]
lib.bg_has_feature.restype = c_int

lib.bg_set_game_type.argtypes = [BoardGameHandle, c_char_p]
lib.bg_set_game_type.restype = None

lib.bg_get_game_type.argtypes = [BoardGameHandle, ctypes.c_char_p, c_int]
lib.bg_get_game_type.restype = None

lib.bg_set_genre.argtypes = [BoardGameHandle, c_char_p]
lib.bg_set_genre.restype = None

lib.bg_get_genre.argtypes = [BoardGameHandle, ctypes.c_char_p, c_int]
lib.bg_get_genre.restype = None

lib.bg_set_mechanics.argtypes = [BoardGameHandle, c_char_p]
lib.bg_set_mechanics.restype = None

lib.bg_get_mechanics.argtypes = [BoardGameHandle, ctypes.c_char_p, c_int]
lib.bg_get_mechanics.restype = None

# === GameDatabase C API ===

lib.db_create.argtypes = []
lib.db_create.restype = GameDatabaseHandle

lib.db_dispose.argtypes = [GameDatabaseHandle]
lib.db_dispose.restype = None

lib.db_add_game.argtypes = [GameDatabaseHandle, BoardGameHandle]
lib.db_add_game.restype = c_int

lib.db_get_game.argtypes = [GameDatabaseHandle, c_char_p]
lib.db_get_game.restype = BoardGameHandle

lib.db_get_games_count.argtypes = [GameDatabaseHandle]
lib.db_get_games_count.restype = c_int

lib.db_add_player.argtypes = [GameDatabaseHandle, c_char_p, c_char_p]
lib.db_add_player.restype = c_int

lib.db_add_rating.argtypes = [GameDatabaseHandle, c_char_p, c_char_p, c_int]
lib.db_add_rating.restype = c_int

lib.db_add_similarity.argtypes = [GameDatabaseHandle, c_char_p, c_char_p]
lib.db_add_similarity.restype = c_int

lib.db_get_recommendations.argtypes = [
    GameDatabaseHandle,
    c_char_p,
    ctypes.POINTER(BoardGameHandle),
    c_int,
]
lib.db_get_recommendations.restype = c_int

lib.db_find_games_by_min_rating.argtypes = [
    GameDatabaseHandle,
    ctypes.c_double,
    ctypes.POINTER(BoardGameHandle),
    c_int,
]
lib.db_find_games_by_min_rating.restype = c_int

lib.db_find_games_by_feature.argtypes = [
    GameDatabaseHandle,
    c_char_p,
    c_char_p,
    ctypes.POINTER(BoardGameHandle),
    c_int,
]
lib.db_find_games_by_feature.restype = c_int

# === Match C API ===

lib.match_create.argtypes = [c_char_p, c_char_p, c_char_p]
lib.match_create.restype = MatchHandle

lib.match_dispose.argtypes = [MatchHandle]
lib.match_dispose.restype = None

lib.match_add_player_result.argtypes = [MatchHandle, c_char_p, ctypes.c_double]
lib.match_add_player_result.restype = c_int

lib.db_add_match.argtypes = [GameDatabaseHandle, MatchHandle]
lib.db_add_match.restype = c_int

lib.db_get_player_rating_in_game.argtypes = [GameDatabaseHandle, c_char_p, c_char_p]
lib.db_get_player_rating_in_game.restype = ctypes.c_double

lib.db_set_similarity_weights.argtypes = [
    GameDatabaseHandle,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    c_int,
]
lib.db_set_similarity_weights.restype = None

lib.db_get_recommendation_stats.argtypes = [
    GameDatabaseHandle,
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
]
lib.db_get_recommendation_stats.restype = c_int


def get_string(getter_func, handle, max_len=256) -> str:
    """Вспомогательная функция: вызывает C-функцию, заполняющую буфер, и
    возвращает результат как Python-строку."""
    buf = create_string_buffer(max_len)
    getter_func(handle, buf, max_len)
    return buf.value.decode("utf-8", errors="ignore")


def main():
    # Создаём базу данных
    db = lib.db_create()

    # Создаём игру через C-обёртку
    game1 = lib.bg_create(
        "Brass: Birmingham".encode("utf-8"),
        "Экономическая евро-игра про промышленную революцию в Англии.".encode("utf-8"),
        2,
        4,
        "2018".encode("utf-8"),
    )

    if not game1:
        print("Ошибка: bg_create вернул NULL для game1")
        return

    # Заполняем жанровые параметры и признаки
    lib.bg_set_game_type(game1, "Евро игра".encode("utf-8"))
    lib.bg_set_genre(game1, "Стратегия".encode("utf-8"))
    lib.bg_set_mechanics(game1, "Экономика, Построение сети".encode("utf-8"))
    lib.bg_add_feature(game1, "Тема".encode("utf-8"), "Индустриальная революция".encode("utf-8"))

    # Добавляем игру в базу
    added1 = lib.db_add_game(db, game1)
    print("Добавление Brass в базу:", "OK" if added1 else "FAIL")

    # Создаём вторую игру
    game2 = lib.bg_create(
        "Wingspan".encode("utf-8"),
        "Семейная игра о птицах.".encode("utf-8"),
        1,
        5,
        "2019".encode("utf-8"),
    )

    if not game2:
        print("Ошибка: bg_create вернул NULL для game2")
        lib.db_dispose(db)
        return

    lib.bg_set_game_type(game2, "Семейная".encode("utf-8"))
    lib.bg_set_genre(game2, "Стратегия".encode("utf-8"))
    lib.bg_set_mechanics(game2, "Карточная игра, Комбо".encode("utf-8"))
    lib.bg_add_feature(game2, "Тема".encode("utf-8"), "Птицы и заповедник".encode("utf-8"))

    added2 = lib.db_add_game(db, game2)
    print("Добавление Wingspan в базу:", "OK" if added2 else "FAIL")

    # Добавляем игроков и оценки
    lib.db_add_player(db, "ivan".encode("utf-8"), "Иван".encode("utf-8"))
    lib.db_add_player(db, "maria".encode("utf-8"), "Мария".encode("utf-8"))

    lib.db_add_rating(db, "Brass: Birmingham".encode("utf-8"), "ivan".encode("utf-8"), 5)
    lib.db_add_rating(db, "Brass: Birmingham".encode("utf-8"), "maria".encode("utf-8"), 4)
    lib.db_add_rating(db, "Wingspan".encode("utf-8"), "ivan".encode("utf-8"), 4)

    count = lib.db_get_games_count(db)
    print("Всего игр в базе (через C API):", count)

    # Достаём одну игру из базы по имени
    game = lib.db_get_game(db, "Brass: Birmingham".encode("utf-8"))

    if not game:
        print("Ошибка: db_get_game не нашёл игру Brass: Birmingham")
        lib.db_dispose(db)
        return

    # Устанавливаем сложность и длительность
    lib.bg_set_complexity(game, "8".encode("utf-8"))
    lib.bg_set_duration(game, 120)

    # Читаем данные обратно
    name = get_string(lib.bg_get_name, game)
    desc = get_string(lib.bg_get_description, game)
    complexity = get_string(lib.bg_get_complexity, game)
    duration = lib.bg_get_duration(game)
    min_players = lib.bg_get_min_players(game)
    max_players = lib.bg_get_max_players(game)

    print("Название:", name)
    print("Описание:", desc)
    print("Игроки:", min_players, "-", max_players)
    print("Сложность:", complexity)
    print("Длительность:", duration, "минут")

    # --- Рекомендации: ищем похожие игры для Brass ---
    max_results = 10
    array_type = BoardGameHandle * max_results
    out_array = array_type()

    rec_count = lib.db_get_recommendations(
        db,
        "Brass: Birmingham".encode("utf-8"),
        out_array,
        max_results,
    )
    print("\nРекомендации для Brass (через C API):")
    if rec_count == 0:
        print("  (нет рекомендаций)")
    else:
        for i in range(rec_count):
            h = out_array[i]
            if not h:
                continue
            rec_name = get_string(lib.bg_get_name, h)
            print(f"  {i + 1}. {rec_name}")

    # --- Фильтр по рейтингу ---
    out_array = array_type()
    high_count = lib.db_find_games_by_min_rating(db, 4.5, out_array, max_results)
    print("\nИгры с рейтингом >= 4.5:")
    for i in range(high_count):
        h = out_array[i]
        if not h:
            continue
        rec_name = get_string(lib.bg_get_name, h)
        print(f"  {i + 1}. {rec_name}")

    # --- Фильтр по признаку Жанр=Стратегия ---
    out_array = array_type()
    feature_count = lib.db_find_games_by_feature(
        db,
        "Жанр".encode("utf-8"),
        "Стратегия".encode("utf-8"),
        out_array,
        max_results,
    )
    print("\nСтратегические игры (Жанр=Стратегия):")
    for i in range(feature_count):
        h = out_array[i]
        if not h:
            continue
        rec_name = get_string(lib.bg_get_name, h)
        print(f"  {i + 1}. {rec_name}")

    # --- Матчи и рейтинг игрока ---
    match = lib.match_create(
        "m1".encode("utf-8"),
        "Brass: Birmingham".encode("utf-8"),
        "2024-10-01".encode("utf-8"),
    )
    lib.match_add_player_result(match, "ivan".encode("utf-8"), 1.0)
    lib.match_add_player_result(match, "maria".encode("utf-8"), 0.0)
    lib.db_add_match(db, match)  # владение матчем переходит базе

    rating_ivan = lib.db_get_player_rating_in_game(
        db,
        "ivan".encode("utf-8"),
        "Brass: Birmingham".encode("utf-8"),
    )
    print(f"\nРейтинг игрока Ivan в Brass (по матчам): {rating_ivan}")

    # --- Настройка весов и статистика рекомендаций (пример для settings) ---
    lib.db_set_similarity_weights(
        db,
        0.3,  # сложность
        0.2,  # количество игроков
        0.1,  # тип игры
        0.1,  # длительность
        0.2,  # механики
        0.05, # жанр
        0.05, # пользовательские параметры
        0.15, # порог схожести
        10,   # максимум рекомендаций
    )

    total_games = c_int()
    games_with_recs = c_int()
    avg_recs = ctypes.c_double()
    avg_sim = ctypes.c_double()

    ok_stats = lib.db_get_recommendation_stats(
        db,
        ctypes.byref(total_games),
        ctypes.byref(games_with_recs),
        ctypes.byref(avg_recs),
        ctypes.byref(avg_sim),
    )
    if ok_stats:
        print(
            "\nСтатистика рекомендаций:"
            f"\n  Всего игр: {total_games.value}"
            f"\n  Игр с рекомендациями: {games_with_recs.value}"
            f"\n  Среднее число рекомендаций на игру: {avg_recs.value:.2f}"
            f"\n  Средняя схожесть: {avg_sim.value:.2f}"
        )

    # Освобождаем память:
    # - сначала удаляем базу (она удалит все игры, которыми владеет)
    # - отдельно dispose для игр вызывать не нужно, чтобы не удалить дважды
    lib.db_dispose(db)


if __name__ == "__main__":
    main()


