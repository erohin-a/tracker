# ============================================================

*Часть 43 из 100. Источник: `BCE.md`.*

[◀ ============================================================](042_part.md) | [Оглавление](00_BCE_INDEX.md) | [--- Проверка синтаксиса --- ▶](044_Proverka_sintaksisa.md)

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
# ... script ...
Stop-Transcript
Then even if window closes, they can check the log.
Yes, that's the way. Let me do this.
Actually Start-Transcript can be finicky. Let me just use simple approach:
powershell
# В самом начале
$logPath = "D:\tracker\_i18n_e2a.log"
"=== E2a started $(Get-Date) ===" | Out-File $logPath -Encoding utf8

# ... operations ...
# в каждой точке 
"step1 OK" | Out-File $logPath -Append -Encoding utf8

# в конце
"=== E2a DONE $(Get-Date) ===" | Out-File $logPath -Append -Encoding utf8
OK let me write this.
Actually I think the most likely issue is simpler than I'm making it. Let me just:
Split into 4 scripts
Each ends with a clear marker line
Each is short
That should work. If any fails, user will still have a running window (since the failure happens early, before Set-Location or docker commands).
Let me write.
Wait, one more thought — the issue might be specifically with the $anchor variable. Let me look at it:
powershell
$anchor = "# ============================================================
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
# ============================================================
# Хук i18n для веб-интерфейса (связка i18n.py и Jinja2)
# ============================================================
# Зачем этот файл отдельно от i18n.py:
#   В i18n.py лежат переводы и функция t(key, lang). Она требует
#   явно указать язык.
#   В веб-интерфейсе язык берётся из cookie текущего запроса.
#   Чтобы не таскать язык явно в каждый вызов, используем
#   contextvars — это переменная, привязанная к текущему потоку.
#   Каждый HTTP-запрос обрабатывается в отдельной задаче, поэтому
#   язык, установленный для одного запроса, не влияет на другие.
#
# Как это работает:
#   1. При рендере шаблона context processor в web_admin.py читает
#      cookie "tracker_lang" и вызывает set_current_lang(lang).
#   2. В шаблоне работает функция `_("ключ")` — она берёт язык из
#      contextvars и передаёт в t().
# ============================================================

import contextvars
from typing import Optional

from .i18n import t, DEFAULT_LANG, is_valid_lang


# Текущий язык запроса. По умолчанию — русский.
_current_lang: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_lang", default=DEFAULT_LANG
)


def set_current_lang(lang: Optional[str]) -> str:
    """
    Устанавливает язык для текущего запроса.
    Если язык не поддерживается — ставит DEFAULT_LANG.
    Возвращает фактически установленный код.
    """
    if not lang or not is_valid_lang(lang):
        lang = DEFAULT_LANG
    _current_lang.set(lang)
    return lang


def get_current_lang() -> str:
    """Возвращает язык текущего запроса."""
    return _current_lang.get()


def _(key: str) -> str:
    """
    Короткая обёртка для использования в шаблонах и коде.
    Пример: _("menu.employees") -> "Сотрудники" или "Employees".
    """
    return t(key, _current_lang.get())
'@

