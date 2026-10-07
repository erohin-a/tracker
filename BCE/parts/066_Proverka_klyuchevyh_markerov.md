# Проверка ключевых маркеров

*Часть 66 из 100. Источник: `BCE.md`.*

[◀ Сначала посмотрим текущее содержимое (в каком месте падает)](065_Snachala_posmotrim_tekuschee_soderzhimoe_v_kakom_meste_padaet.md) | [Оглавление](00_BCE_INDEX.md) | [В apply_theme — emit сигнала после установки stylesheet ▶](067_V_apply_theme_emit_signala_posle_ustanovki_stylesheet.md)

---

# Проверка ключевых маркеров
$check = [System.IO.File]::ReadAllText("D:\tracker\client\themes.py", [System.Text.UTF8Encoding]::new($false))
foreach ($m in @("_CUSTOM_LIGHT", "_CUSTOM_DARK", "#infoPanel", "#btnStart", "#btnStop", "def apply_theme")) {
    if ($check.Contains($m)) {
        Write-Host " OK: $m" -ForegroundColor Green
    } else {
        Write-Host " MISS: $m" -ForegroundColor Red
    }
}
Что ожидаем:
text
OK: themes.py переписан (XXXX символов)
SYNTAX OK
 OK: _CUSTOM_LIGHT
 OK: _CUSTOM_DARK
 OK: #infoPanel
 OK: #btnStart
 OK: #btnStop
 OK: def apply_theme
