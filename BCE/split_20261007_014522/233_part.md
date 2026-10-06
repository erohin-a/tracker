<!-- Часть 233 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 3. Проверка шаблонов](232_3_Proverka_shablonov.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](234_part.md)

---

# ============================================================
Write-Host "`n--- Проверка шаблонов ---" -ForegroundColor Cyan

$requiredTemplates = @(
    "base.html", "login.html", "dashboard.html", "employees.html",
    "computers.html", "tokens.html", "reports.html", "report_result.html",
    "audit.html"
)
$missing = @()
foreach ($t in $requiredTemplates) {
    $p = Join-Path $templatesDir $t
    if (Test-Path $p) {
        Write-Host ("  OK  {0}" -f $t) -ForegroundColor Green
    } else {
        Write-Host ("  MISSING  {0}" -f $t) -ForegroundColor Red
        $missing += $t
    }
}
if ($missing.Count -gt 0) {
    Write-Host "`n  Отсутствуют шаблоны: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "  Нужно создать их перед пересборкой." -ForegroundColor Red
}

