<!-- Часть 92 из 1409 -->
# ?? Быстрый деплой с нуля
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Быстрый деплой с нуля

[◀ `certs/fullchain.pem` и `certs/privkey.pem`](091_certs_fullchain_pem_i_certs_privkey_pem.md) | [Оглавление](00_BCE_INDEX.md) | [? Итог ▶](093_Itog.md)

---

## ?? Быстрый деплой с нуля

```powershell
# 1. Создать структуру папок
mkdir D:\tracker\server, D:\tracker\client, D:\tracker\certs

# 2. Скопировать все файлы из этого документа

# 3. Сгенерировать .env
cd D:\tracker
python -c "from cryptography.fernet import Fernet; print('SECRET_ENCRYPTION_KEY=' + Fernet.generate_key().decode())" | Out-File -Append .env -Encoding ascii
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(48))" | Out-File -Append .env -Encoding ascii
python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(48))" | Out-File -Append .env -Encoding ascii

# 4. Создать сертификаты
cd D:\tracker\certs
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -x509 -newkey rsa:4096 `
    -keyout privkey.pem -out fullchain.pem -days 365 -nodes `
    -subj "/CN=localhost" `
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" `
    -addext "basicConstraints=critical,CA:TRUE"

# 5. Запустить сервер
cd D:\tracker
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose ps

# 6. Установить клиент
cd D:\tracker\client
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 7. Скопировать CA и настроить .env клиента
Copy-Item D:\tracker\certs\fullchain.pem "$env:APPDATA\Tracker\ca.pem"

# 8. Создать client\.env
@"
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
"@ | Out-File D:\tracker\client\.env -Encoding utf8

# 9. Получить bootstrap-токен
$adminKey = (Get-Content D:\tracker\.env | Select-String "ADMIN_API_KEY=").ToString().Replace("ADMIN_API_KEY=","").Trim()
$bodyObj = @{ ttl_hours = 24; issued_by = "admin" }
$bodyJson = $bodyObj | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText("$env:TEMP\boot.json", $bodyJson, [System.Text.UTF8Encoding]::new($false))
$resp = curl.exe -k -X POST "https://localhost/api/v1/admin/bootstrap-tokens" `
    -H "X-Admin-Token: $adminKey" -H "Content-Type: application/json" `
    --data-binary "@$env:TEMP\boot.json" | ConvertFrom-Json
$resp.token | Out-File "$env:APPDATA\Tracker\bootstrap.txt" -Encoding ascii -NoNewline

# 10. Запустить клиент
cd D:\tracker
python -m client.main
```

---

