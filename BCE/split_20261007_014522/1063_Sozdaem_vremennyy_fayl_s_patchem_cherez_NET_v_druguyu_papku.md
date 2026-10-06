<!-- Часть 1063 из 1409 -->
# Создаём временный файл с патчем через .NET (в другую папку!)
*Хлебные крошки:* Создаём временный файл с патчем через .NET (в другую папку!)

[◀ Заменяем оригинал](1062_Zamenyaem_original.md) | [Оглавление](00_BCE_INDEX.md) | [7. Автозакрытие зависших сессий ▶](1064_7_Avtozakrytie_zavisshih_sessiy.md)

---

# Создаём временный файл с патчем через .NET (в другую папку!)
$patcher = @'
import ast
import os

PATH = r"D:\tracker\server\tasks.py"
TMP = r"D:\tracker\_tasks_new.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "def close_stale_sessions" in content:
    print("SKIP: close_stale_sessions уже есть")
    raise SystemExit(0)

marker = "# ============================================================\n# Карта задач: имя в scheduler"

new_func = '''# ============================================================
