#ifndef SIMILARITY_WEIGHTS_H
#define SIMILARITY_WEIGHTS_H

#include <cmath>

// Структура для настройки весов различных параметров при вычислении схожести игр
struct SimilarityWeights {
    // Основные веса (должны суммироваться до 1.0)
    double complexityWeight = 0.25;        // 25% - сложность игры
    double playerCountWeight = 0.20;       // 20% - количество игроков
    double gameTypeWeight = 0.15;          // 15% - тип игры (евро, америтреш, семейная и т.д.)
    double durationWeight = 0.15;          // 15% - длительность игры
    double mechanicsWeight = 0.15;         // 15% - механики игры
    double genreWeight = 0.10;             // 10% - жанр игры
    
    // Веса для пользовательских параметров (материал, тема, дизайн и т.д.)
    double userParametersWeight = 0.05;    // 5% - дополнительные пользовательские параметры
    
    // Константы для обработки отсутствующих данных
    double missingDataPenalty = 0.05;      // 5% штраф за отсутствующий параметр (уменьшен)
    
    // Пороговые значения
    double minSimilarityThreshold = 0.15;  // Минимальный порог схожести (15%)
    int maxRecommendations = 10;           // Максимальное количество рекомендаций
    
    // Конструктор с проверкой корректности весов
    SimilarityWeights() {
        normalizeWeights();
    }
    
    // Нормализация весов (сумма должна быть равна 1.0)
    void normalizeWeights() {
        double totalWeight = complexityWeight + playerCountWeight + gameTypeWeight + 
                           durationWeight + mechanicsWeight + genreWeight + userParametersWeight;
        
        if (totalWeight > 0) {
            complexityWeight /= totalWeight;
            playerCountWeight /= totalWeight;
            gameTypeWeight /= totalWeight;
            durationWeight /= totalWeight;
            mechanicsWeight /= totalWeight;
            genreWeight /= totalWeight;
            userParametersWeight /= totalWeight;
        }
    }
    
    // Проверка корректности настроек
    bool isValid() const {
        double totalWeight = complexityWeight + playerCountWeight + gameTypeWeight + 
                           durationWeight + mechanicsWeight + genreWeight + userParametersWeight;
        return std::abs(totalWeight - 1.0) < 0.001 && 
               minSimilarityThreshold >= 0.0 && minSimilarityThreshold <= 1.0 &&
               maxRecommendations > 0;
    }
};

#endif
