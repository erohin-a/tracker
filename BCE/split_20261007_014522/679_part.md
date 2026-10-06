<!-- Часть 679 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Логин / логаут](678_Login_logaut.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](680_part.md)

---

# ============================================================
'@
    if ($content.Contains($anchor)) {
        $content = $content.Replace($anchor, $setLangBlock.TrimEnd())
        Write-Host "OK: endpoint /admin/set-lang/{code} добавлен" -ForegroundColor Green
    } else {
        Write-Host "Не найден маркер 'Логин / логаут' — правьте вручную" -ForegroundColor Red
        exit 1
    }
}

[System.IO.File]::WriteAllText($webAdminPath, $content, [System.Text.UTF8Encoding]::new($false))
python -c "import ast; ast.parse(open(r'$webAdminPath', encoding='utf-8').read()); print('SYNTAX OK')"


