#include "GenreSimilarityMatrix.h"
#include <algorithm>
#include <cmath>
#include <iostream>

GenreSimilarityMatrix::GenreSimilarityMatrix() {
    initializeDefaultSimilarities();
}

void GenreSimilarityMatrix::initializeDefaultSimilarities() {
    initializeGenreSimilarities();
    initializeThemeSimilarities();
    initializeMaterialSimilarities();
}

void GenreSimilarityMatrix::initializeGenreSimilarities() {
    // Схожие жанры
    genreSimilarityMatrix["Стратегия"]["Тактика"] = 0.8;
    genreSimilarityMatrix["Стратегия"]["Экономическая"] = 0.7;
    genreSimilarityMatrix["Стратегия"]["Военная"] = 0.6;
    genreSimilarityMatrix["Тактика"]["Военная"] = 0.8;
    genreSimilarityMatrix["Экономическая"]["Торговая"] = 0.9;
    genreSimilarityMatrix["Экономическая"]["Городское строительство"] = 0.7;
    
    // Семейные игры
    genreSimilarityMatrix["Семейная"]["Детская"] = 0.8;
    genreSimilarityMatrix["Семейная"]["Парти"] = 0.6;
    genreSimilarityMatrix["Детская"]["Образовательная"] = 0.7;
    
    // Абстрактные игры
    genreSimilarityMatrix["Абстрактная"]["Логическая"] = 0.9;
    genreSimilarityMatrix["Абстрактная"]["Математическая"] = 0.6;
    
    // Приключенческие игры
    genreSimilarityMatrix["Приключения"]["Исследование"] = 0.8;
    genreSimilarityMatrix["Приключения"]["Фэнтези"] = 0.6;
    genreSimilarityMatrix["Фэнтези"]["Магическая"] = 0.8;
    genreSimilarityMatrix["Фэнтези"]["Средневековье"] = 0.7;
    
    // Кооперативные игры
    genreSimilarityMatrix["Кооперативная"]["Командная"] = 0.9;
    genreSimilarityMatrix["Кооперативная"]["Спасение"] = 0.7;
    
    // Дедуктивные игры
    genreSimilarityMatrix["Дедуктивная"]["Детективная"] = 0.9;
    genreSimilarityMatrix["Дедуктивная"]["Загадочная"] = 0.8;
    
    // Делаем матрицу симметричной
    auto tempMatrix = genreSimilarityMatrix;
    for (const auto& genre1 : tempMatrix) {
        for (const auto& genre2 : genre1.second) {
            genreSimilarityMatrix[genre2.first][genre1.first] = genre2.second;
        }
    }
    
    // Добавляем полное совпадение (1.0) для всех жанров с самими собой
    for (const auto& genre : genreSimilarityMatrix) {
        genreSimilarityMatrix[genre.first][genre.first] = 1.0;
    }
}

void GenreSimilarityMatrix::initializeThemeSimilarities() {
    // Исторические периоды
    themeSimilarityMatrix["Древний мир"]["Египет"] = 0.9;
    themeSimilarityMatrix["Древний мир"]["Рим"] = 0.8;
    themeSimilarityMatrix["Древний мир"]["Греция"] = 0.8;
    themeSimilarityMatrix["Средневековье"]["Новые века"] = 0.7;
    themeSimilarityMatrix["Средневековье"]["Рыцарство"] = 0.9;
    themeSimilarityMatrix["Новые века"]["Ренессанс"] = 0.8;
    themeSimilarityMatrix["Современный мир"]["Будущее"] = 0.6;
    themeSimilarityMatrix["Будущее"]["Космос"] = 0.8;
    themeSimilarityMatrix["Будущее"]["Научная фантастика"] = 0.9;
    
    // Географические и природные темы
    themeSimilarityMatrix["Пустыня"]["Египет"] = 0.8;
    themeSimilarityMatrix["Горы"]["Шахты"] = 0.9;
    themeSimilarityMatrix["Горы"]["Пещеры"] = 0.7;
    themeSimilarityMatrix["Океан"]["Море"] = 0.9;
    themeSimilarityMatrix["Океан"]["Острова"] = 0.7;
    themeSimilarityMatrix["Лес"]["Джунгли"] = 0.8;
    themeSimilarityMatrix["Арктика"]["Зима"] = 0.8;
    
    // Мистические и магические темы
    themeSimilarityMatrix["Магия"]["Волшебство"] = 0.9;
    themeSimilarityMatrix["Магия"]["Мистика"] = 0.7;
    themeSimilarityMatrix["Драконы"]["Фэнтези"] = 0.8;
    themeSimilarityMatrix["Драконы"]["Магия"] = 0.7;
    
    // Современные темы
    themeSimilarityMatrix["Город"]["Мегаполис"] = 0.9;
    themeSimilarityMatrix["Город"]["Урбанистика"] = 0.8;
    themeSimilarityMatrix["Технологии"]["Роботы"] = 0.8;
    themeSimilarityMatrix["Технологии"]["Искусственный интеллект"] = 0.7;
    
    // Делаем матрицу симметричной
    auto tempMatrix = themeSimilarityMatrix;
    for (const auto& theme1 : tempMatrix) {
        for (const auto& theme2 : theme1.second) {
            themeSimilarityMatrix[theme2.first][theme1.first] = theme2.second;
        }
    }
    
    // Добавляем полное совпадение для всех тем с самими собой
    for (const auto& theme : themeSimilarityMatrix) {
        themeSimilarityMatrix[theme.first][theme.first] = 1.0;
    }
}

