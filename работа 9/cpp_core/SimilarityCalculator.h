#ifndef SIMILARITY_CALCULATOR_H
#define SIMILARITY_CALCULATOR_H

#include "BoardGame.h"
#include "SimilarityWeights.h"
#include "GenreSimilarityMatrix.h"
#include <map>
#include <vector>
#include <string>
#include <utility>

// Структура для хранения результата сравнения игр
struct SimilarityResult {
    std::string gameName;
    double similarityScore;  // 0.0 - 1.0
    std::map<std::string, double> parameterScores; // Детализация по параметрам
    
    // Конструктор по умолчанию
    SimilarityResult() : gameName(""), similarityScore(0.0) {}
    
    // Конструктор с параметрами
    SimilarityResult(const std::string& name, double score) 
        : gameName(name), similarityScore(score) {}
};

// Класс для вычисления схожести между настольными играми
class SimilarityCalculator {
private:
    SimilarityWeights weights;
    GenreSimilarityMatrix genreMatrix;
    
    // Кэш для хранения уже вычисленных результатов схожести
    mutable std::map<std::pair<std::string, std::string>, double> similarityCache;
    
public:
    SimilarityCalculator();
    SimilarityCalculator(const SimilarityWeights& customWeights);
    
    // Основной метод вычисления схожести между двумя играми
    double calculateSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Вычисление схожести с детализацией по параметрам
    SimilarityResult calculateDetailedSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Поиск наиболее схожих игр для заданной игры
    std::vector<SimilarityResult> findSimilarGames(
        const BoardGame* targetGame, 
        const std::map<std::string, BoardGame*>& allGames,
        int maxResults = -1
    ) const;
    
    // Установка новых весов
    void setWeights(const SimilarityWeights& newWeights);
    const SimilarityWeights& getWeights() const;
    
    // Очистка кэша
    void clearCache();
    
    // Статические константы для типов игр
    static const std::vector<std::string> GAME_TYPES;
    static const std::vector<std::string> GAME_MECHANICS;
    static const std::vector<std::string> COMPLEXITY_LEVELS;
    
private:
    // Методы вычисления схожести по отдельным параметрам
    
    // Схожесть по сложности (1-10 или категории)
    double calculateComplexitySimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Схожесть по количеству игроков (процент совпадения диапазонов)
    double calculatePlayerCountSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Схожесть по типу игры (евро, америтреш, семейная и т.д.)
    double calculateGameTypeSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Схожесть по длительности игры (экспоненциальное убывание)
    double calculateDurationSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Схожесть по механикам игры (количество общих механик)
    double calculateMechanicsSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Схожесть по жанру игры (с использованием матрицы схожести)
    double calculateGenreSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Схожесть по пользовательским параметрам (материал, тема, дизайн и т.д.)
    double calculateUserParametersSimilarity(const BoardGame* game1, const BoardGame* game2) const;
    
    // Вспомогательные методы
    
    // Нормализация числового значения в диапазон 0-1
    double normalizeValue(double value, double min, double max) const;
    
    // Экспоненциальное убывание для временных параметров
    double exponentialDecay(double difference, double halfLife) const;
    
    // Проверка наличия параметра у игры
    bool hasParameter(const BoardGame* game, const std::string& parameterName) const;
    
    // Получение числового значения параметра
    double getNumericParameter(const BoardGame* game, const std::string& parameterName, double defaultValue = 0.0) const;
    
    // Получение строкового значения параметра
    std::string getStringParameter(const BoardGame* game, const std::string& parameterName, const std::string& defaultValue = "") const;
    
    // Получение списка механик из строки (разделенных запятыми)
    std::vector<std::string> parseMechanics(const std::string& mechanicsStr) const;
    
    // Подсчет пересечения двух списков строк
    int countCommonElements(const std::vector<std::string>& list1, const std::vector<std::string>& list2) const;
};

#endif
