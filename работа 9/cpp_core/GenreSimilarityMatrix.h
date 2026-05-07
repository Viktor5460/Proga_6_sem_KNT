#ifndef GENRE_SIMILARITY_MATRIX_H
#define GENRE_SIMILARITY_MATRIX_H

#include <string>
#include <map>
#include <vector>

// Класс для управления схожестью жанров и тем игр
class GenreSimilarityMatrix {
private:
    // Матрица схожести жанров
    std::map<std::string, std::map<std::string, double>> genreSimilarityMatrix;
    
    // Матрица схожести тем
    std::map<std::string, std::map<std::string, double>> themeSimilarityMatrix;
    
    // Матрица схожести материалов
    std::map<std::string, std::map<std::string, double>> materialSimilarityMatrix;
    
public:
    GenreSimilarityMatrix();
    
    // Инициализация предустановленных данных схожести
    void initializeDefaultSimilarities();
    
    // Получение схожести жанров
    double getGenreSimilarity(const std::string& genre1, const std::string& genre2) const;
    
    // Получение схожести тем
    double getThemeSimilarity(const std::string& theme1, const std::string& theme2) const;
    
    // Получение схожести материалов
    double getMaterialSimilarity(const std::string& material1, const std::string& material2) const;
    
    // Добавление пользовательской схожести
    void setGenreSimilarity(const std::string& genre1, const std::string& genre2, double similarity);
    void setThemeSimilarity(const std::string& theme1, const std::string& theme2, double similarity);
    void setMaterialSimilarity(const std::string& material1, const std::string& material2, double similarity);
    
    // Получение всех доступных жанров
    std::vector<std::string> getAllGenres() const;
    
    // Получение всех доступных тем
    std::vector<std::string> getAllThemes() const;
    
    // Получение всех доступных материалов
    std::vector<std::string> getAllMaterials() const;
    
    // Применение гауссовой функции для числовых параметров
    static double gaussianSimilarity(double value1, double value2, double standardDeviation = 1.0);
    
private:
    // Вспомогательные методы для инициализации
    void initializeGenreSimilarities();
    void initializeThemeSimilarities();
    void initializeMaterialSimilarities();
    
    // Нормализация строки (приведение к нижнему регистру, удаление пробелов)
    std::string normalizeString(const std::string& str) const;
};

#endif
