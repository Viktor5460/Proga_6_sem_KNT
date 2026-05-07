#include "GameDatabase.h"
#include "RatingFilter.h"
#include "FeatureFilter.h"
#include "SimilarGamesFilter.h"
#include "GameRecommendationEngine.h"
#include <iostream>
#include <iomanip>

// Конструктор
GameDatabase::GameDatabase() {
    // Инициализируем систему рекомендаций
    recommendationEngine = std::make_unique<GameRecommendationEngine>();
}

// Деструктор - освобождает всю выделенную память
GameDatabase::~GameDatabase() {
    // Удаляем все игры
    for (auto& pair : games) {
        delete pair.second;
    }
    
    // Удаляем всех игроков
    for (auto& pair : players) {
        delete pair.second;
    }
    
    // Удаляем все партии
    for (Match* match : matches) {
        delete match;
    }
}

// === Управление играми ===

bool GameDatabase::addGame(BoardGame* game) {
    if (!game) return false;
    
    std::string name = game->getName();
    if (games.find(name) != games.end()) {
        return false;  // Игра с таким названием уже существует
    }
    
    games[name] = game;
    
    // Добавляем игру в систему рекомендаций
    if (recommendationEngine) {
        recommendationEngine->addGame(game);
    }
    
    return true;
}

bool GameDatabase::removeGame(const std::string& gameName) {
    auto it = games.find(gameName);
    if (it == games.end()) {
        return false;
    }
    
    // Удаляем игру из системы рекомендаций
    if (recommendationEngine) {
        recommendationEngine->removeGame(gameName);
    }
    
    delete it->second;
    games.erase(it);
    return true;
}

BoardGame* GameDatabase::getGame(const std::string& gameName) const {
    auto it = games.find(gameName);
    return (it != games.end()) ? it->second : nullptr;
}

// Возврат по const ссылке - избегаем копирования большого контейнера
const std::map<std::string, BoardGame*>& GameDatabase::getAllGames() const {
    return games;
}

// Перегрузка operator[] для удобного доступа к играм
// Возвращает указатель на игру или nullptr, если игра не найдена
BoardGame* GameDatabase::operator[](const std::string& gameName) const {
    return getGame(gameName);
}

// === Управление игроками ===

bool GameDatabase::addPlayer(Player* player) {
    if (!player) return false;
    
    std::string id = player->getPlayerId();
    if (players.find(id) != players.end()) {
        return false;  // Игрок с таким ID уже существует
    }
    
    players[id] = player;
    return true;
}

bool GameDatabase::removePlayer(const std::string& playerId) {
    auto it = players.find(playerId);
    if (it == players.end()) {
        return false;
    }
    
    delete it->second;
    players.erase(it);
    return true;
}

Player* GameDatabase::getPlayer(const std::string& playerId) const {
    auto it = players.find(playerId);
    return (it != players.end()) ? it->second : nullptr;
}

// Возврат по const ссылке - избегаем копирования контейнера
const std::map<std::string, Player*>& GameDatabase::getAllPlayers() const {
    return players;
}

// === Управление партиями ===

bool GameDatabase::addMatch(Match* match) {
    if (!match) return false;
    
    // Проверяем, что игра существует
    if (games.find(match->getGameName()) == games.end()) {
        return false;  // Игра не найдена
    }
    
    // Добавляем партию в общий список
    matches.push_back(match);
    
    // Добавляем партию в историю каждого игрока
    std::map<std::string, double> results = match->getPlayerResults();
    for (const auto& playerResult : results) {
        const std::string& playerId = playerResult.first;
        Player* player = getPlayer(playerId);
        if (player) {
            player->addMatchToHistory(match->getMatchId());
        }
    }
    
    return true;
}

Match* GameDatabase::getMatch(const std::string& matchId) const {
    for (Match* match : matches) {
        if (match && match->getMatchId() == matchId) {
            return match;
        }
    }
    return nullptr;
}

bool GameDatabase::removeMatch(const std::string& matchId) {
    for (auto it = matches.begin(); it != matches.end(); ++it) {
        Match* match = *it;
        if (match && match->getMatchId() == matchId) {
            delete match;
            matches.erase(it);
            return true;
        }
    }
    return false;
}

// Возврат по const ссылке - избегаем копирования вектора
const std::vector<Match*>& GameDatabase::getAllMatches() const {
    return matches;
}

std::vector<Match*> GameDatabase::getMatchesByGame(const std::string& gameName) const {
    std::vector<Match*> result;
    
    for (Match* match : matches) {
        if (match && match->getGameName() == gameName) {
            result.push_back(match);
        }
    }
    
    return result;
}

