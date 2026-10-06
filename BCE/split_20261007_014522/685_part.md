<!-- Часть 685 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 4. Пересборка](684_4_Peresborka.md) | [Оглавление](00_BCE_INDEX.md) | [Логин / логаут" ▶](686_Login_logaut.md)

---

# ============================================================
Set-Location D:\tracker
Write-Host "`n=== Пересборка API ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose ps
Write-Host "`n=== Логи API ===" -ForegroundColor Cyan
docker compose logs api --tail=20

Write-Host "`n=== Проверка ===" -ForegroundColor Green
Write-Host "Откройте https://localhost/admin" -ForegroundColor Green
Write-Host "В шапке справа — кнопки RU / EN." -ForegroundColor Green
Write-Host "Нажмите EN — меню должно переключиться на английский." -ForegroundColor Green
Write-Host "Обновите страницу — язык должен сохраниться (cookie)." -ForegroundColor Green
________________________________________
Что проверять после E2
Открой https://localhost/admin — должен увидеть шапку с пунктами меню на русском и кнопками RU | EN справа.
Нажми EN — меню переключится: «Employees», «Departments», «Computers», «Tokens», «Reports», «Settings», «Calendar», «Audit», «Logout».
Обнови страницу — язык сохранился (cookie tracker_lang=en).
Нажми RU — вернулось на русский.
Что ещё НЕ переведено (постепенно переведём в следующих шагах):
Содержимое страниц — заголовки внутри (<h3>Дашборд</h3> и т.п.).
Кнопки внутри форм («Сохранить», «Удалить»).
Тултипы (title="").
Сообщения в JS.
Это нормально — переводим инкрементально. Сейчас главное, чтобы инфраструктура работала и переключалась.
________________________________________
Если что-то пошло не так
Симптом: 500 при открытии /admin.
Причина: скорее всего, context processor не отработал.
Действия: пришли docker compose logs api --tail=40.
Симптом: шаблон падает с UndefinedError: '_' is undefined.
Причина: templates.env.globals["_"] = _ не зарегистрировалось.
Проверка: docker compose exec api grep -n "templates.env.globals" /app/server/web_admin.py.
Симптом: при клике на RU/EN ничего не меняется.
Причина: cookie не сохраняется (может быть из-за того, что next_url неправильный).
Проверка: в браузере DevTools ? Application ? Cookies ? должна быть tracker_lang.
________________________________________
Запускай E2, пришли результат. Если меню переключается — идём дальше: E3 (перевод содержимого страниц, инкрементально), потом E4–E5 (клиент), и возвращаемся к Alembic D2–D9.
Windows PowerShell после Скрипт E2 выключается
The user says PowerShell closes after running Script E2. This is a common issue - probably the script crashed somewhere and the window closed, or there's a syntax error causing the shell to terminate. Let me think about what could cause this.
Most likely cause: $ErrorActionPreference = "Stop" combined with something that fails, but that would just show an error and stop the script, not close the window.
Actually, thinking about it more - the user is running the script by copy-pasting into PowerShell. If the script contains something that terminates the shell (like exit command in the middle), or if there's a syntax error that causes the here-string to never close properly, the shell might hang waiting for input... but user says it closes.
Possible causes:
Here-string delimiter collision - one of my @' or '@ sequences might be malformed
Inside the here-string content, there might be a line that starts with '@ (closing delimiter), which would prematurely end the string
An issue with special characters
Let me look at my E2 script carefully:
In the set_lang_block here-string, I have:
text
    from fastapi.responses import RedirectResponse as _RR
    if not is_valid_lang(code):
        code = DEFAULT_LANG
Nothing unusual there.
In the base.html patch, I have:
text
    $oldNav = @'
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
...
'@
Wait - inside the $newNav block, I have Jinja template syntax like {% if ... %} and {{ ... }} - those are fine in a single-quoted here-string. But I have {@ ... @}? No, I don't think so.
Hmm, one issue: the @' should be at the END of a line followed by newline. In my PowerShell scripts, when I paste them into the response, formatting should preserve this. But if the user's copy-paste loses the trailing newlines, or if there's a line-break issue...
Actually, the more likely cause: the user copied the ENTIRE script and pasted it. If the paste happened too fast, or if there was a very long paste, the terminal might have buffered it incorrectly.
But user says "Windows PowerShell после Скрипт E2 выключается" - PowerShell closes after E2.
Wait - another likely cause. The docker compose down and docker compose up -d --build at the end. If Docker Desktop isn't running... no, that wouldn't close PowerShell.
Actually - thinking again - what if the user is running PowerShell in a way that it exits on any terminating error? Like powershell -Command "..." mode? Probably not.
Or maybe when the script finishes, the window auto-closes because the user launched it via double-click on a .ps1 file. In that case, the shell closes after the script ends. But user says after E2 specifically.
Hmm, most likely cause: there's a syntax error somewhere in my script that causes PowerShell to enter a waiting state, and the user pressed Ctrl+C or closed the window. Then when they said "it closes" they mean the previous session ended.
Or: one of the here-strings contains a line that is exactly '@ which ends it early. Let me check...
Looking at my $newNav block - no line is exactly '@.
Actually, wait. There might be an issue. In my PowerShell script I have:
powershell
$anchor = "# ============================================================
