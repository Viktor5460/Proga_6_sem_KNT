#ifndef FILTER_H
#define FILTER_H

#include <vector>
#include <map>
#include <string>

class BoardGame;

// абстрактный базовый класс для фильтров
class Filter {
public:
    virtual ~Filter() {}
    virtual std::vector<BoardGame*> apply(const std::map<std::string, BoardGame*>& games) const = 0;
    virtual void printInfo() const = 0;
};

#endif

