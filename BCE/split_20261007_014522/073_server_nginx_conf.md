<!-- Часть 73 из 1409 -->
# `server/nginx.conf`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `server/` / `server/nginx.conf`

[◀ `server/Dockerfile`](072_server_Dockerfile.md) | [Оглавление](00_BCE_INDEX.md) | [?? Папка `client/` ▶](074_Papka_client.md)

---

### `server/nginx.conf`

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name localhost;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;

    client_max_body_size 10m;

    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

---

