<!-- Часть 728 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Логин / логаут](727_Login_logaut.md) | [Оглавление](00_BCE_INDEX.md) | [--- Сохраняем файл --- ▶](729_Sohranyaem_fayl.md)

---

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

