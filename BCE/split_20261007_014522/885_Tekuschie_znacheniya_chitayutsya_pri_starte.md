<!-- Часть 885 из 1409 -->
# Текущие значения (читаются при старте)
*Хлебные крошки:* Текущие значения (читаются при старте)

[◀ Settings dialog with 3 tabs: reminder, general, registration](884_Settings_dialog_with_3_tabs_reminder_general_registration.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](886_part.md)

---

# Текущие значения (читаются при старте)
LANGUAGE = get_setting("language", "ru")
THEME = get_setting("theme", "light")
Actually, LANGUAGE/THEME at module level won't update. Let me just expose the functions.
OK writing now.
Let me be practical about the response length. The chat is getting long. Let me focus and deliver.
Response structure:
Привет! Вижу контекст. Начинаем Спринт A.
Что делаем сейчас (3 файла):
client/i18n.py — новая инфраструктура переводов
client/themes.py — QSS-темы
client/config.py — добавим функции для работы с config.json
Потом (следующее сообщение):
settings_dialog.py — переписываем с новыми полями
main.py — применяем тему/язык при старте
Script 1: client/i18n.py
Script 2: client/themes.py
Script 3: config.py patch
Test
Let me write.
Also, user emphasized tooltips. Let me add tooltips to key elements.
For i18n keys with hints, add .hint suffix.
OK, writing now. Let me be decisive.
Final decision: I'll write with here-strings, no longer than ~120 lines each. Should work.
For i18n.py, let me use compact format with comments. ~110 lines.
For themes.py, ~60 lines.
For config.py, use Python patcher (small).
Let me write.
Отлично, файлы получил. Разбираю.
Что вижу в settings_dialog.py:
Вкладка «Напоминание» — полностью функциональная, останется как есть + i18n
Вкладка «Общие» — есть автозапуск, но тема/язык — заглушки («скоро»). Надо реализовать.
Вкладка «Регистрация» — показывает UID/hostname/server + перерегистрация. Надо расширить полями URL, отпечатка сертификата, bootstrap-токена и кнопкой «Проверить соединение».
Что вижу в config.py:
Читает .env, дефолты хорошие, но нет сохранения настроек (язык/тема сохранятся только в config.json вручную).
План на этот чат (Спринт A):
client/i18n.py — инфраструктура переводов RU/EN
client/themes.py — QSS-темы (light/dark/system)
Патч config.py — функции get_setting/set_setting
Переписать settings_dialog.py — новая вкладка «Общие» + расширенная «Регистрация» + i18n + тултипы
Патч main.py — применяем тему/язык при старте
Тест
Учитывая твой опыт с большими here-string'ами в PowerShell, я разбиваю работу на две порции. В этой порции — три файла (i18n, themes, config), они небольшие. В следующей — settings_dialog.py (большой) и патч main.py.
________________________________________
Скрипт 1 — client/i18n.py
Помещаем в папку client/. Файл ~100 строк.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$content = @'
