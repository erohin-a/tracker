<!-- Часть 22 из 1409 -->
# Шаг 8. Получить bootstrap-токен
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 5. Пошаговая установка с нуля / Шаг 8. Получить bootstrap-токен

[◀ Шаг 7. Настроить клиент](021_Shag_7_Nastroit_klient.md) | [Оглавление](00_BCE_INDEX.md) | [Шаг 9. Запустить клиент ▶](023_Shag_9_Zapustit_klient.md)

---

### Шаг 8. Получить bootstrap-токен

```powershell
$adminKey = "ВАШ_ADMIN_API_KEY_ИЗ_ENV"
$bodyObj = @{ ttl_hours = 24; issued_by = "admin" }
$bodyJson = $bodyObj | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText("$env:TEMP\boot.json", $bodyJson, [System.Text.UTF8Encoding]::new($false))

curl.exe -k -X POST "https://localhost/api/v1/admin/bootstrap-tokens" `
    -H "X-Admin-Token: $adminKey" `
    -H "Content-Type: application/json" `
    --data-binary "@$env:TEMP\boot.json"
```

Из ответа `{"token":"...","expires_in_hours":24}` скопировать **только значение** токена и сохранить:
```powershell
[System.IO.File]::WriteAllText("$env:APPDATA\Tracker\bootstrap.txt", "ТОКЕН", [System.Text.UTF8Encoding]::new($false))
```

