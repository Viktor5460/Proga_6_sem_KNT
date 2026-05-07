import ctypes
from ctypes import c_char_p, c_int, c_double, c_void_p, POINTER, create_string_buffer
from pathlib import Path


#
# Высокоуровневая Python-обёртка над board_game_lib.dll.
#

ROOT_DIR = Path(__file__).resolve().parent
DLL_PATH = ROOT_DIR / "board_game_lib.dll"

lib = ctypes.CDLL(str(DLL_PATH))


BoardGameHandle = c_void_p
GameDatabaseHandle = c_void_p
MatchHandle = c_void_p


def _setup_c_api() -> None:
    # BoardGame
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

    lib.bg_get_average_rating.argtypes = [BoardGameHandle]
    lib.bg_get_average_rating.restype = c_double

    lib.bg_get_ratings_count.argtypes = [BoardGameHandle]
    lib.bg_get_ratings_count.restype = c_int

    lib.bg_add_rating.argtypes = [BoardGameHandle, c_char_p, c_int]
    lib.bg_add_rating.restype = c_int

    lib.bg_remove_feature.argtypes = [BoardGameHandle, c_char_p]
    lib.bg_remove_feature.restype = c_int

    # GameDatabase
    lib.db_create.argtypes = []
    lib.db_create.restype = GameDatabaseHandle

    lib.db_dispose.argtypes = [GameDatabaseHandle]
    lib.db_dispose.restype = None

    lib.db_add_game.argtypes = [GameDatabaseHandle, BoardGameHandle]
    lib.db_add_game.restype = c_int

    lib.db_remove_game.argtypes = [GameDatabaseHandle, c_char_p]
    lib.db_remove_game.restype = c_int

    lib.db_get_game.argtypes = [GameDatabaseHandle, c_char_p]
    lib.db_get_game.restype = BoardGameHandle

    lib.db_get_games_count.argtypes = [GameDatabaseHandle]
    lib.db_get_games_count.restype = c_int

    lib.db_add_player.argtypes = [GameDatabaseHandle, c_char_p, c_char_p]
    lib.db_add_player.restype = c_int

    lib.db_remove_player.argtypes = [GameDatabaseHandle, c_char_p]
    lib.db_remove_player.restype = c_int

    lib.db_add_rating.argtypes = [GameDatabaseHandle, c_char_p, c_char_p, c_int]
    lib.db_add_rating.restype = c_int

    lib.db_add_similarity.argtypes = [GameDatabaseHandle, c_char_p, c_char_p]
    lib.db_add_similarity.restype = c_int

    lib.db_are_similar.argtypes = [GameDatabaseHandle, c_char_p, c_char_p]
    lib.db_are_similar.restype = c_int

    lib.db_get_recommendations.argtypes = [
        GameDatabaseHandle,
        c_char_p,
        POINTER(BoardGameHandle),
        c_int,
    ]
    lib.db_get_recommendations.restype = c_int

    lib.db_find_games_by_min_rating.argtypes = [
        GameDatabaseHandle,
        c_double,
        POINTER(BoardGameHandle),
        c_int,
    ]
    lib.db_find_games_by_min_rating.restype = c_int

    lib.db_find_games_by_feature.argtypes = [
        GameDatabaseHandle,
        c_char_p,
        c_char_p,
        POINTER(BoardGameHandle),
        c_int,
    ]
    lib.db_find_games_by_feature.restype = c_int

    # Match
    lib.match_create.argtypes = [c_char_p, c_char_p, c_char_p]
    lib.match_create.restype = MatchHandle

    lib.match_dispose.argtypes = [MatchHandle]
    lib.match_dispose.restype = None

    lib.match_add_player_result.argtypes = [MatchHandle, c_char_p, c_double]
    lib.match_add_player_result.restype = c_int

    lib.db_add_match.argtypes = [GameDatabaseHandle, MatchHandle]
    lib.db_add_match.restype = c_int

    lib.db_remove_match.argtypes = [GameDatabaseHandle, c_char_p]
    lib.db_remove_match.restype = c_int

    lib.db_get_player_rating_in_game.argtypes = [GameDatabaseHandle, c_char_p, c_char_p]
    lib.db_get_player_rating_in_game.restype = c_double

    # Weights & stats
    lib.db_set_similarity_weights.argtypes = [
        GameDatabaseHandle,
        c_double,
        c_double,
        c_double,
        c_double,
        c_double,
        c_double,
        c_double,
        c_double,
        c_double,
        c_int,
    ]
    lib.db_set_similarity_weights.restype = None

    lib.db_get_recommendation_stats.argtypes = [
        GameDatabaseHandle,
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_double),
        POINTER(c_double),
    ]
    lib.db_get_recommendation_stats.restype = c_int

    lib.db_run_tests.argtypes = []
    lib.db_run_tests.restype = c_int


_setup_c_api()


