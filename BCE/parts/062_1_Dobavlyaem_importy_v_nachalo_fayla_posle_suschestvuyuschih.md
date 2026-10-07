# 1. Добавляем импорты в начало файла (после существующих)

*Часть 62 из 100. Источник: `BCE.md`.*

[◀ ...docstring...](061_docstring.md) | [Оглавление](00_BCE_INDEX.md) | [Очистим лог — будем смотреть только свежее ▶](063_Ochistim_log_budem_smotret_tolko_svezhee.md)

---

# 1. Добавляем импорты в начало файла (после существующих)
old_imports_marker = "from .updater import UpdateChecker, apply_update"
new_imports = (
    "from .updater import UpdateChecker, apply_update\n"
    "from . import themes\n"
    "from .i18n import set_language\n"
    "from .config import get_language_code, get_theme_code, get_setting, set_setting"
)

if "from . import themes" not in content:
    if old_imports_marker in content:
        content = content.replace(old_imports_marker, new_imports, 1)
        print("OK: добавлены импорты themes/i18n/config")
    else:
        print("ERROR: не найден маркер импортов updater")
        raise SystemExit(1)

# 2. Патчим функцию main() — применяем язык и тему до/после создания QApplication
old_main = '''def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)'''

new_main = '''def main():
    # --- Применяем сохранённый язык до создания любых виджетов ---
    try:
        set_language(get_language_code())
        log.info("Client language = %s", get_language_code())
    except Exception:
        log.exception("Failed to set language")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # --- Применяем сохранённую тему ---
    try:
        _theme = get_theme_code()
        themes.apply_theme(app, _theme)
        log.info("Client theme = %s", _theme)
    except Exception:
        log.exception("Failed to apply theme")

    # --- Сбрасываем флаг restart_required после перезапуска ---
    try:
        if get_setting("restart_required"):
            set_setting("restart_required", False)
            log.info("Restart flag cleared")
    except Exception:
        log.exception("Failed to clear restart flag")'''

if old_main in content:
    content = content.replace(old_main, new_main, 1)
    print("OK: main() пропатчен — тема и язык применяются")
else:
    print("ERROR: не найден блок 'def main()'")
    print("Проверьте вручную: ищите 'def main():' в client/main.py")
    raise SystemExit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_main_client.py", $patcher, [System.Text.UTF8Encoding]::new($false))

Write-Host "=== Запуск патчера main.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_main_client.py
Что ожидаем:
text
OK: добавлены импорты themes/i18n/config
OK: main() пропатчен — тема и язык применяются
SYNTAX OK
________________________________________
Скрипт 6 — Финальный тест
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
client\.venv\Scripts\Activate.ps1

# Проверка импортов всего клиента
python -c @"
from client import i18n, themes, config
from client.settings_dialog import SettingsDialog, ReminderTab, GeneralTab, RegistrationTab
from client import main as client_main

print('=== Все импорты OK ===')
print()

# Проверим i18n во всех ключах, которые использует settings_dialog
import re
with open(r'D:\tracker\client\settings_dialog.py', encoding='utf-8') as f:
    src = f.read()

keys = set(re.findall(r't\(["\']([a-z_]+\.[a-z_.0-9]+)["\']', src))
# Плюс ключи из f-строк
keys |= set(re.findall(r't\(f["\']([a-z_]+\.[a-z_.0-9.]+)', src))

print(f'Всего ключей i18n использовано в settings_dialog.py: {len(keys)}')
missing = [k for k in sorted(keys) if k not in i18n.TRANSLATIONS]
if missing:
    print('ОТСУТСТВУЮТ в TRANSLATIONS:')
    for k in missing:
        print(f'  {k}')
else:
    print('Все ключи найдены в TRANSLATIONS')
"@
Что ожидаем:
text
=== Все импорты OK ===

