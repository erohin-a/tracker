<!-- Часть 72 из 1409 -->
# `server/Dockerfile`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/Dockerfile`

[◀ `server/main.py`](071_server_main_py.md) | [Оглавление](00_BCE_INDEX.md) | [`server/nginx.conf` ▶](073_server_nginx_conf.md)

---

### `server/Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Зависимости
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем пакет server целиком
COPY server/ ./server/

# Гарантируем, что это пакет (важно для относительных импортов)
RUN touch /app/server/__init__.py

EXPOSE 8000

# Указываем gunicorn'у пакет server, модуль main, объект app
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", \
     "-b", "0.0.0.0:8000", "server.main:app"]
```