std::vector<Match*> GameDatabase::getMatchesByPlayer(const std::string& playerId) const {
    std::vector<Match*> result;
    
    for (Match* match : matches) {
        if (match && match->hasPlayer(playerId)) {
            result.push_back(match);
        }
    }
    
    return result;
}

// === Управление оценками ===

bool GameDatabase::addRating(const std::string& gameName, const std::string& playerId, int rating) {
    BoardGame* game = getGame(gameName);
    Player* player = getPlayer(playerId);
    
    if (!game || !player) {
        return false;
    }
    
    return game->addRating(playerId, rating);
}

// === Управление схожестью игр ===

bool GameDatabase::addSimilarity(const std::string& game1, const std::string& game2) {
    // Проверяем существование обеих игр
    if (games.find(game1) == games.end() || games.find(game2) == games.end()) {
        return false;
    }
    
    // Избегаем самосвязей
    if (game1 == game2) {
        return false;
    }
    
    // Добавляем связь (храним в лексикографическом порядке для единообразия)
    std::string first = (game1 < game2) ? game1 : game2;
    std::string second = (game1 < game2) ? game2 : game1;
    
    similarGames.insert({first, second});
    return true;
}

bool GameDatabase::areSimilar(const std::string& game1, const std::string& game2) const {
    std::string first = (game1 < game2) ? game1 : game2;
    std::string second = (game1 < game2) ? game2 : game1;
    
    return similarGames.find({first, second}) != similarGames.end();
}

std::vector<std::string> GameDatabase::getSimilarGames(const std::string& gameName) const {
    std::vector<std::string> result;
    
    for (const auto& pair : similarGames) {
        if (pair.first == gameName) {
            result.push_back(pair.second);
        } else if (pair.second == gameName) {
            result.push_back(pair.first);
        }
    }
    
    return result;
}

const std::set<std::pair<std::string, std::string>>* GameDatabase::getSimilarityData() const {
    return &similarGames;
}

// === Статистика и аналитика ===

double GameDatabase::getPlayerRatingInGame(const std::string& playerId, const std::string& gameName) const {
    // Находим все партии игрока в указанной игре
    std::vector<Match*> playerMatches = getMatchesByPlayer(playerId);
    
    std::vector<double> results;
    for (Match* match : playerMatches) {
        if (match->getGameName() == gameName) {
            double result = match->getPlayerResult(playerId);
            if (result >= 0) {  // Проверка на валидность результата
                results.push_back(result);
            }
        }
    }
    
    // Используем метод Player для расчета среднего
    Player* player = getPlayer(playerId);
    if (player) {
        return player->calculateRatingInGame(results);
    }
    
    return 0.0;
}

std::vector<std::string> GameDatabase::getPlayerGames(const std::string& playerId) const {
    std::vector<Match*> playerMatches = getMatchesByPlayer(playerId);
    
    std::set<std::string> uniqueGames;  // Используем set для уникальности
    for (Match* match : playerMatches) {
        uniqueGames.insert(match->getGameName());
    }
    
    return std::vector<std::string>(uniqueGames.begin(), uniqueGames.end());
}

// === Фильтрация игр ===

std::vector<BoardGame*> GameDatabase::findGames(Filter* filter) const {
    if (!filter) {
        return std::vector<BoardGame*>();
    }
    
    std::vector<BoardGame*> result = filter->apply(games);
    sortGamesByRating(result);
    return result;
}

std::vector<BoardGame*> GameDatabase::findGames(const std::vector<Filter*>& filters) const {
    if (filters.empty()) {
        return std::vector<BoardGame*>();
    }
    
    // Применяем первый фильтр ко всем играм
    std::vector<BoardGame*> result = filters[0]->apply(games);
    
    // Последовательно применяем остальные фильтры к результату
    for (size_t i = 1; i < filters.size(); ++i) {
        // Преобразуем вектор в map для передачи в фильтр
        std::map<std::string, BoardGame*> tempMap;
        for (BoardGame* game : result) {
            tempMap[game->getName()] = game;
        }
        
        result = filters[i]->apply(tempMap);
    }
    
    sortGamesByRating(result);
    return result;
}

// Сортировка игр по убыванию среднего рейтинга
void GameDatabase::sortGamesByRating(std::vector<BoardGame*>& games) const {
    std::sort(games.begin(), games.end(), 
        [](BoardGame* a, BoardGame* b) {
            return a->getAverageRating() > b->getAverageRating();
        });
}

// === Вывод информации ===

