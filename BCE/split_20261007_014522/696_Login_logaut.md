<!-- Часть 696 из 1409 -->
# Логин / логаут"
*Хлебные крошки:* Логин / логаут"

[◀ в конце](695_v_kontse.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](697_part.md)

---

# Логин / логаут"
This creates a string with an embedded newline. When used with .Contains(), this should work IF the source file has exactly this text with this newline. But the file may have \n or \r\n line endings. If the file uses \r\n and my string in PowerShell has just \n, it won't match.
That's a real possible issue! On Windows, files written via [System.IO.File]::WriteAllText with default might use whatever... actually WriteAllText writes exactly what you give it, and my here-string in PowerShell preserves \r\n from the source if that's what PowerShell's here-strings produce.
Actually here-strings in PowerShell DO preserve the newline characters from the actual file content. If the user's PowerShell session interprets the paste with \n line endings... it gets complicated.
Simpler: use .Replace() where the anchor is just a single line + look for that. Or use two separate searches.
Actually, the safest thing is to make the anchor single-line:
powershell
$anchor = "# Логин / логаут"
Then replace from marker to end of file. But that's dangerous.
Alternatively, use regex. Or find the # --- Логин marker that's unique.
Or better: just append the set-lang endpoint at the very end of the file. Since it's a router endpoint, it will still work fine.
Hmm. Let me reconsider.
Looking at the actual file structure, I know that in web_admin.py there's a section "# Логин / логаут" with a specific structure. My script tries to insert before it. But if the anchor match fails, .Contains() returns false and my code says "маркер не найден" and exits. Not a crash.
Unless... exit 1 in PowerShell at top-level closes the window! YES. That's it.
If the script hits exit 1, PowerShell exits. When user is running from a .ps1 or an embedded context, that would close the shell.
So the issue is: my safety checks exit 1 close PowerShell.
Fix: replace all exit 1 with throw "..." or return (in script scope) or just log and continue.
Great, now I understand. Let me rewrite E2 with:
No exit statements
Error handling that logs but doesn't kill shell
Split into smaller parts
Each part clearly tells what succeeded
Let me write.
Диагностика: exit 1 в скрипте закрывает PowerShell
Нашёл причину. У меня в E2 было exit 1 в нескольких проверках — если какая-то проверка не находила блок (например, из-за \r\n vs \n при копипасте), скрипт делал exit 1. В PowerShell это закрывает оболочку целиком, если запущено не из интерактивной консоли, а из .ps1 или встроенного терминала.
Плюс есть вторая проблема: многострочный $anchor с # ============... может не совпасть из-за разных переносов строк.
Что делаю:
Убираю все exit. Вместо них — понятные сообщения об ошибке.
Разбиваю E2 на 4 маленьких скрипта — каждый самодостаточный, чтобы понять, где проблема.
Пишу короткий лог в файл, чтобы даже если окно закроется, остался след.
________________________________________
Что важно — как запускать
Запускай PowerShell не двойным кликом по .ps1, а через:
VS Code ? Terminal ? PowerShell, либо
Пуск ? PowerShell ? открыть, потом cd D:\tracker и вставить.
Так окно не закроется даже при ошибке.
________________________________________
Скрипт E2a — создаём server/web_i18n.py
Этот файл целиком новый, никаких Replace() — просто запись.
powershell
$ErrorActionPreference = "Continue"
$log = "D:\tracker\_e2a.log"
"=== E2a started $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8 -Force

$webI18n = @'
