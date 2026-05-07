@echo off
echo ===================================================
echo Сборка динамической библиотеки модели настольных игр (DLL)...
echo ===================================================

rem Собираем модель настольных игр и C-обёртки.
rem main.cpp НЕ используется, т.к. у библиотеки не должно быть функции main().

g++ -O2 -std=c++17 -shared ^
    BoardGame.cpp BoardGameCAPI.cpp ^
    Player.cpp Match.cpp MatchCAPI.cpp ^
    RatingFilter.cpp FeatureFilter.cpp SimilarGamesFilter.cpp ^
    SimilarityCalculator.cpp GenreSimilarityMatrix.cpp ^
    GameRecommendationEngine.cpp GameDatabase.cpp GameDatabaseCAPI.cpp ^
    -o board_game_lib.dll

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo Библиотека board_game_lib.dll успешно собрана.
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo Ошибка при сборке библиотеки!
    echo ===================================================
)

pause


