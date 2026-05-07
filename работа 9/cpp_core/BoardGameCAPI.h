#ifndef BOARDGAME_C_API_H
#define BOARDGAME_C_API_H

#include "BoardGame.h"

// C-интерфейс к классу BoardGame для использования из Python через ctypes.
// По лекциям: создаём набор C-функций-обёрток над методами класса.

#ifdef _WIN32
    #define BG_API __declspec(dllexport)
#else
    #define BG_API
#endif

extern "C" {

// Оpaque-тип: в C-коде и Python мы будем работать с указателем на BoardGame
// как с непрозрачной "ручкой".
typedef BoardGame* BoardGameHandle;

// === Создание и уничтожение объекта ===

// Аналог конструктора BoardGame(const std::string&, const std::string&, int, int, const std::string&).
BG_API BoardGameHandle bg_create(const char* name,
                          const char* description,
                          int minPlayers,
                          int maxPlayers,
                          const char* edition);

// Уничтожение объекта (обёртка над деструктором).
BG_API void bg_dispose(BoardGameHandle game);

// === Базовые геттеры ===

// Копирует имя игры в переданный буфер (как в примере get_name из лекций).
// Строка всегда завершается '\0', даже при усечении.
BG_API void bg_get_name(BoardGameHandle game, char* buffer, int max_len);

// Копирует описание игры.
BG_API void bg_get_description(BoardGameHandle game, char* buffer, int max_len);

BG_API int  bg_get_min_players(BoardGameHandle game);
BG_API int  bg_get_max_players(BoardGameHandle game);

// === Сложность и длительность ===

// Установка строкового значения сложности (1-10 или текстовое описание).
BG_API void bg_set_complexity(BoardGameHandle game, const char* complexity);

// Получение сложности как строки.
BG_API void bg_get_complexity(BoardGameHandle game, char* buffer, int max_len);

// Установка длительности (среднее время, в минутах).
BG_API void bg_set_duration(BoardGameHandle game, int durationMinutes);

// Получение длительности (если не задана, может вернуть 0).
BG_API int  bg_get_duration(BoardGameHandle game);

// === Признаки и жанровые параметры ===

// Добавить (или обновить) произвольный признак игры.
BG_API int bg_add_feature(BoardGameHandle game, const char* feature_name, const char* feature_value);

// Получить значение произвольного признака.
BG_API void bg_get_feature(BoardGameHandle game, const char* feature_name, char* buffer, int max_len);

// Проверить наличие признака.
BG_API int bg_has_feature(BoardGameHandle game, const char* feature_name);

// Тип игры (Евро, кооперативная и т.п.).
BG_API void bg_set_game_type(BoardGameHandle game, const char* game_type);
BG_API void bg_get_game_type(BoardGameHandle game, char* buffer, int max_len);

// Жанр игры.
BG_API void bg_set_genre(BoardGameHandle game, const char* genre);
BG_API void bg_get_genre(BoardGameHandle game, char* buffer, int max_len);

// Механики игры (строка, например: "Размещение рабочих, Декбилдинг").
BG_API void bg_set_mechanics(BoardGameHandle game, const char* mechanics);
BG_API void bg_get_mechanics(BoardGameHandle game, char* buffer, int max_len);

// === Работа с рейтингами ===

// Получить средний рейтинг игры.
BG_API double bg_get_average_rating(BoardGameHandle game);

// Получить количество оценок.
BG_API int bg_get_ratings_count(BoardGameHandle game);

// Добавить оценку от игрока (1-5).
BG_API int bg_add_rating(BoardGameHandle game, const char* player_id, int rating);

// Удалить признак игры.
BG_API int bg_remove_feature(BoardGameHandle game, const char* feature_name);

} // extern "C"

#endif // BOARDGAME_C_API_H


