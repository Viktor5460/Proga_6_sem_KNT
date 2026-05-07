#include "SimilarityCalculator.h"
#include "GenreSimilarityMatrix.h"
#include <algorithm>
#include <cmath>
#include <sstream>
#include <iostream>

// Статические константы для типов игр
const std::vector<std::string> SimilarityCalculator::GAME_TYPES = {
    "Евро игра", "Америтреш", "Абстрактная", "Семейная", 
    "Парти игра", "Кооперативная", "Соревновательная", "Смешанная"
};

const std::vector<std::string> SimilarityCalculator::GAME_MECHANICS = {
    "Торговля", "Боевая система", "Экономика", "Размещение рабочих", 
    "Карточная игра", "Кости", "Тайлы", "Территория", "Сбор ресурсов",
    "Управление рукой", "Аукцион", "Программирование", "Временная шкала"
};

const std::vector<std::string> SimilarityCalculator::COMPLEXITY_LEVELS = {
    "Очень легкая", "Легкая", "Средняя", "Сложная", "Экспертная"
};

SimilarityCalculator::SimilarityCalculator() : weights() {}

SimilarityCalculator::SimilarityCalculator(const SimilarityWeights& customWeights) 
    : weights(customWeights) {
    if (!weights.isValid()) {
        std::cerr << "Предупреждение: Некорректные веса, используются значения по умолчанию" << std::endl;
        weights = SimilarityWeights();
    }
}

double SimilarityCalculator::calculateSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    if (!game1 || !game2) return 0.0;
    
    // Проверяем кэш
    std::pair<std::string, std::string> cacheKey = std::make_pair(
        std::min(game1->getName(), game2->getName()),
        std::max(game1->getName(), game2->getName())
    );
    
    auto cacheIt = similarityCache.find(cacheKey);
    if (cacheIt != similarityCache.end()) {
        return cacheIt->second;
    }
    
    // Вычисляем схожесть по каждому параметру
    double complexitySim = calculateComplexitySimilarity(game1, game2);
    double playerCountSim = calculatePlayerCountSimilarity(game1, game2);
    double gameTypeSim = calculateGameTypeSimilarity(game1, game2);
    double durationSim = calculateDurationSimilarity(game1, game2);
    double mechanicsSim = calculateMechanicsSimilarity(game1, game2);
    double genreSim = calculateGenreSimilarity(game1, game2);
    double userParamsSim = calculateUserParametersSimilarity(game1, game2);
    
    // Вычисляем общую схожесть с учетом весов
    double totalSimilarity = complexitySim * weights.complexityWeight +
                           playerCountSim * weights.playerCountWeight +
                           gameTypeSim * weights.gameTypeWeight +
                           durationSim * weights.durationWeight +
                           mechanicsSim * weights.mechanicsWeight +
                           genreSim * weights.genreWeight +
                           userParamsSim * weights.userParametersWeight;
    
    // Кэшируем результат
    similarityCache[cacheKey] = totalSimilarity;
    
    return totalSimilarity;
}

SimilarityResult SimilarityCalculator::calculateDetailedSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    if (!game1 || !game2) {
        return SimilarityResult("", 0.0);
    }
    
    SimilarityResult result(game2->getName(), 0.0);
    
    // Вычисляем схожесть по каждому параметру с детализацией
    result.parameterScores["Сложность"] = calculateComplexitySimilarity(game1, game2);
    result.parameterScores["Количество игроков"] = calculatePlayerCountSimilarity(game1, game2);
    result.parameterScores["Тип игры"] = calculateGameTypeSimilarity(game1, game2);
    result.parameterScores["Длительность"] = calculateDurationSimilarity(game1, game2);
    result.parameterScores["Механики"] = calculateMechanicsSimilarity(game1, game2);
    result.parameterScores["Жанр"] = calculateGenreSimilarity(game1, game2);
    result.parameterScores["Пользовательские параметры"] = calculateUserParametersSimilarity(game1, game2);
    
    // Вычисляем общую схожесть
    result.similarityScore = result.parameterScores["Сложность"] * weights.complexityWeight +
                           result.parameterScores["Количество игроков"] * weights.playerCountWeight +
                           result.parameterScores["Тип игры"] * weights.gameTypeWeight +
                           result.parameterScores["Длительность"] * weights.durationWeight +
                           result.parameterScores["Механики"] * weights.mechanicsWeight +
                           result.parameterScores["Жанр"] * weights.genreWeight +
                           result.parameterScores["Пользовательские параметры"] * weights.userParametersWeight;
    
    return result;
}

