<!-- Часть 1223 из 1409 -->
# 2. Структура проекта
*Хлебные крошки:* Трекер — учёт рабочего времени. Handoff-документ / 2. Структура проекта

[◀ 1. Что это за проект](1222_1_Chto_eto_za_proekt.md) | [Оглавление](00_BCE_INDEX.md) | [3. Команды ▶](1224_3_Komandy.md)

---

## 2. Структура проекта

```
D:\tracker\
??? .env                          # SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY
??? docker-compose.yml            # db + api + nginx
??? certs/                        # fullchain.pem, privkey.pem (self-signed)
?
??? server/                       # FastAPI + PostgreSQL
?   ??? main.py                   # все API-эндпоинты
?   ??? web_admin.py              # вся веб-админка (~2500 строк)
?   ??? models.py                 # SQLAlchemy ORM
?   ??? schemas.py                # Pydantic
?   ??? security.py               # HMAC-SHA256, canonical_json
?   ??? security_passwords.py     # bcrypt + роли
?   ??? config.py                 # pydantic-settings, читает .env
?   ??? database.py               # engine, SessionLocal
?   ??? i18n.py                   # RU/EN словарь
?   ??? web_i18n.py               # contextvars hook для Jinja
?   ??? tasks.py                  # задачи планировщика
?   ??? scheduler.py              # APScheduler + advisory lock
?   ??? init_tasks.py             # регистрация задач
?   ??? alembic/                  # миграции (6 штук)
?   ?   ??? env.py                # с include_object (защита партиций)
?   ?   ??? versions/
?   ??? templates/                # ~25 HTML-шаблонов
?   ??? fonts/DejaVuSans.ttf      # для PDF
?   ??? Dockerfile
?   ??? nginx.conf
?   ??? requirements.txt
?
??? client/                       # PyQt6
?   ??? main.py                   # окно, трей, кнопки
?   ??? settings_dialog.py        # 3 вкладки: Напоминание, Общие, Регистрация
?   ??? registration.py           # регистрация ПК, keyring
?   ??? registration_dialog.py
?   ??? collector.py              # сбор активности (только при сессии)
?   ??? activity_watcher.py       # пассивный слушатель (всегда)
?   ??? reminder.py               # напоминания о старте/EOD
?   ??? sync.py                   # SyncWorker (30 сек цикл)
?   ??? db.py                     # SQLite (WAL)
?   ??? crypto.py                 # HMAC (идентичен серверу)
?   ??? http_client.py            # httpx + pinning
?   ??? autostart.py              # реестр / .desktop
?   ??? updater.py                # автообновление
?   ??? config.py                 # читает client/.env
?   ??? i18n.py                   # RU/EN словарь
?   ??? themes.py                 # светлая/тёмная тема (QSS)
?   ??? .env                      # TRACKER_SERVER_URL=https://127.0.0.1
?   ??? requirements.txt
?
??? control/
    ??? gui.py                    # SCP (Server Control Panel) для админа
    ??? main.py
```

---

