#ifndef RATING_FILTER_H
#define RATING_FILTER_H

#include "Filter.h"
#include "BoardGame.h"
#include <iostream>

// фильтр по минимальному рейтингу
class RatingFilter : public Filter {
private:
    double minRating; // минимальный требуемый рейтинг
    
public:
    explicit RatingFilter(double minRating);
    virtual ~RatingFilter();
    virtual std::vector<BoardGame*> apply(const std::map<std::string, BoardGame*>& games) const override;
    virtual void printInfo() const override;
    double getMinRating() const;
    static void runTests();
};

#endif

