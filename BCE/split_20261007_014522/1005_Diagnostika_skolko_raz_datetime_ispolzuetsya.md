<!-- Часть 1005 из 1409 -->
# Диагностика: сколько раз datetime используется
*Хлебные крошки:* Диагностика: сколько раз datetime используется

[◀ ---------- 3. Проверим синтаксис ----------](1004_3_Proverim_sintaksis.md) | [Оглавление](00_BCE_INDEX.md) | [Добавляем QObject-обёртку с сигналом после SUPPORTED_THEMES ▶](1006_Dobavlyaem_QObject_obertku_s_signalom_posle_SUPPORTED_THEMES.md)

---

# Диагностика: сколько раз datetime используется
cnt = content.count("datetime.")
print(f"Использований datetime.: {cnt}")
print(f"Строка с 'from datetime': {'OK' if 'from datetime import' in content else 'MISS'}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_sync_datetime.py", $patcher, [System.Text.UTF8Encoding]::new($false))
& client\.venv\Scripts\python.exe _patch_sync_datetime.py
Что ожидаем:
text
OK: datetime/timezone добавлены в импорты
OK: комментарий к connected почищен
SYNTAX OK
Использований datetime.: N (больше 0)
Строка с 'from datetime': OK
________________________________________
Скрипт 2 — Диагностика main.py
Нужно увидеть 3 блока. Пришли полный вывод.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$lines = [System.IO.File]::ReadAllLines("D:\tracker\client\main.py", [System.Text.UTF8Encoding]::new($false))

Write-Host "=== Блок 1: строки 1-50 (импорты + STYLE_*) ===" -ForegroundColor Cyan
for ($i = 0; $i -lt [Math]::Min(50, $lines.Length); $i++) {
    Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
}

Write-Host "`n=== Блок 2: строки 80-165 (кнопки + панель) ===" -ForegroundColor Cyan
for ($i = 79; $i -lt [Math]::Min(165, $lines.Length); $i++) {
    Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
}

Write-Host "`n=== Блок 3: строки 225-300 (_update_buttons и рядом) ===" -ForegroundColor Cyan
for ($i = 224; $i -lt [Math]::Min(300, $lines.Length); $i++) {
    Write-Host ("{0,4}: {1}" -f ($i+1), $lines[$i])
}

Write-Host "`n=== Блок 4: все использования STYLE_* ===" -ForegroundColor Cyan
Select-String -Path "D:\tracker\client\main.py" -Pattern "STYLE_" | Select-Object -First 40
Что я ищу:
Где определены STYLE_GREEN, STYLE_RED, STYLE_DISABLED, STYLE_RESUME — наверху файла или внутри класса.
Полный код _update_buttons (или как называется метод, управляющий состоянием кнопок).
Есть ли ещё inline-стили на панели (лейблы, заголовки).
После этого дам финальный патч main.py, который:
Уберёт inline-стили с кнопок btn_start, btn_stop, btn_pause, lbl_session_clock.
Сделает два набора стилей — светлый и тёмный.
Добавит в MainWindow метод _refresh_theme(), который применяет нужный набор.
Подключит _refresh_theme() к themes.apply_theme() через глобальный сигнал/колбэк.
________________________________________
Скрипт 3 — Пока запусти, добавлю сигнал в themes.py
Проблема: сейчас themes.apply_theme() вызывается из settings_dialog._on_theme_changed(), но главное окно не узнаёт об этом. Нужно как-то уведомить MainWindow.
Решение: глобальный сигнал в модуле themes.py, который MainWindow подхватит в __init__.
Допишу themes.py — добавлю theme_changed = pyqtSignal(str) (обёртка через QObject-класс).
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\themes.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

if "class _ThemeSignals" in content:
    print("SKIP: сигнал уже есть")
    raise SystemExit(0)