std::vector<SimilarityResult> SimilarityCalculator::findSimilarGames(
    const BoardGame* targetGame, 
    const std::map<std::string, BoardGame*>& allGames,
    int maxResults
) const {
    std::vector<SimilarityResult> results;
    
    if (!targetGame) return results;
    
    if (maxResults == -1) {
        maxResults = weights.maxRecommendations;
    }
    
    // Вычисляем схожесть со всеми играми
    for (const auto& pair : allGames) {
        const BoardGame* game = pair.second;
        if (!game || game->getName() == targetGame->getName()) {
            continue; // Пропускаем саму целевую игру
        }
        
        SimilarityResult result = calculateDetailedSimilarity(targetGame, game);
        
        // Добавляем только игры, превышающие минимальный порог
        if (result.similarityScore >= weights.minSimilarityThreshold) {
            results.push_back(result);
        }
    }
    
    // Сортируем по убыванию схожести
    std::sort(results.begin(), results.end(), 
        [](const SimilarityResult& a, const SimilarityResult& b) {
            return a.similarityScore > b.similarityScore;
        });
    
    // Ограничиваем количество результатов
    if (results.size() > static_cast<size_t>(maxResults)) {
        results.resize(maxResults);
    }
    
    return results;
}

void SimilarityCalculator::setWeights(const SimilarityWeights& newWeights) {
    weights = newWeights;
    if (!weights.isValid()) {
        std::cerr << "Предупреждение: Некорректные веса, используются значения по умолчанию" << std::endl;
        weights = SimilarityWeights();
    }
    clearCache(); // Очищаем кэш при изменении весов
}

const SimilarityWeights& SimilarityCalculator::getWeights() const {
    return weights;
}

void SimilarityCalculator::clearCache() {
    similarityCache.clear();
}

// Реализация методов вычисления схожести по отдельным параметрам

double SimilarityCalculator::calculateComplexitySimilarity(const BoardGame* game1, const BoardGame* game2) const {
    bool hasComplexity1 = hasParameter(game1, "Сложность");
    bool hasComplexity2 = hasParameter(game2, "Сложность");
    
    if (!hasComplexity1 && !hasComplexity2) {
        return 1.0; // Оба параметра отсутствуют - нейтрально
    }
    
    if (!hasComplexity1 || !hasComplexity2) {
        return 1.0 - weights.missingDataPenalty; // Штраф за отсутствующий параметр
    }
    
    std::string complexity1 = getStringParameter(game1, "Сложность");
    std::string complexity2 = getStringParameter(game2, "Сложность");
    
    // Если это строковые значения сложности
    if (complexity1 == complexity2) {
        return 1.0; // Полное совпадение
    }
    
    // Если это числовые значения (1-10), используем гауссову функцию
    try {
        double comp1 = std::stod(complexity1);
        double comp2 = std::stod(complexity2);
        
        // Используем гауссову функцию с стандартным отклонением 2.5
        // Это дает 100% схожесть при полном совпадении и экспоненциальное убывание
        return GenreSimilarityMatrix::gaussianSimilarity(comp1, comp2, 2.5);
    } catch (...) {
        // Если не удалось преобразовать в число, считаем как строки
        return 0.0; // Разные строковые значения = 0% схожести
    }
}

double SimilarityCalculator::calculatePlayerCountSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    int min1 = game1->getMinPlayers();
    int max1 = game1->getMaxPlayers();
    int min2 = game2->getMinPlayers();
    int max2 = game2->getMaxPlayers();
    
    // Вычисляем пересечение диапазонов
    int overlapMin = std::max(min1, min2);
    int overlapMax = std::min(max1, max2);
    
    if (overlapMin > overlapMax) {
        return 0.0; // Нет пересечения диапазонов
    }
    
    int overlap = overlapMax - overlapMin + 1;
    int totalRange1 = max1 - min1 + 1;
    int totalRange2 = max2 - min2 + 1;
    
    // Процент совпадения = пересечение / среднее от общих диапазонов
    double averageRange = (totalRange1 + totalRange2) / 2.0;
    return overlap / averageRange;
}

