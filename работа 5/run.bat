@echo off
chcp 65001 > nul
setlocal

cd /d "%~dp0"

python work5_run.py
if errorlevel 1 (
  echo Ошибка запуска.
  exit /b 1
)

echo Готово.
