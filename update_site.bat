@echo off
chcp 65001 > nul
setlocal

cd /d D:\tracker\docs

echo ============================================
echo   Обновление сайта Трекер (GitHub Pages)
echo ============================================
echo.

REM Проверка, что это git-репозиторий
if not exist ".git" (
    echo [ОШИБКА] Папка D:\tracker\docs не является git-репозиторием.
    echo Сначала выполните инициализацию:
    echo   cd D:\tracker\docs
    echo   git init
    echo   git remote add origin https://github.com/erohin-a/tracker.git
    pause
    exit /b 1
)

REM Показать текущий статус
echo --- Текущие изменения ---
git status --short
echo.

REM Если нет изменений — выходим
git diff --quiet && git diff --cached --quiet
if %errorlevel%==0 (
    echo Нет изменений для коммита.
    echo.
    pause
    exit /b 0
)

REM Запрос сообщения коммита
set /p COMMIT_MSG="Введите сообщение коммита (Enter = 'обновление KB'): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=обновление KB

echo.
echo --- Добавляем файлы ---
git add .

echo --- Коммит ---
git commit -m "%COMMIT_MSG%"

echo --- Пуш на GitHub ---
git push

if %errorlevel%==0 (
    echo.
    echo ============================================
    echo   ГОТОВО! Сайт обновится через 30-60 секунд.
    echo   https://erohin-a.github.io/tracker/
    echo ============================================
) else (
    echo.
    echo [ОШИБКА] Пуш не удался. Проверьте настройки remote.
)

echo.
pause
endlocal