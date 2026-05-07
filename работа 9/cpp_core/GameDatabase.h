#ifndef GAME_DATABASE_H
#define GAME_DATABASE_H

#include "BoardGame.h"
#include "Player.h"
#include "Match.h"
#include "Filter.h"
#include "GameRecommendationEngine.h"
#include <map>
#include <set>
#include <vector>
#include <string>
#include <algorithm>

// Центральный класс базы данных настольных игр
// Управляет всеми сущностями: играми, игроками, партиями, связями схожести
// Предоставляет единый интерфейс для работы со всей системой
class GameDatabase {
private:
    std::map<std::string, BoardGame*> games;           // Игры: название -> объект
    std::map<std::string, Player*> players;            // Игроки: ID -> объект
    std::vector<Match*> matches;                       // Все партии
    std::set<std::pair<std::string, std::string>> similarGames;  // Пары схожих игр
    
    // Система рекомендаций
    std::unique_ptr<GameRecommendationEngine> recommendationEngine;
    
public:
    // Конструктор и деструктор
    GameDatabase();
    ~GameDatabase();  // Освобождает всю выделенную память
    
    // === Управление играми ===
    
    // Добавление игры (база берет владение указателем)
    bool addGame(BoardGame* game);
    
    // Удаление игры по названию
    bool removeGame(const std::string& gameName);
    
    // Получение игры по названию
    BoardGame* getGame(const std::string& gameName) const;
    
    // Получение всех игр (возврат по const ссылке для эффективности)
    const std::map<std::string, BoardGame*>& getAllGames() const;
    
    // Перегрузка operator[] для доступа к играм по названию (Лекция 3, стр. 135)
    // Возвращает ссылку на указатель для возможности изменения
    // Если игры нет - возвращает nullptr
    BoardGame* operator[](const std::string& gameName) const;
    
    // === Управление игроками ===
    
    // Добавление игрока (база берет владение указателем)
    bool addPlayer(Player* player);
    
    // Удаление игрока по ID
    bool removePlayer(const std::string& playerId);
    
    // Получение игрока по ID
    Player* getPlayer(const std::string& playerId) const;
    
    // Получение всех игроков (возврат по const ссылке для эффективности)
    const std::map<std::string, Player*>& getAllPlayers() const;
    
    // === Управление партиями ===
    
    // Добавление партии (база берет владение указателем)
    // Автоматически добавляет партию в историю каждого игрока
    bool addMatch(Match* match);

    // Удаление партии по ID
    bool removeMatch(const std::string& matchId);
    
    // Получение партии по ID
    Match* getMatch(const std::string& matchId) const;
    
    // Получение всех партий (возврат по const ссылке для эффективности)
    const std::vector<Match*>& getAllMatches() const;
    
    // Получение партий конкретной игры
    std::vector<Match*> getMatchesByGame(const std::string& gameName) const;
    
    // Получение партий конкретного игрока
    std::vector<Match*> getMatchesByPlayer(const std::string& playerId) const;
    
    // === Управление оценками ===
    
    // Выставление оценки игре от игрока
    // Логика: находит игру и игрока, вызывает addRating
    bool addRating(const std::string& gameName, const std::string& playerId, int rating);
    
    // === Управление схожестью игр ===
    
    // Добавление связи схожести между играми (симметричная)
    bool addSimilarity(const std::string& game1, const std::string& game2);
    
    // Проверка схожести двух игр
    bool areSimilar(const std::string& game1, const std::string& game2) const;
    
    // Получение всех игр, схожих с данной
    std::vector<std::string> getSimilarGames(const std::string& gameName) const;
    
    // Получение множества всех связей схожести (для фильтров)
    const std::set<std::pair<std::string, std::string>>* getSimilarityData() const;
    
    // === Система автоматических рекомендаций ===
    
    // Получение рекомендаций для игры на основе схожести параметров
    std::vector<SimilarityResult> getRecommendations(const std::string& gameName, int maxResults = 5) const;
    
    // Получение детализированных рекомендаций с объяснениями
    std::vector<SimilarityResult> getDetailedRecommendations(const std::string& gameName, int maxResults = 5) const;
    
    // Поиск игр, похожих на несколько образцов
    std::vector<SimilarityResult> findGamesSimilarToMultiple(const std::vector<std::string>& referenceGames, int maxResults = 5) const;
    
    // Настройка системы рекомендаций
    void setRecommendationWeights(const SimilarityWeights& weights);
    const SimilarityWeights& getRecommendationWeights() const;
    
    // Обновление рекомендаций для всех игр
    void refreshAllRecommendations();
    
    // Получение статистики системы рекомендаций
    GameRecommendationEngine::RecommendationStats getRecommendationStats() const;
    
    // === Статистика и аналитика ===
    
    // Расчет рейтинга игрока в конкретной игре
    // Логика: находит все партии игрока в этой игре, считает средний результат
    double getPlayerRatingInGame(const std::string& playerId, const std::string& gameName) const;
    
    // Получение всех игр игрока
    std::vector<std::string> getPlayerGames(const std::string& playerId) const;
    
    // === Фильтрация игр ===
    
    // Применение одного фильтра
    std::vector<BoardGame*> findGames(Filter* filter) const;
    
    // Применение цепочки фильтров последовательно
    // Каждый следующий фильтр применяется к результату предыдущего
    std::vector<BoardGame*> findGames(const std::vector<Filter*>& filters) const;
    
    // === Вывод информации ===
    
    void printAllGames() const;
    void printAllPlayers() const;
    void printAllMatches() const;
    void printStatistics() const;
    
    // Встроенные тесты
    static void runTests();
    
private:
    // Вспомогательный метод: сортировка игр по убыванию среднего рейтинга
    void sortGamesByRating(std::vector<BoardGame*>& games) const;
};

#endif

