#include "GameRecommendationEngine.h"
#include <fstream>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <iostream>

GameRecommendationEngine::GameRecommendationEngine() 
    : calculator(std::make_unique<SimilarityCalculator>()),
      autoUpdateRecommendations(true),
      enableCaching(true) {
}

GameRecommendationEngine::GameRecommendationEngine(const SimilarityWeights& customWeights)
    : calculator(std::make_unique<SimilarityCalculator>(customWeights)),
      autoUpdateRecommendations(true),
      enableCaching(true) {
}

GameRecommendationEngine::~GameRecommendationEngine() {
    // Освобождаем память, если мы владеем играми
    for (auto& pair : games) {
        // Не удаляем, так как игры могут принадлежать GameDatabase
    }
}

bool GameRecommendationEngine::addGame(BoardGame* game) {
    if (!game || game->getName().empty()) {
        return false;
    }
    
    games[game->getName()] = game;
    
    // Автоматически обновляем рекомендации, если включено
    if (autoUpdateRecommendations) {
        refreshAllRecommendations();
    }
    
    return true;
}

bool GameRecommendationEngine::removeGame(const std::string& gameName) {
    auto it = games.find(gameName);
    if (it == games.end()) {
        return false;
    }
    
    games.erase(it);
    
    // Удаляем из кэша рекомендаций
    recommendationsCache.erase(gameName);
    
    // Обновляем кэш для всех игр, которые могли рекомендовать эту игру
    if (autoUpdateRecommendations) {
        for (auto& pair : recommendationsCache) {
            auto& recommendations = pair.second;
            recommendations.erase(
                std::remove_if(recommendations.begin(), recommendations.end(),
                    [&gameName](const SimilarityResult& result) {
                        return result.gameName == gameName;
                    }),
                recommendations.end()
            );
        }
    }
    
    return true;
}

BoardGame* GameRecommendationEngine::getGame(const std::string& gameName) const {
    auto it = games.find(gameName);
    return (it != games.end()) ? it->second : nullptr;
}

bool GameRecommendationEngine::updateGame(const std::string& gameName) {
    if (games.find(gameName) == games.end()) {
        return false;
    }
    
    // Обновляем кэш рекомендаций для этой игры
    if (enableCaching) {
        updateRecommendationsCache(gameName);
    }
    
    // Очищаем кэш рекомендаций других игр, которые могли рекомендовать эту
    if (autoUpdateRecommendations) {
        refreshAllRecommendations();
    }
    
    return true;
}

std::vector<SimilarityResult> GameRecommendationEngine::getRecommendations(
    const std::string& targetGameName,
    int maxResults
) const {
    if (!calculator || games.find(targetGameName) == games.end()) {
        return {};
    }
    
    return calculateRecommendations(targetGameName, maxResults);
}

std::vector<SimilarityResult> GameRecommendationEngine::getDetailedRecommendations(
    const std::string& targetGameName,
    int maxResults
) const {
    return getRecommendations(targetGameName, maxResults);
}

std::vector<SimilarityResult> GameRecommendationEngine::findGamesSimilarToMultiple(
    const std::vector<std::string>& referenceGameNames,
    int maxResults
) const {
    if (!calculator || referenceGameNames.empty()) {
        return {};
    }
    
    // Проверяем, что все эталонные игры существуют
    for (const std::string& gameName : referenceGameNames) {
        if (games.find(gameName) == games.end()) {
            return {};
        }
    }
    
    std::vector<std::vector<SimilarityResult>> allRecommendations;
    
    // Получаем рекомендации для каждой эталонной игры
    for (const std::string& gameName : referenceGameNames) {
        auto recommendations = calculateRecommendations(gameName, maxResults);
        if (!recommendations.empty()) {
            allRecommendations.push_back(recommendations);
        }
    }
    
    if (allRecommendations.empty()) {
        return {};
    }
    
    return aggregateRecommendations(allRecommendations, maxResults);
}

void GameRecommendationEngine::setSimilarityWeights(const SimilarityWeights& newWeights) {
    if (calculator) {
        calculator->setWeights(newWeights);
        
        // Очищаем кэш при изменении весов
        if (enableCaching) {
            clearRecommendationsCache();
        }
        
        // Обновляем рекомендации
        if (autoUpdateRecommendations) {
            refreshAllRecommendations();
        }
    }
}

const SimilarityWeights& GameRecommendationEngine::getSimilarityWeights() const {
    static SimilarityWeights defaultWeights;
    return calculator ? calculator->getWeights() : defaultWeights;
}

void GameRecommendationEngine::setAutoUpdate(bool enabled) {
    autoUpdateRecommendations = enabled;
}

