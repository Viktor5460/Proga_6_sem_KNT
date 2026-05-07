@echo off
setlocal
cd /d "%~dp0"

if not exist results mkdir results

g++ --version >nul 2>nul
if %errorlevel% neq 0 (
  echo [ERROR] g++ not found
  exit /b 1
)

py --version >nul 2>nul
if %errorlevel% neq 0 (
  python --version >nul 2>nul
  if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    exit /b 1
  )
)

g++ -std=c++17 -O2 -Iinclude src\main.cpp -o lab9_benchmark.exe
if %errorlevel% neq 0 (
  echo [ERROR] Build failed
  exit /b 1
)

lab9_benchmark.exe
if %errorlevel% neq 0 (
  echo [ERROR] Runtime failed
  exit /b 1
)

echo [OK] Done
pause
endlocal
