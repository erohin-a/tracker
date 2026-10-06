<!-- Часть 267 из 1409 -->
# Проверка синтаксиса
*Хлебные крошки:* Проверка синтаксиса

[◀ ============================================================](266_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](268_part.md)

---

# Проверка синтаксиса
Write-Host "`n--- Проверка синтаксиса Python ---" -ForegroundColor Cyan
python -c "import ast; ast.parse(open(r'$serverDir\config.py', encoding='utf-8').read()); ast.parse(open(r'$serverDir\web_admin.py', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — шаблоны reports.html и report_result.html
powershell
$ErrorActionPreference = "Stop"
$templatesDir = "D:\tracker\server\templates"

