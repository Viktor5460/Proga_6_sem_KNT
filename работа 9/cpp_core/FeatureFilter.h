#ifndef FEATURE_FILTER_H
#define FEATURE_FILTER_H

#include "Filter.h"
#include "BoardGame.h"
#include <iostream>

// фильтр по признакам игры
class FeatureFilter : public Filter {
private:
    std::map<std::string, std::string> requiredFeatures; // требуемые признаки
    
public:
    explicit FeatureFilter(const std::map<std::string, std::string>& features);
    virtual ~FeatureFilter();
    virtual std::vector<BoardGame*> apply(const std::map<std::string, BoardGame*>& games) const override;
    virtual void printInfo() const override;
    std::map<std::string, std::string> getRequiredFeatures() const;
    static void runTests();
    
private:
    bool matchesAllFeatures(BoardGame* game) const; // проверка соответствия всем признакам
};

#endif

