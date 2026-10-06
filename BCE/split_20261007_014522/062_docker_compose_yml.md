<!-- Часть 62 из 1409 -->
# `docker-compose.yml`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Корень `D:\tracker\` / `docker-compose.yml`

[◀ `.env`](061_env.md) | [Оглавление](00_BCE_INDEX.md) | [?? Папка `server/` ▶](063_Papka_server.md)

---

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: tracker
      POSTGRES_PASSWORD: tracker
      POSTGRES_DB: tracker
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracker"]
      interval: 5s
      retries: 10
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: server/Dockerfile
    environment:
      DATABASE_URL: postgresql+psycopg2://tracker:tracker@db:5432/tracker
      SECRET_ENCRYPTION_KEY: "${SECRET_ENCRYPTION_KEY}"
      JWT_SECRET: "${JWT_SECRET}"
      ADMIN_API_KEY: "${ADMIN_API_KEY}"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:1.27-alpine
    ports:
      - "443:443"
    volumes:
      - ./server/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  pgdata:
```

---

