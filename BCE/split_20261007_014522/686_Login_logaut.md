<!-- Часть 686 из 1409 -->
# Логин / логаут"
*Хлебные крошки:* Логин / логаут"

[◀ ============================================================](685_part.md) | [Оглавление](00_BCE_INDEX.md) | [Логин / логаут" ▶](687_Login_logaut.md)

---

# Логин / логаут"
This is a double-quoted string spanning multiple lines. In PowerShell, double-quoted strings can span lines, so that should be fine. But it could cause issues if the multi-line string isn't handled the way I expect.
Actually, let me look at the actual issue. The user just says "выключается" (turns off/closes). This is very vague. Let me:
First ask what exactly they see before it closes (any error message?)
Suggest they run it in a way that keeps the window open
Give a more robust approach - split into smaller scripts or write to file first
Actually, the simplest explanation: the user is running a .ps1 file with double-click, and the script completes normally (maybe with error) but the window closes immediately so they can't see anything.
Best approach: rewrite E2 as multiple smaller scripts, each with pause at the end. Or give instructions to capture output to a file.
Let me also reconsider - there may be a syntax problem. One issue I see:
powershell
$anchor = "# ============================================================