double SimilarityCalculator::calculateGameTypeSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    bool hasType1 = hasParameter(game1, "ТипИгры");
    bool hasType2 = hasParameter(game2, "ТипИгры");
    
    if (!hasType1 && !hasType2) {
        return 1.0; // Оба параметра отсутствуют - нейтрально
    }
    
    if (!hasType1 || !hasType2) {
        return 1.0 - weights.missingDataPenalty; // Штраф за отсутствующий параметр
    }
    
    std::string type1 = getStringParameter(game1, "ТипИгры");
    std::string type2 = getStringParameter(game2, "ТипИгры");
    
    return (type1 == type2) ? 1.0 : 0.0;
}

double SimilarityCalculator::calculateDurationSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    bool hasDuration1 = hasParameter(game1, "Длительность") || hasParameter(game1, "МинДлительность");
    bool hasDuration2 = hasParameter(game2, "Длительность") || hasParameter(game2, "МинДлительность");
    
    if (!hasDuration1 && !hasDuration2) {
        return 1.0; // Оба параметра отсутствуют - нейтрально
    }
    
    if (!hasDuration1 || !hasDuration2) {
        return 1.0 - weights.missingDataPenalty; // Штраф за отсутствующий параметр
    }
    
    // Получаем диапазоны длительности
    int minDur1 = game1->getMinDuration();
    int maxDur1 = game1->getMaxDuration();
    int minDur2 = game2->getMinDuration();
    int maxDur2 = game2->getMaxDuration();
    
    if (minDur1 <= 0 || maxDur1 <= 0 || minDur2 <= 0 || maxDur2 <= 0) {
        return 0.5; // Если длительность не указана корректно
    }
    
    // Вычисляем пересечение диапазонов
    int overlapMin = std::max(minDur1, minDur2);
    int overlapMax = std::min(maxDur1, maxDur2);
    
    if (overlapMin > overlapMax) {
        // Нет пересечения - используем гауссову функцию для средних значений
        double avg1 = (minDur1 + maxDur1) / 2.0;
        double avg2 = (minDur2 + maxDur2) / 2.0;
        return GenreSimilarityMatrix::gaussianSimilarity(avg1, avg2, 30.0); // Стандартное отклонение 30 минут
    }
    
    // Есть пересечение - вычисляем процент пересечения
    int overlap = overlapMax - overlapMin + 1;
    int totalRange1 = maxDur1 - minDur1 + 1;
    int totalRange2 = maxDur2 - minDur2 + 1;
    
    double averageRange = (totalRange1 + totalRange2) / 2.0;
    double overlapRatio = overlap / averageRange;
    
    return std::max(0.0, overlapRatio);
}

double SimilarityCalculator::calculateMechanicsSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    bool hasMechanics1 = hasParameter(game1, "Механики");
    bool hasMechanics2 = hasParameter(game2, "Механики");
    
    if (!hasMechanics1 && !hasMechanics2) {
        return 1.0; // Оба параметра отсутствуют - нейтрально
    }
    
    if (!hasMechanics1 || !hasMechanics2) {
        return 1.0 - weights.missingDataPenalty; // Штраф за отсутствующий параметр
    }
    
    std::string mechanics1Str = getStringParameter(game1, "Механики");
    std::string mechanics2Str = getStringParameter(game2, "Механики");
    
    std::vector<std::string> mechanics1 = parseMechanics(mechanics1Str);
    std::vector<std::string> mechanics2 = parseMechanics(mechanics2Str);
    
    if (mechanics1.empty() && mechanics2.empty()) {
        return 1.0;
    }
    
    if (mechanics1.empty() || mechanics2.empty()) {
        return 0.0;
    }
    
    int commonCount = countCommonElements(mechanics1, mechanics2);
    int totalCount = std::max(mechanics1.size(), mechanics2.size());
    
    return static_cast<double>(commonCount) / totalCount;
}

