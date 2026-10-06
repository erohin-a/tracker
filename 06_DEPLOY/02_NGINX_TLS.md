# Nginx и TLS
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 06_DEPLOY\01_DOCKER.md, 05_SCP\02_CERTIFICATES.md, 03_SERVER\01_ARCHITECTURE.md, 04_CLIENT\09_REGISTRATION.md

## Назначение
Описать конфигурацию nginx как reverse-proxy и TLS-терминатора в «Трекере»: что слушает, куда проксирует, какие сертификаты, какие заголовки. Это карта для администратора, который настраивает сервер, и для разработчика, который дорабатывает конфиг.

## Содержание

### Роль nginx
- **TLS-терминация** — расшифровка HTTPS, проксирование в `api:8000` по HTTP.
- **Reverse-proxy** — маршрутизация запросов: `/api/`, `/admin/`, `/`.
- **HSTS** — заголовок безопасности.
- **Отдача статики** — через api (Jinja2), не через nginx.
- **Один порт:** 443. Порт 80 не используется.

### Файл конфигурации
- **Путь:** `D:\tracker\server\nginx.conf`.
- **Монтируется:** `./server/nginx.conf:/etc/nginx/conf.d/default.conf:ro` в `docker-compose.yml`.
- **Read-only** — изменения требуют `docker compose restart nginx`.

### Структура `nginx.conf`
```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name localhost;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
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

    location /admin/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    location = / {
        return 302 /admin/login;
    }
}
Разбор по блокам
listen 443 ssl
Слушает 443 на IPv4 и IPv6.

http2 on — HTTP/2.

Только HTTPS, без HTTP-редиректа.

server_name localhost
Для локального развёртывания.

В проде — заменить на реальный домен.

Сертификаты
nginx
ssl_certificate /etc/nginx/certs/fullchain.pem;
ssl_certificate_key /etc/nginx/certs/privkey.pem;
Монтируются из ./certs:/etc/nginx/certs:ro.

fullchain.pem — публичный сертификат (для клиента).

privkey.pem — приватный ключ (только nginx, не раздавать).

Протоколы
nginx
ssl_protocols TLSv1.2 TLSv1.3;
Только TLS 1.2 и 1.3.

TLS 1.0 и 1.1 — отключены (устарели, небезопасны).

HSTS
nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
max-age=63072000 — 2 года.

includeSubDomains — для всех поддоменов.

always — заголовок добавляется всегда (включая ошибки).

⚠ Опасно: браузер запомнит и будет требовать HTTPS 2 года.

client_max_body_size 10m
Максимальный размер тела запроса — 10 МБ.

Для загрузки CSV/XLSX — достаточно.

Локации
location /api/
Проксирует все запросы /api/* → http://api:8000.

НЕ переписывает путь: /api/v1/version → http://api:8000/api/v1/version.

Заголовки:

Host — оригинальный хост.

X-Real-IP — реальный IP клиента.

X-Forwarded-For — цепочка прокси.

X-Forwarded-Proto — https (важно для FastAPI).

proxy_read_timeout 60s — если API не отвечает 60 секунд, соединение рвётся.

location /admin/
То же, что /api/, но для админки.

Отдаёт HTML-страницы через Jinja2.

location = /
= / — точное совпадение только для /.

Возвращает 302 на /admin/login.

Пользователь сразу попадает на форму входа.

Что НЕ покрыто
Что	Статус
HTTP → HTTPS редирект (порт 80)	Не реализован
Отдача статики напрямую	Не реализована
Кэширование	Не реализовано
Rate limiting	Не реализован
Basic Auth	Не реализован
IP-whitelist	Не реализован
CORS-заголовки	Не добавлены
gzip/brotli	Не включены
Let's Encrypt	Не реализован
Сертификаты
Расположение
Файл	Путь
Публичный сертификат	D:\tracker\certs\fullchain.pem
Приватный ключ	D:\tracker\certs\privkey.pem
Копия для клиента	D:\tracker\client\ca.pem
Генерация (self-signed)
powershell
cd D:\tracker\certs
& "C:\Program Files\OpenSSL-Win64\bin\openssl.exe" req -x509 -newkey rsa:4096 `
  -keyout privkey.pem -out fullchain.pem -days 365 -nodes `
  -subj "/CN=localhost" `
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" `
  -addext "basicConstraints=critical,CA:TRUE"
Параметры:

-x509 — самоподписанный.

-newkey rsa:4096 — новый ключ RSA 4096.

-days 365 — срок действия.

-nodes — без пароля на ключ.

-subj "/CN=localhost" — Common Name.

-addext subjectAltName=... — обязательно для современных клиентов.

-addext basicConstraints=critical,CA:TRUE — CA-сертификат (для self-signed цепочки).

Проверка сертификата
powershell
# CN и SAN
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -subject -ext subjectAltName

# Отпечаток SHA-256
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -fingerprint -sha256

# Даты действия
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -dates

# Проверка соединения
curl.exe -k https://localhost/api/v1/version
Перевыпуск через SCP
Вкладка «Сертификат» в SCP.

Диалог RenewCertDialog.

Бэкап → генерация → копирование в client/ca.pem → перезапуск nginx.

Подробности — в 05_SCP\02_CERTIFICATES.md.

Прод (production)
Замена self-signed на Let's Encrypt
Получить сертификат через certbot (отдельно, не через SCP).

Положить fullchain.pem и privkey.pem в certs/.

docker compose restart nginx.

Требования Let's Encrypt:

Реальный домен.

Валидация владения доменом (HTTP или DNS).

Автоматическое продление (cron или systemd timer).

Корпоративный CA
Заменить fullchain.pem и privkey.pem на выданные корпоративным CA.

Обновить client/ca.pem.

