@echo off
setlocal
cd /d "%~dp0"

set "CPP_DIR=..\cpp_core"
set "DLL_PATH=%CD%\board_game_lib.dll"

if not exist "%DLL_PATH%" (
  if exist "%CPP_DIR%\BoardGame.cpp" (
    pushd "%CPP_DIR%"
    g++ -O2 -std=c++17 -shared ^
      BoardGame.cpp BoardGameCAPI.cpp ^
      Player.cpp Match.cpp MatchCAPI.cpp ^
      RatingFilter.cpp FeatureFilter.cpp SimilarGamesFilter.cpp ^
      SimilarityCalculator.cpp GenreSimilarityMatrix.cpp ^
      GameRecommendationEngine.cpp GameDatabase.cpp GameDatabaseCAPI.cpp ^
      -o board_game_lib.dll
    popd
  )
  if exist "%CPP_DIR%\board_game_lib.dll" (
    copy /Y "%CPP_DIR%\board_game_lib.dll" "%DLL_PATH%" >nul
  )
)

if not exist "%DLL_PATH%" (
  echo [ERROR] board_game_lib.dll not found
  exit /b 1
)

py --version >nul 2>nul
if %errorlevel% neq 0 (
  python app_gui.py
  exit /b %errorlevel%
)

py app_gui.py
pause
endlocal
