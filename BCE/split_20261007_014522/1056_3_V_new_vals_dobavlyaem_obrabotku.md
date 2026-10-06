<!-- Часть 1056 из 1409 -->
# 3. В new_vals добавляем обработку
*Хлебные крошки:* 3. В new_vals добавляем обработку

[◀ 2. В settings_save добавляем параметр](1055_2_V_settings_save_dobavlyaem_parametr.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка ▶](1057_Proverka.md)

---

# 3. В new_vals добавляем обработку
old_vals = '''        "end_of_day_hour": max(0, min(23, int(end_of_day_hour))),
        "end_of_day_minute": max(0, min(59, int(end_of_day_minute))),
    }'''

new_vals = '''        "end_of_day_hour": max(0, min(23, int(end_of_day_hour))),
        "end_of_day_minute": max(0, min(59, int(end_of_day_minute))),
        "stale_session_hours": max(1, min(24, int(stale_session_hours))),
    }'''

if old_vals in content:
    content = content.replace(old_vals, new_vals, 1)
    print("OK: обработка stale_session_hours в new_vals")
else:
    print("ERROR: не найден блок new_vals")
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

[System.IO.File]::WriteAllText("D:\tracker\_patch_settings_stale.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Патч настроек ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_settings_stale.py
Что ожидаем:
text
OK: stale_session_hours в settings_dict
OK: параметр stale_session_hours в settings_save
OK: обработка stale_session_hours в new_vals
SYNTAX OK
________________________________________
Шаг 5c — Патч шаблона settings.html
Добавляем поле на страницу /admin/settings. Найдём блок «Idle-порог» и вставим рядом.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$path = "D:\tracker\server\templates\settings.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("stale_session_hours")) {
    Write-Host "SKIP: поле уже есть" -ForegroundColor Yellow
} else {
    # Ищем блок Idle-порог и вставляем новую строку после него
    $oldBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
'@

    $newBlock = @'
                <div class="col-md-6">
                    <label class="form-label">
                        Idle-порог (авто-закрытие сессий)
                        <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени — клиент закроет сессию временем последней активности.">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="idle_close_minutes" class="form-control"
                               value="{{ cfg.idle_close_minutes }}" min="5" max="480">
                        <span class="input-group-text">минут</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">
                        Автозакрытие зависших сессий
                        <span class="hint" data-bs-toggle="tooltip" title="Если сессия висит без session_end дольше указанного времени — сервер закроет её временем последней активности. Защита от ситуации «сотрудник забыл нажать Конец работы, ПК выключили».">?</span>
                    </label>
                    <div class="input-group">
                        <input type="number" name="stale_session_hours" class="form-control"
                               value="{{ cfg.stale_session_hours }}" min="1" max="24">
                        <span class="input-group-text">часов</span>
                    </div>
                    <div class="form-text">По умолчанию 2 часа. Рекомендуется 1–3.</div>
                </div>
'@

    if ($content.Contains($oldBlock)) {
        $content = $content.Replace($oldBlock, $newBlock)
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "OK: поле stale_session_hours добавлено" -ForegroundColor Green
    } else {
        Write-Host "ERROR: не найден блок Idle-порог в settings.html" -ForegroundColor Red
        Write-Host "Откройте вручную и вставьте блок рядом с idle_close_minutes" -ForegroundColor Yellow
    }
}

