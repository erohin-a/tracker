<!-- Часть 46 из 1409 -->
# 10. Что делать при типовых сбоях
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 10. Что делать при типовых сбоях

[◀ Проверка БД](045_Proverka_BD.md) | [Оглавление](00_BCE_INDEX.md) | [11. Безопасность и ротация секретов ▶](047_11_Bezopasnost_i_rotatsiya_sekretov.md)

---

## 10. Что делать при типовых сбоях

| Симптом | Решение |
|---|---|
| `docker compose ps` — api в `Restarting` | `docker compose logs api --tail=50` ? искать причину |
| nginx не поднимается | `docker compose logs nginx --tail=50` — обычно сертификат или порт |
| Порт 443 занят | `netstat -ano \| findstr :443` ? сменить порт в `docker-compose.yml` |
| Клиент висит на «Инициализация» | Открыть `client.log` в UTF-8, смотреть `Registration failed` |
| `401 Unauthorized` | Bootstrap-токен сгорел — выпустить новый |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Проверить `ca.pem`, перевыпустить сертификат с SAN |
| `Hostname mismatch` | Сертификат без SAN для `localhost` |
| `getaddrinfo failed` | `.env` не читается, `SERVER_URL` дефолтный |
| Клиент не пишет данные | `pynput` не работает — Wayland? нет прав? |
| «Синхронизировано 0» | Сервер отвергает батч: `unknown_session` или `bad_signature`. Проверить `docker compose logs api` |
| `.env` игнорируется | UTF-16 BOM ? перезаписать через `WriteAllText` |
| PowerShell съедает кавычки | Использовать `ConvertTo-Json` + `--data-binary @файл` |

---

