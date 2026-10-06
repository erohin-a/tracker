<!-- Часть 828 из 1409 -->
# Проверки
*Хлебные крошки:* Проверки

[◀ Новая версия функции](827_Novaya_versiya_funktsii.md) | [Оглавление](00_BCE_INDEX.md) | [Вставляем после функции get_client_config ▶](829_Vstavlyaem_posle_funktsii_get_client_config.md)

---

# Проверки
checks = [
    "def _merge_effective_settings",   # не должно быть — просто маркер, что мы не переписали
    "source_reminder",                  # появилось
    "source_end_of_day",                # появилось
    "comp.employee_id",                 # логика поиска
    "_ES",                              # алиас EmployeeSettings
]
for c in checks:
    found = c in new_content
    mark = "OK" if (c != "def _merge_effective_settings" or not found) else "ОШИБКА"
    print(f"  {mark}: {c} = {found}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_client_config.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _patch_client_config.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_client_config.py
Что ожидаем:
text
OK: get_client_config переписан с мержем персональных
SYNTAX OK
  OK: def _merge_effective_settings = False
  OK: source_reminder = True
  OK: source_end_of_day = True
  OK: comp.employee_id = True
  OK: _ES = True
________________________________________
Скрипт 4 — endpoint PUT /api/v1/client-settings
Добавляем новый endpoint после get_client_config. Он принимает JSON, применяет к employee_settings, отдаёт эффективные.
Приоритет — server wins: если сервер недавно менял (updated_at > 5 минут назад и updated_by != "client"), отклоняем. Иначе принимаем.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import sys
import ast

MAIN = r"D:\tracker\server\main.py"

with open(MAIN, "r", encoding="utf-8") as f:
    content = f.read()

if "/api/v1/client-settings" in content:
    print("SKIP: /client-settings уже есть")
    raise SystemExit(0)

