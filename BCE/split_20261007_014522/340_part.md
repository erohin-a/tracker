<!-- Часть 340 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 1. db.py — добавляем get_idle_close_minutes](339_1_db_py_dobavlyaem_get_idle_close_minutes.md) | [Оглавление](00_BCE_INDEX.md) | [--- Настройка idle-порога (получается с сервера) --- ▶](341_Nastroyka_idle_poroga_poluchaetsya_s_servera.md)

---

# ============================================================
Write-Host "--- db.py ---" -ForegroundColor Cyan
$dbPath = "$clientDir\db.py"
$dbContent = [System.IO.File]::ReadAllText($dbPath, [System.Text.UTF8Encoding]::new($false))

if ($dbContent.Contains("def get_idle_close_minutes")) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} else {
    $addition = @'