void GameDatabase::printAllGames() const {
    std::cout << "\n=== Все игры в базе ===" << std::endl;
    if (games.empty()) {
        std::cout << "База игр пуста." << std::endl;
        return;
    }
    
    for (const auto& pair : games) {
        pair.second->printInfo();
        std::cout << std::endl;
    }
}

void GameDatabase::printAllPlayers() const {
    std::cout << "\n=== Все игроки ===" << std::endl;
    if (players.empty()) {
        std::cout << "Нет зарегистрированных игроков." << std::endl;
        return;
    }
    
    for (const auto& pair : players) {
        pair.second->printInfo();
        std::cout << std::endl;
    }
}

void GameDatabase::printAllMatches() const {
    std::cout << "\n=== Все партии ===" << std::endl;
    if (matches.empty()) {
        std::cout << "Партий пока не было." << std::endl;
        return;
    }
    
    for (Match* match : matches) {
        match->printInfo();
        std::cout << std::endl;
    }
}

void GameDatabase::printStatistics() const {
    std::cout << "\n=== Статистика базы данных ===" << std::endl;
    std::cout << "Всего игр: " << games.size() << std::endl;
    std::cout << "Всего игроков: " << players.size() << std::endl;
    std::cout << "Всего партий: " << matches.size() << std::endl;
    std::cout << "Связей схожести: " << similarGames.size() << std::endl;
}

// === Автоматические тесты ===