________________________________________
Что делаем после диагностики
Как только пришлёшь вывод Скрипта 1 (диагностика main.py + sync.py), я:
Патч main.py — приведём кнопки и панель к новым objectName, уберём остатки inline-стилей.
Патч sync.py — добавим глобальный from datetime import datetime, timezone, устраним cap pause_sec баг.
Патч main.py — retranslate для главного окна (кнопки «Начать работу», «Конец работы», «Настройки», статусы).
Порядок сейчас:
Скрипт 1 — диагностика. Пришли вывод.
Скрипт 2 — замена themes.py. Проверь SYNTAX OK и 6 маркеров.
Оба — параллельно. Ничего не запускай больше, пока не увижу вывод диагностики.
Отлично, теперь всё ясно.
Что видно из диагностики:
main.py кнопки: inline-стили кнопок старт/стоп/пауза НЕ были убраны (в патче 3 я искал точный текст с определённой пунктуацией, но там другой пробел — двойной после ?). Есть также btn_pause со своим стилем, который я не тронул.
Есть константы STYLE_GREEN, STYLE_RED, STYLE_DISABLED, STYLE_RESUME — используются в _update_buttons(). Значит, inline-стили применяются не только при создании, но и при каждом обновлении статуса.
main.py панель: panel.setObjectName("infoPanel") — уже стоит. Хорошо.
main.py лейблы: lbl_session_clock имеет inline-стиль font-size:13px; font-weight:bold; color:#28a745; — не подхватится QSS для тёмной темы. Нужно убрать inline или сделать через objectName + QSS.
sync.py cap pause_sec: проблема — в блоке try вызывается (t2 - t1).total_seconds(), где t1/t2 — вероятно, datetime объекты, полученные из datetime.fromisoformat(). Но datetime не импортирован глобально. Смотрим импорты sync.py — действительно нет from datetime import datetime. Есть import json, logging, threading. Значит, где-то внутри функции делается datetime.fromisoformat(...), а datetime не определён.
Смешной момент: в docstring-комментарии к connected — крокозябры (СЃРµСЂРІРµСЂ). Это старый баг копипаста. Надо почистить.
total > 0 and pause_sec > total — вот откуда cap pause_sec failed: name 'datetime' is not defined. Дело в том, что t2 и t1 — это, вероятно, datetime объекты, которые вернул datetime.fromisoformat(), а сам datetime не импортирован.
План действий:
Патч sync.py — добавить from datetime import datetime, timezone в импорты + почистить крокозябры в комментарии.
Патч main.py:
Убрать inline-стили с кнопок (setStyleSheet после создания) — они должны задаваться через objectName.
Найти константы STYLE_GREEN, STYLE_RED, STYLE_DISABLED, STYLE_RESUME — они применяются в _update_buttons(). Заменить их на переключение свойств, а стили описать через QSS. Это сложнее. Проще: оставить логику со стилями, но добавить методы, которые применяют QSS+objectName в зависимости от темы.
Проще и надёжнее: перенести всю логику кнопок на QSS + динамические свойства (setProperty). В QSS можно писать QPushButton#btnStart[state="disabled"] { ... }.
Хм, это большая переделка. Давай сначала минимально:
Идея: оставить inline-стили кнопок, но менять их в зависимости от темы. То есть не убирать inline полностью, а добавить метод _refresh_button_styles() в MainWindow, который применяет нужные inline-стили в зависимости от текущей темы (dark / light).
Это проще, чем городить QSS+setProperty. Минус: при смене темы надо пересоздавать стили кнопок. Но у нас есть themes.apply_theme(), который вызывается в settings_dialog._on_theme_changed(). Нужно как-то уведомить главное окно.
Как уведомить главное окно:
Проще всего — сделать глобальный сигнал themes.theme_changed = pyqtSignal(str) в модуле themes.py.
В MainWindow подписаться и вызвать _refresh_button_styles().
Или ещё проще: у themes есть apply_theme, которая вызывается из settings_dialog. Внутри apply_theme можно найти все top-level windows и вызвать repaint() / update(). Но inline-стили не перезагрузятся просто от update().
Решение простое и надёжное:
В themes.py добавить глобальный сигнал theme_changed (использовать QObject-обёртку).
В settings_dialog._on_theme_changed — emit этого сигнала.
В MainWindow — подписаться и вызвать _refresh_button_styles().
Или, ещё проще: _refresh_button_styles() будет вызываться и при старте, и при смене темы. При смене темы он читает актуальную тему из config.get_theme_code().
Как уведомить при смене темы: для простоты используем QApplication.instance().topLevelWidgets() и ищем наш MainWindow, дёргаем метод.
Ещё проще: дать apply_theme вызывать QApplication.instance().topLevelWidgets() и у каждого окна, если есть метод _refresh_theme(), вызвать его.
Пойдём этим путём.
Конкретный план по патчам:
Патч sync.py
Добавить from datetime import datetime, timezone (глобально).
Заодно почистить крокозябры в комментарии.
Патч main.py
Убрать setStyleSheet сразу после создания кнопок — они будут назначаться через _refresh_theme().
Убрать setStyleSheet у lbl_session_clock.
Найти определения STYLE_GREEN, STYLE_RED, STYLE_DISABLED, STYLE_RESUME — они где-то наверху файла. Их тоже надо переделать, либо оставить, но в _update_buttons применять с учётом темы.
Добавить метод _refresh_theme() в MainWindow, который:
Применяет нужные стили кнопкам в зависимости от текущего статуса (idle/session/paused) и темы.
Применяет цвет к lbl_session_clock.
В themes.apply_theme() после app.setStyleSheet(...) вызвать _refresh_top_level_windows(app) — чтобы главное окно само перерисовало inline-стили.
В MainWindow._update_buttons() (или как она называется) — вызывать _refresh_theme() для кнопок после изменения свойств enabled/paused.
Хм, тут много. Возможно, надо упростить.
Альтернатива проще: оставить inline-стили в main.py как есть, но сделать два набора: светлый и тёмный. _refresh_theme() в MainWindow выбирает набор и применяет.
Смотрим на код из диагностики:
text
2026-09-23 11:00:20,858 INFO tracker.main ActivityWatcher thread started
Из более раннего сообщения пользователя:
text
self.btn_start.setStyleSheet(STYLE_GREEN)
Значит, есть константы STYLE_GREEN, STYLE_DISABLED, STYLE_RED, STYLE_RESUME. Скорее всего, наверху файла:
python
STYLE_GREEN = "background-color:#28a745; color:white; ..."
STYLE_RED = "..."
...
Мне нужно увидеть эти константы. Давай добавим диагностику в следующий скрипт — покажем первые 100 строк main.py.
Хотя нет, давайте сделаем иначе. Я могу поступить так:
Не трогать константы STYLE_*, а добавить их варианты для тёмной темы (STYLE_GREEN_DARK, STYLE_RED_DARK, ...).
Добавить в MainWindow метод _apply_current_theme(), который при вызове:
Смотрит текущую тему (config.get_theme_code()).
Выбирает нужный набор стилей.
Применяет к кнопкам по их текущему состоянию.
Переделать все вызовы setStyleSheet(STYLE_*) на вызовы _apply_current_theme() — то есть, просто вызвать общий метод обновления вместо прямого применения стиля. Но тогда логика setEnabled(True/False) тоже должна быть внутри метода.
Вызвать _apply_current_theme() из _update_buttons().
Из themes.apply_theme() дёрнуть все top-level окна и вызвать у них _apply_current_theme(), если такой метод есть.
Это перепишет _update_buttons полностью. Мне нужно её увидеть целиком.
Хорошо, давай в этом сообщении:
Сделаем фикс sync.py (это просто).
Попросим пользователя показать первые 100 строк main.py и метод _update_buttons целиком.
Или ещё проще — показать ключевые куски. Уже видели:
строки 84-96 (создание кнопок с inline)
строки 240-256 (логика _update_buttons в кусках)
строки 134-137 (lbl_session_clock с inline)
Нам нужны:
Строки 1-30 (импорты + STYLE_*)
Строки 130-160 (панель целиком)
Строки 230-280 (_update_buttons или _on_start_work/_on_stop_work целиком)
Давай так: сначала sync.py фикс — быстро. Потом диагностика main.py — с прицелом на следующие патчи.
Про заголовок окна (title bar):
Пользователь заметил, что в тёмной теме остаётся белая шапка. Это Windows. Решается через DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ...). Можно сделать через ctypes. Это не QSS, а WinAPI.
Давай сделаем это отдельным небольшим скриптом — добавлю в themes.py функцию enable_dark_titlebar(widget) для Windows, и вызову из MainWindow.__init__ и при смене темы.
Ок, план такой:
Скрипт 1: Фикс sync.py — добавить from datetime import datetime, timezone + почистить крокозябры.
Скрипт 2: Диагностика main.py (строки 1-30, 80-160, 230-290).
Скрипт 3: Обновить themes.py — добавить:
функцию enable_dark_titlebar(widget) для Windows
функцию apply_theme — вызывать refresh top-level windows
Потом следующим сообщением — патчи main.py.
Давай так.
________________________________________
Также замечу: в sync.py есть комментарий с крокозябрами:
text
connected = pyqtSignal()      # СЃРµСЂРІРµСЂ РґРѕСЃС‚СѓРїРµРЅ (РґР»СЏ UI: "вњ“ РѕРЅР»Р°Р№РЅ")
Это тот же баг кодировки при копипасте. Мы это уже видели в users.html/logins.html. Почищу в патче.
Начинаю писать ответ. Порядок:
Разбор что вижу
Скрипт 1: фикс sync.py
Скрипт 2: диагностика main.py
План: что дальше
Не буду торопиться с патчем main.py — сначала увижу код.
Отлично, картина ясна. Разбираю.
Что вижу:
main.py кнопки — inline-стили (setStyleSheet) применяются дважды: при создании (строки 85–96) и при каждом обновлении статуса через STYLE_GREEN, STYLE_RED, STYLE_DISABLED, STYLE_RESUME (строки 240–256). Значит, надо править обе точки.
main.py панель — objectName="infoPanel" уже стоит ? (наш первый патч сработал).
main.py lbl_session_clock — inline-стиль font-weight:bold; color:#28a745; (строки 135–137). В тёмной теме останется зелёным, но на тёмном фоне это может быть нормально — но всё же лучше через QSS.
sync.py баг — где-то в _sync_sessions вызывается datetime.fromisoformat(...), но datetime не импортирован. Импорты в начале файла: json, logging, threading, PyQt6, tenacity, .crypto/db/http_client/reminder_settings, .config, .registration. Нет datetime — вот откуда name 'datetime' is not defined.
sync.py крокозябры — комментарий к connected = pyqtSignal() испорчен (СЃРµСЂРІРµСЂ РґРѕСЃС‚СѓРїРµРЅ). Нужно починить.
Работаем так: сначала фикс sync.py (просто и быстро), потом диагностика main.py, потом массовый патч.
________________________________________
Скрипт 1 — Фикс sync.py
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\sync.py"