try {
    [System.IO.File]::WriteAllText("D:\tracker\server\web_i18n.py", $webI18n, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: server/web_i18n.py создан" -ForegroundColor Green
    "OK: web_i18n.py written" | Out-File $log -Append -Encoding utf8
} catch {
    Write-Host "ОШИБКА при записи web_i18n.py: $_" -ForegroundColor Red
    "ERROR: $_" | Out-File $log -Append -Encoding utf8
}

# Проверка синтаксиса
try {
    python -c "import ast; ast.parse(open(r'D:\tracker\server\web_i18n.py', encoding='utf-8').read()); print('SYNTAX OK')"
} catch {
    Write-Host "Не удалось проверить синтаксис: $_" -ForegroundColor Yellow
}

"=== E2a DONE $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Host "`n=== E2a завершён. Лог: $log ===" -ForegroundColor Cyan
Ожидаемый вывод:
text
OK: server/web_i18n.py создан
SYNTAX OK

=== E2a завершён. Лог: D:\tracker\_e2a.log ===
________________________________________
Скрипт E2b — патчим web_admin.py
Тут три патча: импорты, регистрация _() + context processor, endpoint для смены языка. Все exit 1 убраны. Если что-то не найдётся — просто сообщение, скрипт идёт дальше.
powershell
$ErrorActionPreference = "Continue"
$log = "D:\tracker\_e2b.log"
"=== E2b started $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8 -Force

$path = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))
$changed = $false

# --- Патч 1: импорты ---
if ($content -match "from \.web_i18n import") {
    Write-Host "Патч 1: импорты i18n уже есть" -ForegroundColor Yellow
    "step1: already patched" | Out-File $log -Append -Encoding utf8
} else {
    $old = "from .config import settings"
    $new = @'
from .config import settings
from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang
from .web_i18n import _, set_current_lang, get_current_lang
'@
    if ($content.Contains($old)) {
        $content = $content.Replace($old, $new)
        Write-Host "Патч 1: OK — импорты добавлены" -ForegroundColor Green
        "step1: imports added" | Out-File $log -Append -Encoding utf8
        $changed = $true
    } else {
        Write-Host "Патч 1: НЕ НАЙДЕН 'from .config import settings'" -ForegroundColor Red
        "step1: FAILED" | Out-File $log -Append -Encoding utf8
    }
}

# --- Патч 2: регистрация _() и context processor ---
if ($content -match "templates\.context_processors\.append") {
    Write-Host "Патч 2: _() и context processor уже зарегистрированы" -ForegroundColor Yellow
    "step2: already patched" | Out-File $log -Append -Encoding utf8
} else {
    # Используем простые однострочные маркеры (без переносов)
    $oldFilter = 'templates.env.filters["dt"] = _fmt_dt_global'
    if ($content.Contains($oldFilter)) {
        $addition = @'

# ------------------------------------------------------------
# i18n: регистрируем функцию перевода _() в Jinja2.
# Теперь в любом шаблоне работает {{ _("ключ") }}.
# ------------------------------------------------------------
templates.env.globals["_"] = _


def _i18n_context_processor(request):
    """
    Context processor: перед рендером каждого шаблона
    читает cookie "tracker_lang", устанавливает язык
    в contextvars и добавляет в шаблон переменные
    current_lang и supported_langs (для переключателя).
    """
    lang = request.cookies.get("tracker_lang") or DEFAULT_LANG
    lang = set_current_lang(lang)
    return {
        "current_lang": lang,
        "supported_langs": SUPPORTED_LANGS,
    }

templates.context_processors.append(_i18n_context_processor)
'@
        $content = $content.Replace($oldFilter, $oldFilter + $addition)
        Write-Host "Патч 2: OK — _() и context processor зарегистрированы" -ForegroundColor Green
        "step2: filters+context_processor added" | Out-File $log -Append -Encoding utf8
        $changed = $true
    } else {
        Write-Host "Патч 2: НЕ НАЙДЕН маркер '_fmt_dt_global'" -ForegroundColor Red
        Write-Host "   Проверьте: docker compose exec api grep -n 'templates.env.filters' /app/server/web_admin.py" -ForegroundColor Yellow
        "step2: FAILED - no marker" | Out-File $log -Append -Encoding utf8
    }
}

# --- Патч 3: endpoint /admin/set-lang/{code} ---
if ($content -match "/set-lang/") {
    Write-Host "Патч 3: endpoint /set-lang/ уже есть" -ForegroundColor Yellow
    "step3: already patched" | Out-File $log -Append -Encoding utf8
} else {
    # Простой однострочный маркер
    $oldMarker = '# Логин / логаут'
    if ($content.Contains($oldMarker)) {
        # Вставляем НАД маркером — заменяем его на [блок нового кода] + [маркер]
        $setLangBlock = @'
# ============================================================
# Переключение языка интерфейса
# ============================================================
@router.get("/set-lang/{code}")
def set_lang(code: str, request: Request):
    """
    Устанавливает язык админки через cookie.
    После переключения возвращает пользователя на ту же страницу.
    """
    from fastapi.responses import RedirectResponse as _RR
    if not is_valid_lang(code):
        code = DEFAULT_LANG
    next_url = request.query_params.get("next") or "/admin"
    if not next_url.startswith("/"):
        next_url = "/admin"
    resp = _RR(next_url, status_code=303)
    resp.set_cookie(
        "tracker_lang", code,
        max_age=365 * 24 * 3600,
        path="/",
        samesite="lax",
    )
    return resp


# ============================================================
# Логин / логаут
# ============================================================
'@
        $content = $content.Replace($oldMarker, $setLangBlock.TrimEnd())
        Write-Host "Патч 3: OK — endpoint /set-lang/ добавлен" -ForegroundColor Green
        "step3: set-lang endpoint added" | Out-File $log -Append -Encoding utf8
        $changed = $true
    } else {
        Write-Host "Патч 3: НЕ НАЙДЕН маркер '# Логин / логаут'" -ForegroundColor Red
        Write-Host "   Проверьте: docker compose exec api grep -n 'Логин' /app/server/web_admin.py" -ForegroundColor Yellow
        "step3: FAILED - no marker" | Out-File $log -Append -Encoding utf8
    }
}

# --- Сохраняем файл ---
if ($changed) {
    try {
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "`nOK: web_admin.py сохранён" -ForegroundColor Green
        "saved: web_admin.py" | Out-File $log -Append -Encoding utf8
    } catch {
        Write-Host "ОШИБКА сохранения: $_" -ForegroundColor Red
        "ERROR saving: $_" | Out-File $log -Append -Encoding utf8
    }
} else {
    Write-Host "`nФайл не изменён (все патчи уже применены или не найдены)" -ForegroundColor Yellow
}

