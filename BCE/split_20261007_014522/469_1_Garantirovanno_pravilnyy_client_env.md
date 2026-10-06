<!-- Часть 469 из 1409 -->
# --- 1. Гарантированно правильный client/.env ---
*Хлебные крошки:* --- 1. Гарантированно правильный client/.env ---

[◀ Берём UID активного ПК прямо из БД](468_Berem_UID_aktivnogo_PK_pryamo_iz_BD.md) | [Оглавление](00_BCE_INDEX.md) | [--- 2. Патчим config.py: дефолт = 127.0.0.1 --- ▶](470_2_Patchim_config_py_defolt_127_0_0_1.md)

---

# --- 1. Гарантированно правильный client/.env ---
$envContent = @'
TRACKER_SERVER_URL=https://127.0.0.1
TRACKER_PIN=
TRACKER_VERSION=1.0.0
'@
[System.IO.File]::WriteAllText("$clientDir\.env", $envContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client\.env" -ForegroundColor Green

