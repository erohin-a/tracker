<!-- Часть 344 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 2. sync.py — подтягиваем client-config раз в 10 циклов](343_2_sync_py_podtyagivaem_client_config_raz_v_10_tsiklov.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](345_part.md)

---

# ============================================================
Write-Host "`n--- sync.py ---" -ForegroundColor Cyan
$syncPath = "$clientDir\sync.py"
$syncContent = [System.IO.File]::ReadAllText($syncPath, [System.Text.UTF8Encoding]::new($false))

if ($syncContent.Contains("_fetch_client_config")) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} else {
    # 1) добавляем счётчик циклов в __init__
    $syncContent = $syncContent.Replace(
        "        self._running = False`n        self._wake = threading.Event()",
        "        self._running = False`n        self._wake = threading.Event()`n        self._cycles = 0"
    )

    # 2) добавляем вызов в run() перед wait
    $syncContent = $syncContent.Replace(
        "            # Спим SYNC_INTERVAL секунд, но можно разбудить через trigger()`n            self._wake.wait(timeout=SYNC_INTERVAL)",
        "            # Подтягиваем client-config раз в 10 циклов (примерно раз в 5 минут)`n            self._cycles += 1`n            if self._cycles % 10 == 1:`n                self._fetch_client_config()`n`n            # Спим SYNC_INTERVAL секунд, но можно разбудить через trigger()`n            self._wake.wait(timeout=SYNC_INTERVAL)"
    )

    # 3) добавляем метод _fetch_client_config перед _headers
    $method = @'
    def _fetch_client_config(self):
        """Забирает настройки с сервера (idle_close_minutes) и сохраняет в локальную БД."""
        try:
            r = http_client.get(f"{SERVER_URL}/api/v1/client-config",
                                headers=self._headers(), timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                idle = int(data.get("idle_close_minutes", 30))
                current = db.get_meta("idle_close_minutes")
                if str(idle) != current:
                    db.set_meta("idle_close_minutes", str(idle))
                    log.info("idle_close_minutes updated: %d", idle)
        except Exception as e:
            log.debug("client-config fetch failed: %s", e)

    def _headers(self):
'@
    $syncContent = $syncContent.Replace("    def _headers(self):", $method)

    [System.IO.File]::WriteAllText($syncPath, $syncContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  _fetch_client_config добавлена" -ForegroundColor Green
}
python -c "import ast; ast.parse(open(r'$syncPath', encoding='utf-8').read()); print('  sync.py SYNTAX OK')"

