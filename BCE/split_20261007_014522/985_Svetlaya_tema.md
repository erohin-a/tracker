<!-- Часть 985 из 1409 -->
# Светлая тема
*Хлебные крошки:* Светлая тема

[◀ Сначала посмотрим текущее содержимое (в каком месте падает)](984_Snachala_posmotrim_tekuschee_soderzhimoe_v_kakom_meste_padaet.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](986_part.md)

---

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
