<!-- Часть 337 из 1409 -->
# ---------- Version ----------
*Хлебные крошки:* ---------- Version ----------

[◀ ---------- Client config ----------](336_Client_config.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](338_part.md)

---

# ---------- Version ----------
'@

    if ($content.Contains("# ---------- Version ----------")) {
        $content = $content.Replace("# ---------- Version ----------", $endpoint)
        [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "  OK  /api/v1/client-config добавлен" -ForegroundColor Green
    } else {
        Write-Host "  ОШИБКА: не найден маркер '# ---------- Version ----------'" -ForegroundColor Red
    }
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"
________________________________________
Скрипт 4 — клиент: db.py + sync.py + main.py
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