def _get_string(getter, handle, max_len: int = 256) -> str:
    buf = create_string_buffer(max_len)
    getter(handle, buf, max_len)
    return buf.value.decode("utf-8", errors="ignore")


class BoardGame:
    def __init__(self, handle: BoardGameHandle):
        self._h = handle

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        min_players: int,
        max_players: int,
        edition: str = "",
    ) -> "BoardGame":
        h = lib.bg_create(
            name.encode("utf-8"),
            description.encode("utf-8"),
            min_players,
            max_players,
            edition.encode("utf-8"),
        )
        if not h:
            raise RuntimeError("bg_create returned NULL")
        return cls(h)

    @property
    def handle(self) -> BoardGameHandle:
        return self._h

    def get_name(self) -> str:
        return _get_string(lib.bg_get_name, self._h)

    def get_description(self) -> str:
        return _get_string(lib.bg_get_description, self._h, 1024)

    def get_min_players(self) -> int:
        return lib.bg_get_min_players(self._h)

    def get_max_players(self) -> int:
        return lib.bg_get_max_players(self._h)

    def set_complexity(self, value: str) -> None:
        lib.bg_set_complexity(self._h, value.encode("utf-8"))

    def get_complexity(self) -> str:
        return _get_string(lib.bg_get_complexity, self._h)

    def set_duration(self, minutes: int) -> None:
        lib.bg_set_duration(self._h, minutes)

    def get_duration(self) -> int:
        return lib.bg_get_duration(self._h)

    def set_game_type(self, value: str) -> None:
        lib.bg_set_game_type(self._h, value.encode("utf-8"))

    def get_game_type(self) -> str:
        return _get_string(lib.bg_get_game_type, self._h)

    def set_genre(self, value: str) -> None:
        lib.bg_set_genre(self._h, value.encode("utf-8"))

    def get_genre(self) -> str:
        return _get_string(lib.bg_get_genre, self._h)

    def set_mechanics(self, value: str) -> None:
        lib.bg_set_mechanics(self._h, value.encode("utf-8"))

    def get_mechanics(self) -> str:
        return _get_string(lib.bg_get_mechanics, self._h, 1024)

    def add_feature(self, name: str, value: str) -> bool:
        return bool(lib.bg_add_feature(self._h, name.encode("utf-8"), value.encode("utf-8")))

    def get_feature(self, name: str) -> str:
        buf = create_string_buffer(256)
        lib.bg_get_feature(self._h, name.encode("utf-8"), buf, 256)
        return buf.value.decode("utf-8", errors="ignore")

    def has_feature(self, name: str) -> bool:
        return bool(lib.bg_has_feature(self._h, name.encode("utf-8")))

    def get_average_rating(self) -> float:
        return float(lib.bg_get_average_rating(self._h))

    def get_ratings_count(self) -> int:
        return int(lib.bg_get_ratings_count(self._h))

    def add_rating_direct(self, player_id: str, rating: int) -> bool:
        """Добавить оценку напрямую в игру (альтернатива db_add_rating)."""
        return bool(lib.bg_add_rating(self._h, player_id.encode("utf-8"), rating))

    def remove_feature(self, name: str) -> bool:
        return bool(lib.bg_remove_feature(self._h, name.encode("utf-8")))


class Match:
    def __init__(self, handle: MatchHandle):
        self._h = handle

    @classmethod
    def create(cls, match_id: str, game_name: str, date: str) -> "Match":
        h = lib.match_create(
            match_id.encode("utf-8"),
            game_name.encode("utf-8"),
            date.encode("utf-8"),
        )
        if not h:
            raise RuntimeError("match_create returned NULL")
        return cls(h)

    @property
    def handle(self) -> MatchHandle:
        return self._h

    def add_result(self, player_id: str, result: float) -> bool:
        return bool(lib.match_add_player_result(self._h, player_id.encode("utf-8"), result))


