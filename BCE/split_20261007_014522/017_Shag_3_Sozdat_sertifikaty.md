<!-- Часть 17 из 1409 -->
# Шаг 3. Создать сертификаты
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 5. Пошаговая установка с нуля / Шаг 3. Создать сертификаты

[◀ Шаг 2. Создать `.env` в корне](016_Shag_2_Sozdat_env_v_korne.md) | [Оглавление](00_BCE_INDEX.md) | [Шаг 4. Запустить сервер ▶](018_Shag_4_Zapustit_server.md)

---

### Шаг 3. Создать сертификаты

```powershell
cd D:\tracker\certs
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -x509 -newkey rsa:4096 `
    -keyout privkey.pem -out fullchain.pem -days 365 -nodes `
    -subj "/CN=localhost" `
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" `
    -addext "basicConstraints=critical,CA:TRUE"
```