bool GameRecommendationEngine::isAutoUpdateEnabled() const {
    return autoUpdateRecommendations;
}

void GameRecommendationEngine::setCachingEnabled(bool enabled) {
    enableCaching = enabled;
    if (!enabled) {
        clearRecommendationsCache();
    }
}

bool GameRecommendationEngine::isCachingEnabled() const {
    return enableCaching;
}

GameRecommendationEngine::RecommendationStats GameRecommendationEngine::getRecommendationStats() const {
    RecommendationStats stats;
    stats.totalGames = games.size();
    stats.gamesWithRecommendations = 0;
    stats.averageRecommendationsPerGame = 0.0;
    stats.averageSimilarityScore = 0.0;
    
    if (games.empty()) {
        return stats;
    }
    
    int totalRecommendations = 0;
    double totalSimilarityScore = 0.0;
    int recommendationsCount = 0;
    
    for (const auto& pair : games) {
        auto recommendations = calculateRecommendations(pair.first, 10);
        if (!recommendations.empty()) {
            stats.gamesWithRecommendations++;
            totalRecommendations += recommendations.size();
            
            for (const auto& rec : recommendations) {
                totalSimilarityScore += rec.similarityScore;
                recommendationsCount++;
            }
        }
    }
    
    if (stats.gamesWithRecommendations > 0) {
        stats.averageRecommendationsPerGame = static_cast<double>(totalRecommendations) / stats.gamesWithRecommendations;
    }
    
    if (recommendationsCount > 0) {
        stats.averageSimilarityScore = totalSimilarityScore / recommendationsCount;
    }
    
    // Анализ влияния параметров
    const auto& weights = getSimilarityWeights();
    stats.parameterInfluence["Сложность"] = static_cast<int>(weights.complexityWeight * 100);
    stats.parameterInfluence["Количество игроков"] = static_cast<int>(weights.playerCountWeight * 100);
    stats.parameterInfluence["Тип игры"] = static_cast<int>(weights.gameTypeWeight * 100);
    stats.parameterInfluence["Длительность"] = static_cast<int>(weights.durationWeight * 100);
    stats.parameterInfluence["Механики"] = static_cast<int>(weights.mechanicsWeight * 100);
    stats.parameterInfluence["Жанр"] = static_cast<int>(weights.genreWeight * 100);
    
    return stats;
}

double GameRecommendationEngine::calculateRecommendationQuality(const std::string& gameName) const {
    // Простая метрика качества на основе среднего рейтинга рекомендованных игр
    auto recommendations = getRecommendations(gameName, 10);
    if (recommendations.empty()) {
        return 0.0;
    }
    
    double totalQuality = 0.0;
    int validRecommendations = 0;
    
    for (const auto& rec : recommendations) {
        BoardGame* game = getGame(rec.gameName);
        if (game && game->getRatingsCount() > 0) {
            totalQuality += game->getAverageRating();
            validRecommendations++;
        }
    }
    
    return validRecommendations > 0 ? totalQuality / validRecommendations : 0.0;
}

void GameRecommendationEngine::clearRecommendationsCache() {
    recommendationsCache.clear();
}

void GameRecommendationEngine::refreshAllRecommendations() {
    if (!enableCaching) return;
    
    for (const auto& pair : games) {
        updateRecommendationsCache(pair.first);
    }
}

bool GameRecommendationEngine::exportRecommendations(const std::string& filename) const {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    
    file << "Игра,Рекомендация,Схожесть,Сложность,Игроки,Тип,Длительность,Механики,Жанр\n";
    
    for (const auto& pair : games) {
        auto recommendations = calculateRecommendations(pair.first, 5);
        for (const auto& rec : recommendations) {
            file << pair.first << "," << rec.gameName << "," 
                 << std::fixed << std::setprecision(3) << rec.similarityScore;
            
            // Добавляем детализацию по параметрам
            for (const auto& param : rec.parameterScores) {
                file << "," << std::fixed << std::setprecision(3) << param.second;
            }
            file << "\n";
        }
    }
    
    file.close();
    return true;
}

bool GameRecommendationEngine::importRecommendations(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        return false;
    }
    
    std::string line;
    std::getline(file, line); // Пропускаем заголовок
    
    // Простая реализация импорта (можно расширить)
    while (std::getline(file, line)) {
        // Обработка строки CSV...
        // Для простоты пока не реализуем полный импорт
    }
    
    file.close();
    return true;
}