class GameDatabase:
    def __init__(self, handle: GameDatabaseHandle | None = None):
        self._h = handle or lib.db_create()
        if not self._h:
            raise RuntimeError("db_create returned NULL")

    @property
    def handle(self) -> GameDatabaseHandle:
        return self._h

    # --- Игры ---

    def add_game(self, game: BoardGame) -> bool:
        return bool(lib.db_add_game(self._h, game.handle))

    def remove_game(self, name: str) -> bool:
        return bool(lib.db_remove_game(self._h, name.encode("utf-8")))

    def get_game(self, name: str) -> BoardGame | None:
        h = lib.db_get_game(self._h, name.encode("utf-8"))
        if not h:
            return None
        return BoardGame(h)

    def games_count(self) -> int:
        return lib.db_get_games_count(self._h)

    # --- Игроки и оценки ---

    def add_player(self, player_id: str, name: str) -> bool:
        return bool(
            lib.db_add_player(self._h, player_id.encode("utf-8"), name.encode("utf-8"))
        )
    
    def add_player_with_null_check(self, player_id: str | None, name: str | None) -> bool:
        """
        Добавить игрока с возможностью передачи NULL указателей для демонстрации обработки ошибок.
        
        ВНИМАНИЕ: Этот метод предназначен только для демонстрации обработки ошибок NULL указателей.
        В нормальном использовании используйте add_player().
        
        Args:
            player_id: ID игрока или None (будет передано как NULL)
            name: Имя игрока или None (будет передано как NULL)
        
        Returns:
            True если успешно, False если передан NULL указатель (обрабатывается библиотекой)
        """
        # В ctypes, если передать None для c_char_p, он автоматически преобразуется в NULL указатель
        # Преобразуем строки в байты, если они не None
        player_id_bytes = None if player_id is None else player_id.encode("utf-8")
        name_bytes = None if name is None else name.encode("utf-8")
        
        # Передаём указатели (None будет интерпретирован как NULL в ctypes)
        result = lib.db_add_player(
            self._h,
            player_id_bytes,
            name_bytes
        )
        return bool(result)

    def remove_player(self, player_id: str) -> bool:
        return bool(lib.db_remove_player(self._h, player_id.encode("utf-8")))

    def add_rating(self, game_name: str, player_id: str, rating: int) -> bool:
        return bool(
            lib.db_add_rating(
                self._h,
                game_name.encode("utf-8"),
                player_id.encode("utf-8"),
                rating,
            )
        )

    def add_similarity(self, game1: str, game2: str) -> bool:
        return bool(
            lib.db_add_similarity(
                self._h,
                game1.encode("utf-8"),
                game2.encode("utf-8"),
            )
        )

    def are_similar(self, game1: str, game2: str) -> bool:
        return bool(
            lib.db_are_similar(
                self._h,
                game1.encode("utf-8"),
                game2.encode("utf-8"),
            )
        )

    # --- Матчи и статистика ---

    def add_match(self, match: Match) -> bool:
        return bool(lib.db_add_match(self._h, match.handle))

    def remove_match(self, match_id: str) -> bool:
        return bool(lib.db_remove_match(self._h, match_id.encode("utf-8")))

    def get_player_rating_in_game(self, player_id: str, game_name: str) -> float:
        return float(
            lib.db_get_player_rating_in_game(
                self._h, player_id.encode("utf-8"), game_name.encode("utf-8")
            )
        )

    # --- Рекомендации и поиск ---

    def _collect_games(self, count: int, array) -> list[BoardGame]:
        result: list[BoardGame] = []
        for i in range(count):
            h = array[i]
            if h:
                result.append(BoardGame(h))
        return result

    def get_recommendations(self, game_name: str, max_results: int = 10) -> list[BoardGame]:
        array_type = BoardGameHandle * max_results
        out = array_type()
        count = lib.db_get_recommendations(
            self._h, game_name.encode("utf-8"), out, max_results
        )
        return self._collect_games(count, out)

    def find_games_by_min_rating(self, min_rating: float, max_results: int = 20) -> list[BoardGame]:
        array_type = BoardGameHandle * max_results
        out = array_type()
        count = lib.db_find_games_by_min_rating(self._h, min_rating, out, max_results)
        return self._collect_games(count, out)

    def find_games_by_feature(
        self, feature_name: str, feature_value: str, max_results: int = 50
    ) -> list[BoardGame]:
        array_type = BoardGameHandle * max_results
        out = array_type()
        count = lib.db_find_games_by_feature(
            self._h,
            feature_name.encode("utf-8"),
            feature_value.encode("utf-8"),
            out,
            max_results,
        )
        return self._collect_games(count, out)

    # --- Веса и статистика ---

    def set_similarity_weights(
        self,
        complexity: float,
        player_count: float,
        game_type: float,
        duration: float,
        mechanics: float,
        genre: float,
        user_params: float,
        min_threshold: float,
        missing_data_penalty: float,
        max_recs: int,
    ) -> None:
        lib.db_set_similarity_weights(
            self._h,
            complexity,
            player_count,
            game_type,
            duration,
            mechanics,
            genre,
            user_params,
            min_threshold,
            missing_data_penalty,
            max_recs,
        )

    def get_recommendation_stats(self) -> dict:
        total = c_int()
        with_recs = c_int()
        avg_recs = c_double()
        avg_sim = c_double()
        ok = lib.db_get_recommendation_stats(
            self._h,
            ctypes.byref(total),
            ctypes.byref(with_recs),
            ctypes.byref(avg_recs),
            ctypes.byref(avg_sim),
        )
        if not ok:
            return {}
        return {
            "total_games": total.value,
            "games_with_recommendations": with_recs.value,
            "average_recommendations_per_game": avg_recs.value,
            "average_similarity_score": avg_sim.value,
        }

    @staticmethod
    def run_tests() -> bool:
        """Запустить тесты всех классов модели."""
        return bool(lib.db_run_tests())


__all__ = ["BoardGame", "GameDatabase", "Match", "DLL_PATH"]



