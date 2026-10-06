<!-- Часть 276 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Патч db.py — добавляем auto_close_idle_session](275_Patch_db_py_dobavlyaem_auto_close_idle_session.md) | [Оглавление](00_BCE_INDEX.md) | [Проверяем, есть ли уже функция ▶](277_Proveryaem_est_li_uzhe_funktsiya.md)

---

# ============================================================
Write-Host "--- Патч db.py ---" -ForegroundColor Cyan

$dbPath = "$clientDir\db.py"
$dbContent = [System.IO.File]::ReadAllText($dbPath, [System.Text.UTF8Encoding]::new($false))

