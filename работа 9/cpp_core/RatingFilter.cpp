#include "RatingFilter.h"
#include <iomanip>

RatingFilter::RatingFilter(double minRating) : minRating(minRating) {}

RatingFilter::~RatingFilter() {}

std::vector<BoardGame*> RatingFilter::apply(const std::map<std::string, BoardGame*>& games) const {
    std::vector<BoardGame*> result;
    
    // отбираем игры с рейтингом выше порога
    for (const auto& pair : games) {
        BoardGame* game = pair.second;
        if (game && game->getAverageRating() >= minRating) {
            result.push_back(game);
        }
    }
    
    return result;
}

void RatingFilter::printInfo() const {
    std::cout << "RatingFilter[минимальный рейтинг >= " << std::fixed 
              << std::setprecision(2) << minRating << "]";
}

double RatingFilter::getMinRating() const {
    return minRating;
}
void RatingFilter::runTests() {
    std::cout << "\n=== Тестирование класса RatingFilter ===" << std::endl;
    
    BoardGame* g1 = new BoardGame("Игра А", "Описание", 2, 4, "1-е издание");
    BoardGame* g2 = new BoardGame("Игра Б", "Описание", 2, 6, "2-е издание");
    BoardGame* g3 = new BoardGame("Игра В", "Описание", 3, 5, "1-е издание");
    
    g1->addRating("p1", 5);
    g1->addRating("p2", 5);
    
    g2->addRating("p1", 3);
    g2->addRating("p2", 4);
    
    g3->addRating("p1", 4);
    g3->addRating("p2", 4);
    g3->addRating("p3", 5);
    
    std::map<std::string, BoardGame*> games;
    games["Игра А"] = g1;
    games["Игра Б"] = g2;
    games["Игра В"] = g3;
    
    RatingFilter filter1(4.0);
    std::vector<BoardGame*> result1 = filter1.apply(games);
    
    std::cout << "Тест 1 - Фильтр рейтинг >= 4.0:" << std::endl;
    std::cout << "  Ожидается 2 игры с рейтингом >= 4.0" << std::endl;
    std::cout << "  Найдено игр: " << result1.size() << std::endl;
    if (!result1.empty()) {
        std::cout << "  Отфильтрованные игры: ";
        for (size_t i = 0; i < result1.size(); ++i) {
            if (i > 0) std::cout << ", ";
            std::cout << result1[i]->getName() << " (" 
                      << std::fixed << std::setprecision(1) 
                      << result1[i]->getAverageRating() << ")";
        }
        std::cout << std::endl;
    }
    std::cout << "  Результат: ";
    if (result1.size() == 2) {
        std::cout << "PASSED ✓" << std::endl;
    } else {
        std::cout << "FAILED ✗ (ожидалось 2)" << std::endl;
    }
    
    RatingFilter filter2(5.0);
    std::vector<BoardGame*> result2 = filter2.apply(games);
    
    std::cout << "Тест 2 - Фильтр рейтинг >= 5.0:" << std::endl;
    std::cout << "  Ожидается 1 игра с рейтингом >= 5.0" << std::endl;
    std::cout << "  Найдено игр: " << result2.size() << std::endl;
    if (!result2.empty()) {
        std::cout << "  Отфильтрованные игры: ";
        for (size_t i = 0; i < result2.size(); ++i) {
            if (i > 0) std::cout << ", ";
            std::cout << result2[i]->getName() << " (" 
                      << std::fixed << std::setprecision(1) 
                      << result2[i]->getAverageRating() << ")";
        }
        std::cout << std::endl;
    }
    std::cout << "  Результат: ";
    if (result2.size() == 1) {
        std::cout << "PASSED ✓" << std::endl;
    } else {
        std::cout << "FAILED ✗ (ожидалось 1)" << std::endl;
    }
    
    RatingFilter filter3(6.0);
    std::vector<BoardGame*> result3 = filter3.apply(games);
    
    std::cout << "Тест 3 - Фильтр рейтинг >= 6.0:" << std::endl;
    std::cout << "  Ожидается 0 игр с рейтингом >= 6.0" << std::endl;
    std::cout << "  Найдено игр: " << result3.size() << std::endl;
    std::cout << "  Результат: ";
    if (result3.empty()) {
        std::cout << "PASSED ✓" << std::endl;
    } else {
        std::cout << "FAILED ✗ (ожидалось 0)" << std::endl;
    }
    
    std::cout << "Тест 4 - Вывод информации:" << std::endl;
    std::cout << "  Информация о фильтре: ";
    filter1.printInfo();
    std::cout << " ✓" << std::endl;
    
    delete g1;
    delete g2;
    delete g3;
    
    std::cout << "=== Тестирование RatingFilter завершено ===\n" << std::endl;
}

