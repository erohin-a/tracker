<!-- Часть 21 из 1409 -->
# Шаг 7. Настроить клиент
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 5. Пошаговая установка с нуля / Шаг 7. Настроить клиент

[◀ Шаг 6. Установить клиент](020_Shag_6_Ustanovit_klient.md) | [Оглавление](00_BCE_INDEX.md) | [Шаг 8. Получить bootstrap-токен ▶](022_Shag_8_Poluchit_bootstrap_token.md)

---

### Шаг 7. Настроить клиент

Скопировать CA-сертификат:
```powershell
Copy-Item D:\tracker\certs\fullchain.pem "$env:APPDATA\Tracker\ca.pem"
```

Создать `client\.env`:
```
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
```

