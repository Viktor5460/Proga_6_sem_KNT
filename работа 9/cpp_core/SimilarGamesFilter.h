#ifndef SIMILAR_GAMES_FILTER_H
#define SIMILAR_GAMES_FILTER_H

#include "Filter.h"
#include "BoardGame.h"
#include <set>
#include <iostream>

// фильтр похожих игр
class SimilarGamesFilter : public Filter {
private:
    std::vector<std::string> referenceGames; // игры-образцы
    const std::set<std::pair<std::string, std::string>>* similarityData; // данные о схожести
    
public:
    SimilarGamesFilter(const std::vector<std::string>& referenceGames,
                       const std::set<std::pair<std::string, std::string>>* similarityData);
    virtual ~SimilarGamesFilter();
    virtual std::vector<BoardGame*> apply(const std::map<std::string, BoardGame*>& games) const override;
    virtual void printInfo() const override;
    std::vector<std::string> getReferenceGames() const;
    static void runTests();
    
private:
    bool areSimilar(const std::string& game1, const std::string& game2) const; // проверка схожести
    int countSimilarityScore(const std::string& gameName) const; // подсчет очков схожести
};

#endif

