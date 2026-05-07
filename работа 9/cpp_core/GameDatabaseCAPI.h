#ifndef GAME_DATABASE_C_API_H
#define GAME_DATABASE_C_API_H

#include "GameDatabase.h"
#include "BoardGameCAPI.h"

// Нужен тип MatchHandle для работы с матчами.
class Match;
typedef Match* MatchHandle;

// C-интерфейс к классу GameDatabase.
// Идея как в лекциях: Python работает с непрозрачными указателями и
// вызывает только C-функции, которые внутри обращаются к C++-классам.

#ifdef _WIN32
    #define DB_API __declspec(dllexport)
#else
    #define DB_API
#endif

extern "C" {

// Непрозрачный тип "ручки" для базы данных.
typedef GameDatabase* GameDatabaseHandle;

// === Создание и уничтожение базы ===

// Создать новую пустую базу данных.
DB_API GameDatabaseHandle db_create();

// Уничтожить базу и освободить всю связанную с ней память.
DB_API void db_dispose(GameDatabaseHandle db);

// === Работа с играми ===

// Добавить уже созданный объект BoardGame в базу.
// Владелец указателя передаёт владение базе (по смыслу addGame).
DB_API int db_add_game(GameDatabaseHandle db, BoardGameHandle game);

// Удалить игру по имени.
DB_API int db_remove_game(GameDatabaseHandle db, const char* name);

// Найти игру по имени, вернуть её "ручку" (BoardGameHandle) или NULL.
DB_API BoardGameHandle db_get_game(GameDatabaseHandle db, const char* name);

// Получить количество игр в базе (size_t — передаём как int для простоты ctypes).
DB_API int db_get_games_count(GameDatabaseHandle db);

// === Работа с игроками и оценками ===

// Добавить игрока по ID и имени.
DB_API int db_add_player(GameDatabaseHandle db, const char* player_id, const char* player_name);

// Удалить игрока по ID.
DB_API int db_remove_player(GameDatabaseHandle db, const char* player_id);

// Поставить оценку игре от игрока (1-5).
DB_API int db_add_rating(GameDatabaseHandle db, const char* game_name, const char* player_id, int rating);

// === Схожесть и рекомендации ===

// Добавить связь схожести между двумя играми.
DB_API int db_add_similarity(GameDatabaseHandle db, const char* game1, const char* game2);

// Проверить, похожи ли две игры.
DB_API int db_are_similar(GameDatabaseHandle db, const char* game1, const char* game2);

// Получить рекомендации для игры: заполняет массив указателей на BoardGame (out_array)
// длиной не более max_results. Возвращает фактическое количество рекомендаций.
DB_API int db_get_recommendations(
    GameDatabaseHandle db,
    const char* game_name,
    BoardGameHandle* out_array,
    int max_results
);

// Найти игры с минимальным средним рейтингом.
DB_API int db_find_games_by_min_rating(
    GameDatabaseHandle db,
    double min_rating,
    BoardGameHandle* out_array,
    int max_results
);

// Найти игры по значению feature (например, Жанр=Стратегия).
DB_API int db_find_games_by_feature(
    GameDatabaseHandle db,
    const char* feature_name,
    const char* feature_value,
    BoardGameHandle* out_array,
    int max_results
);

// === Матчи и статистика игроков ===

// Добавить Match в базу (владение партией переходит базе).
DB_API int db_add_match(GameDatabaseHandle db, MatchHandle match);

// Удалить Match по ID.
DB_API int db_remove_match(GameDatabaseHandle db, const char* match_id);

// Получить средний рейтинг игрока в конкретной игре.
DB_API double db_get_player_rating_in_game(
    GameDatabaseHandle db,
    const char* player_id,
    const char* game_name
);

// === Настройка весов рекомендаций и статистика ===

// Установить веса SimilarityWeights (упрощённый интерфейс).
DB_API void db_set_similarity_weights(
    GameDatabaseHandle db,
    double complexityWeight,
    double playerCountWeight,
    double gameTypeWeight,
    double durationWeight,
    double mechanicsWeight,
    double genreWeight,
    double userParametersWeight,
    double minSimilarityThreshold,
    double missingDataPenalty,
    int maxRecommendations
);

// Получить общую статистику рекомендаций.
DB_API int db_get_recommendation_stats(
    GameDatabaseHandle db,
    int* totalGames,
    int* gamesWithRecommendations,
    double* averageRecommendationsPerGame,
    double* averageSimilarityScore
);

// === Тестирование ===

// Запустить тесты всех классов модели.
// Результаты выводятся в stdout, функция возвращает 1 при успехе, 0 при ошибке.
DB_API int db_run_tests();

} // extern "C"

#endif // GAME_DATABASE_C_API_H


