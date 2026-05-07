#include "GameDatabaseCAPI.h"
#include "RatingFilter.h"
#include "FeatureFilter.h"
#include "SimilarGamesFilter.h"
#include "Player.h"
#include "Match.h"
#include "GameRecommendationEngine.h"

// Реализация C-обёртки для GameDatabase.

extern "C" {

GameDatabaseHandle db_create() {
    return new GameDatabase();
}

void db_dispose(GameDatabaseHandle db) {
    delete db;
}

int db_add_game(GameDatabaseHandle db, BoardGameHandle game) {
    if (!db || !game) {
        return 0;
    }
    return db->addGame(game) ? 1 : 0;
}

int db_remove_game(GameDatabaseHandle db, const char* name) {
    if (!db || !name) {
        return 0;
    }
    return db->removeGame(std::string(name)) ? 1 : 0;
}

BoardGameHandle db_get_game(GameDatabaseHandle db, const char* name) {
    if (!db || !name) {
        return nullptr;
    }
    return db->getGame(std::string(name));
}

int db_get_games_count(GameDatabaseHandle db) {
    if (!db) {
        return 0;
    }
    return static_cast<int>(db->getAllGames().size());
}

int db_add_player(GameDatabaseHandle db, const char* player_id, const char* player_name) {
    if (!db || !player_id || !player_name) {
        return 0;
    }
    Player* player = new Player(std::string(player_id), std::string(player_name));
    return db->addPlayer(player) ? 1 : 0;
}

int db_remove_player(GameDatabaseHandle db, const char* player_id) {
    if (!db || !player_id) {
        return 0;
    }
    return db->removePlayer(std::string(player_id)) ? 1 : 0;
}

int db_add_rating(GameDatabaseHandle db, const char* game_name, const char* player_id, int rating) {
    if (!db || !game_name || !player_id) {
        return 0;
    }
    return db->addRating(std::string(game_name), std::string(player_id), rating) ? 1 : 0;
}

int db_add_similarity(GameDatabaseHandle db, const char* game1, const char* game2) {
    if (!db || !game1 || !game2) {
        return 0;
    }
    return db->addSimilarity(std::string(game1), std::string(game2)) ? 1 : 0;
}

int db_are_similar(GameDatabaseHandle db, const char* game1, const char* game2) {
    if (!db || !game1 || !game2) {
        return 0;
    }
    return db->areSimilar(std::string(game1), std::string(game2)) ? 1 : 0;
}

int db_get_recommendations(
    GameDatabaseHandle db,
    const char* game_name,
    BoardGameHandle* out_array,
    int max_results
) {
    if (!db || !game_name || !out_array || max_results <= 0) {
        return 0;
    }

    auto recs = db->getRecommendations(std::string(game_name), max_results);
    int count = static_cast<int>(recs.size());
    if (count > max_results) {
        count = max_results;
    }

    for (int i = 0; i < count; ++i) {
        out_array[i] = db->getGame(recs[i].gameName);
    }

    return count;
}

int db_find_games_by_min_rating(
    GameDatabaseHandle db,
    double min_rating,
    BoardGameHandle* out_array,
    int max_results
) {
    if (!db || !out_array || max_results <= 0) {
        return 0;
    }

    RatingFilter filter(min_rating);
    auto games = db->findGames(&filter);

    int count = static_cast<int>(games.size());
    if (count > max_results) {
        count = max_results;
    }

    for (int i = 0; i < count; ++i) {
        out_array[i] = games[i];
    }

    return count;
}

int db_find_games_by_feature(
    GameDatabaseHandle db,
    const char* feature_name,
    const char* feature_value,
    BoardGameHandle* out_array,
    int max_results
) {
    if (!db || !feature_name || !feature_value || !out_array || max_results <= 0) {
        return 0;
    }

    std::map<std::string, std::string> features;
    features[std::string(feature_name)] = std::string(feature_value);

    FeatureFilter filter(features);
    auto games = db->findGames(&filter);

    int count = static_cast<int>(games.size());
    if (count > max_results) {
        count = max_results;
    }

    for (int i = 0; i < count; ++i) {
        out_array[i] = games[i];
    }

    return count;
}

int db_add_match(GameDatabaseHandle db, MatchHandle match) {
    if (!db || !match) {
        return 0;
    }
    return db->addMatch(match) ? 1 : 0;
}

int db_remove_match(GameDatabaseHandle db, const char* match_id) {
    if (!db || !match_id) {
        return 0;
    }
    return db->removeMatch(std::string(match_id)) ? 1 : 0;
}

double db_get_player_rating_in_game(
    GameDatabaseHandle db,
    const char* player_id,
    const char* game_name
) {
    if (!db || !player_id || !game_name) {
        return 0.0;
    }
    return db->getPlayerRatingInGame(
        std::string(player_id),
        std::string(game_name)
    );
}

void db_set_similarity_weights(
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
) {
    if (!db) return;

    SimilarityWeights weights;
    weights.complexityWeight       = complexityWeight;
    weights.playerCountWeight      = playerCountWeight;
    weights.gameTypeWeight         = gameTypeWeight;
    weights.durationWeight         = durationWeight;
    weights.mechanicsWeight        = mechanicsWeight;
    weights.genreWeight            = genreWeight;
    weights.userParametersWeight   = userParametersWeight;
    weights.minSimilarityThreshold = minSimilarityThreshold;
    weights.missingDataPenalty     = missingDataPenalty;
    weights.maxRecommendations     = maxRecommendations;

    weights.normalizeWeights();

    if (weights.isValid()) {
        db->setRecommendationWeights(weights);
    }
}

int db_get_recommendation_stats(
    GameDatabaseHandle db,
    int* totalGames,
    int* gamesWithRecommendations,
    double* averageRecommendationsPerGame,
    double* averageSimilarityScore
) {
    if (!db) return 0;

    auto stats = db->getRecommendationStats();

    if (totalGames) {
        *totalGames = stats.totalGames;
    }
    if (gamesWithRecommendations) {
        *gamesWithRecommendations = stats.gamesWithRecommendations;
    }
    if (averageRecommendationsPerGame) {
        *averageRecommendationsPerGame = stats.averageRecommendationsPerGame;
    }
    if (averageSimilarityScore) {
        *averageSimilarityScore = stats.averageSimilarityScore;
    }

    return 1;
}

int db_run_tests() {
    try {
        // Запускаем тесты всех классов в том же порядке, что и в main.cpp
        Player::runTests();
        Match::runTests();
        RatingFilter::runTests();
        FeatureFilter::runTests();
        SimilarGamesFilter::runTests();
        GameDatabase::runTests();
        GameRecommendationEngine::runTests();
        return 1;
    } catch (...) {
        return 0;
    }
}

} // extern "C"


