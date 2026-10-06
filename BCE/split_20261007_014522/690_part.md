<!-- Часть 690 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Логин / логаут](689_Login_logaut.md) | [Оглавление](00_BCE_INDEX.md) | [... script ... ▶](691_script.md)

---

# ============================================================
with trailing blank line. My anchor is missing the second # === line.
Hmm, but that would just fail with "не найден маркер", not close the window.
Let me think again about the most likely scenario:
The user is likely copy-pasting the whole script into PowerShell. If the paste is very long, PowerShell's terminal might have issues. Or if there's a character that breaks the paste.
Also, I wrote Set-Location D:\tracker at the end after a bunch of operations. If D:\tracker doesn't exist in current context or something...
Actually, I think the real issue might be simpler: the script has too many here-strings with complex content, and one of them has an issue that puts PowerShell into a "waiting for more input" state (like unclosed here-string), and then the user closes the window manually.
Let me restructure the approach:
Split E2 into multiple small scripts — each self-contained, each with a final Write-Host so user sees the result.
Write files using Set-Content with simpler logic where possible.
Avoid complex multi-line here-strings where I can — break into simpler pieces.
Actually, a much better approach for this specific case: since we're just appending small snippets and doing simple Replace() operations, let me:
Write each Python/HTML block to a temp file first, then move.
Or use base64 encoding — but that's overkill.
Best: split E2 into 4 sub-scripts, one per logical step. Each is small and safe.
Let me also consider: maybe the issue is that the user needs to be in the venv or NOT in the venv when running the script. And there might be a permission issue.
Let me just make it simpler and safer. Here's my plan:
E2a — create server/web_i18n.py (small, single here-string)
E2b — patch web_admin.py (imports + filters + context processor + set-lang endpoint)
E2c — patch base.html (navbar with language switcher)
E2d — rebuild and verify
Each script ends with a clear "OK" or "ERROR" message, so if PowerShell closes we know it either succeeded silently or...
Actually, wait. Let me re-read: "Windows PowerShell после Скрипт E2 выключается". Could mean:
(a) PowerShell window closes by itself after the script
(b) PowerShell closes and user sees nothing
For (a), that happens when running via .ps1 double-click. The solution is to run via terminal that stays open.
For (b), the script errors out somewhere and the window closes.
Either way, the fix is: capture output to a file so we can see what happened even if the window closes.
Let me give them a script that:
Redirects all output to a log file
Runs the E2 logic
At the end, prints "DONE" and asks for confirmation
Or even simpler: split into small scripts so they can identify which one fails.
Let me go with splitting + each script writes its own log.
Actually the cleanest: user runs each script from a persistent PowerShell window (not by double-clicking). Let me ask them:
Where are they running it? In VS Code terminal, PowerShell ISE, or via powershell -File?
But to keep momentum, let me just give a robust E2 that:
Writes everything to D:\tracker_i18n_setup.log
Uses try/catch
Explicitly catches errors and prints them
Let me write E2 as a single script but more robust.
Wait, actually I want to also consider: maybe the pasted script has some special characters that get lost in paste (like Unicode em-dash — or Cyrillic). Let me use ASCII-only where possible in script structure.
Also — Cyrillic in here-strings is fine but maybe a copy-paste issue. Let me test.
Actually the cleanest solution to prevent PowerShell from closing: at the very end of script, add:
text
Write-Host "`nГотово. Нажмите любую клавишу..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
But if user's actual issue is a syntax error, this wouldn't help.
Let me just split into small safe scripts. Small = less chance of paste issues.
Also, let me first ask a diagnostic question to understand better:
What exactly do they see? Empty window for a moment, then close?
Or nothing happens?
Or some error text flashes?
But the user may not know. So let me just give safe-split scripts.
Actually, I'll give a diagnostic + fixed E2. Let me write it.
The plan:
Ask them to run a very simple command first to test PowerShell works: Write-Host "test" and confirm they see output.
Then give E2 in 4 small pieces.
Each piece is written so that it can't hang or close the window.
Let me write this response.
Also I should not start with "here's E2 split" — should first check what's happening. Because if the window is closing on simple commands too, it's a different problem (maybe execution policy, maybe antivirus).
Let me structure:
Short diagnostic question
But also give safe E2 split, in case they just want to proceed
Actually, I'll just go straight to the split version with a "how to run safely" note. Add at end of each script a pause.
Let me write it.
For the pause — in PowerShell, Read-Host is cleanest:
text
Read-Host "`nНажмите Enter, чтобы закрыть окно"
But this would hang if running from IDE that doesn't send input. Hmm. Better:
text
Write-Host "`n=== Готово. Скрипт E2a завершён. ===" -ForegroundColor Green
If they're running in VS Code terminal or normal PowerShell window, they'll see it. If double-clicked, window will close but at least the operations succeeded.
Alternative: redirect to log:
text
Start-Transcript -Path "D:\tracker\_e2a.log" -Force