Пересобрать установщик клиента.

Отказ от HSTS при переходе
Если нужно временно отключить HSTS — убрать add_header.

Браузер запомнил на 2 года, но при отсутствии заголовка в новых ответах — по истечении срока перестанет требовать.

Проверка конфигурации
Проверить синтаксис:

powershell
docker compose exec nginx nginx -t
Посмотреть текущий конфиг:

powershell
docker compose exec nginx cat /etc/nginx/conf.d/default.conf
Проверить, что сертификаты видны:

powershell
docker compose exec nginx ls -la /etc/nginx/certs/
Логи
powershell
docker compose logs nginx --tail=50
Типичные ошибки в логах:

Ошибка	Причина	Решение
cannot load certificate	Файл сертификата не найден	Проверить certs/, монтирование
PEM_read_bio_X509_AUX() failed	Битый сертификат	Перевыпустить
unknown directive "CN=localhost"	Мусор в nginx.conf	Перезаписать конфиг
host not found in upstream "api"	api не поднялся	docker compose ps, логи api
bind() to 0.0.0.0:443 failed	Порт 443 занят	netstat -ano | findstr :443
Известные проблемы
Проблема	Причина	Решение
Порт 80 занят Windows HTTP.sys	IIS/WinRM	Использовать только 443
unknown directive "CN=localhost"	Ошибка при копипасте в nginx.conf	Перезаписать файл
nginx не поднимается	Ошибка сертификата или порта	docker compose logs nginx --tail=50
Клиент не подключается	Нет ca.pem или истёк сертификат	Обновить ca.pem
Hostname mismatch	Сертификат без SAN	Перевыпустить с -addext subjectAltName=...
HSTS блокирует переход на HTTP	Заголовок запомнился	Только ждать или менять домен
Let's Encrypt не продлевается	Порт 80 закрыт	Использовать DNS-валидацию
Что делать при смене сертификата
Выпустить новый сертификат (SCP → «Обновить сертификат»).

Убедиться, что client/ca.pem обновлён.

Пересобрать установщик клиента с новым ca.pem.

Раздать сотрудникам (или заменить %APPDATA%\Tracker\ca.pem вручную).

Перезапустить nginx: docker compose restart nginx.

Проверить: curl.exe -k https://localhost/api/v1/version.

Заголовки безопасности
Что есть:

Strict-Transport-Security (HSTS).

Что можно добавить (не реализовано):

X-Frame-Options: DENY — защита от clickjacking.

X-Content-Type-Options: nosniff — защита от MIME-sniffing.

Content-Security-Policy — ограничение источников.

Referrer-Policy — контроль referer.

Permissions-Policy — ограничение API браузера.

Быстрая проверка
powershell
# 1. nginx запущен
docker compose ps nginx

# 2. Сертификаты на месте
docker compose exec nginx ls /etc/nginx/certs/

# 3. Конфиг валиден
docker compose exec nginx nginx -t

# 4. API отвечает
curl.exe -k https://localhost/api/v1/version

# 5. HSTS в заголовках
curl.exe -k -I https://localhost/admin/login
Что НЕ реализовано
HTTP-редирект (порт 80).

Кэширование статики.

Rate limiting.

IP-whitelist.

CORS-заголовки.

gzip/brotli.

Let's Encrypt через SCP.

Автопродление сертификатов.

Мониторинг срока действия сертификата.

Заголовки безопасности (X-Frame-Options, CSP и др.).

Ключевые решения
Один порт 443. Порт 80 занят Windows HTTP.sys.

TLS 1.2 и 1.3. Устаревшие протоколы отключены.

HSTS на 2 года. Защита от downgrade-атак.

Self-signed сертификат для локальной разработки. Let's Encrypt — для прода.

SAN обязателен. Без него современные клиенты отказываются.

X-Forwarded-Proto — важно для корректной генерации URL в FastAPI.

client_max_body_size 10m — для загрузки CSV/XLSX.

proxy_read_timeout 60s — защита от зависших запросов.

Только location / редиректит. Остальные локации — прокси.

nginx.conf монтируется read-only. Изменения — только через restart nginx.

Ссылки на код
запросить: server/nginx.conf — конфиг

запросить: docker-compose.yml — монтирование nginx.conf и certs/

запросить: certs/fullchain.pem, certs/privkey.pem — сертификаты

запросить: client/ca.pem — копия для клиента

запросить: control/gui.py — CertificateTab, RenewCertDialog, docker_compose_restart

запросить: server/main.py — как FastAPI читает X-Forwarded-Proto

Открытые вопросы / чего не хватает
нет данных: есть ли отдельная конфигурация для прода (например, nginx.prod.conf).

нет данных: тестировался ли HTTP/2 — http2 on заявлен.

нет данных: есть ли access-логи nginx — по умолчанию в stdout.

нет данных: как обрабатывается 404 от api — пробрасывается.

не решено: нужен ли HTTP-редирект на 80 порту.

не решено: нужен ли rate limiting на /admin/login.

не решено: нужны ли заголовки безопасности (X-Frame-Options, CSP и др.).

не решено: интегрировать ли Let's Encrypt в SCP.

не решено: как автоматически продлевать сертификат.

не решено: нужен ли IP-whitelist для админки.

не решено: включать ли gzip/brotli для статики.

не решено: как быть с CORS — сейчас не настроен.

не решено: нужен ли отдельный server блок для домена в проде.

не решено: как быть с поддоменами (wildcard-сертификаты).

не решено: нужно ли кэширование статики на уровне nginx.

не решено: как обрабатывать большие загрузки (XLSX импорт) — client_max_body_size 10m может быть мало.

Готово. Один файл выше. Следующий по индексу — 06_DEPLOY\03_WINDOWS_SETUP.md.