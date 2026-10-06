<!-- Часть 729 из 1409 -->
# --- Сохраняем файл ---
*Хлебные крошки:* --- Сохраняем файл ---

[◀ ============================================================](728_part.md) | [Оглавление](00_BCE_INDEX.md) | [--- Проверка синтаксиса --- ▶](730_Proverka_sintaksisa.md)

---

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

