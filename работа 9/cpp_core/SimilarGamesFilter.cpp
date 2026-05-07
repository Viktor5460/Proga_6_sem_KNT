#include "SimilarGamesFilter.h"
#include <algorithm>

// Конструктор
SimilarGamesFilter::SimilarGamesFilter(
    const std::vector<std::string>& referenceGames,
    const std::set<std::pair<std::string, std::string>>* similarityData)
    : referenceGames(referenceGames), similarityData(similarityData) {}

// Деструктор
SimilarGamesFilter::~SimilarGamesFilter() {}

// Реализация фильтрации по схожести
std::vector<BoardGame*> SimilarGamesFilter::apply(const std::map<std::string, BoardGame*>& games) const {
    // Структура для хранения игры и её "счета схожести"
    std::vector<std::pair<BoardGame*, int>> gamesWithScores;
    
    for (const auto& pair : games) {
        BoardGame* game = pair.second;
        if (!game) continue;
        
        std::string gameName = game->getName();
        
        // Пропускаем сами игры-образцы
        if (std::find(referenceGames.begin(), referenceGames.end(), gameName) != referenceGames.end()) {
            continue;
        }
        
        // Считаем степень схожести (с сколькими образцами схожа эта игра)
        int score = countSimilarityScore(gameName);
        
        if (score > 0) {
            gamesWithScores.push_back({game, score});
        }
    }
    
    // Сортируем по убыванию степени схожести
    std::sort(gamesWithScores.begin(), gamesWithScores.end(),
        [](const std::pair<BoardGame*, int>& a, const std::pair<BoardGame*, int>& b) {
            return a.second > b.second;  // Больший счет = выше в списке
        });
    
    // Формируем результат (только указатели на игры)
    std::vector<BoardGame*> result;
    for (const auto& gameScore : gamesWithScores) {
        result.push_back(gameScore.first);
    }
    
    return result;
}

// Проверка схожести двух игр
// Учитываем симметричность: если есть пара (A, B), то A схожа с B и B схожа с A
bool SimilarGamesFilter::areSimilar(const std::string& game1, const std::string& game2) const {
    if (!similarityData) return false;
    
    // Проверяем оба порядка, так как связь симметрична
    std::pair<std::string, std::string> pair1(game1, game2);
    std::pair<std::string, std::string> pair2(game2, game1);
    
    return similarityData->find(pair1) != similarityData->end() ||
           similarityData->find(pair2) != similarityData->end();
}

// Подсчет степени схожести игры с образцами
// Чем больше образцов схожи с игрой, тем выше счет
int SimilarGamesFilter::countSimilarityScore(const std::string& gameName) const {
    int score = 0;
    
    for (const std::string& referenceGame : referenceGames) {
        if (areSimilar(gameName, referenceGame)) {
            score++;
        }
    }
    
    return score;
}

// Вывод информации о фильтре
void SimilarGamesFilter::printInfo() const {
    std::cout << "SimilarGamesFilter[образцы: ";
    for (size_t i = 0; i < referenceGames.size(); ++i) {
        if (i > 0) std::cout << ", ";
        std::cout << "'" << referenceGames[i] << "'";
    }
    std::cout << "]";
}

// Геттер
std::vector<std::string> SimilarGamesFilter::getReferenceGames() const {
    return referenceGames;
}

// Автоматические тесты
void SimilarGamesFilter::runTests() {
    std::cout << "\n=== Тестирование класса SimilarGamesFilter ===" << std::endl;
    
    // Создаем тестовые игры (из BGG топ-50)
    BoardGame* g1 = new BoardGame("Brass: Birmingham", "Экономическая стратегия", 2, 4, "2018");
    BoardGame* g2 = new BoardGame("Brass: Lancashire", "Экономическая стратегия", 2, 4, "2007");
    BoardGame* g3 = new BoardGame("Terraforming Mars", "Стратегия колонизации Марса", 1, 5, "2016");
    BoardGame* g4 = new BoardGame("Wingspan", "Семейная игра о птицах", 1, 5, "2019");
    BoardGame* g5 = new BoardGame("Ark Nova", "Стратегия зоопарка", 1, 4, "2021");
    
    std::map<std::string, BoardGame*> games;
    games["Brass: Birmingham"] = g1;
    games["Brass: Lancashire"] = g2;
    games["Terraforming Mars"] = g3;
    games["Wingspan"] = g4;
    games["Ark Nova"] = g5;
    
    // Создаем данные о схожести
    // Логика: Brass: Birmingham похож на Brass: Lancashire, Terraforming Mars похож на Wingspan
    std::set<std::pair<std::string, std::string>> similarities;
    similarities.insert({"Brass: Birmingham", "Brass: Lancashire"});
    similarities.insert({"Terraforming Mars", "Wingspan"});
    similarities.insert({"Ark Nova", "Wingspan"});
    
    // Тест 1: Поиск игр, похожих на Brass: Birmingham
    std::vector<std::string> ref1 = {"Brass: Birmingham"};
    SimilarGamesFilter filter1(ref1, &similarities);
    
    std::vector<BoardGame*> result1 = filter1.apply(games);
    std::cout << "Тест 1 - Похожие на Brass: Birmingham: ";
    if (result1.size() == 1) {  // Brass: Lancashire
        std::cout << "PASSED (найдено " << result1.size() << " игра)" << std::endl;
        for (auto game : result1) {
            std::cout << "  - " << game->getName() << std::endl;
        }
    } else {
        std::cout << "FAILED (ожидалось 1, найдено " << result1.size() << ")" << std::endl;
    }
    
    // Тест 2: Поиск игр, похожих на Terraforming Mars И Wingspan
    std::vector<std::string> ref2 = {"Terraforming Mars", "Wingspan"};
    SimilarGamesFilter filter2(ref2, &similarities);
    
    std::vector<BoardGame*> result2 = filter2.apply(games);
    std::cout << "\nТест 2 - Похожие на Terraforming Mars ИЛИ Wingspan: ";
    if (result2.size() >= 1) {  // Минимум Ark Nova (похож на Wingspan)
        std::cout << "PASSED (найдено " << result2.size() << " игр)" << std::endl;
        std::cout << "  Проверка сортировки по степени схожести:" << std::endl;
        for (auto game : result2) {
            std::cout << "  - " << game->getName() << std::endl;
        }
    } else {
        std::cout << "FAILED (ожидалось минимум 1, найдено " << result2.size() << ")" << std::endl;
    }
    
    // Тест 3: Поиск игр, для которых нет схожих
    std::vector<std::string> ref3 = {"Несуществующая игра"};
    SimilarGamesFilter filter3(ref3, &similarities);
    
    std::vector<BoardGame*> result3 = filter3.apply(games);
    std::cout << "\nТест 3 - Нет схожих игр: ";
    if (result3.empty()) {
        std::cout << "PASSED (найдено 0 игр)" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 4: Вывод информации
    std::cout << "\nТест 4 - Вывод информации: ";
    filter2.printInfo();
    std::cout << " - OK" << std::endl;
    
    // Очистка памяти
    delete g1;
    delete g2;
    delete g3;
    delete g4;
    delete g5;
    
    std::cout << "=== Тестирование SimilarGamesFilter завершено ===\n" << std::endl;
}

