<!-- Часть 182 из 1409 -->
# ---------------- web_admin.py ----------------
*Хлебные крошки:* ---------------- web_admin.py ----------------

[◀ ---------------- config.py ----------------](181_config_py.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](183_part.md)

---

# ---------------- web_admin.py ----------------
$web_admin_py = @'
...
'@
[System.IO.File]::WriteAllText("$serverDir\web_admin.py", $web_admin_py, [System.Text.UTF8Encoding]::new($false))

Write-Host "OK — server files written" -ForegroundColor Green
Now I need to be careful: inside the here-string for web_admin.py, does the content contain any line that starts with '@? Let me check... no.
Does it contain any line that is exactly the closing delimiter on its own? No.
OK let me write it all out.
Wait, there's a subtle issue with PowerShell here-strings. The closing '@ must be at the very start of a line (no leading whitespace). And the opening @' must also be at the end of a line, followed by a newline. Let me make sure to format them correctly.
Also, I realize a potential issue: [System.Text.UTF8Encoding]::new($false) — this creates UTF-8 without BOM. Good.
Let me now write everything out carefully.
One more check on the Python code — it needs to be exactly as I wrote before. Let me re-verify the key parts.
OK, going to write it now.
PowerShell-скрипты для безопасной перезаписи всех файлов
Разбил на 3 скрипта, чтобы ничего не потерялось. Запускать по очереди в PowerShell.
________________________________________
Скрипт 1 — серверные Python-файлы
Скопируйте весь блок в PowerShell, нажмите Enter.
powershell
$ErrorActionPreference = "Stop"

$serverDir = "D:\tracker\server"
$templatesDir = "D:\tracker\server\templates"
New-Item -ItemType Directory -Force -Path $serverDir | Out-Null
New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null