void GameDatabase::runTests() {
    std::cout << "\n=== Тестирование класса GameDatabase ===" << std::endl;
    
    GameDatabase db;
    
    // Тест 1: Добавление игр (из BGG топ-50)
    BoardGame* g1 = new BoardGame("Brass: Birmingham", "Экономическая стратегия", 2, 4, "2018");
    BoardGame* g2 = new BoardGame("Wingspan", "Семейная игра о птицах", 1, 5, "2019");
    BoardGame* g3 = new BoardGame("Terraforming Mars", "Стратегия колонизации Марса", 1, 5, "2016");
    
    db.addGame(g1);
    db.addGame(g2);
    db.addGame(g3);
    
    std::cout << "Тест 1 - Добавление игр: ";
    if (db.getAllGames().size() == 3) {
        std::cout << "PASSED" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 2: Добавление игроков
    Player* p1 = new Player("player_001", "Иван");
    Player* p2 = new Player("player_002", "Мария");
    Player* p3 = new Player("player_003", "Петр");
    
    db.addPlayer(p1);
    db.addPlayer(p2);
    db.addPlayer(p3);
    
    std::cout << "Тест 2 - Добавление игроков: ";
    if (db.getAllPlayers().size() == 3) {
        std::cout << "PASSED" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 3: Выставление оценок
    db.addRating("Brass: Birmingham", "player_001", 5);
    db.addRating("Brass: Birmingham", "player_002", 4);
    db.addRating("Wingspan", "player_001", 4);
    db.addRating("Wingspan", "player_003", 5);
    db.addRating("Terraforming Mars", "player_002", 3);
    
    std::cout << "Тест 3 - Выставление оценок: ";
    BoardGame* brass = db.getGame("Brass: Birmingham");
    if (brass && brass->getRatings().size() == 2) {
        std::cout << "PASSED" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 4: Добавление партий
    Match* m1 = new Match("match_001", "Brass: Birmingham", "2024-01-15");
    m1->addPlayerResult("player_001", 1.0);  // Победа
    m1->addPlayerResult("player_002", 0.0);  // Поражение
    
    Match* m2 = new Match("match_002", "Wingspan", "2024-01-16");
    m2->addPlayerResult("player_001", 85.0);
    m2->addPlayerResult("player_002", 92.0);
    m2->addPlayerResult("player_003", 78.0);
    
    db.addMatch(m1);
    db.addMatch(m2);
    
    std::cout << "Тест 4 - Добавление партий: ";
    if (db.getAllMatches().size() == 2) {
        std::cout << "PASSED" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 5: Получение партий игрока
    std::vector<Match*> player1Matches = db.getMatchesByPlayer("player_001");
    
    std::cout << "Тест 5 - Получение партий игрока: ";
    if (player1Matches.size() == 2) {
        std::cout << "PASSED" << std::endl;
    } else {
        std::cout << "FAILED (ожидалось 2, получено " << player1Matches.size() << ")" << std::endl;
    }
    
    // Тест 6: Расчет рейтинга игрока в игре
    double rating = db.getPlayerRatingInGame("player_001", "Wingspan");
    
    std::cout << "Тест 6 - Расчет рейтинга игрока: ";
    if (rating == 85.0) {
        std::cout << "PASSED (рейтинг: " << rating << ")" << std::endl;
    } else {
        std::cout << "FAILED (ожидалось 85.0, получено " << rating << ")" << std::endl;
    }
    
    // Тест 7: Добавление схожести
    db.addSimilarity("Brass: Birmingham", "Wingspan");
    db.addSimilarity("Wingspan", "Terraforming Mars");
    
    std::cout << "Тест 7 - Добавление схожести: ";
    if (db.areSimilar("Brass: Birmingham", "Wingspan") && db.areSimilar("Terraforming Mars", "Wingspan")) {
        std::cout << "PASSED" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 8: Фильтрация по рейтингу
    RatingFilter ratingFilter(4.0);
    std::vector<BoardGame*> highRatedGames = db.findGames(&ratingFilter);
    
    std::cout << "Тест 8 - Фильтрация по рейтингу: ";
    if (highRatedGames.size() >= 2) {
        std::cout << "PASSED (найдено " << highRatedGames.size() << " игр)" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 9: Фильтрация по признакам
    g1->addFeature("Жанр", "Стратегия");
    g2->addFeature("Жанр", "Семейная");
    g3->addFeature("Жанр", "Стратегия");
    
    std::map<std::string, std::string> features;
    features["Жанр"] = "Стратегия";
    FeatureFilter featureFilter(features);
    
    std::vector<BoardGame*> strategyGames = db.findGames(&featureFilter);
    
    std::cout << "Тест 9 - Фильтрация по признакам: ";
    if (strategyGames.size() == 2) {
        std::cout << "PASSED (найдено " << strategyGames.size() << " игры)" << std::endl;
    } else {
        std::cout << "FAILED (ожидалось 2, найдено " << strategyGames.size() << ")" << std::endl;
    }
    
    // Тест 10: Фильтрация по схожести
    std::vector<std::string> refs = {"Brass: Birmingham"};
    SimilarGamesFilter similarFilter(refs, db.getSimilarityData());
    
    std::vector<BoardGame*> similarGames = db.findGames(&similarFilter);
    
    std::cout << "Тест 10 - Фильтрация по схожести: ";
    if (similarGames.size() >= 1) {
        std::cout << "PASSED (найдено " << similarGames.size() << " игра)" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 11: Цепочка фильтров
    std::vector<Filter*> filterChain;
    filterChain.push_back(&ratingFilter);
    filterChain.push_back(&featureFilter);
    
    std::vector<BoardGame*> chainResult = db.findGames(filterChain);
    
    std::cout << "Тест 11 - Цепочка фильтров: ";
    if (chainResult.size() >= 1) {
        std::cout << "PASSED (найдено " << chainResult.size() << " игр)" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Вывод статистики
    db.printStatistics();
    
    std::cout << "=== Тестирование GameDatabase завершено ===\n" << std::endl;
}

// === Реализация методов системы рекомендаций ===

std::vector<SimilarityResult> GameDatabase::getRecommendations(const std::string& gameName, int maxResults) const {
    if (!recommendationEngine) {
        return {};
    }
    
    return recommendationEngine->getRecommendations(gameName, maxResults);
}

std::vector<SimilarityResult> GameDatabase::getDetailedRecommendations(const std::string& gameName, int maxResults) const {
    if (!recommendationEngine) {
        return {};
    }
    
    return recommendationEngine->getDetailedRecommendations(gameName, maxResults);
}

std::vector<SimilarityResult> GameDatabase::findGamesSimilarToMultiple(const std::vector<std::string>& referenceGames, int maxResults) const {
    if (!recommendationEngine) {
        return {};
    }
    
    return recommendationEngine->findGamesSimilarToMultiple(referenceGames, maxResults);
}

void GameDatabase::setRecommendationWeights(const SimilarityWeights& weights) {
    if (recommendationEngine) {
        recommendationEngine->setSimilarityWeights(weights);
    }
}

const SimilarityWeights& GameDatabase::getRecommendationWeights() const {
    static SimilarityWeights defaultWeights;
    return recommendationEngine ? recommendationEngine->getSimilarityWeights() : defaultWeights;
}

void GameDatabase::refreshAllRecommendations() {
    if (recommendationEngine) {
        recommendationEngine->refreshAllRecommendations();
    }
}

GameRecommendationEngine::RecommendationStats GameDatabase::getRecommendationStats() const {
    static GameRecommendationEngine::RecommendationStats emptyStats;
    return recommendationEngine ? recommendationEngine->getRecommendationStats() : emptyStats;
}

