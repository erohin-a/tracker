<!-- Часть 481 из 1409 -->
# --- requirements.txt: добавить reportlab ---
*Хлебные крошки:* --- requirements.txt: добавить reportlab ---

[◀ Миграция БД](480_Migratsiya_BD.md) | [Оглавление](00_BCE_INDEX.md) | [--- Скачиваем DejaVuSans.ttf для PDF --- ▶](482_Skachivaem_DejaVuSans_ttf_dlya_PDF.md)

---

# --- requirements.txt: добавить reportlab ---
$reqPath = "$serverDir\requirements.txt"
$req = [System.IO.File]::ReadAllText($reqPath, [System.Text.UTF8Encoding]::new($false))

if ($req -notmatch "reportlab") {
    $req = $req.TrimEnd() + "`nreportlab==4.2.2`n"
    [System.IO.File]::WriteAllText($reqPath, $req, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  reportlab добавлен в requirements.txt" -ForegroundColor Green
} else {
    Write-Host "reportlab уже есть" -ForegroundColor Yellow
}

Get-Content $reqPath