void GenreSimilarityMatrix::initializeMaterialSimilarities() {
    // Материалы компонентов
    materialSimilarityMatrix["Пластик"]["Картон"] = 0.6;
    materialSimilarityMatrix["Пластик"]["Дерево"] = 0.5;
    materialSimilarityMatrix["Картон"]["Бумага"] = 0.8;
    materialSimilarityMatrix["Дерево"]["Металл"] = 0.4;
    materialSimilarityMatrix["Металл"]["Камень"] = 0.5;
    
    // Качество материалов
    materialSimilarityMatrix["Премиум"]["Высокое качество"] = 0.9;
    materialSimilarityMatrix["Премиум"]["Люкс"] = 0.8;
    materialSimilarityMatrix["Стандарт"]["Обычный"] = 0.9;
    materialSimilarityMatrix["Эконом"]["Бюджетный"] = 0.9;
    
    // Делаем матрицу симметричной
    auto tempMatrix = materialSimilarityMatrix;
    for (const auto& material1 : tempMatrix) {
        for (const auto& material2 : material1.second) {
            materialSimilarityMatrix[material2.first][material1.first] = material2.second;
        }
    }
    
    // Добавляем полное совпадение для всех материалов с самими собой
    for (const auto& material : materialSimilarityMatrix) {
        materialSimilarityMatrix[material.first][material.first] = 1.0;
    }
}

double GenreSimilarityMatrix::getGenreSimilarity(const std::string& genre1, const std::string& genre2) const {
    if (genre1 == genre2) return 1.0;
    
    std::string normGenre1 = normalizeString(genre1);
    std::string normGenre2 = normalizeString(genre2);
    
    auto it1 = genreSimilarityMatrix.find(normGenre1);
    if (it1 != genreSimilarityMatrix.end()) {
        auto it2 = it1->second.find(normGenre2);
        if (it2 != it1->second.end()) {
            return it2->second;
        }
    }
    
    return 0.0; // Если схожесть не найдена, возвращаем 0
}

double GenreSimilarityMatrix::getThemeSimilarity(const std::string& theme1, const std::string& theme2) const {
    if (theme1 == theme2) return 1.0;
    
    std::string normTheme1 = normalizeString(theme1);
    std::string normTheme2 = normalizeString(theme2);
    
    auto it1 = themeSimilarityMatrix.find(normTheme1);
    if (it1 != themeSimilarityMatrix.end()) {
        auto it2 = it1->second.find(normTheme2);
        if (it2 != it1->second.end()) {
            return it2->second;
        }
    }
    
    return 0.0;
}

double GenreSimilarityMatrix::getMaterialSimilarity(const std::string& material1, const std::string& material2) const {
    if (material1 == material2) return 1.0;
    
    std::string normMaterial1 = normalizeString(material1);
    std::string normMaterial2 = normalizeString(material2);
    
    auto it1 = materialSimilarityMatrix.find(normMaterial1);
    if (it1 != materialSimilarityMatrix.end()) {
        auto it2 = it1->second.find(normMaterial2);
        if (it2 != it1->second.end()) {
            return it2->second;
        }
    }
    
    return 0.0;
}

void GenreSimilarityMatrix::setGenreSimilarity(const std::string& genre1, const std::string& genre2, double similarity) {
    std::string normGenre1 = normalizeString(genre1);
    std::string normGenre2 = normalizeString(genre2);
    
    genreSimilarityMatrix[normGenre1][normGenre2] = similarity;
    genreSimilarityMatrix[normGenre2][normGenre1] = similarity; // Делаем симметричной
}

void GenreSimilarityMatrix::setThemeSimilarity(const std::string& theme1, const std::string& theme2, double similarity) {
    std::string normTheme1 = normalizeString(theme1);
    std::string normTheme2 = normalizeString(theme2);
    
    themeSimilarityMatrix[normTheme1][normTheme2] = similarity;
    themeSimilarityMatrix[normTheme2][normTheme1] = similarity;
}

void GenreSimilarityMatrix::setMaterialSimilarity(const std::string& material1, const std::string& material2, double similarity) {
    std::string normMaterial1 = normalizeString(material1);
    std::string normMaterial2 = normalizeString(material2);
    
    materialSimilarityMatrix[normMaterial1][normMaterial2] = similarity;
    materialSimilarityMatrix[normMaterial2][normMaterial1] = similarity;
}

std::vector<std::string> GenreSimilarityMatrix::getAllGenres() const {
    std::vector<std::string> genres;
    for (const auto& genre : genreSimilarityMatrix) {
        genres.push_back(genre.first);
    }
    return genres;
}

std::vector<std::string> GenreSimilarityMatrix::getAllThemes() const {
    std::vector<std::string> themes;
    for (const auto& theme : themeSimilarityMatrix) {
        themes.push_back(theme.first);
    }
    return themes;
}

std::vector<std::string> GenreSimilarityMatrix::getAllMaterials() const {
    std::vector<std::string> materials;
    for (const auto& material : materialSimilarityMatrix) {
        materials.push_back(material.first);
    }
    return materials;
}

double GenreSimilarityMatrix::gaussianSimilarity(double value1, double value2, double standardDeviation) {
    double difference = std::abs(value1 - value2);
    return std::exp(-(difference * difference) / (2.0 * standardDeviation * standardDeviation));
}

std::string GenreSimilarityMatrix::normalizeString(const std::string& str) const {
    std::string normalized = str;
    std::transform(normalized.begin(), normalized.end(), normalized.begin(), ::tolower);
    
    // Удаляем лишние пробелы
    normalized.erase(std::remove_if(normalized.begin(), normalized.end(), ::isspace), normalized.end());
    
    return normalized;
}