double SimilarityCalculator::calculateGenreSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    bool hasGenre1 = hasParameter(game1, "Жанр");
    bool hasGenre2 = hasParameter(game2, "Жанр");
    
    if (!hasGenre1 && !hasGenre2) {
        return 1.0; // Оба параметра отсутствуют - нейтрально
    }
    
    if (!hasGenre1 || !hasGenre2) {
        return 1.0 - weights.missingDataPenalty; // Штраф за отсутствующий параметр
    }
    
    std::string genre1 = getStringParameter(game1, "Жанр");
    std::string genre2 = getStringParameter(game2, "Жанр");
    
    // Используем матрицу схожести жанров
    return genreMatrix.getGenreSimilarity(genre1, genre2);
}

double SimilarityCalculator::calculateUserParametersSimilarity(const BoardGame* game1, const BoardGame* game2) const {
    // Список пользовательских параметров для сравнения
    std::vector<std::string> userParams = {"Материал", "Тема", "Дизайн", "Стиль", "Качество"};
    
    double totalSimilarity = 0.0;
    int validParams = 0;
    
    for (const std::string& param : userParams) {
        bool hasParam1 = hasParameter(game1, param);
        bool hasParam2 = hasParameter(game2, param);
        
        if (hasParam1 && hasParam2) {
            std::string value1 = getStringParameter(game1, param);
            std::string value2 = getStringParameter(game2, param);
            
            double similarity = 0.0;
            
            if (param == "Материал") {
                similarity = genreMatrix.getMaterialSimilarity(value1, value2);
            } else if (param == "Тема") {
                similarity = genreMatrix.getThemeSimilarity(value1, value2);
            } else {
                // Для остальных параметров - простое сравнение строк
                similarity = (value1 == value2) ? 1.0 : 0.0;
            }
            
            totalSimilarity += similarity;
            validParams++;
        } else if (hasParam1 || hasParam2) {
            // Штраф за отсутствующий параметр
            totalSimilarity += (1.0 - weights.missingDataPenalty);
            validParams++;
        }
    }
    
    // Если нет пользовательских параметров, возвращаем нейтральное значение
    if (validParams == 0) {
        return 1.0;
    }
    
    return totalSimilarity / validParams;
}

// Вспомогательные методы

double SimilarityCalculator::normalizeValue(double value, double min, double max) const {
    if (max <= min) return 0.5;
    return std::max(0.0, std::min(1.0, (value - min) / (max - min)));
}

double SimilarityCalculator::exponentialDecay(double difference, double halfLife) const {
    return std::exp(-difference * std::log(2.0) / halfLife);
}

bool SimilarityCalculator::hasParameter(const BoardGame* game, const std::string& parameterName) const {
    return game && game->hasFeature(parameterName);
}

double SimilarityCalculator::getNumericParameter(const BoardGame* game, const std::string& parameterName, double defaultValue) const {
    if (!game) return defaultValue;
    
    std::string value = game->getFeature(parameterName);
    if (value.empty()) return defaultValue;
    
    try {
        return std::stod(value);
    } catch (...) {
        return defaultValue;
    }
}

std::string SimilarityCalculator::getStringParameter(const BoardGame* game, const std::string& parameterName, const std::string& defaultValue) const {
    if (!game) return defaultValue;
    
    std::string value = game->getFeature(parameterName);
    return value.empty() ? defaultValue : value;
}

std::vector<std::string> SimilarityCalculator::parseMechanics(const std::string& mechanicsStr) const {
    std::vector<std::string> mechanics;
    std::stringstream ss(mechanicsStr);
    std::string item;
    
    while (std::getline(ss, item, ',')) {
        // Удаляем пробелы в начале и конце
        item.erase(0, item.find_first_not_of(" \t"));
        item.erase(item.find_last_not_of(" \t") + 1);
        
        if (!item.empty()) {
            mechanics.push_back(item);
        }
    }
    
    return mechanics;
}

int SimilarityCalculator::countCommonElements(const std::vector<std::string>& list1, const std::vector<std::string>& list2) const {
    int count = 0;
    for (const std::string& item : list1) {
        if (std::find(list2.begin(), list2.end(), item) != list2.end()) {
            count++;
        }
    }
    return count;
}
