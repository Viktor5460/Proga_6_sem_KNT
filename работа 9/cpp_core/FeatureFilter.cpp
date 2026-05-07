#include "FeatureFilter.h"
#include <sstream>

// Конструктор
FeatureFilter::FeatureFilter(const std::map<std::string, std::string>& features) 
    : requiredFeatures(features) {}

// Деструктор
FeatureFilter::~FeatureFilter() {}

// Реализация фильтрации по признакам
std::vector<BoardGame*> FeatureFilter::apply(const std::map<std::string, BoardGame*>& games) const {
    std::vector<BoardGame*> result;
    
    for (const auto& pair : games) {
        BoardGame* game = pair.second;
        if (game && matchesAllFeatures(game)) {
            result.push_back(game);
        }
    }
    
    return result;
}

// Проверка соответствия игры всем требуемым признакам
// Логика: игра должна иметь ВСЕ признаки с точно такими значениями
bool FeatureFilter::matchesAllFeatures(BoardGame* game) const {
    for (const auto& required : requiredFeatures) {
        const std::string& featureName = required.first;
        const std::string& featureValue = required.second;
        
        // Специальная обработка универсальных признаков (число игроков)
        if (featureName == "minPlayers") {
            std::stringstream ss;
            ss << game->getMinPlayers();
            if (ss.str() != featureValue) {
                return false;
            }
        } else if (featureName == "maxPlayers") {
            std::stringstream ss;
            ss << game->getMaxPlayers();
            if (ss.str() != featureValue) {
                return false;
            }
        } else if (featureName == "players") {
            // Специальный признак: проверка диапазона игроков
            // Формат значения: "N" - ищем игры, в которые может играть N игроков
            int playerCount = std::stoi(featureValue);
            if (playerCount < game->getMinPlayers() || playerCount > game->getMaxPlayers()) {
                return false;
            }
        } else {
            // Обычные пользовательские признаки
            if (!game->hasFeature(featureName) || game->getFeature(featureName) != featureValue) {
                return false;
            }
        }
    }
    
    return true;  // Все признаки совпали
}

// Вывод информации о фильтре
void FeatureFilter::printInfo() const {
    std::cout << "FeatureFilter[требуемые признаки: ";
    bool first = true;
    for (const auto& feature : requiredFeatures) {
        if (!first) std::cout << ", ";
        std::cout << feature.first << "='" << feature.second << "'";
        first = false;
    }
    std::cout << "]";
}

// Геттер
std::map<std::string, std::string> FeatureFilter::getRequiredFeatures() const {
    return requiredFeatures;
}

// Автоматические тесты
void FeatureFilter::runTests() {
    std::cout << "\n=== Тестирование класса FeatureFilter ===" << std::endl;
    
    // Создаем тестовые игры с разными признаками (из BGG топ-50)
    BoardGame* g1 = new BoardGame("Brass: Birmingham", "Экономическая стратегия", 2, 4, "2018");
    g1->setComplexity("8");
    g1->addFeature("Жанр", "Стратегия");
    g1->addFeature("ТипИгры", "Евро игра");
    g1->addFeature("Время", "90");
    
    BoardGame* g2 = new BoardGame("Wingspan", "Семейная игра о птицах", 1, 5, "2019");
    g2->setComplexity("4");
    g2->addFeature("Жанр", "Семейная");
    g2->addFeature("ТипИгры", "Семейная");
    g2->addFeature("Время", "55");
    
    BoardGame* g3 = new BoardGame("Terraforming Mars", "Стратегия колонизации Марса", 1, 5, "2016");
    g3->setComplexity("5");
    g3->addFeature("Жанр", "Стратегия");
    g3->addFeature("ТипИгры", "Евро игра");
    g3->addFeature("Время", "120");
    
    std::map<std::string, BoardGame*> games;
    games["Brass: Birmingham"] = g1;
    games["Wingspan"] = g2;
    games["Terraforming Mars"] = g3;
    
    // Тест 1: Фильтр по одному признаку (Жанр = Стратегия)
    std::map<std::string, std::string> filter1Features;
    filter1Features["Жанр"] = "Стратегия";
    FeatureFilter filter1(filter1Features);
    
    std::vector<BoardGame*> result1 = filter1.apply(games);
    std::cout << "Тест 1 - Фильтр Жанр=Стратегия: ";
    if (result1.size() == 2) {  // Brass: Birmingham и Terraforming Mars
        std::cout << "PASSED (найдено " << result1.size() << " игры)" << std::endl;
    } else {
        std::cout << "FAILED (ожидалось 2, найдено " << result1.size() << ")" << std::endl;
    }
    
    // Тест 2: Фильтр по нескольким признакам (Жанр + Сложность)
    std::map<std::string, std::string> filter2Features;
    filter2Features["Жанр"] = "Стратегия";
    filter2Features["ТипИгры"] = "Евро игра";
    FeatureFilter filter2(filter2Features);
    
    std::vector<BoardGame*> result2 = filter2.apply(games);
    std::cout << "Тест 2 - Фильтр Жанр=Стратегия И ТипИгры=Евро игра: ";
    if (result2.size() == 2) {  // Brass: Birmingham и Terraforming Mars
        std::cout << "PASSED (найдено " << result2.size() << " игры)" << std::endl;
    } else {
        std::cout << "FAILED (ожидалось 2, найдено " << result2.size() << ")" << std::endl;
    }
    
    // Тест 3: Фильтр по числу игроков (универсальный признак)
    std::map<std::string, std::string> filter3Features;
    filter3Features["players"] = "3";  // Игры, в которые можно играть втроем
    FeatureFilter filter3(filter3Features);
    
    std::vector<BoardGame*> result3 = filter3.apply(games);
    std::cout << "Тест 3 - Фильтр по числу игроков (3): ";
    if (result3.size() == 3) {  // Все игры поддерживают 3 игроков
        std::cout << "PASSED (найдено " << result3.size() << " игры)" << std::endl;
    } else {
        std::cout << "FAILED (ожидалось 2, найдено " << result3.size() << ")" << std::endl;
    }
    
    // Тест 4: Фильтр с несуществующим значением
    std::map<std::string, std::string> filter4Features;
    filter4Features["Жанр"] = "Несуществующий";
    FeatureFilter filter4(filter4Features);
    
    std::vector<BoardGame*> result4 = filter4.apply(games);
    std::cout << "Тест 4 - Фильтр с несуществующим значением: ";
    if (result4.empty()) {
        std::cout << "PASSED (найдено 0 игр)" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 5: Вывод информации
    std::cout << "Тест 5 - Вывод информации: ";
    filter2.printInfo();
    std::cout << " - OK" << std::endl;
    
    // Очистка памяти
    delete g1;
    delete g2;
    delete g3;
    
    std::cout << "=== Тестирование FeatureFilter завершено ===\n" << std::endl;
}

