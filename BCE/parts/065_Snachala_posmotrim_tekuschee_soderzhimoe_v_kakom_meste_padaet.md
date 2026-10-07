# Сначала посмотрим текущее содержимое (в каком месте падает)

*Часть 65 из 100. Источник: `BCE.md`.*

[◀ ---------- 1.4. Убираем методы _on_save_server и _on_check_connection из GeneralTab ----------](064_1_4_Ubiraem_metody_on_save_server_i_on_check_connection_iz_GeneralTab.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ключевых маркеров ▶](066_Proverka_klyuchevyh_markerov.md)

---

# Сначала посмотрим текущее содержимое (в каком месте падает)
Write-Host "=== Ищем проблемное место ===" -ForegroundColor Cyan
Select-String -Path "D:\tracker\client\sync.py" -Pattern "cap pause_sec|datetime" -Context 2,2

Write-Host "`n=== Импорты в sync.py ===" -ForegroundColor Cyan
Get-Content "D:\tracker\client\sync.py" | Select-Object -First 20
Запусти этот скрипт и пришли вывод. По нему я дам точечный патч — там просто нужно либо добавить глобальный from datetime import datetime, timezone, либо подправить локальный импорт внутри функции.
________________________________________
Порядок запуска
Скрипт 1 — убираем дубли + защита ?. Ожидаем 6 строк OK и SYNTAX OK.
Скрипт 2 — retranslate. Ожидаем 8 строк OK и SYNTAX OK.
Скрипт 3 — чистим inline-стили в main.py. Ожидаем 3 OK и SYNTAX OK.
Скрипт 4 — QSS. Ожидаем 5 маркеров OK.
Скрипт 5 — диагностика sync.py. Пришли вывод.
Не запускай клиент пока. После всех скриптов я дам финальный тест.
________________________________________
Что важно знать
Про title bar: цвет заголовка окна (то, что показывает «Tracker 1.0.0» и кнопки свернуть/закрыть) — это системный элемент Windows. Qt его перекрашивать не умеет без использования WinAPI DwmSetWindowAttribute. Сейчас его не трогаем — сделаем отдельно, если захочешь.
Про retranslate: теперь при смене языка в «Общих» все вкладки настроек мгновенно перерисуются на новый язык. Главное окно и трей — тоже нужно будет обновлять, но это следующий шаг.
Запускай скрипты 1–4 по порядку, присылай вывод. Пятый — просто диагностика, по нему я доработаю патч.
>> & client\.venv\Scripts\python.exe _patch_sd_cleanup.py OK: _hint защищена от пустых переводов OK: _label_with_hint не добавляет пустые иконки OK: секция Подключение убрана из Общих OK: методы _on_save_server / _on_check_connection убраны из GeneralTab OK: _load() больше не читает сервер/отпечаток OK: _wrap_row убран SYNTAX OK >> & client\.venv\Scripts\python.exe _patch_sd_retranslate.py OK: ReminderTab._retranslate добавлен OK: GeneralTab._retranslate добавлен OK: RegistrationTab._retranslate добавлен OK: SettingsDialog._on_language_changed добавлен OK: pyqtSignal импортирован OK: GeneralTab.language_changed сигнал добавлен OK: _on_lang_changed работает без перезапуска SYNTAX OK >> & client\.venv\Scripts\python.exe _patch_main_cleanup.py OK: inline-стиль панели убран SYNTAX OK >> & client\.venv\Scripts\python.exe _patch_themes.py File "D:\tracker\_patch_themes.py", line 75 marker = '"""\n\n\ndef apply_theme' ^ SyntaxError: unexpected character after line continuation character
Пользователь запустил скрипты 1, 2, 3 успешно. Скрипт 4 упал с ошибкой — проблема в моём Python-патчере: строка marker = '"""\n\n\ndef apply_theme' содержит \n\n\n внутри одинарных кавычек, но Python видит \n как литерал, а не как перенос — и всё ломается из-за \".
Проблема в том, что я использовал '"""\n\n\ndef apply_theme' — Python думает, что это тройные кавычки начинаются. Надо экранировать """ ? \"\"\" или использовать chr(34).
Также я вижу в скрипте 3 не сообщил про кнопки Старт/Стоп — их не нашёл. Посмотрю на вывод: OK только про панель, не про кнопки. Значит кнопки старт/стоп имеют другой inline-стиль, чем я предполагал. Нужно проверить.
Давай исправлю оба скрипта:
Скрипт 4 (themes.py) — проблема с тройными кавычками в Python-патчере. Перепишу через chr(34) или через другой паттерн.
Скрипт 3 (main.py) — кнопки Старт/Стоп не нашли. Надо посмотреть текущий вид этих кнопок в main.py, чтобы понять реальный inline-стиль.
Также я вижу, что скрипт 3 вывел только "OK: inline-стиль панели убран" и SYNTAX OK, но ничего про кнопки — значит кнопки старт/стоп не нашли. Надо диагностику.
Давай сделаю так:
Диагностика main.py — покажу реальный код кнопок старт/стоп и панели.
Патчер для themes.py — исправлю проблему с кавычками.
Диагностика sync.py — по cap pause_sec.
Структура ответа:
Разбор проблем
Скрипт 1: диагностика main.py (только вывод)
Скрипт 2: диагностика sync.py (только вывод)
Скрипт 3: исправленный патчер для themes.py
После этого дадут финальные патчи.
Про themes.py — важно! Файл сейчас в промежуточном состоянии: скрипт упал до записи, значит он НЕ изменён. Это хорошо. Надо переписать патчер аккуратно.
Дай сделаю через chr(34) для тройных кавычек или через склеивание строк.
Самый надёжный способ — использовать f-строку с тройными кавычками, но они будут конфликтовать с содержимым. Или использовать конкатенацию:
python
marker = chr(34) * 3 + "\n\n\ndef apply_theme"
Или проще — не искать """ в конце DARK_QSS, а искать def apply_theme. Дополнение вставляю ПЕРЕД def apply_theme, а закрывающие кавычки DARK_QSS уже стоят выше.
Смотрим структуру файла themes.py:
python
DARK_QSS = """
...
"""

