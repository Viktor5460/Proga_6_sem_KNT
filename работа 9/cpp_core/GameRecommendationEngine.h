#ifndef GAME_RECOMMENDATION_ENGINE_H
#define GAME_RECOMMENDATION_ENGINE_H

#include "BoardGame.h"
#include "SimilarityCalculator.h"
#include "SimilarityWeights.h"
#include <map>
#include <vector>
#include <string>
#include <memory>

// Класс для управления системой рекомендаций настольных игр
// Автоматически вычисляет схожесть игр и предоставляет рекомендации
class GameRecommendationEngine {
private:
    std::unique_ptr<SimilarityCalculator> calculator;
    std::map<std::string, BoardGame*> games;
    
    // Кэш для хранения рекомендаций
    mutable std::map<std::string, std::vector<SimilarityResult>> recommendationsCache;
    
    // Настройки
    bool autoUpdateRecommendations;
    bool enableCaching;
    
public:
    GameRecommendationEngine();
    GameRecommendationEngine(const SimilarityWeights& customWeights);
    ~GameRecommendationEngine();
    
    // === Основные методы управления играми ===
    
    // Добавление игры в систему рекомендаций
    bool addGame(BoardGame* game);
    
    // Удаление игры из системы рекомендаций
    bool removeGame(const std::string& gameName);
    
    // Получение игры по названию
    BoardGame* getGame(const std::string& gameName) const;
    
    // Обновление игры (пересчет рекомендаций)
    bool updateGame(const std::string& gameName);
    
    // === Методы рекомендаций ===
    
    // Получение рекомендаций для конкретной игры
    std::vector<SimilarityResult> getRecommendations(
        const std::string& targetGameName,
        int maxResults = -1
    ) const;
    
    // Получение рекомендаций с объяснениями
    std::vector<SimilarityResult> getDetailedRecommendations(
        const std::string& targetGameName,
        int maxResults = -1
    ) const;
    
    // Поиск игр, похожих на несколько образцов
    std::vector<SimilarityResult> findGamesSimilarToMultiple(
        const std::vector<std::string>& referenceGameNames,
        int maxResults = -1
    ) const;
    
    // === Настройка системы ===
    
    // Установка новых весов для вычисления схожести
    void setSimilarityWeights(const SimilarityWeights& newWeights);
    
    // Получение текущих весов
    const SimilarityWeights& getSimilarityWeights() const;
    
    // Включение/выключение автоматического обновления рекомендаций
    void setAutoUpdate(bool enabled);
    bool isAutoUpdateEnabled() const;
    
    // Включение/выключение кэширования
    void setCachingEnabled(bool enabled);
    bool isCachingEnabled() const;
    
    // === Аналитика и статистика ===
    
    // Получение статистики по рекомендациям
    struct RecommendationStats {
        int totalGames;
        int gamesWithRecommendations;
        double averageRecommendationsPerGame;
        double averageSimilarityScore;
        std::map<std::string, int> parameterInfluence; // Влияние каждого параметра
    };
    
    RecommendationStats getRecommendationStats() const;
    
    // Анализ качества рекомендаций (на основе пользовательских оценок)
    double calculateRecommendationQuality(const std::string& gameName) const;
    
    // === Утилиты ===
    
    // Очистка кэша рекомендаций
    void clearRecommendationsCache();
    
    // Принудительное обновление всех рекомендаций
    void refreshAllRecommendations();
    
    // Экспорт рекомендаций в файл
    bool exportRecommendations(const std::string& filename) const;
    
    // Импорт рекомендаций из файла
    bool importRecommendations(const std::string& filename);
    
    // === Отладочные методы ===
    
    // Вывод информации о рекомендациях для игры
    void printRecommendations(const std::string& gameName) const;
    
    // Вывод статистики системы рекомендаций
    void printRecommendationStats() const;
    
    // Тестирование системы рекомендаций
    static void runTests();
    
private:
    // Вспомогательные методы
    
    // Вычисление рекомендаций для игры (с кэшированием)
    std::vector<SimilarityResult> calculateRecommendations(
        const std::string& gameName,
        int maxResults
    ) const;
    
    // Проверка валидности игры для рекомендаций
    bool isValidGameForRecommendations(const BoardGame* game) const;
    
    // Обновление кэша рекомендаций
    void updateRecommendationsCache(const std::string& gameName) const;
    
    // Получение игр, исключая указанные
    std::map<std::string, BoardGame*> getFilteredGames(
        const std::vector<std::string>& excludeGames = {}
    ) const;
    
    // Агрегация рекомендаций от нескольких игр
    std::vector<SimilarityResult> aggregateRecommendations(
        const std::vector<std::vector<SimilarityResult>>& allRecommendations,
        int maxResults
    ) const;
};

#endif
