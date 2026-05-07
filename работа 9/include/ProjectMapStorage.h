#pragma once

#include "GameRecord.h"

#include <map>

class ProjectMapStorage {
public:
    void insert(const GameRecord& game) {
        gamesByRating_[game.rating] = game;
    }

    bool contains(double rating) const {
        return gamesByRating_.find(rating) != gamesByRating_.end();
    }

    void erase(double rating) {
        gamesByRating_.erase(rating);
    }

    std::size_t size() const {
        return gamesByRating_.size();
    }

private:
    // Аналогично текущему проекту: ассоциативный контейнер std::map.
    std::map<double, GameRecord> gamesByRating_;
};
