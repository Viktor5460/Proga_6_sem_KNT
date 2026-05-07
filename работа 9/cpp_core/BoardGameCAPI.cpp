#include "BoardGameCAPI.h"

#include <cstring>  // для std::strncpy

// Реализация C-обёртки для класса BoardGame.
// Структура повторяет пример с Monster из лекций:
// - блок extern "C"
// - функции принимают только C-совместимые типы

extern "C" {

BoardGameHandle bg_create(const char* name,
                          const char* description,
                          int minPlayers,
                          int maxPlayers,
                          const char* edition) {
    // Защищаемся от nullptr, подставляя пустые строки.
    const std::string nameStr        = name ? name : "";
    const std::string descStr        = description ? description : "";
    const std::string editionStr     = edition ? edition : "";

    return new BoardGame(nameStr, descStr, minPlayers, maxPlayers, editionStr);
}

void bg_dispose(BoardGameHandle game) {
    delete game;
}

// Вспомогательная функция для копирования std::string в C-буфер.
static void copy_string_to_buffer(const std::string& src, char* buffer, int max_len) {
    if (!buffer || max_len <= 0) {
        return;
    }
    // Оставляем место под завершающий ноль.
    const size_t copy_len = (max_len > 0)
        ? static_cast<size_t>(max_len - 1)
        : 0;

    std::strncpy(buffer, src.c_str(), copy_len);
    buffer[copy_len] = '\0';
}

void bg_get_name(BoardGameHandle game, char* buffer, int max_len) {
    if (!game) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(game->getName(), buffer, max_len);
}

void bg_get_description(BoardGameHandle game, char* buffer, int max_len) {
    if (!game) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(game->getDescription(), buffer, max_len);
}

int bg_get_min_players(BoardGameHandle game) {
    return game ? game->getMinPlayers() : 0;
}

int bg_get_max_players(BoardGameHandle game) {
    return game ? game->getMaxPlayers() : 0;
}

void bg_set_complexity(BoardGameHandle game, const char* complexity) {
    if (!game) return;
    const std::string value = complexity ? complexity : "";
    game->setComplexity(value);
}

void bg_get_complexity(BoardGameHandle game, char* buffer, int max_len) {
    if (!game) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(game->getComplexity(), buffer, max_len);
}

void bg_set_duration(BoardGameHandle game, int durationMinutes) {
    if (!game) return;
    game->setDuration(durationMinutes);
}

int bg_get_duration(BoardGameHandle game) {
    return game ? game->getDuration() : 0;
}

int bg_add_feature(BoardGameHandle game, const char* feature_name, const char* feature_value) {
    if (!game || !feature_name || !feature_value) {
        return 0;
    }
    return game->addFeature(std::string(feature_name), std::string(feature_value)) ? 1 : 0;
}

void bg_get_feature(BoardGameHandle game, const char* feature_name, char* buffer, int max_len) {
    if (!game || !feature_name) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(game->getFeature(std::string(feature_name)), buffer, max_len);
}

int bg_has_feature(BoardGameHandle game, const char* feature_name) {
    if (!game || !feature_name) {
        return 0;
    }
    return game->hasFeature(std::string(feature_name)) ? 1 : 0;
}

void bg_set_game_type(BoardGameHandle game, const char* game_type) {
    if (!game) return;
    const std::string value = game_type ? game_type : "";
    game->setGameType(value);
}

void bg_get_game_type(BoardGameHandle game, char* buffer, int max_len) {
    if (!game) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(game->getGameType(), buffer, max_len);
}

void bg_set_genre(BoardGameHandle game, const char* genre) {
    if (!game) return;
    const std::string value = genre ? genre : "";
    game->setGenre(value);
}

void bg_get_genre(BoardGameHandle game, char* buffer, int max_len) {
    if (!game) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(game->getGenre(), buffer, max_len);
}

void bg_set_mechanics(BoardGameHandle game, const char* mechanics) {
    if (!game) return;
    const std::string value = mechanics ? mechanics : "";
    game->setMechanics(value);
}

void bg_get_mechanics(BoardGameHandle game, char* buffer, int max_len) {
    if (!game) {
        copy_string_to_buffer("", buffer, max_len);
        return;
    }
    copy_string_to_buffer(game->getMechanics(), buffer, max_len);
}

double bg_get_average_rating(BoardGameHandle game) {
    if (!game) {
        return 0.0;
    }
    return game->getAverageRating();
}

int bg_get_ratings_count(BoardGameHandle game) {
    if (!game) {
        return 0;
    }
    return static_cast<int>(game->getRatingsCount());
}

int bg_add_rating(BoardGameHandle game, const char* player_id, int rating) {
    if (!game || !player_id) {
        return 0;
    }
    return game->addRating(std::string(player_id), rating) ? 1 : 0;
}

int bg_remove_feature(BoardGameHandle game, const char* feature_name) {
    if (!game || !feature_name) {
        return 0;
    }
    return game->removeFeature(std::string(feature_name)) ? 1 : 0;
}

} // extern "C"


