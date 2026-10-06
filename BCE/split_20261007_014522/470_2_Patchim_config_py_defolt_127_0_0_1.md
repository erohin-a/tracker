<!-- Часть 470 из 1409 -->
# --- 2. Патчим config.py: дефолт = 127.0.0.1 ---
*Хлебные крошки:* --- 2. Патчим config.py: дефолт = 127.0.0.1 ---

[◀ --- 1. Гарантированно правильный client/.env ---](469_1_Garantirovanno_pravilnyy_client_env.md) | [Оглавление](00_BCE_INDEX.md) | [--- 3. Патчим http_client.py: отключаем IPv6-предпочтение если нужно --- ▶](471_3_Patchim_http_client_py_otklyuchaem_IPv6_predpochtenie_esli_nuzhno.md)

---

# --- 2. Патчим config.py: дефолт = 127.0.0.1 ---
$cfgPath = "$clientDir\config.py"
$cfg = [System.IO.File]::ReadAllText($cfgPath, [System.Text.UTF8Encoding]::new($false))

$oldLine = 'SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://tracker.example.com")'
$newLine = 'SERVER_URL = os.environ.get("TRACKER_SERVER_URL", "https://127.0.0.1")'

if ($cfg.Contains($newLine)) {
    Write-Host "  config.py уже пропатчен" -ForegroundColor Yellow
} elseif ($cfg.Contains($oldLine)) {
    $cfg = $cfg.Replace($oldLine, $newLine)
    [System.IO.File]::WriteAllText($cfgPath, $cfg, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  дефолт SERVER_URL ? https://127.0.0.1" -ForegroundColor Green
} else {
    # Возможно уже другой дефолт — не трогаем, только предупредим
    Write-Host "  ВНИМАНИЕ: строка с дефолтом SERVER_URL не найдена. Проверьте вручную:" -ForegroundColor Yellow
    Select-String -Path $cfgPath -Pattern "SERVER_URL"
}

