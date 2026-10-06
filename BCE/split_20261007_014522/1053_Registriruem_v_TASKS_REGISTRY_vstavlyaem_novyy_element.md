<!-- Часть 1053 из 1409 -->
# Регистрируем в TASKS_REGISTRY — вставляем новый элемент
*Хлебные крошки:* Регистрируем в TASKS_REGISTRY — вставляем новый элемент

[◀ ============================================================](1052_part.md) | [Оглавление](00_BCE_INDEX.md) | [1. В get_settings_dict добавляем поле ▶](1054_1_V_get_settings_dict_dobavlyaem_pole.md)

---

# Регистрируем в TASKS_REGISTRY — вставляем новый элемент
old_reg = '''    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

new_reg = '''    "close_stale_sessions": {
        "func": close_stale_sessions,
        "label_ru": "Автозакрытие зависших сессий",
        "label_en": "Auto-close stale sessions",
        "desc_ru": "Закрывает сессии без активности дольше N часов (N настраивается в /admin/settings).",
        "desc_en": "Closes sessions without activity for N hours (configured in /admin/settings).",
        "default_cron": "*/30 * * * *",   # каждые 30 минут
        "default_enabled": True,
    },
    "aggregate_daily_stats": {
        "func": aggregate_daily_stats,'''

if old_reg in content:
    content = content.replace(old_reg, new_reg, 1)
    print("OK: задача зарегистрирована в TASKS_REGISTRY")
else:
    print("WARN: не найден блок aggregate_daily_stats в реестре")

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_tasks_stale.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч tasks.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_tasks_stale.py
Что ожидаем:
text
OK: задача зарегистрирована в TASKS_REGISTRY
SYNTAX OK
________________________________________
Шаг 5b — Патч server/web_admin.py (настройка stale_session_hours)
Добавляем новую настройку в get_settings_dict, settings_save и settings_page.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\server\web_admin.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "stale_session_hours" in content:
    print("SKIP: stale_session_hours уже есть")
    raise SystemExit(0)

