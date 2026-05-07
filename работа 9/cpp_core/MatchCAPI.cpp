#include "MatchCAPI.h"
#include <cstring>

// Вспомогательная функция для копирования строки в буфер
static void copy_string_to_buffer(const std::string& src, char* buffer, int max_len) {
    if (!buffer || max_len <= 0) {
        return;
    }
    const size_t copy_len = (max_len > 0)
        ? static_cast<size_t>(max_len - 1)
        : 0;
    std::strncpy(buffer, src.c_str(), copy_len);
    buffer[copy_len] = '\0';
}

extern "C" {

MatchHandle match_create(const char* match_id, const char* game_name, const char* date) {
    const std::string id   = match_id ? match_id : "";
    const std::string game = game_name ? game_name : "";
    const std::string dt   = date ? date : "";
    return new Match(id, game, dt);
}

void match_dispose(MatchHandle match) {
    delete match;
}

int match_add_player_result(MatchHandle match, const char* player_id, double result) {
    if (!match || !player_id) {
        return 0;
    }
    return match->addPlayerResult(std::string(player_id), result) ? 1 : 0;
}

void match_get_winner(MatchHandle match, char* buffer, int max_len) {
    if (!match) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(match->getWinner(), buffer, max_len);
}

void match_get_match_id(MatchHandle match, char* buffer, int max_len) {
    if (!match) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(match->getMatchId(), buffer, max_len);
}

void match_get_game_name(MatchHandle match, char* buffer, int max_len) {
    if (!match) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(match->getGameName(), buffer, max_len);
}

void match_get_date(MatchHandle match, char* buffer, int max_len) {
    if (!match) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(match->getDate(), buffer, max_len);
}

} // extern "C"


