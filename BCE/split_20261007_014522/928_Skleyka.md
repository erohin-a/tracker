<!-- Часть 928 из 1409 -->
# Склейка
*Хлебные крошки:* Склейка

[◀ Проверяем наличие ключевых функций](927_Proveryaem_nalichie_klyuchevyh_funktsiy.md) | [Оглавление](00_BCE_INDEX.md) | [...docstring... ▶](929_docstring.md)

---

# Склейка
Get-Content "D:\tracker\client\_sd_part1.tmp" -Raw -Encoding UTF8 | Set-Content ...
Хм, проще через .NET:
powershell
$full = [System.IO.File]::ReadAllText("...part1.tmp") + [System.IO.File]::ReadAllText("...part2.tmp") + [System.IO.File]::ReadAllText("...part3.tmp")
[System.IO.File]::WriteAllText("D:\tracker\client\settings_dialog.py", $full, [System.Text.UTF8Encoding]::new($false))
Remove-Item ...part*.tmp
Это надёжно. Каждая часть — до 200 строк here-string, что должно пройти.
Действуем. Разобью новую settings_dialog.py на 3 части:
Часть 1: заголовок + импорты + ReminderTab (с i18n и тултипами)
Часть 2: GeneralTab (тема, язык, автозапуск, уведомления, адрес сервера)
Часть 3: RegistrationTab (переписан: адрес, отпечаток, токен, проверка) + SettingsDialog
Затем main.py патч.
По main.py — надо применить тему и язык при старте. Это делается в main() перед созданием QApplication или сразу после. Также нужно подписаться на сохранение настроек — сейчас SettingsDialog закрывается, надо чтобы изменения применились. Вариант: после закрытия диалога перечитать config.json и применить тему/язык. Если язык изменился — предложить перезапуск.
Начнём.
Пишу код для всех трёх частей.
Часть 1 — заголовок + ReminderTab:
python
