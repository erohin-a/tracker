<!-- Часть 341 из 1409 -->
# --- Настройка idle-порога (получается с сервера) ---
*Хлебные крошки:* --- Настройка idle-порога (получается с сервера) ---

[◀ ============================================================](340_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](342_part.md)

---

# --- Настройка idle-порога (получается с сервера) ---

def get_idle_close_minutes(default: int = 30) -> int:
    val = get_meta("idle_close_minutes")
    if val:
        try:
            return max(5, min(480, int(val)))
        except (ValueError, TypeError):
            pass
    return default
'@
    $dbContent = $dbContent + $addition
    [System.IO.File]::WriteAllText($dbPath, $dbContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  get_idle_close_minutes добавлена" -ForegroundColor Green
}
python -c "import ast; ast.parse(open(r'$dbPath', encoding='utf-8').read()); print('  db.py SYNTAX OK')"

