<!-- Часть 927 из 1409 -->
# Проверяем наличие ключевых функций
*Хлебные крошки:* Проверяем наличие ключевых функций

[◀ ============================================================](926_part.md) | [Оглавление](00_BCE_INDEX.md) | [Склейка ▶](928_Skleyka.md)

---

# Проверяем наличие ключевых функций
for name in ["load_config", "save_config", "get_setting", "set_setting",
             "get_server_url", "get_cert_fingerprint",
             "get_language_code", "get_theme_code"]:
    ok = f"def {name}" in content
    print(f" {'OK' if ok else 'MISS'}: {name}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_config.py", $patcher, [System.Text.UTF8Encoding]::new($false))

Write-Host "=== Запуск патчера ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_config.py
Что ожидаем:
text
OK: config.py дополнен функциями load/save/get/set
SYNTAX OK
 OK: load_config
 OK: save_config
 OK: get_setting
 OK: set_setting
 OK: get_server_url
 OK: get_cert_fingerprint
 OK: get_language_code
 OK: get_theme_code
________________________________________
Проверка, что всё связалось
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
from client import i18n, themes, config

print('=== i18n ===')
print('Язык сейчас:', i18n.get_language())
print('RU:', i18n.t('settings.title'))
i18n.set_language('en')
print('EN:', i18n.t('settings.title'))
i18n.set_language('ru')

print()
print('=== themes ===')
print('Темы:', [t['code'] for t in themes.SUPPORTED_THEMES])
print('Тёмная QSS:', len(themes.DARK_QSS), 'символов')

print()
print('=== config ===')
print('Текущий язык (из config):', config.get_language_code())
print('Текущая тема (из config):', config.get_theme_code())
print('URL сервера:', config.get_server_url())
print('Отпечаток:', config.get_cert_fingerprint() or '(не задан)')
"@
Что ожидаем:
text
=== i18n ===
Язык сейчас: ru
RU: Настройки Tracker
EN: Tracker Settings

=== themes ===
Темы: ['light', 'dark', 'system']
Тёмная QSS: 2847 символов

