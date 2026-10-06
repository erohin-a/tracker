<!-- Часть 90 из 1409 -->
# Создание (одна команда)
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Сертификаты `D:\tracker\certs\` / Создание (одна команда)

[◀ ?? Сертификаты `D:\tracker\certs\`](089_Sertifikaty_D_tracker_certs.md) | [Оглавление](00_BCE_INDEX.md) | [`certs/fullchain.pem` и `certs/privkey.pem` ▶](091_certs_fullchain_pem_i_certs_privkey_pem.md)

---

### Создание (одна команда)

```powershell
cd D:\tracker\certs
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -x509 -newkey rsa:4096 `
    -keyout privkey.pem -out fullchain.pem -days 365 -nodes `
    -subj "/CN=localhost" `
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" `
    -addext "basicConstraints=critical,CA:TRUE"
```

