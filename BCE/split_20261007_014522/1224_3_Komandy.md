<!-- Часть 1224 из 1409 -->
# 3. Команды
*Хлебные крошки:* Трекер — учёт рабочего времени. Handoff-документ / 3. Команды

[◀ 2. Структура проекта](1223_2_Struktura_proekta.md) | [Оглавление](00_BCE_INDEX.md) | [4. Ключевые модели БД ▶](1225_4_Klyuchevye_modeli_BD.md)

---

## 3. Команды

```powershell
# Сервер
cd D:\tracker
docker compose up -d --build       # собрать и запустить
docker compose down                # остановить
docker compose down -v             # СБРОС БД (удалить данные!)
docker compose ps
docker compose logs api --tail=30
docker compose exec -T db psql -U tracker -d tracker -c "SELECT 1"
docker compose exec -T api grep -n "функция" /app/server/web_admin.py

# Клиент
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 30 -Encoding UTF8

# Alembic
docker compose exec -T api alembic -c /app/server/alembic.ini revision --autogenerate -m "описание"
docker compose exec -T api alembic -c /app/server/alembic.ini upgrade head

# Админка
https://localhost/admin/login
Логин: admin
Пароль: ADMIN_API_KEY из D:\tracker\.env
```

**ВАЖНО:** `docker compose restart api` НЕ перечитывает Python-код. После правок `server/*.py` — только `down && up -d --build`. После правок HTML — достаточно `restart api`.

---