def apply_theme(app, code: str) -> bool:
    ...
Значит, если я хочу дополнить DARK_QSS, надо вставить перед """ которое закрывает DARK_QSS. Оно идёт непосредственно ПЕРЕД def apply_theme (с парой переносов строк).
Мой патчер искал маркер '"""\n\n\ndef apply_theme'. Проблема в том, что в одинарных кавычках """ — это три двойные кавычки внутри одной строки. Python их должен принять без проблем... Но проблема в том, что за \n\n\n идёт def — нет, тут проблем быть не должно.
СТОП. Вижу ошибку: marker = '"""\n\n\ndef apply_theme' — тут '"""\n\n\ndef apply_theme'. Python видит \n как escape, это норм. Проблема в том, что PowerShell здесь-строка @'...'@ сохранила всё буквально, включая """.
А ошибка: SyntaxError: unexpected character after line continuation character на строке 75, колонка после '""". Это означает, что Python парсит """ как начало docstring, а не как строку! Потому что в контексте marker = '...' открывающая одинарная кавычка должна закрыть строку, но у меня '"""' — открывается ', потом """ (это часть строки), потом закрытие — но Python может видеть \"\"\" неправильно.
Хм. Точно, проблема в том, что \n\n\n в PowerShell here-string при передаче в Python-файл не преобразуется! То есть в файле написан буквально \n\n\n — и это правильно, потому что мы пишем Python-код. Но '"""\n\n\ndef apply_theme' в Python — открывается одинарная кавычка, идёт """, потом \n (escape), потом def apply_theme, потом закрывающая одинарная кавычка. Это должна быть валидная строка.
Но ошибка говорит: unexpected character after line continuation character. Это значит, что где-то есть \ за которым идёт символ, который Python не ожидает.
А! Я вижу проблему. В here-string @'...'@ в PowerShell одинарные кавычки literal, но обратный слэш \ — это literal backslash. То есть в Python-файл попадает буквально '"""\n\n\ndef apply_theme'. Python читает \n как newline escape, \n — newline, \n — newline, def apply_theme — текст, ' — закрытие строки. Это должно работать.
Хм, а почему ошибка? Может проблема в другом месте? Строка 75 — там где-то есть ещё что-то? Давай посмотрю на патчер:
python
marker = '"""\n\n\ndef apply_theme'
pos = content.find(marker)
Это должно быть валидно. Хм.
Стоп. А может проблема в том, что выше есть какой-то другой блок с """ который нарушает парсинг? Смотрю на патчер:
python
addition = '''
/* ---------- Главное окно ---------- */
QMainWindow { background-color: #2b2b2b; }
...
/* ---------- Светлый QSS-вариант тоже нужен ---------- */
'''

LIGHT_QSS = """
QFrame#infoPanel {
...
}
"""

"""
ВОТ ОНО! Я написал в патчере:
python
LIGHT_QSS = """
...
"""

