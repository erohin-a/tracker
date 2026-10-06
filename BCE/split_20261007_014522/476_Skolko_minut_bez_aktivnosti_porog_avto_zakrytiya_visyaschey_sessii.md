<!-- Часть 476 из 1409 -->
# Сколько минут без активности — порог авто-закрытия висящей сессии
*Хлебные крошки:* Сколько минут без активности — порог авто-закрытия висящей сессии

[◀ Дефолт — 127.0.0.1, чтобы не упираться в IPv6-резолвинг localhost](475_Defolt_127_0_0_1_chtoby_ne_upiratsya_v_IPv6_rezolving_localhost.md) | [Оглавление](00_BCE_INDEX.md) | [Чистим лог, чтобы видеть только свежее ▶](477_Chistim_log_chtoby_videt_tolko_svezhee.md)

---

# Сколько минут без активности — порог авто-закрытия висящей сессии
IDLE_CLOSE_MINUTES = 30
'@
[System.IO.File]::WriteAllText($cfgPath, $config_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/config.py перезаписан" -ForegroundColor Green

python -c "import ast; ast.parse(open(r'$cfgPath', encoding='utf-8').read()); print('  SYNTAX OK')"

Write-Host "`n--- Что теперь читается из .env ---" -ForegroundColor Cyan
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -c @"
from client.config import SERVER_URL, BASE_DIR, _loaded_from if False else None
print('  SERVER_URL =', SERVER_URL)
print('  BASE_DIR   =', BASE_DIR)
"@
Ожидаемый вывод:
text
OK  client/config.py перезаписан
  SYNTAX OK

--- Что теперь читается из .env ---
  SERVER_URL = https://127.0.0.1
  BASE_DIR   = C:\Users\erohin\AppData\Roaming\Tracker
________________________________________
Перезапуск клиента
Закройте клиент (трей ? Выход). Затем:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

