<!-- Часть 227 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 1. Патч web_admin.py — добавляем фильтр dt](226_1_Patch_web_admin_py_dobavlyaem_filtr_dt.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](228_part.md)

---

# ============================================================
Write-Host "--- Патч web_admin.py ---" -ForegroundColor Cyan

$webAdminPath = "$serverDir\web_admin.py"
$content = [System.IO.File]::ReadAllText($webAdminPath, [System.Text.UTF8Encoding]::new($false))

$old = 'templates.env.filters["dur"] = _fmt_dur'

$new = @'
def _fmt_dt_global(dt):
    if dt is None:
        return "—"
    try:
        tz = ZoneInfo(settings.report_timezone)
    except Exception:
        tz = ZoneInfo("UTC")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")


templates.env.filters["dur"] = _fmt_dur
templates.env.filters["dt"] = _fmt_dt_global
'@

if ($content.Contains($new)) {
    Write-Host "  Уже пропатчен — пропускаем" -ForegroundColor Yellow
} elseif ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($webAdminPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  фильтр dt добавлен" -ForegroundColor Green
} else {
    Write-Host "  ОШИБКА: не найдена точка вставки!" -ForegroundColor Red
    Write-Host "  Возможно, web_admin.py не был обновлён. Перезапустите скрипт 1." -ForegroundColor Red
    exit 1
}