with open(PATH, encoding="utf-8") as f:
    content = f.read()

# ---------- 1. Добавляем datetime в импорты ----------
if "from datetime import datetime" in content:
    print("SKIP: datetime уже импортирован")
else:
    old = "import json\nimport logging\nimport threading\n"
    new = ("import json\nimport logging\nimport threading\n"
           "from datetime import datetime, timezone\n")
    if old in content:
        content = content.replace(old, new, 1)
        print("OK: datetime/timezone добавлены в импорты")
    else:
        print("ERROR: не найдены импорты в начале sync.py")
        raise SystemExit(1)

# ---------- 2. Чистим крокозябры в комментарии к connected ----------
# Ищем проблемный comment и заменяем
import re
old_comment_pat = re.compile(
    r'(connected = pyqtSignal\(\)\s*#[^\n]*)\n'
)
def fix_comment(m):
    line = m.group(1)
    return 'connected = pyqtSignal()   # сервер доступен (для UI: "? онлайн")\n'

new_content, n = old_comment_pat.subn(fix_comment, content, count=1)
if n > 0:
    content = new_content
    print("OK: комментарий к connected почищен")
else:
    print("SKIP: comment к connected не найден (возможно уже чистый)")

# ---------- 3. Проверим синтаксис ----------
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

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

# Добавляем QObject-обёртку с сигналом после SUPPORTED_THEMES
old_marker = '''SUPPORTED_THEMES = [
    {"code": "light"},
    {"code": "dark"},
    {"code": "system"},
]
'''

new_block = '''SUPPORTED_THEMES = [
    {"code": "light"},
    {"code": "dark"},
    {"code": "system"},
]


# ============================================================
# Глобальный сигнал смены темы
# ============================================================
# Любое окно может подписаться:
#   from .themes import theme_signals
#   theme_signals.theme_changed.connect(self._on_theme_changed)
#
# Или вызвать вручную:
#   theme_signals.theme_changed.emit("dark")
# ============================================================
from PyQt6.QtCore import QObject, pyqtSignal


class _ThemeSignals(QObject):
    theme_changed = pyqtSignal(str)  # передаёт код темы: "light" / "dark" / "system"


theme_signals = _ThemeSignals()
'''

if old_marker in content:
    content = content.replace(old_marker, new_block, 1)
    print("OK: добавлен глобальный сигнал theme_signals")
else:
    print("ERROR: не найден SUPPORTED_THEMES")
    raise SystemExit(1)