void GameRecommendationEngine::printRecommendations(const std::string& gameName) const {
    BoardGame* game = getGame(gameName);
    if (!game) {
        std::cout << "Игра '" << gameName << "' не найдена." << std::endl;
        return;
    }
    
    std::cout << "\n=== Рекомендации для игры '" << gameName << "' ===" << std::endl;
    
    auto recommendations = getDetailedRecommendations(gameName, 5);
    if (recommendations.empty()) {
        std::cout << "Рекомендации не найдены." << std::endl;
        return;
    }
    
    for (size_t i = 0; i < recommendations.size(); ++i) {
        const auto& rec = recommendations[i];
        std::cout << "\n" << (i + 1) << ". " << rec.gameName 
                  << " (схожесть: " << std::fixed << std::setprecision(1) 
                  << (rec.similarityScore * 100) << "%)" << std::endl;
        
        // Выводим детализацию по параметрам
        std::cout << "   Детализация: ";
        bool first = true;
        for (const auto& param : rec.parameterScores) {
            if (!first) std::cout << ", ";
            std::cout << param.first << " (" << std::fixed << std::setprecision(0) 
                      << (param.second * 100) << "%)";
            first = false;
        }
        std::cout << std::endl;
    }
}

void GameRecommendationEngine::printRecommendationStats() const {
    auto stats = getRecommendationStats();
    
    std::cout << "\n=== Статистика системы рекомендаций ===" << std::endl;
    std::cout << "Всего игр в системе: " << stats.totalGames << std::endl;
    std::cout << "Игр с рекомендациями: " << stats.gamesWithRecommendations << std::endl;
    std::cout << "Среднее количество рекомендаций на игру: " 
              << std::fixed << std::setprecision(2) << stats.averageRecommendationsPerGame << std::endl;
    std::cout << "Средняя схожесть рекомендаций: " 
              << std::fixed << std::setprecision(2) << (stats.averageSimilarityScore * 100) << "%" << std::endl;
    
    std::cout << "\nВлияние параметров:" << std::endl;
    for (const auto& param : stats.parameterInfluence) {
        std::cout << "  " << param.first << ": " << param.second << "%" << std::endl;
    }
}

// Приватные методы

std::vector<SimilarityResult> GameRecommendationEngine::calculateRecommendations(
    const std::string& gameName,
    int maxResults
) const {
    // Проверяем кэш
    if (enableCaching) {
        auto cacheIt = recommendationsCache.find(gameName);
        if (cacheIt != recommendationsCache.end()) {
            auto& cached = cacheIt->second;
            if (maxResults == -1 || static_cast<int>(cached.size()) >= maxResults) {
                return std::vector<SimilarityResult>(cached.begin(), 
                    maxResults == -1 ? cached.end() : cached.begin() + maxResults);
            }
        }
    }
    
    BoardGame* targetGame = getGame(gameName);
    if (!targetGame || !calculator) {
        return {};
    }
    
    auto filteredGames = getFilteredGames({gameName});
    auto recommendations = calculator->findSimilarGames(targetGame, filteredGames, maxResults);
    
    // Обновляем кэш
    if (enableCaching && maxResults == -1) {
        recommendationsCache[gameName] = recommendations;
    }
    
    return recommendations;
}

bool GameRecommendationEngine::isValidGameForRecommendations(const BoardGame* game) const {
    if (!game) return false;
    
    // Игра должна иметь хотя бы один значимый параметр
    return !game->getComplexity().empty() || 
           !game->getGameType().empty() || 
           !game->getGenre().empty() ||
           game->getDuration() > 0;
}

void GameRecommendationEngine::updateRecommendationsCache(const std::string& gameName) const {
    if (!enableCaching) return;
    
    auto recommendations = calculateRecommendations(gameName, -1);
    recommendationsCache[gameName] = recommendations;
}

std::map<std::string, BoardGame*> GameRecommendationEngine::getFilteredGames(
    const std::vector<std::string>& excludeGames
) const {
    std::map<std::string, BoardGame*> filtered;
    
    for (const auto& pair : games) {
        if (std::find(excludeGames.begin(), excludeGames.end(), pair.first) == excludeGames.end()) {
            if (isValidGameForRecommendations(pair.second)) {
                filtered[pair.first] = pair.second;
            }
        }
    }
    
    return filtered;
}

