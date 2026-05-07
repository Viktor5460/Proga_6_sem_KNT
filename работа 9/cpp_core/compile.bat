@echo off
echo ===================================================
echo Компиляция иерархии классов BoardGame...
echo ===================================================

g++ -O2 -std=c++17 main.cpp BoardGame.cpp Player.cpp Match.cpp RatingFilter.cpp FeatureFilter.cpp SimilarGamesFilter.cpp GameDatabase.cpp SimilarityCalculator.cpp GameRecommendationEngine.cpp GenreSimilarityMatrix.cpp -o board_game_recommendations.exe

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo Компиляция успешна!
    echo ===================================================
    echo Запуск программы:
    echo.
    board_game_recommendations.exe
) else (
    echo.
    echo ===================================================
    echo Ошибка компиляции!
    echo ===================================================
)

pause