"""
Тут """ после закрытия LIGHT_QSS = """...""" — это НАЧАЛО НОВОЙ тройной кавычки, которая не закрывается! Python парсит это как начало новой строки, и всё ломается.
Это моя ошибка в патчере. Надо убрать эти лишние """. LIGHT_QSS внутри основной строки addition — он должен быть как константа в файле themes.py. Но в патчере я его определил как Python-переменную, а не как текст для записи!
Правильный подход: всё содержимое должно быть внутри одного addition-стринга, тогда LIGHT_QSS = """...""" будет частью текста, а не Python-кодом.
Давай перепишу патчер правильно:
python
addition = '''
/* ... стили для тёмной темы ... */
"""

# Светлая тема
LIGHT_QSS = """
QFrame#infoPanel {
    background-color: #f8f9fa;
    ...
}
QPushButton#btnStart { ... }
QPushButton#btnStop { ... }
"""

'''
Но тут проблема: addition содержит """ внутри — он закроет addition. Нужно использовать другой delimiter или экранировать.
Решение: использовать '''...''' для addition, но тогда нельзя использовать ''' внутри. Или наоборот — использовать """...""" для addition.
Проблема в том, что в addition есть и """ (закрытие DARK_QSS и LIGHT_QSS = """...""").
Самое чистое: писать addition через escape-последовательности. Или использовать chr().
Или — что намного проще — писать патчер в несколько шагов с промежуточными файлами.
Или — ещё проще — писать файл themes.py целиком заново. Он небольшой (~150 строк). Так будет надёжнее.
Давай так:
Скрипт 1: показать текущие кнопки Старт/Стоп в main.py + cap pause_sec в sync.py + cap pause_sec datetime import
Скрипт 2: полная замена themes.py (пишем с нуля с учётом того что уже есть)
Всё. Начинаю.
Три скрипта прошли успешно, скрипт 4 упал по моей ошибке — я неправильно написал патчер (внутри Python-строки addition очутились три подряд двойные кавычки, которые Python попытался интерпретировать как начало новой строки).
Также вижу, что скрипт 3 нашёл только панель, но не нашёл кнопки Старт/Стоп. Значит, у них другой формат в main.py. Нужно посмотреть реальный код.
Давай так: сначала диагностика (посмотрим реальное состояние main.py и sync.py), потом правильный патч.
________________________________________
Скрипт 1 — диагностика main.py и sync.py
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== main.py: кнопки Старт и Стоп ===" -ForegroundColor Cyan
Select-String -Path "D:\tracker\client\main.py" -Pattern "btn_start|btn_stop" -Context 0,4 | Select-Object -First 20

Write-Host "`n=== main.py: панель (infoPanel) ===" -ForegroundColor Cyan
Select-String -Path "D:\tracker\client\main.py" -Pattern "infoPanel|QFrame" -Context 1,3 | Select-Object -First 10

Write-Host "`n=== main.py: лейбл статуса сервера ===" -ForegroundColor Cyan
Select-String -Path "D:\tracker\client\main.py" -Pattern "lbl_server|lbl_session_clock|lbl_pending" -Context 0,2 | Select-Object -First 15

Write-Host "`n=== sync.py: cap pause_sec ===" -ForegroundColor Cyan
Select-String -Path "D:\tracker\client\sync.py" -Pattern "cap pause_sec" -Context 8,8

Write-Host "`n=== sync.py: все импорты (первые 25 строк) ===" -ForegroundColor Cyan
Get-Content "D:\tracker\client\sync.py" | Select-Object -First 25
Пришли мне полный вывод. По нему я увижу:
Какие реально inline-стили у кнопок Старт/Стоп (возможно, они уже через setStyleSheet с другим синтаксисом, или уже без inline).
Где в sync.py падает datetime — какой импорт потерялся.
Какие объекты в панели нуждаются в цвете.
________________________________________
Что я уже знаю из логов
cap pause_sec failed: name 'datetime' is not defined — где-то в sync.py в функции _sync_sessions (или похожей) есть вызов datetime.now(), но модуль не импортирован глобально. Из лога видно:
text
2026-09-23 11:00:22,852 WARNING tracker.sync cap pause_sec failed: name 'datetime' is not defined
Функция работает, но какой-то cap pause_sec падает. То есть, скорее всего, там был локальный импорт from datetime import datetime, который потерялся при каком-то патче. Лечится добавлением глобального импорта в начале файла.
Про темы: сейчас в main.py панель имеет objectName="infoPanel", кнопки — вероятно, сохранили inline или тоже получили objectName в предыдущей версии. Посмотрю на диагностику.
________________________________________
Скрипт 2 — полностью переписываем themes.py
Раз патч через Python падает на кавычках — напишу файл целиком через PowerShell here-string (одинарные кавычки @'...'@, чтобы """ внутри были литеральными). Файл небольшой (~200 строк).
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$content = @'
# ============================================================
# Темы оформления клиента Tracker
# ============================================================
# Light  — светлая (QSS для кастомных элементов + системные)
# Dark   — тёмная (полный QSS)
# System — по умолчанию совпадает со светлой
#
# Применение:
#   from . import themes
#   themes.apply_theme(QApplication.instance(), "dark")
# ============================================================