=== config ===
Текущий язык (из config): ru
Текущая тема (из config): light
URL сервера: https://127.0.0.1
Отпечаток: (не задан)
________________________________________
Что делаем дальше
Проверь эти 4 скрипта. Если всё чисто — пришли подтверждение, и в следующем сообщении я:
Полностью перепишу settings_dialog.py — новая вкладка «Общие» + расширенная «Регистрация» + i18n + тултипы на всех элементах
Патчну main.py — применение темы и языка при старте
Дам settings_dialog.py через Python-патчер (для обхода проблем с большими here-string'ами)
Если где-то SYNTAX ERROR или MISS — не иди дальше, пришли вывод, поправим точечно.
По твоему замечанию про подсказки: я везде добавляю ключи .hint для тултипов. В settings_dialog.py на каждой группе будет иконка ? или <span class="hint"> с title — чтобы новый пользователь сразу понимал, что за настройка.
OK: client/i18n.py создан SYNTAX OK OK: client/themes.py создан SYNTAX OK >> & client\.venv\Scripts\python.exe _patch_config.py === Запуск патчера === OK: config.py дополнен функциями load/save/get/set SYNTAX OK OK: load_config OK: save_config OK: get_setting OK: set_setting OK: get_server_url OK: get_cert_fingerprint OK: get_language_code OK: get_theme_code === i18n === Язык сейчас: ru RU: Настройки Tracker EN: Tracker Settings === themes === Темы: ['light', 'dark', 'system'] Тёмная QSS: 2907 символов === config === Текущий язык (из config): ru Текущая тема (из config): light URL сервера: https://127.0.0.1 Отпечаток: (не задан)
Отлично, все 4 скрипта прошли чисто. Теперь переходим к большому блоку — переписыванию settings_dialog.py и патчу main.py.
Ключевые задачи:
settings_dialog.py — полностью переписать:
Вкладка «Напоминание» — оставить логику, добавить i18n + тултипы
Вкладка «Общие» — тема (light/dark/system), язык (ru/en) с перезапуском, автозапуск, уведомления, адрес сервера + отпечаток + кнопка «Проверить соединение»
Вкладка «Регистрация» — расширить: URL сервера, отпечаток, bootstrap-токен, кнопка «Проверить соединение», оставить перерегистрацию
main.py патч — при старте применяем тему и язык из config.json.
Важно: файл settings_dialog.py получится большой (~600+ строк). По опыту пользователя с here-string'ами — надо использовать Python-патчер или разбить на несколько блоков.
Стратегия: используем Python-патчер, который пишет файл целиком через io.open с UTF-8. Это надёжнее всего. Патчер будет содержать полный текст нового settings_dialog.py в виде Python-строки.
Но это тоже большая Python-строка... Другой вариант — писать файл построчно через массив строк. Но проще всего — дать пользователю скрипт, который строит файл через массив строк в Python, затем записывает.
Или ещё проще: использовать подход @() массив строк в PowerShell + Out-File. Как они делали в конце — это работало.
Хм, но проблема в том, что в строках будут и " и ' и \ — экранирование сложное.
Самое надёжное — использовать Python-патчер, где строки кодируются через тройные кавычки. Но тогда внутри Python-строки не должно быть """.
Другой вариант — использовать base64. Это вообще надёжно, но громоздко.
Или — как раньше делал пользователь — здесь-строки в PowerShell с одинарными кавычками. Внутри — Python-код с двойными кавычками. Это работало.
Решу так: разобью на 3 скрипта по вкладкам + главный диалог. Каждый скрипт — небольшой here-string в PowerShell.
Скрипт A1: сначала создаём новый файл settings_dialog.py с частью 1 (импорты + ReminderTab)
Скрипт A2: добавляем GeneralTab через Python-патчер (append к файлу)
Скрипт A3: добавляем RegistrationTab + SettingsDialog через Python-патчер
Скрипт A4: патч main.py — применяем тему/язык при старте
Хм, но тогда получится несколько промежуточных состояний с неработающим файлом. Лучше сначала собрать полностью в памяти, потом записать.
Наилучший подход: используем Python-патчер, который строит файл из нескольких блоков (конкатенация строк). Каждый блок — тройные кавычки '''...''' в Python. Внутри Python-кода — не должно быть '''. А двойные кавычки — ок.
Проверю свой будущий settings_dialog.py — там будут docstring'и через """. Не '''. Значит тройные одинарные кавычки подойдут.
Но ещё проблема — PowerShell here-string для самого Python-патчера. Внутри Python-кода с '''...''' могут быть одинарные кавычки — они не поломают PowerShell here-string @'...'@, потому что там всё literal, но надо чтобы не было строки, начинающейся с '@.
ОК, попробую так. Пишу Python-патчер, содержащий в себе все три вкладки как тройные строки.
Другой подход — вообще не использовать Python-патчер, а использовать base64. Пользователь даёт команду:
powershell
$b64 = "....."  # длинная base64-строка
[System.IO.File]::WriteAllBytes("D:\tracker\client\settings_dialog.py", [Convert]::FromBase64String($b64))
Но мне нужно сгенерировать base64 из контента, а я не могу это сделать, потому что это текст на русском с разными кавычками.
Ладно, не буду изобретать. Давайте так:
Подход: разбить на 3 части через here-string, каждая часть пишется в отдельный .tmp файл, потом склеиваем.
powershell
$part1 = @'
...imports + ReminderTab...
'@
[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part1.tmp", $part1, [System.Text.UTF8Encoding]::new($false))

$part2 = @'
...GeneralTab...
'@
[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part2.tmp", $part2, [System.Text.UTF8Encoding]::new($false))

$part3 = @'
...RegistrationTab + SettingsDialog...
'@
[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part3.tmp", $part3, [System.Text.UTF8Encoding]::new($false))

