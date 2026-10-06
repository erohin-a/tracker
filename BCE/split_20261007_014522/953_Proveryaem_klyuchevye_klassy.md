<!-- Часть 953 из 1409 -->
# Проверяем ключевые классы
*Хлебные крошки:* Проверяем ключевые классы

[◀ Проверка синтаксиса](952_Proverka_sintaksisa.md) | [Оглавление](00_BCE_INDEX.md) | [1. Добавляем импорты в начало файла (после существующих) ▶](954_1_Dobavlyaem_importy_v_nachalo_fayla_posle_suschestvuyuschih.md)

---

# Проверяем ключевые классы
$content = [System.IO.File]::ReadAllText("D:\tracker\client\settings_dialog.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("class ReminderTab", "class GeneralTab", "class RegistrationTab", "class SettingsDialog",
                 "get_server_url", "get_cert_fingerprint", "themes.apply_theme", "SUPPORTED_LANGS")) {
    if ($content.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}
Что ожидаем:
text
OK: settings_dialog.py собран (~25000 символов)
SYNTAX OK
 OK: class ReminderTab
 OK: class GeneralTab
 OK: class RegistrationTab
 OK: class SettingsDialog
 OK: get_server_url
 OK: get_cert_fingerprint
 OK: themes.apply_theme
 OK: SUPPORTED_LANGS
________________________________________
Скрипт 5 — Патч main.py (применение темы + языка при старте)
Смотрим на текущий main() в client/main.py. Сейчас там создаётся QApplication и MainWindow. Нужно:
Перед созданием окна — применить сохранённый язык к i18n
После создания QApplication — применить тему через themes.apply_theme
Если в config.json есть флаг restart_required=True — сбросить и логировать
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast
import re

PATH = r"D:\tracker\client\main.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "themes.apply_theme" in content and "set_language(get_language_code())" in content:
    print("SKIP: main.py уже пропатчен")
    raise SystemExit(0)