import logging

log = logging.getLogger("tracker.themes")

SUPPORTED_THEMES = [
    {"code": "light"},
    {"code": "dark"},
    {"code": "system"},
]


# ============================================================
# Кастомные элементы: стили, общие для светлой и тёмной темы.
# Задаются через objectName у виджета.
# ============================================================

_CUSTOM_LIGHT = """
QFrame#infoPanel {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { color: #333333; background: transparent; }
QFrame#infoPanel QLabel[role="title"] { color: #6c757d; }

QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:pressed { background-color: #218838; }
QPushButton#btnStart:disabled { background-color: #c0c0c0; color: #888888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:pressed { background-color: #c82333; }
QPushButton#btnStop:disabled { background-color: #c0c0c0; color: #888888; }
"""

_CUSTOM_DARK = """
/* ---------- Главное окно ---------- */
QMainWindow { background-color: #2b2b2b; }
QMainWindow > QWidget { background-color: #2b2b2b; }
QDialog { background-color: #2b2b2b; }

QWidget { background-color: #2b2b2b; color: #e0e0e0; }
QLabel { color: #e0e0e0; background: transparent; }
QLabel[role="title"] { color: #a0a0a0; }

QPushButton {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555555; border-radius: 4px;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #4a4a4a; }
QPushButton:pressed { background-color: #555555; }
QPushButton:disabled { color: #777777; background-color: #333333; }

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
QPlainTextEdit, QTextEdit {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555555; border-radius: 4px;
    padding: 4px 6px;
}
QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {
    background-color: #333333; color: #777777;
}
QComboBox QAbstractItemView {
    background-color: #2b2b2b; color: #e0e0e0;
    selection-background-color: #4a4a4a;
    border: 1px solid #555555;
}

QCheckBox { color: #e0e0e0; background: transparent; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #666666; border-radius: 3px;
    background-color: #3c3c3c;
}
QCheckBox::indicator:checked {
    background-color: #4a90e2; border-color: #4a90e2;
}

QGroupBox {
    color: #e0e0e0;
    border: 1px solid #555555; border-radius: 4px;
    margin-top: 12px; padding-top: 10px;
}
QGroupBox::title {
    left: 10px; padding: 0 4px;
    background-color: #2b2b2b; color: #e0e0e0;
}

QTabWidget::pane { border: 1px solid #555555; background-color: #2b2b2b; }
QTabBar::tab {
    background-color: #3c3c3c; color: #e0e0e0;
    padding: 6px 14px; border: 1px solid #555555;
    border-bottom: none;
    border-top-left-radius: 4px; border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #2b2b2b; color: #ffffff;
    border-bottom: 1px solid #2b2b2b;
}
QTabBar::tab:hover:!selected { background-color: #4a4a4a; }

QMenu {
    background-color: #2b2b2b; color: #e0e0e0;
    border: 1px solid #555555;
}
QMenu::item { padding: 6px 20px; }
QMenu::item:selected { background-color: #4a4a4a; }

QToolTip {
    background-color: #3c3c3c; color: #e0e0e0;
    border: 1px solid #555555; padding: 4px 6px;
}

QMessageBox { background-color: #2b2b2b; }

QScrollBar:vertical {
    background-color: #2b2b2b; width: 12px;
    border: none; margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #555555; border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #666666; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0; background: none;
}
QScrollBar:horizontal {
    background-color: #2b2b2b; height: 12px;
    border: none; margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: #555555; border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background-color: #666666; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0; background: none;
}

/* ---------- Панель информации в главном окне ---------- */
QFrame#infoPanel {
    background-color: #3a3a3a;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { color: #e0e0e0; background: transparent; }
QFrame#infoPanel QLabel[role="title"] { color: #a0a0a0; }

/* ---------- Кнопки старт/стоп ---------- */
QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:pressed { background-color: #218838; }
QPushButton#btnStart:disabled { background-color: #404040; color: #888888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:pressed { background-color: #c82333; }
QPushButton#btnStop:disabled { background-color: #404040; color: #888888; }
"""


def apply_theme(app, code: str) -> bool:
    """
    Применяет тему к приложению.
    code: "light" | "dark" | "system"
    """
    if app is None:
        return False
    if code == "dark":
        app.setStyleSheet(_CUSTOM_DARK)
        log.info("Applied dark theme")
        return True
    elif code in ("light", "system", "", None):
        app.setStyleSheet(_CUSTOM_LIGHT)
        log.info("Applied %s theme", code or "light")
        return True
    else:
        log.warning("Unknown theme: %s, using light", code)
        app.setStyleSheet(_CUSTOM_LIGHT)
        return False


def is_valid_theme(code: str) -> bool:
    return code in [t["code"] for t in SUPPORTED_THEMES]
'@

[System.IO.File]::WriteAllText("D:\tracker\client\themes.py", $content, [System.Text.UTF8Encoding]::new($false))

Write-Host "OK: themes.py переписан ($($content.Length) символов)" -ForegroundColor Green

python -c "import ast; ast.parse(open(r'D:\tracker\client\themes.py', encoding='utf-8').read()); print('SYNTAX OK')"

