<!-- Часть 425 из 1409 -->
# --- 1. Обновляем client/.env ---
*Хлебные крошки:* --- 1. Обновляем client/.env ---

[◀ Чистим лог, чтобы видеть только свежее](424_Chistim_log_chtoby_videt_tolko_svezhee.md) | [Оглавление](00_BCE_INDEX.md) | [--- 2. Проверяем связь --- ▶](426_2_Proveryaem_svyaz.md)

---

# --- 1. Обновляем client/.env ---
$envPath = "D:\tracker\client\.env"

$newEnv = @'
TRACKER_SERVER_URL=https://127.0.0.1
TRACKER_PIN=
TRACKER_VERSION=1.0.0
'@

[System.IO.File]::WriteAllText($envPath, $newEnv, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/.env обновлён" -ForegroundColor Green
Get-Content $envPath

