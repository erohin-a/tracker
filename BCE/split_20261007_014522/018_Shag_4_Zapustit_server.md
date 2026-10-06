<!-- Часть 18 из 1409 -->
# Шаг 4. Запустить сервер
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 5. Пошаговая установка с нуля / Шаг 4. Запустить сервер

[◀ Шаг 3. Создать сертификаты](017_Shag_3_Sozdat_sertifikaty.md) | [Оглавление](00_BCE_INDEX.md) | [Шаг 5. Проверить API ▶](019_Shag_5_Proverit_API.md)

---

### Шаг 4. Запустить сервер

```powershell
cd D:\tracker
docker compose up -d --build
Start-Sleep -Seconds 20
docker compose ps
```

Все три контейнера должны быть `Up`.