Всего ключей i18n использовано в settings_dialog.py: N
Все ключи найдены в TRANSLATIONS
________________________________________
Порядок запуска
Скрипт 1 — часть 1 (_sd_part1.tmp)
Скрипт 2 — часть 2 (_sd_part2.tmp)
Скрипт 3 — часть 3 (_sd_part3.tmp)
Скрипт 4 — склейка + проверка. Здесь важно увидеть SYNTAX OK и 8 строк OK:.
Скрипт 5 — патч main.py. Ожидаем 3 строки OK.
Скрипт 6 — финальная проверка. Ожидаем «Все ключи найдены в TRANSLATIONS».
Не запускай клиент до окончания всех 6 скриптов.
Если где-то будет SYNTAX ERROR — не иди дальше, пришли вывод конкретного скрипта, поправим точечно.
После успешного завершения — запустим клиент и проверим, что:
Открывается новый диалог настроек с 3 вкладками на русском
Тема переключается на «Тёмная» сразу, без перезапуска
Язык переключается на «English» с предложением перезапуска
«Проверить соединение» показывает версию сервера
OK: часть 1 записана (12509 символов) OK: часть 2 записана (10250 символов) OK: часть 3 записана (8681 символов) OK: settings_dialog.py собран (31440 символов) SYNTAX OK OK: class ReminderTab OK: class GeneralTab OK: class RegistrationTab OK: class SettingsDialog OK: get_server_url OK: get_cert_fingerprint OK: themes.apply_theme OK: SUPPORTED_LANGS >> & client\.venv\Scripts\python.exe _patch_main_client.py === Запуск патчера main.py === OK: добавлены импорты themes/i18n/config OK: main() пропатчен — тема и язык применяются SYNTAX OK File "<string>", line 15 keys |= set(re.findall(r't\(f[\']([a-z_]+\.[a-z_.0-9.]+)', ^ SyntaxError: '(' was never closed
The user has successfully completed all the scripts. The only error is in the final test script (Скрипт 6) — the Python verification command has a syntax error in my regex. It's my mistake, not theirs. The actual settings_dialog.py, main.py, i18n.py, themes.py, config.py are all fine.
The issue is in this line:
python
keys |= set(re.findall(r't\(f["\']([a-z_]+\.[a-z_.0-9.]+)', src))
The problem: inside a PowerShell here-string that's @'...'@ (single-quoted), the content is literal. But inside this Python code I'm using r't\(f["\'](...)' — the \' inside a Python raw string is problematic. Actually the issue is that in raw strings, \' still escapes the quote for parsing purposes but keeps the backslash.
Wait, actually the problem is more subtle. Let me look again:
python
keys |= set(re.findall(r't\(f["\']([a-z_]+\.[a-z_.0-9.]+)', src))
In a Python raw string r'...', a \' is technically valid but the backslash is kept as-is. But the parser needs to know when the string ends. Since we opened with ', the \' inside is an escaped quote, so it doesn't end the string. But then it says "was never closed" — that suggests something else.
Actually looking at the error:
text
File "<string>", line 15
    keys |= set(re.findall(r't\(f[\']([a-z_]+\.[a-z_.0-9.]+)',
                          ^
SyntaxError: '(' was never closed
The caret points to re.findall( — the ( was never closed. This means Python thinks the string isn't closed, so the ( is still inside the string.
Hmm. The issue is that this is embedded in a PowerShell here-string @"..."@ (double-quoted version, which allows variable interpolation). Wait, no, I used @"..."@ in the last test script? Let me re-check.
Looking back at my Скрипт 6:
powershell
python -c @"
...
keys |= set(re.findall(r't\(f["\']([a-z_]+\.[a-z_.0-9.]+)', src))
...
"@
Yes, it's @"..."@ (double-quoted PowerShell here-string). In double-quoted here-strings, " needs to be escaped. But \" inside @""@ — I don't think that's how it works. PowerShell double-quoted strings don't use \" for escaping.
Actually in PowerShell, you escape " by doubling it: "". So r't\(f["\'](...)' gets mangled because PowerShell interprets the " inside.
Also \$ isn't special in PowerShell, but the whole thing is problematic.
The FIX is simple: don't embed Python code that contains both " and ' inside a double-quoted PowerShell here-string. Use a Python script file instead, or use @'...'@ (single-quoted).
Let me write a small Python verification script to a file, then run it.
Now, what should I say to the user?
The user has done everything correctly. Only my test script has a bug. Let me:
Reassure them — everything works, this is just my regex bug
Give them a corrected verification script (via Python file, not inline)
Then let them launch the client and test
Also, I should be thinking about what's next:
Run the client to test
Check that new SettingsDialog works
Check theme switching
Check language switching
Maybe patch main.py to open new settings dialog if it references old one
Let me check — in main.py of client, is SettingsDialog imported? Probably. Also, does main.py have a "Настройки" button that opens it? Yes, per the file summary.
Let me write the response.
First, verification via Python file:
python
# check_i18n_keys.py
import sys
sys.path.insert(0, r'D:\tracker')

from client import i18n
import re

with open(r'D:\tracker\client\settings_dialog.py', encoding='utf-8') as f:
    src = f.read()

# t("...") — обычные
keys = set(re.findall(r"""t\(["']([a-z_]+\.[a-z_.0-9]+)["']""", src))
# t(f"...") — f-строки для general.theme.{code}
keys |= set(re.findall(r"""t\(f["']([a-z_]+\.[a-z_0-9.{}]+)""", src))

# Заменяем плейсхолдеры f-строк на реальные значения
resolved = set()
for k in keys:
    if '{' in k:
        # general.theme.{code}
        for code in ('light', 'dark', 'system'):
            resolved.add(k.replace('{code}', code))
        # general.lang.restart_text — уже конкретное
    else:
        resolved.add(k)

print(f'Всего ключей: {len(resolved)}')
missing = [k for k in sorted(resolved) if k not in i18n.TRANSLATIONS]
if missing:
    print('ОТСУТСТВУЮТ:')
    for k in missing:
        print(f'  {k}')
else:
    print('Все ключи найдены в TRANSLATIONS')
Actually, my original regex was overly complex. Let me simplify.
Now — what should happen next:
Run the client to test the new dialog
But wait — will the client use the new SettingsDialog? Need to check main.py to see where it's opened. The user's summary says:
Кнопка «? Настройки» в главном окне
So there's a button that opens SettingsDialog. If it imports from .settings_dialog import SettingsDialog — new dialog will be used automatically.
OK, I'll:
Fix the test script
Give user a script to launch and test
Have them report back what they see
Let me be concise. The user is probably tired after so many scripts.
Отлично, всё сработало! 8 из 8 маркеров OK, settings_dialog.py собран (31 КБ), main.py пропатчен.
Ошибка — в моём проверочном скрипте, не в твоём коде. Я неправильно экранировал кавычки внутри PowerShell @"..."@ — двойные кавычки в двойном here-string конфликтуют с Python-синтаксисом. Сам файл settings_dialog.py — рабочий (SYNTAX OK это подтвердил).
Исправляю проверку — через файл, чтобы не мучиться с экранированием.
________________________________________
Скрипт 6 (исправленный) — проверка ключей i18n
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$checker = @'
import sys
sys.path.insert(0, r'D:\tracker')
import re
from client import i18n

with open(r'D:\tracker\client\settings_dialog.py', encoding='utf-8') as f:
    src = f.read()

# t("key") и t('key')
pattern1 = re.compile(r'''\bt\(\s*["']([a-z_][a-z_.0-9]*)["']''')
keys = set(pattern1.findall(src))

# t(f"key.{var}") — f-строки
pattern2 = re.compile(r'''\bt\(\s*f["']([a-z_][a-z_.0-9]*\.)\{''')
for prefix in pattern2.findall(src):
    # prefix оканчивается точкой, ищем какому полю соответствует
    for suffix in ('light', 'dark', 'system'):
        keys.add(prefix + suffix)

print(f'Всего ключей найдено в settings_dialog.py: {len(keys)}')
missing = [k for k in sorted(keys) if k not in i18n.TRANSLATIONS]
if missing:
    print()
    print('ОТСУТСТВУЮТ в TRANSLATIONS:')
    for k in missing:
        print(f'  {k}')
    sys.exit(1)
else:
    print('Все ключи найдены в TRANSLATIONS')
    sys.exit(0)
'@

[System.IO.File]::WriteAllText("D:\tracker\_check_i18n_keys.py", $checker, [System.Text.UTF8Encoding]::new($false))

client\.venv\Scripts\Activate.ps1
& client\.venv\Scripts\python.exe _check_i18n_keys.py
Что ожидаем:
text
Всего ключей найдено в settings_dialog.py: 60 (примерно)
Все ключи найдены в TRANSLATIONS
Если увидишь ОТСУТСТВУЮТ — пришли мне список, добавлю их в i18n.py.
________________________________________
Скрипт 7 — запуск клиента и проверка
Закрой старый клиент (трей ? Выход). Затем:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker
client\.venv\Scripts\Activate.ps1

