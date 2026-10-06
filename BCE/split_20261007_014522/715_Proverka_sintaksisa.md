<!-- Часть 715 из 1409 -->
# Проверка синтаксиса
*Хлебные крошки:* Проверка синтаксиса

[◀ Текущий язык запроса. По умолчанию — русский.](714_Tekuschiy_yazyk_zaprosa_Po_umolchaniyu_russkiy.md) | [Оглавление](00_BCE_INDEX.md) | [--- Патч 1: импорты --- ▶](716_Patch_1_importy.md)

---

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

