<!-- Часть 905 из 1409 -->
# Проверка синтаксиса
*Хлебные крошки:* Проверка синтаксиса

[◀ ============================================================](904_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](906_part.md)

---

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'D:\tracker\client\i18n.py', encoding='utf-8').read()); print('SYNTAX OK')"
Что ожидаем:
text
OK: client/i18n.py создан
SYNTAX OK
________________________________________
Скрипт 2 — client/themes.py
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$content = @'