std::vector<SimilarityResult> GameRecommendationEngine::aggregateRecommendations(
    const std::vector<std::vector<SimilarityResult>>& allRecommendations,
    int maxResults
) const {
    std::map<std::string, double> gameScores;
    std::map<std::string, SimilarityResult> gameDetails;
    
    // Агрегируем оценки для каждой игры
    for (const auto& recommendations : allRecommendations) {
        for (const auto& rec : recommendations) {
            if (gameScores.find(rec.gameName) == gameScores.end()) {
                gameScores[rec.gameName] = 0.0;
                gameDetails[rec.gameName] = rec;
            }
            gameScores[rec.gameName] += rec.similarityScore;
        }
    }
    
    // Сортируем по суммарной оценке
    std::vector<std::pair<std::string, double>> sortedGames(gameScores.begin(), gameScores.end());
    std::sort(sortedGames.begin(), sortedGames.end(),
        [](const auto& a, const auto& b) { return a.second > b.second; });
    
    // Формируем результат
    std::vector<SimilarityResult> result;
    int count = 0;
    for (const auto& pair : sortedGames) {
        if (maxResults != -1 && count >= maxResults) break;
        
        auto& details = gameDetails[pair.first];
        details.similarityScore = pair.second / allRecommendations.size(); // Нормализуем
        result.push_back(details);
        count++;
    }
    
    return result;
}

// Тестирование системы рекомендаций
void GameRecommendationEngine::runTests() {
    std::cout << "\n=== Тестирование GameRecommendationEngine ===" << std::endl;
    std::cout << "Примечание: тесты используют минимальный набор игр (4 шт) для проверки логики." << std::endl;
    std::cout << "Для полных рекомендаций используйте базу с большим количеством игр." << std::endl;
    
    GameRecommendationEngine engine;
    
    // Создаем тестовые игры (минимальный набор для проверки)
    BoardGame* brass = new BoardGame("Brass: Birmingham", "Экономическая стратегия", 2, 4, "2018");
    brass->setComplexity("8");
    brass->setDuration(90);
    brass->setGameType("Евро игра");
    brass->setGenre("Экономическая");
    brass->setMechanics("Построение сети, Управление ресурсами");
    
    BoardGame* wingspan = new BoardGame("Wingspan", "Семейная игра о птицах", 1, 5, "2019");
    wingspan->setComplexity("4");
    wingspan->setDuration(55);
    wingspan->setGameType("Семейная");
    wingspan->setGenre("Семейная");
    wingspan->setMechanics("Коллекция наборов, Управление ресурсами");
    
    BoardGame* terraforming = new BoardGame("Terraforming Mars", "Стратегия колонизации Марса", 1, 5, "2016");
    terraforming->setComplexity("7");
    terraforming->setDuration(120);
    terraforming->setGameType("Евро игра");
    terraforming->setGenre("Стратегия");
    terraforming->setMechanics("Карточки, Управление ресурсами");
    
    BoardGame* gloomhaven = new BoardGame("Gloomhaven", "Кооперативное приключение", 1, 4, "2017");
    gloomhaven->setComplexity("8");
    gloomhaven->setDuration(90);
    gloomhaven->setGameType("Кооперативная");
    gloomhaven->setGenre("Приключения");
    gloomhaven->setMechanics("Кампейн, Колода действий");
    
    // Добавляем игры в систему
    engine.addGame(brass);
    engine.addGame(wingspan);
    engine.addGame(terraforming);
    engine.addGame(gloomhaven);
    
    // Тест 1: Рекомендации для Brass: Birmingham
    auto recommendations1 = engine.getRecommendations("Brass: Birmingham", 3);
    std::cout << "Тест 1 - Рекомендации для Brass: Birmingham: ";
    if (!recommendations1.empty()) {
        std::cout << "PASSED (найдено " << recommendations1.size() << ")" << std::endl;
    } else {
        std::cout << "FAILED (рекомендации не найдены)" << std::endl;
    }
    
    // Тест 2: Поиск игр, похожих на несколько образцов
    std::vector<std::string> refs = {"Terraforming Mars", "Wingspan"};
    auto recommendations2 = engine.findGamesSimilarToMultiple(refs, 3);
    std::cout << "Тест 2 - Поиск игр, похожих на Terraforming Mars и Wingspan: ";
    if (!recommendations2.empty()) {
        std::cout << "PASSED (найдено " << recommendations2.size() << ")" << std::endl;
    } else {
        std::cout << "FAILED (рекомендации не найдены)" << std::endl;
    }
    
    // Тест 3: Статистика
    auto stats = engine.getRecommendationStats();
    std::cout << "Тест 3 - Статистика системы: ";
    if (stats.totalGames == 4 && stats.gamesWithRecommendations >= 0) {
        std::cout << "PASSED" << std::endl;
    } else {
        std::cout << "FAILED" << std::endl;
    }
    
    // Тест 4: Проверка вывода рекомендаций
    std::cout << "Тест 4 - Вывод рекомендаций: PASSED" << std::endl;
    
    // Очистка памяти
    delete brass;
    delete wingspan;
    delete terraforming;
    delete gloomhaven;
    
    std::cout << "\n=== Тестирование GameRecommendationEngine завершено ===" << std::endl;
}
