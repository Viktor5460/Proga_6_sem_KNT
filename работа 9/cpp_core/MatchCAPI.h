#ifndef MATCH_C_API_H
#define MATCH_C_API_H

#include "Match.h"

#ifdef _WIN32
    #define MATCH_API __declspec(dllexport)
#else
    #define MATCH_API
#endif

extern "C" {

typedef Match* MatchHandle;

// Создать новую партию.
MATCH_API MatchHandle match_create(const char* match_id, const char* game_name, const char* date);

// Уничтожить партию (если она не передана в GameDatabase).
MATCH_API void match_dispose(MatchHandle match);

// Добавить результат игрока.
MATCH_API int match_add_player_result(MatchHandle match, const char* player_id, double result);

// Получить победителя партии (ID игрока с максимальным результатом).
MATCH_API void match_get_winner(MatchHandle match, char* buffer, int max_len);

// Получить ID партии.
MATCH_API void match_get_match_id(MatchHandle match, char* buffer, int max_len);

// Получить название игры.
MATCH_API void match_get_game_name(MatchHandle match, char* buffer, int max_len);

// Получить дату партии.
MATCH_API void match_get_date(MatchHandle match, char* buffer, int max_len);

} // extern "C"

#endif // MATCH_C_API_H


