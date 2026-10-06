<!-- Часть 170 из 1409 -->
# ---------- Version ----------
*Хлебные крошки:* ---------- Version ----------

[◀ ---------- Records ----------](169_Records.md) | [Оглавление](00_BCE_INDEX.md) | [--- сессии --- ▶](171_sessii.md)

---

# ---------- Version ----------

@app.get("/api/v1/version", response_model=VersionResponse)
def get_latest_version(current: str = "", db: Session = Depends(get_db)):
    latest = (db.query(ClientVersion)
              .order_by(ClientVersion.release_date.desc()).first())
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
    return VersionResponse(latest_version=latest.version,
                           download_url=latest.download_url,
                           mandatory=latest.mandatory,
                           release_notes=latest.release_notes)
Сохраните.
________________________________________
Что мы только что изменили — простыми словами
Файл	Что изменилось
requirements.txt	Добавили 3 библиотеки: jinja2 (шаблоны), itsdangerous (сессии), openpyxl (Excel)
config.py	Добавили 3 настройки: admin_login, session_secret, web_secure_cookie
models.py	У Computer появились employee_id и assigned_at. У Employee появились last_name, first_name, middle_name
main.py	Подключили SessionMiddleware и веб-роутер admin_web_router. В создание сессии добавили employee_id=comp.employee_id
________________________________________
Что делать прямо сейчас
Не запускайте Docker ещё! Сначала нужно положить ещё два файла:
server/web_admin.py — я его уже прислал в предыдущем сообщении. Скопируйте целиком туда.
Папку server/templates/ с 9 HTML-файлами — они тоже в предыдущем сообщении.
Если не хотите искать — скажите «дай web_admin.py целиком» и «дай шаблоны целиком», я пришлю их одним сообщением каждое.
После того как все файлы на месте:
powershell
cd D:\tracker
docker compose down
docker compose up -d --build
docker compose logs api --tail=100
И открывайте https://localhost/admin/login.
________________________________________
Скажите, что прислать следующим сообщением:
A) полный server/web_admin.py
B) все 9 шаблонов server/templates/*.html одним блоком
C) сразу A + B
Этот ответ сгенерирован AI, только для справки.
https://localhost/admin/login 404 Not Found nginx/1.27.5
User gets 404 from nginx when accessing /admin/login. The nginx config only proxies /api/ to the API. Need to add /admin/ location.
Let me give the full nginx.conf with /admin/ proxy added.
Причина 404 — nginx не проксирует /admin/
Ваш nginx.conf умеет проксировать только /api/. Всё остальное (в том числе /admin/...) nginx ищет как статику и не находит ? 404.
Нужно добавить в nginx.conf блок location /admin/. Даю полный файл — замените целиком.
________________________________________
Файл server/nginx.conf — полная замена
Откройте D:\tracker\server\nginx.conf, удалите всё и вставьте:
nginx
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

    # --- API ---
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # --- Веб-интерфейс администратора ---
    location /admin/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # --- Редирект с корня сразу в админку (по желанию) ---
    location = / {
        return 302 /admin/login;
    }
}
Сохраните.
________________________________________
Что сделать дальше
Перезапустить только nginx (быстрее, чем всё):
powershell
cd D:\tracker
docker compose restart nginx
Или полностью пересобрать, если ещё не пересобирали после правок requirements.txt:
powershell
cd D:\tracker
docker compose down
docker compose up -d --build
docker compose logs api --tail=80
docker compose logs nginx --tail=40
________________________________________
Проверка по шагам
Откройте https://localhost/admin/login
Должна появиться страница входа (Bootstrap, тёмный заголовок Tracker Admin).
Если всё ещё 404:
docker compose logs nginx --tail=50 — посмотрите, применился ли конфиг.
Если в логах unknown directive — значит в файле остался мусор, перезапишите ещё раз.
docker compose exec nginx cat /etc/nginx/conf.d/default.conf — убедитесь, что внутри то, что вы вставили.
Если ошибка 502 Bad Gateway (а не 404) — значит nginx настроен правильно, но контейнер api упал. Смотрите:
powershell
docker compose logs api --tail=100
Типичные причины:
Не установлены новые библиотеки — пересоберите (--build).
Ошибка импорта web_admin — файла нет или лежит не там.
Отсутствует server/templates/ — FastAPI ругнётся при старте.
Если 500 Internal Server Error на самой странице логина — смотрите docker compose logs api --tail=50, там будет traceback.
________________________________________
Быстрый чек-лист, что должно быть на диске
text
D:\tracker\
??? server\
?   ??? web_admin.py          ? файл из предыдущего сообщения
?   ??? templates\            ? папка
?   ?   ??? base.html
?   ?   ??? login.html
?   ?   ??? dashboard.html
?   ?   ??? employees.html
?   ?   ??? computers.html
?   ?   ??? tokens.html
?   ?   ??? reports.html
?   ?   ??? report_result.html
?   ?   ??? audit.html
?   ??? main.py               ? обновлён (подключён роутер)
?   ??? models.py             ? обновлён (employee_id)
?   ??? config.py             ? обновлён
?   ??? requirements.txt      ? обновлён
?   ??? nginx.conf            ? обновлён (это сообщение)
Проверить, что все шаблоны на месте, можно так:
powershell
dir D:\tracker\server\templates
Должно быть 9 файлов .html.
________________________________________
Если шаблонов или web_admin.py ещё нет
Скажите — пришлю одним сообщением:
A) полный server/web_admin.py
B) все 9 HTML-шаблонов
C) сразу A + B
После того как убедимся, что /admin/login открывается — переходим к:
Проверке привязки сотрудника к ПК через интерфейс.
Отучим клиент падать, если в сессии нет employee_id.
Дальше — heartbeat, PDF, роли.
The log shows nginx still tries to serve /admin/login as static file from /etc/nginx/html/. This means nginx is still using the OLD config — the new nginx.conf wasn't applied. Two possibilities:
The user didn't save the new nginx.conf
The volume mount is read-only and it can't be modified... actually the message "can not modify /etc/nginx/conf.d/default.conf (read-only file system?)" is normal for a mounted read-only config.
Looking at the log message: "10-listen-on-ipv6-by-default.sh: info: can not modify /etc/nginx/conf.d/default.conf (read-only file system?)" — that's expected because we mount :ro.
But error shows it's still looking for static file. So the config file was NOT updated. Either user didn't save, or saved in wrong place, or Docker didn't pick up new file.
Actually — docker compose mounts ./server/nginx.conf to /etc/nginx/conf.d/default.conf:ro. If the file was changed on host, restart should pick it up. But if the file wasn't actually saved, we still have old config.
Wait — actually looking at compose from the doc:
yaml
nginx:
    image: nginx:1.27-alpine
    ports:
      - "443:443"
    volumes:
      - ./server/nginx.conf:/etc/nginx/conf.d/default.conf:ro
So the file is ./server/nginx.conf. That's what user needs to edit.
Let me help verify:
Check current content of nginx.conf on host
Also check inside container
Restart nginx
Also important: when using docker compose down and up, the mount will reload the file. restart nginx alone doesn't reload config because it doesn't re-read the mounted file... actually restart DOES re-create container so it re-mounts. But docker compose restart nginx restarts the same container without re-creating — the file bind-mount is preserved so content changes ARE visible.
Hmm actually docker compose restart reuses the same container. Bind mount reflects host changes immediately. So restart should work... unless user actually didn't save.
Let me check: error path is /etc/nginx/html/admin/login. That's nginx default html root. That means there's no location /admin/ block matching. So config really doesn't have that.
Let's guide user to verify.
Also — I should NOT just tell them to edit nginx.conf. Let me give a verification command and a "let's actually check" approach.
Let me be concrete and short.
Диагностика: nginx всё ещё работает со старым конфигом
Из лога видно: nginx пытается отдать /etc/nginx/html/admin/login — это дефолтная папка статики. Значит, в контейнере нет location /admin/, то есть новый nginx.conf не применился.
Давайте проверим по шагам, где расходятся файлы.
________________________________________
Шаг 1. Проверить, что реально лежит на хосте
Выполните в PowerShell:
powershell
Get-Content D:\tracker\server\nginx.conf
Ожидаемо: должны увидеть блок location /admin/ и location = /.
Если его нет — файл не был сохранён. Откройте заново и перезапишите целиком (файл в предыдущем сообщении).
________________________________________
Шаг 2. Проверить, что видит сам nginx-контейнер
powershell
docker compose exec nginx cat /etc/nginx/conf.d/default.conf
Если содержимое совпадает с хостом — отлично, монтирование работает.
Если там старый конфиг или что-то другое — значит, в docker-compose.yml указан не тот путь.
Проверьте:
powershell
docker compose config | Select-String "nginx.conf"
Должно быть:
text
source: D:\tracker\server\nginx.conf
target: /etc/nginx/conf.d/default.conf
Если путь другой — поправьте docker-compose.yml.
________________________________________
Шаг 3. Перезапустить контейнер
Даже если файл на хосте изменился, при restart контейнер перечитывает bind-mount только при пересоздании. Надёжнее сделать:
powershell
cd D:\tracker
docker compose stop nginx
docker compose rm -f nginx
docker compose up -d nginx
Или вообще:
powershell
docker compose down
docker compose up -d
Проверьте, что nginx поднялся, и повторите запрос:
powershell
docker compose logs nginx --tail=20
Откройте https://localhost/admin/login снова.
________________________________________
Шаг 4. Если снова 404
Пришлите мне вывод двух команд:
powershell
Get-Content D:\tracker\server\nginx.conf
и
powershell
docker compose exec nginx cat /etc/nginx/conf.d/default.conf
По ним сразу будет видно: файл не сохранён, или монтируется не туда, или в docker-compose.yml переопределён путь.
________________________________________
На всякий случай — ещё раз полный nginx.conf
Скопируйте этот текст целиком и замените содержимое файла D:\tracker\server\nginx.conf (не добавляйте, а именно замените — Ctrl+A ? Delete ? вставить):
nginx
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
Сохраните (Ctrl+S). Убедитесь, что редактор не добавил .txt в имя файла.
________________________________________
Как проверить сохранение за 2 секунды
powershell
Get-Content D:\tracker\server\nginx.conf | Select-String "location"
Должны увидеть три строки:
text
    location /api/ {
    location /admin/ {
    location = / {
Если видите только location /api/ — сохранение не сработало, файл всё ещё старый.
Сделайте шаги 1–3 и пришлите результат — либо откройте /admin/login и скажите, что показывает (404 / 502 / страница логина).
(.venv) PS D:\tracker> Get-Content D:\tracker\server\nginx.conf server { listen 443 ssl; listen [::]:443 ssl; http2 on; server_name localhost; ssl_certificate /etc/nginx/certs/fullchain.pem; ssl_certificate_key /etc/nginx/certs/privkey.pem; ssl_protocols TLSv1.2 TLSv1.3; add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always; client_max_body_size 10m; location /api/ { proxy_pass http://api:8000; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; proxy_read_timeout 60s; } } (.venv) PS D:\tracker> docker compose exec nginx cat /etc/nginx/conf.d/default.conf server { listen 443 ssl; listen [::]:443 ssl; http2 on; server_name localhost; ssl_certificate /etc/nginx/certs/fullchain.pem; ssl_certificate_key /etc/nginx/certs/privkey.pem; ssl_protocols TLSv1.2 TLSv1.3; add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always; client_max_body_size 10m; location /api/ { proxy_pass http://api:8000; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto $scheme; proxy_read_timeout 60s; } } (.venv) PS D:\tracker> docker compose config | Select-String "nginx.conf" source: D:\tracker\server\nginx.conf target: /etc/nginx/conf.d/default.conf
Файл nginx.conf на хосте всё ещё старый — там нет location /admin/. Пользователь просто не сохранил новый. Нужно ему сказать перезаписать файл.
Также docker-compose config показывает правильное монтирование. Значит всё ок, просто файл не перезаписан.
Дам ему команду через PowerShell, которая перезапишет файл одной командой — так надёжнее, чем через редактор.
Причина найдена: файл nginx.conf на хосте — старый
Смотрите на вывод:
Get-Content D:\tracker\server\nginx.conf ? нет location /admin/
docker compose config ? монтирование настроено правильно (D:\tracker\server\nginx.conf ? /etc/nginx/conf.d/default.conf)
Значит: nginx-контейнер честно читает ваш файл, но в файле просто нет блока /admin/. Нужно реально перезаписать файл — видимо, сохранение в редакторе не сработало (или сохранилось в другой файл, или Ctrl+S не нажали).
________________________________________
Надёжный способ — перезаписать файл одной командой PowerShell
Скопируйте весь блок ниже целиком в PowerShell и нажмите Enter. Он перезапишет D:\tracker\server\nginx.conf правильным содержимым и сразу покажет результат.
powershell
$nginxConf = @'
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
'@

[System.IO.File]::WriteAllText("D:\tracker\server\nginx.conf", $nginxConf, [System.Text.UTF8Encoding]::new($false))

Write-Host "--- Проверка содержимого ---" -ForegroundColor Cyan
Get-Content D:\tracker\server\nginx.conf | Select-String "location"
Ожидаемый вывод в конце:
text
    location /api/ {
    location /admin/ {
    location = / {
Если видите эти три строки — файл перезаписан правильно.
________________________________________
Пересоздать nginx-контейнер
Важно: restart не всегда перечитывает bind-mount. Нужно именно пересоздать контейнер:
powershell
cd D:\tracker
docker compose stop nginx
docker compose rm -f nginx
docker compose up -d nginx
Проверить, что контейнер увидел новый конфиг:
powershell
docker compose exec nginx cat /etc/nginx/conf.d/default.conf | Select-String "location"
Должны увидеть те же три строки location /api/, location /admin/, location = /.
________________________________________
Проверить страницу
Откройте в браузере:
https://localhost/admin/login
Если увидели страницу входа (Bootstrap, тёмный заголовок «?? Tracker Admin») — победа ??
Если получили 502 Bad Gateway — nginx работает, но упал контейнер api. Смотрите:
powershell
docker compose logs api --tail=80
Типичные причины на этом этапе:
Не пересобрали образ после правок requirements.txt ? пересоберите: docker compose up -d --build.
Не создан server/web_admin.py или server/templates/ ? пришлите мне, дам заново.
Если снова 404 — пришлите вывод:
powershell
Get-Content D:\tracker\server\nginx.conf
docker compose exec nginx cat /etc/nginx/conf.d/default.conf
Сравним построчно.
Зашёл на страницу. вбил ADMIN_API_KEY Внутренняя ошибка сервера
500 на логине. Скорее всего проблема с SessionMiddleware или чем-то ещё. Надо посмотреть логи api.
Наиболее вероятные причины:
Не пересобрали образ после добавления itsdangerous ? ImportError
Проблема с шаблоном
Проблема с сессией (SessionMiddleware) - но он бы упал при старте
Скорее всего api вообще не перезапущен с новым main.py и web_admin.py. Или падает TemplateResponse.
Дадим команды для диагностики + типичные фиксы. Пусть пришлют логи api.
500 на логине — смотрим логи API
Ошибка «Внутренняя ошибка сервера» — это ответ FastAPI. Значит nginx работает правильно, дошли до API, но внутри что-то упало. Нужно увидеть traceback.
Шаг 1. Посмотреть логи API
powershell
cd D:\tracker
docker compose logs api --tail=100
Ищите строки Traceback, Error, Exception. Пришлите мне последние 40–50 строк.
________________________________________
Пока вы смотрите логи — 5 самых частых причин 500 на /admin/login
Причина 1: не пересобрали образ после правки requirements.txt
Новые библиотеки (itsdangerous, jinja2, openpyxl) не установлены. В логах будет:
text
ModuleNotFoundError: No module named 'itsdangerous'
Фикс:
powershell
cd D:\tracker
docker compose down
docker compose up -d --build
Именно --build — иначе образ возьмётся из кеша.
________________________________________
Причина 2: контейнер api не видит web_admin.py
Если файл лежит не в D:\tracker\server\web_admin.py, а, например, в корне или с опечаткой — будет:
text
ModuleNotFoundError: No module named 'server.web_admin'
Проверьте:
powershell
dir D:\tracker\server\web_admin.py
Файл должен существовать.
________________________________________
Причина 3: контейнер api не видит папку templates
Jinja2Templates(directory="server/templates") не находит шаблоны. В логах:
text
jinja2.exceptions.TemplateNotFound: login.html
Проверьте:
powershell
dir D:\tracker\server\templates
Должно быть 9 файлов .html: base, login, dashboard, employees, computers, tokens, reports, report_result, audit.
Проверьте, что видит контейнер:
powershell
docker compose exec api ls -la /app/server/templates
Если пусто или «No such file» — нужно поправить server/Dockerfile, чтобы копировалась вся папка server/ вместе с шаблонами. Судя по текущему Dockerfile, там есть COPY server/ ./server/, значит должно работать. Но проверьте.
________________________________________
Причина 4: в main.py не подключен роутер или middleware
Если main.py остался старый — на /admin/login вернётся 404, а не 500. Раз 500 — значит main.py уже новый, роутер подключён. Хорошо.
________________________________________
Причина 5: ошибка в шаблоне login.html
Например, в шаблоне использована переменная, которой нет. TemplateResponse в FastAPI при request и error=None работает штатно, но синтаксическая ошибка Jinja ломает рендеринг. В логах будет jinja2.exceptions.TemplateSyntaxError.
________________________________________
Что мне прислать, чтобы точно понять причину
Пришлите мне одним сообщением:
Логи API (последние 60 строк):
powershell
docker compose logs api --tail=60
Вывод проверки файлов:
powershell
dir D:\tracker\server\web_admin.py
dir D:\tracker\server\templates
docker compose exec api ls /app/server/
docker compose exec api ls /app/server/templates
Что в .env (без самих секретов, только имена строк):
powershell
Get-Content D:\tracker\.env | ForEach-Object { ($_ -split '=')[0] }
Должны увидеть: SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY.
По этим трём выводам я точно скажу, в чём проблема, и мы это починим за 1 шаг.
Этот ответ сгенерирован AI, только для справки.
Ошибка ясна: колонки last_name, first_name, middle_name отсутствуют в таблице employees в БД. Нужно сделать ALTER TABLE или снести volume. Проще всего — ALTER TABLE.
Также надо проверить, что колонки employee_id и assigned_at в computers тоже добавлены. И на всякий случай — employee_id в work_sessions (он был в исходной модели, так что должен быть).
Даю команды ALTER TABLE и общий скрипт проверки/добавления.
Причина: в БД нет новых колонок
Логи предельно ясны:
text
column employees.last_name does not exist
create_all не изменяет существующие таблицы — он создаёт только те, которых нет. А таблица employees у вас уже была создана раньше, ещё без last_name / first_name / middle_name. Поэтому запрос падает.
Нужно вручную добавить 5 колонок (3 в employees, 2 в computers). Это делается одной командой.
________________________________________
Шаг 1. Добавить колонки в БД
Скопируйте весь блок ниже целиком в PowerShell и нажмите Enter. Он зайдёт в контейнер db и выполнит нужные ALTER TABLE.
powershell
cd D:\tracker

docker compose exec -T db psql -U tracker -d tracker -c @"
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_name VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS first_name VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS middle_name VARCHAR(50);
ALTER TABLE computers ADD COLUMN IF NOT EXISTS employee_id INTEGER REFERENCES employees(id);
ALTER TABLE computers ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMPTZ;
"@
Ожидаемый вывод — несколько строк ALTER TABLE. Если увидите ошибки — пришлите их.
________________________________________
Шаг 2. Проверить, что колонки появились
powershell
docker compose exec -T db psql -U tracker -d tracker -c "\d employees"
docker compose exec -T db psql -U tracker -d tracker -c "\d computers"
В employees должны быть: last_name, first_name, middle_name.
В computers должны быть: employee_id, assigned_at.
________________________________________
Шаг 3. Обновить страницу
Откройте снова:
https://localhost/admin/login
Введите логин admin и ваш ADMIN_API_KEY. Должен открыться дашборд.
Если получите новую 500-ошибку — пришлите docker compose logs api --tail=40, посмотрим следующую колонку/проблему. Скорее всего, их больше не будет, но подстрахуемся.
________________________________________
На будущее — как избежать таких сюрпризов
create_all в on_startup не мигрирует схему. Любое добавление поля требует либо:
Ручного ALTER TABLE (быстро, но забывчиво).
Alembic (правильно, ставится один раз и потом alembic upgrade head при каждом изменении моделей).
Сейчас, чтобы не спотыкаться, есть два пути:
Dev-путь: каждый раз при изменении моделей делать docker compose down -v (это снесёт БД и create_all создаст всё заново). Подходит только пока нет важных данных.
Прод-путь: подключить Alembic. Это наша следующая крупная задача после того, как админка заведётся.
________________________________________
Что делать, если данных в БД ещё нет
Если в БД нет ни одного ПК и ни одной сессии (то есть система только что поднята и используется для тестов), можно просто снести volume — тогда схема соберётся уже с новыми колонками:
powershell
cd D:\tracker
docker compose down -v
docker compose up -d --build
?? -v удалит все данные (computers, sessions, records, tokens, audit). Если у вас уже есть зарегистрированные ПК или тестовые записи — не делайте так, используйте ALTER TABLE из шага 1.
Сделайте шаг 1 и отпишитесь, что показывает страница.
как запустить клиента
User wants to know how to run the client. Let me give clear instructions.
Как запустить клиента «Трекер»
Ниже — полная последовательность, от подготовки bootstrap-токена до запуска. Делайте строго по шагам.
________________________________________
Шаг 1. Убедиться, что сервер работает
powershell
cd D:\tracker
docker compose ps
Все три контейнера (db, api, nginx) должны быть Up. Проверка API:
powershell
curl.exe -k https://localhost/api/v1/version
Должен вернуться JSON. Если это работает — идём дальше.
________________________________________
Шаг 2. Выпустить bootstrap-токен
Есть два способа — выберите любой.
Способ А — через веб-интерфейс (проще)
Откройте https://localhost/admin/tokens
Введите TTL (например, 24) и нажмите «Выпустить»
Скопируйте токен — он покажется один раз, в зелёной плашке сверху
Способ Б — через curl
powershell
$adminKey = (Get-Content D:\tracker\.env | Select-String "ADMIN_API_KEY=").ToString().Replace("ADMIN_API_KEY=","").Trim()

$bodyJson = '{"ttl_hours": 24, "issued_by": "admin"}'
[System.IO.File]::WriteAllText("$env:TEMP\boot.json", $bodyJson, [System.Text.UTF8Encoding]::new($false))

$resp = curl.exe -k -X POST "https://localhost/api/v1/admin/bootstrap-tokens" `
  -H "X-Admin-Token: $adminKey" `
  -H "Content-Type: application/json" `
  --data-binary "@$env:TEMP\boot.json" | ConvertFrom-Json

$resp.token
Скопируйте выведенную строку — это и есть токен.
________________________________________
Шаг 3. Положить токен в файл для клиента
Клиент при первом запуске читает токен из %APPDATA%\Tracker\bootstrap.txt.
Создайте папку и файл одной командой (подставьте свой токен вместо ВСТАВЬТЕ_СЮДА):
powershell
$token = "ВСТАВЬТЕ_СЮДА"
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Tracker" | Out-Null
[System.IO.File]::WriteAllText("$env:APPDATA\Tracker\bootstrap.txt", $token, [System.Text.UTF8Encoding]::new($false))
Проверьте:
powershell
Get-Content "$env:APPDATA\Tracker\bootstrap.txt"
Должен вывести ваш токен без лишних пробелов и кавычек.
________________________________________
Шаг 4. Скопировать CA-сертификат (для проверки TLS)
Клиент должен доверять самоподписанному сертификату сервера.
powershell
Copy-Item D:\tracker\certs\fullchain.pem "$env:APPDATA\Tracker\ca.pem" -Force
Проверьте:
powershell
Get-Item "$env:APPDATA\Tracker\ca.pem"
________________________________________
Шаг 5. Проверить client\.env
Откройте D:\tracker\client\.env — там должно быть:
ini
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
Если файла нет — создайте через PowerShell:
powershell
@"
TRACKER_SERVER_URL=https://localhost
TRACKER_PIN=
TRACKER_VERSION=1.0.0
"@ | Set-Content D:\tracker\client\.env -Encoding utf8
________________________________________
Шаг 6. Активировать venv и запустить клиент
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
?? Важно: запускать из D:\tracker, а не из D:\tracker\client. Иначе Python не найдёт пакет client и упадёт с ModuleNotFoundError: No module named 'client'.
________________________________________
Что должно произойти
В течение 3–5 секунд появится иконка в системном трее (рядом с часами, возможно в скрытых).
Откроется окно «Tracker 1.0.0» со статусом «Сессия: xxxxxxxx...».
Через ~30 секунд в окне появится «Синхронизировано N» — первая отправка данных на сервер.
Bootstrap-файл %APPDATA%\Tracker\bootstrap.txt удалится автоматически после успешной регистрации.
В %APPDATA%\Tracker\ появятся:
data.db — локальная SQLite
client.log — лог
credentials.enc (если keyring не сработал)
________________________________________
Проверка, что клиент зарегистрировался
Через веб-интерфейс:
Откройте https://localhost/admin/computers
Должна появиться строка с вашим ПК (hostname, UID).
Через SQL:
powershell
docker compose exec db psql -U tracker -d tracker -c "SELECT id, hostname, computer_uid, last_seen_at, is_active FROM computers;"
________________________________________
Если что-то не работает
Окно «Ошибка: Регистрация: ...»
Откройте лог:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 50 -Encoding UTF8
Ищите строки Registration failed или sync failed. Типичные причины:
Симптом в логе	Причина	Решение
SSL: CERTIFICATE_VERIFY_FAILED	Нет ca.pem или он не тот	Повторите шаг 4
401 Unauthorized	Токен неверный / сгорел	Выпустите новый (шаг 2)
getaddrinfo failed	client\.env не читается	Проверьте файл (шаг 5)
Bootstrap token required	Нет bootstrap.txt	Повторите шаг 3
Клиент сразу закрывается
Запустите из консоли (шаг 6 — python -m client.main без pythonw), тогда увидите traceback прямо в PowerShell.
ModuleNotFoundError: No module named 'pynput' или подобное
Значит venv не активирован или зависимости не установлены:
powershell
cd D:\tracker\client
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
________________________________________
Как остановить клиент
В окне клиента ? закрыть окно (свернётся в трей).
Чтобы выключить полностью: правый клик по иконке в трее ? «Выход».
________________________________________
Запуск в следующий раз
После успешной регистрации — уже не нужен ни bootstrap.txt, ни токен. Просто:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Секреты хранятся в keyring Windows, bootstrap.txt удалён, регистрация не потребуется.
________________________________________
Следующий шаг (после того, как клиент заработает)
Привязать ПК к сотруднику через https://localhost/admin/computers — выберите в выпадающем списке.
Тогда новые сессии этого ПК будут автоматически привязываться к этому сотруднику, и отчёты по нему появятся.
Проверить отчёт на https://localhost/admin/reports.
Запускайте — если что-то пойдёт не так, пришлите мне docker compose logs api --tail=40 и Get-Content "$env:APPDATA\Tracker\client.log" -Tail 40 -Encoding UTF8, разберём.
Давай у трекера клиентского создадим кнопку начало работы и окончание работы. программа продолжает работать но передает на сервер время, дату начала работы, и время окончания работы. Данным способом вычисляется что человек отработал столько то времени, в такие то дни.
User wants to add "Начало работы" and "Конец работы" buttons to the client. Program continues to work, but sends start/end times to server. Sessions currently auto-start on client launch. Need to change so session starts on button click, ends on button click.
Let me think about current client flow:
main.py _start(): calls ensure_registered(), db.init_db(), db.detect_abnormal_termination(), generates session_uid, db.start_session(session_uid), starts collector and sync threads.
Now we need:
Don't auto-create session on launch.
Button "Начать работу" ? creates session_uid, starts collector worker.
Button "Конец работы" ? stops collector, closes session (with end time), triggers sync.
Sync worker always running.
On next launch, if there's an active session in DB (no session_end), we should NOT auto-close it silently — well actually the current detect_abnormal_termination marks it after 12h of inactivity. Should keep that.
But if the user closed the client with session active (crash), on reopen show state? Simpler: on reopen if there's an unclosed session, ask user or auto-close as abnormal.
Let's keep it simple:
On startup, if there's active session in meta, close it as abnormal (crash).
User must press "Начать работу" to start a new session.
UI changes:
Add two buttons: "Начать работу" (green) and "Конец работы" (red/grey).
Add "Автозапуск" checkbox (already discussed).
Add status label with session info.
Also need to make sure CollectorWorker is created/destroyed per session.
Sync worker keeps running all the time, sending sessions and records.
Let me plan the changes:
client/db.py
start_session(uid) — already exists, adds session with start time, no end.
close_session(uid, abnormal) — already exists, sets end time.
Need get_active_session() — read from meta.
Keep detect_abnormal_termination — but call only on startup.
Actually looking at existing detect_abnormal_termination — it looks at last_activity and if >12h, closes as abnormal. But if user just closed the app cleanly, session should be closed. Let me adjust: on startup, if active_session is set, it means app was killed without closing session ? close as abnormal (or normal? we don't know). Let's mark as abnormal but log.
Actually the current code has close_session called from _shutdown_workers — that closes the active session with abnormal=False. Good. So if session was properly closed, meta active_session is empty. If app crashed, active_session still set ? on startup detect that and close as abnormal.
client/main.py
Rewrite:
Remove auto session creation from _start().
Add buttons in UI.
Add method _start_work():
Generate session_uid
db.start_session(uid)
Create CollectorWorker, move to thread, start
Update button states
Add method _stop_work():
Confirm dialog
self.collector.stop()
thread quit, wait
db.close_session(uid, abnormal=False)
Clear session_uid
Trigger sync to send session
Update button states
On startup: check meta active_session, if set ? close as abnormal.
On close: don't auto-close session (user might want to keep working).
Actually user said "программа продолжает работать но передает на сервер время" — hmm, that's about the client program continuing to run in background. Let me re-read.
"программа продолжает работать но передает на сервер время, дату начала работы, и время окончания работы"
I think it means: The client app keeps running (in tray), but on button click it sends start/end times. Yes that's what I designed.
On close of app: should we close session? Probably yes — if user closes client, they finished work. Let's close session with abnormal=False on close.
Actually let me think — user might minimize to tray (window close ? hide). Real quit via tray menu ? should we end session? I think yes, log as abnormal since they didn't press "Конец работы". Or ask. Let me just close normally on quit. Keep simple.
Actually let me reconsider — on quit if session still active, we should ask or auto-close as abnormal. I'll close as abnormal and log.
Hmm, but simpler approach: when app quits via tray "Выход" or Windows shutdown, close session as normal. When it crashes, on next launch detect active_session in meta and close as abnormal.
OK let me write the code.
Also need client/db.py change? Let me check get_meta and set_meta exist — yes.
New helper: get_active_session():
python
def get_active_session():
    return get_meta("active_session") or None
Actually already have get_meta("active_session") — just use it.
Wait, there's a bug in close_session: it sets active_session to "" if matches. Good.
Let me now write the new main.py.
Also UI: need buttons. Add to MainWindow.
Let me write:
python
from PyQt6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenu,
                             QMessageBox, QSystemTrayIcon, QVBoxLayout,
                             QHBoxLayout, QWidget, QPushButton, QCheckBox)
Status label shows: idle / session running since HH:MM.
Let me draft the MainWindow:
python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Tracker {CLIENT_VERSION}")
        self.resize(480, 240)
        
        self.status = QLabel("Готов к работе")
        self.status.setStyleSheet("font-size: 14px;")
        
        self.session_label = QLabel("Сессия: —")
        self.session_label.setStyleSheet("color: #666;")
        
        self.btn_start = QPushButton("?  Начать работу")
        self.btn_start.setStyleSheet("background-color:#28a745; color:white; font-weight:bold; padding:10px;")
        self.btn_start.clicked.connect(self._start_work)
        
        self.btn_stop = QPushButton("?  Конец работы")
        self.btn_stop.setStyleSheet("background-color:#dc3545; color:white; font-weight:bold; padding:10px;")
        self.btn_stop.clicked.connect(self._stop_work)
        self.btn_stop.setEnabled(False)
        
        self.autostart_cb = QCheckBox("Автозапуск при входе в систему")
        self.autostart_cb.setChecked(self._load_autostart_setting())
        self.autostart_cb.stateChanged.connect(self._on_autostart_changed)
        
        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.session_label)
        
        btns = QHBoxLayout()
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_stop)
        layout.addLayout(btns)
        layout.addWidget(self.autostart_cb)
        
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        
        self.session_uid = None
        self.collector = None
        self.collector_thread = None
        self.sync = None
        self.sync_thread = None
        ...
Then _start():
ensure_registered
db.init_db
detect_abnormal_termination (handles crash leftovers)
start sync worker (always on)
check updates
do NOT start collector
if there's an active session (from a crash less than threshold, or something), handle? Let's just close as abnormal on startup and start clean.
Actually the current detect_abnormal_termination does a threshold of 12h. Let me change: on startup, if active_session is set at all, close it as abnormal immediately. Because if we're starting, previous run must have ended (cleanly or not) — either way the session should be closed.
Wait no. If the client crashed and immediately restarted, then the previous session might still be open. We want to close it (since we're starting fresh) as abnormal. Good.
But what if user's client crashed and they want to continue? Too complex, just close it.
Let me simplify: on startup, close any active session as abnormal.
python
active = db.get_meta("active_session")
if active:
    log.warning("Previous session %s was not closed cleanly, closing as abnormal", active)
    db.close_session(active, abnormal=True)
Sync worker needs to be running to send this session. So sync must start before this check, or the check must be in _start after sync.
Order:
ensure_registered
db.init_db
close leftover session (as abnormal)
start sync worker thread
check updates
Then user presses "Начать работу" to create new session and start collector.
Sync worker:
fetches unsynced sessions and records every 30s
OK, no changes needed.
But sync needs to run even when no session is active — yes it does, sending past sessions/records.
Button states:
Initially: start enabled, stop disabled.
After start: start disabled, stop enabled.
After stop: start enabled, stop disabled.
Also update session_label with current session start time.
Let me write it out fully.
Also need to change _shutdown_workers:
stop collector (if any)
close active session as abnormal if still active (user clicked Выход without ending session)
Actually should we ask? Let's just close as abnormal and log.
Hmm, or maybe close as normal? If user clicked "Выход" in tray, they probably ended work. But they might have forgotten to click "Конец работы". Let's just close normally.
Actually you know what, I'll close as normal, since it's a clean shutdown. If app crashes, the next launch will detect and mark abnormal.
Let me now write out full main.py.
Also — I should update db.py to have a function to fetch current active session start time. Or read sessions table directly. Actually easier: use get_meta("active_session") to get the uid, then query sessions table for session_start.
Let me add to db.py:
python
def get_session(uid):
    row = get_conn().execute("SELECT * FROM sessions WHERE session_uid=?", (uid,)).fetchone()
    return row
Actually there's already fetch_unsynced_sessions. Let me just add a simple getter.
Hmm, I don't want to overhaul db.py too much. Let me just add one helper function.
Actually let me look at db.py again. There's:
start_session(uid) — creates session row with current time
close_session(uid, abnormal) — sets end time
get_meta(key) / set_meta(key, value)
I'll add:
python
def get_active_session_uid():
    return get_meta("active_session") or None

def get_session_start(uid):
    row = get_conn().execute("SELECT session_start FROM sessions WHERE session_uid=?", (uid,)).fetchone()
    return row["session_start"] if row else None
OK. Let me write it.
I think the cleanest approach is:
Give full client/db.py with small additions.
Give full client/main.py with the new buttons.
Give full client/autostart.py (referenced by main).
Explain what to do.
Also — should I add a heartbeat endpoint? No, keep this task focused.
Also — the sync worker currently starts in _start() and runs forever. That's fine. When user clicks "Начать работу", we start collector thread. When user clicks "Конец работы", we stop collector thread and close session, then next sync cycle (within 30s) will send the session to server.
But user might want immediate sync after stop. Could trigger it, but the sync worker doesn't have a "sync now" trigger easily. Simple solution: reduce sync interval, or add a signal. Let me add a simple "trigger" using a threading.Event.
Actually simpler: leave it as is. 30 seconds isn't long. Or if we want, we can call http_client.post from main thread — but that would block GUI.
Let me add a threading.Event to SyncWorker:
python
class SyncWorker(QObject):
    def __init__(self):
        super().__init__()
        self._running = False
        self._wake = threading.Event()
    
    def run(self):
        self._running = True
        while self._running:
            try:
                ...sync...
            except ...
            # wait for interval OR wake event
            self._wake.wait(timeout=SYNC_INTERVAL)
            self._wake.clear()
    
    def trigger(self):
        self._wake.set()
But trigger() called from main thread while worker is in another QThread — thread-safe since Event is thread-safe. Good. But we need to reference sync object from main thread — that's OK, it's just calling a method that sets an Event.
Wait, there's a subtlety: SyncWorker is a QObject moved to another thread. Calling its method directly from main thread executes in main thread, not worker thread. But since trigger just sets an Event, that's fine (thread-safe).
OK let me write it.
Actually, I need to be careful: the existing sync.py has a loop with time.sleep(0.5) for checking self._running. Let me rewrite with Event.
Let me now write the final versions.
client/db.py — additions only
I'll give the whole file but keep it mostly same with 2 new functions.
client/main.py — full rewrite
client/sync.py — full rewrite with Event
client/autostart.py — new file
Let me write all four.
Let me carefully write db.py first based on the original I have.
Original db.py functions:
get_conn
close_conn
_migrate
_quarantine_corrupt_db
init_db
set_meta, get_meta
start_session, touch_activity, close_session
detect_abnormal_termination
insert_record
fetch_unsynced
apply_sync_result
fetch_unsynced_sessions
mark_session_synced
enforce_size_limit
I'll keep all of these and add:
get_active_session_uid
get_session_start
OK.
Now let me write it out.
Also thinking about sync.py — the sessions are sent one by one; the current sync code has _sync_sessions that only sends sessions without session_end if the session was closed? Let me check.
Looking at _sync_sessions:
python
for r in db.fetch_unsynced_sessions():
    payload = {
        "session_uid": r["session_uid"],
        "session_start": r["session_start"],
        "session_end": r["session_end"],
        ...
    }
fetch_unsynced_sessions returns SELECT * FROM sessions WHERE synced=0. So it takes all unsynced sessions. For an open session (no session_end), it will still send it with session_end=None. That's fine — server upserts. When we later close it, synced=0 is set again (look at close_session: SET session_end=?, abnormal_termination=?, synced=0), so it gets re-sent with the end time.
Wait actually close_session sets synced=0. So on next sync cycle it'll be sent again. Good.
But there's an issue: if sync runs while session is active (before user clicks stop), it will send session with session_end=None. Server creates WorkSession with no end. That's OK — it's good to have visibility that user started.
But then when we close it, sync sends again with session_end set. Server upsert_session updates it. Good.
OK, this flow works.
Now the actual button flow:
User opens app ? sync worker starts, sends any leftover sessions/records
User clicks "Начать работу" ? generates session_uid ? db.start_session(uid) ? starts collector
Sync worker picks it up on next cycle, sends to server (session_end=None)
User works, collector generates records
User clicks "Конец работы" ? stop collector ? db.close_session(uid, abnormal=False) ? sync worker next cycle sends session with end time
Also trigger immediate sync
Good.
Let me write all files now.
I'll keep sync.py simple and add the wake event.
Also — _shutdown_workers in main.py: currently stops collector, closes session. New version: stop collector (if active), close session as normal, stop sync.
Actually on shutdown, if user didn't press "Конец работы", should we close session? I think yes — but mark as abnormal since they forgot to properly end the workday.
Hmm actually, let's be practical: if user closes the app, session closes as normal. If app crashes, on next launch we detect and mark abnormal.
OK, let me write.
One more consideration: what if user clicks "Начать работу" twice? Button should be disabled after first click. Handle state.
Let me write it now.
Actually let me reconsider — should collector still run before starting session? No, no session = no records to attach them to. So collector must only run during an active session.
Now the full main.py:
python
import logging
import os
import signal
import socket
import sys
import uuid
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QSocketNotifier, QThread
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QHBoxLayout, QLabel, QMainWindow, QMenu,
    QMessageBox, QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget,
)

from . import db, http_client
from .autostart import set_autostart
from .collector import CollectorWorker
from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH
from .registration import ensure_registered
from .sync import SyncWorker
from .updater import UpdateChecker, apply_update

import json

handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024,
                              backupCount=3, encoding="utf-8")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s",
                    handlers=[handler])
log = logging.getLogger("tracker.main")


def _icon_path() -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "icon.ico")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Tracker {CLIENT_VERSION}")
        self.resize(480, 260)

        # --- UI ---
        self.status = QLabel("Инициализация...")
        self.status.setStyleSheet("font-size: 14px; padding: 4px;")

        self.session_label = QLabel("Сессия: не запущена")
        self.session_label.setStyleSheet("color: #666; padding: 4px;")

        self.btn_start = QPushButton("?  Начать работу")
        self.btn_start.setStyleSheet(
            "background-color:#28a745; color:white; font-weight:bold; "
            "padding:12px; font-size:14px; border:none; border-radius:6px;"
        )
        self.btn_start.clicked.connect(self._on_start_work)

        self.btn_stop = QPushButton("?  Конец работы")
        self.btn_stop.setStyleSheet(
            "background-color:#dc3545; color:white; font-weight:bold; "
            "padding:12px; font-size:14px; border:none; border-radius:6px;"
        )
        self.btn_stop.clicked.connect(self._on_stop_work)
        self.btn_stop.setEnabled(False)

        self.autostart_cb = QCheckBox("Автозапуск при входе в систему")
        self.autostart_cb.setChecked(self._load_autostart_setting())
        self.autostart_cb.stateChanged.connect(self._on_autostart_changed)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_stop)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.session_label)
        layout.addLayout(btns)
        layout.addWidget(self.autostart_cb)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        # --- state ---
        self.session_uid = None
        self.collector = None
        self.collector_thread = None
        self.sync = None
        self.sync_thread = None
        self._signal_notifier = None
        self._signal_socks = None

        self._build_tray()
        self._start()

    # --- tray ---
    def _build_tray(self):
        self.tray = QSystemTrayIcon(self)
        ip = _icon_path()
        if os.path.exists(ip):
            self.tray.setIcon(QIcon(ip))
        else:
            self.tray.setIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_ComputerIcon))

        menu = QMenu()
        a1 = QAction("Показать", self)
        a1.triggered.connect(self._show)
        a2 = QAction("Начать работу", self)
        a2.triggered.connect(self._on_start_work)
        a3 = QAction("Конец работы", self)
        a3.triggered.connect(self._on_stop_work)
        a4 = QAction("Выход", self)
        a4.triggered.connect(self._quit)
        menu.addAction(a1)
        menu.addAction(a2)
        menu.addAction(a3)
        menu.addSeparator()
        menu.addAction(a4)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def _show(self):
        self.showNormal()
        self.activateWindow()

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.tray.showMessage("Tracker", "Свёрнуто в трей",
                              QSystemTrayIcon.MessageIcon.Information, 2000)

    # --- lifecycle ---
    def _start(self):
        try:
            ensure_registered()
        except Exception as e:
            log.exception("Registration failed")
            QMessageBox.critical(self, "Ошибка", f"Регистрация: {e}")
            self._quit()
            return

        try:
            db.init_db()
        except Exception as e:
            log.exception("DB init failed")
            QMessageBox.critical(self, "Ошибка БД", str(e))
            self._quit()
            return

        # закрываем «висячую» сессию от прошлого запуска
        active = db.get_meta("active_session")
        if active:
            log.warning("Найдена незакрытая сессия %s — закрываем как аварийную", active)
            try:
                db.close_session(active, abnormal=True)
            except Exception:
                log.exception("close_session on start failed")

        self.status.setText("Готов к работе")

        # sync worker работает всегда
        self._start_sync_worker()

        # проверка обновлений
        self._check_updates()

    def _start_sync_worker(self):
        self.sync_thread = QThread()
        self.sync = SyncWorker()
        self.sync.moveToThread(self.sync_thread)
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.server_down.connect(lambda: self.status.setText("Offline — данные копятся локально"))
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()

    def _on_synced(self, n):
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")

    def _on_auth_failed(self):
        QMessageBox.warning(self, "Авторизация",
                            "Сервер отклонил клиента. Требуется перерегистрация.")
        self.status.setText("Ошибка авторизации")

    # --- work session ---
    def _on_start_work(self):
        if self.session_uid is not None:
            return  # уже идёт

        try:
            self.session_uid = str(uuid.uuid4())
            db.start_session(self.session_uid)
        except Exception as e:
            log.exception("start_session failed")
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать сессию: {e}")
            self.session_uid = None
            return

        # запускаем collector в отдельном QThread
        self.collector_thread = QThread()
        self.collector = CollectorWorker(self.session_uid)
        self.collector.moveToThread(self.collector_thread)
        self.collector_thread.started.connect(self.collector.run)
        self.collector.error.connect(lambda m: self.status.setText(f"Сбор: {m}"))
        self.collector_thread.start()

        started = db.get_session_start(self.session_uid) or ""
        self.session_label.setText(f"Сессия: {self.session_uid[:8]}…  (с {started[:19].replace('T',' ')})")
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status.setText("Работа начата")

        # просим sync отправить сессию на сервер сейчас
        if self.sync:
            self.sync.trigger()

        log.info("Work session started uid=%s", self.session_uid)

    def _on_stop_work(self):
        if self.session_uid is None:
            return

        r = QMessageBox.question(
            self, "Конец работы",
            "Завершить рабочий день? Данные будут отправлены на сервер.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return

        uid = self.session_uid

        # останавливаем collector
        self._stop_collector()

        try:
            db.close_session(uid, abnormal=False)
        except Exception:
            log.exception("close_session failed")

        self.session_uid = None
        self.session_label.setText("Сессия: завершена")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status.setText("Работа завершена, синхронизация…")

        if self.sync:
            self.sync.trigger()

        log.info("Work session stopped uid=%s", uid)

    def _stop_collector(self):
        if self.collector:
            try:
                self.collector.stop()
            except Exception:
                log.exception("collector.stop")
        if self.collector_thread:
            self.collector_thread.quit()
            if not self.collector_thread.wait(5000):
                log.warning("collector thread didn't stop")
        self.collector = None
        self.collector_thread = None

    # --- autostart ---
    def _load_autostart_setting(self) -> bool:
        cfg = BASE_DIR / "config.json"
        if cfg.exists():
            try:
                return json.loads(cfg.read_text(encoding="utf-8")).get("autostart_enabled", False)
            except Exception:
                pass
        return False

    def _on_autostart_changed(self, state):
        enabled = (state == 2)  # Qt.CheckState.Checked
        ok = set_autostart(enabled)
        if not ok:
            QMessageBox.warning(self, "Автозапуск",
                                "Не удалось изменить автозапуск. Проверьте права.")
            return
        cfg = BASE_DIR / "config.json"
        data = {}
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
            except Exception:
                pass
        data["autostart_enabled"] = enabled
        cfg.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- updates ---
    def _check_updates(self):
        self._upd_thread = QThread()
        self._upd = UpdateChecker(auto_download=False)
        self._upd.moveToThread(self._upd_thread)
        self._upd_thread.started.connect(self._upd.run)
        self._upd.no_update.connect(self._upd_thread.quit)
        self._upd.update_available.connect(self._on_update_available)
        self._upd.update_ready.connect(self._on_update_ready)
        self._upd.error.connect(lambda e: log.warning("upd: %s", e))
        self._upd_thread.start()

    def _on_update_available(self, info):
        if info.get("mandatory"):
            self._download_and_apply(info)
        else:
            r = QMessageBox.question(
                self, "Обновление",
                f"Обновиться до {info['latest_version']}?")
            if r == QMessageBox.StandardButton.Yes:
                self._download_and_apply(info)

    def _on_update_ready(self, info, path):
        try:
            self._stop_collector()
            self._shutdown_sync()
            http_client.close_client()
            db.close_conn()
            from pathlib import Path
            apply_update(Path(path))
        except Exception:
            log.exception("apply update failed")

    def _download_and_apply(self, info):
        self._dl_thread = QThread()
        self._dl = UpdateChecker(auto_download=True)
        self._dl.moveToThread(self._dl_thread)
        self._dl_thread.started.connect(self._dl.run)
        self._dl.update_ready.connect(self._on_update_ready)
        self._dl.error.connect(lambda e: QMessageBox.warning(self, "Ошибка", e))
        self._dl_thread.start()

    # --- signals ---
    def install_signal_handlers(self):
        r, w = socket.socketpair()
        r.setblocking(False)
        w.setblocking(False)

        def _noop(*_a):
            pass

        signal.signal(signal.SIGTERM, _noop)
        signal.signal(signal.SIGINT, _noop)
        signal.set_wakeup_fd(w.fileno())

        n = QSocketNotifier(r.fileno(), QSocketNotifier.Type.Read, self)

        def _on():
            try:
                r.recv(1024)
            except BlockingIOError:
                pass
            self._quit()

        n.activated.connect(_on)
        self._signal_notifier = n
        self._signal_socks = (r, w)

    def _shutdown_sync(self):
        if self.sync:
            try:
                self.sync.stop()
            except Exception:
                log.exception("sync.stop")
        if self.sync_thread:
            self.sync_thread.quit()
            if not self.sync_thread.wait(5000):
                log.warning("sync thread didn't stop")
        self.sync = None
        self.sync_thread = None

    def _quit(self):
        log.info("Shutting down")
        self._stop_collector()

        # если сессия активна — закрываем её
        if self.session_uid:
            try:
                db.close_session(self.session_uid, abnormal=True)
                log.info("Closed session %s on quit (abnormal=True)", self.session_uid)
            except Exception:
                log.exception("close_session on quit")
            self.session_uid = None

        self._shutdown_sync()
        http_client.close_client()
        db.close_conn()

        try:
            if self._signal_notifier:
                self._signal_notifier.setEnabled(False)
                self._signal_notifier = None
            if self._signal_socks:
                r, w = self._signal_socks
                signal.set_wakeup_fd(-1)
                r.close()
                w.close()
                self._signal_socks = None
        except Exception:
            log.exception("signal cleanup")

        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    win = MainWindow()
    win.install_signal_handlers()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
Now sync.py with wake event:
python
import json
import logging
import threading
import time

from PyQt6.QtCore import QObject, pyqtSignal
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

from . import crypto, db, http_client
from .config import BATCH_SIZE, SERVER_URL, SYNC_INTERVAL
from .registration import get_computer_uid

log = logging.getLogger("tracker.sync")


class SyncWorker(QObject):
    synced = pyqtSignal(int)
    error = pyqtSignal(str)
    server_down = pyqtSignal()
    auth_failed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._wake = threading.Event()

    def run(self):
        self._running = True
        while self._running:
            try:
                ok = self._sync_sessions()
                if ok:
                    ok = self._sync_records()
                if not ok:
                    break
                db.enforce_size_limit()
            except Exception as e:
                log.warning("sync failed: %s", e)
                self.server_down.emit()

            # ждём SYNC_INTERVAL или пока не разбудят trigger()
            self._wake.wait(timeout=SYNC_INTERVAL)
            self._wake.clear()

    def stop(self):
        self._running = False
        self._wake.set()  # разбудить цикл

    def trigger(self):
        """Немедленно разбудить цикл синхронизации."""
        self._wake.set()

    def _headers(self):
        return {"X-Computer-Uid": get_computer_uid() or ""}

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((http_client.httpx.HTTPError,)),
           reraise=True)
    def _post(self, url, **kw):
        resp = http_client.post(url, **kw)
        if 500 <= resp.status_code < 600:
            raise http_client.httpx.HTTPStatusError(
                f"{resp.status_code}", request=resp.request, response=resp)
        return resp

    def _sync_sessions(self) -> bool:
        for r in db.fetch_unsynced_sessions():
            payload = {
                "session_uid": r["session_uid"],
                "session_start": r["session_start"],
                "session_end": r["session_end"],
                "abnormal_termination": bool(r["abnormal_termination"]),
            }
            resp = self._post(f"{SERVER_URL}/api/v1/sessions",
                              json=payload, headers=self._headers())
            if resp.status_code in (401, 403):
                self.auth_failed.emit()
                self._running = False
                return False
            if resp.status_code == 200:
                db.mark_session_synced(r["session_uid"])
            else:
                log.warning("session %s ? %d", r["session_uid"], resp.status_code)
        return True

    def _sync_records(self) -> bool:
        batch = db.fetch_unsynced(limit=BATCH_SIZE)
        if not batch:
            return True

        records = [{
            "record_uid": r["record_uid"],
            "session_uid": r["session_uid"],
            "kind": r["kind"],
            "data": json.loads(r["data"]),
            "client_ts": r["client_ts"],
            "signature": r["signature"],
        } for r in batch]

        batch_sig = crypto.sign_payload({"records": records})

        resp = self._post(
            f"{SERVER_URL}/api/v1/records/batch",
            json={"records": records, "batch_signature": batch_sig},
            headers=self._headers())

        if resp.status_code in (401, 403):
            self.auth_failed.emit()
            self._running = False
            return False

        resp.raise_for_status()
        body = resp.json()

        server_sig = body.pop("server_signature", None)
        if not server_sig or not crypto.verify_payload(server_sig, body):
            log.error("Server signature invalid — возможен MITM")
            self.error.emit("server signature invalid")
            return False

        accepted = body.get("accepted_uuids", [])
        rejected = body.get("rejected_uuids", [])
        reasons = body.get("reasons", {})

        permanent = [u for u in rejected if reasons.get(u) == "bad_signature"]
        temporary = [u for u in rejected if u not in permanent]

        db.apply_sync_result(accepted, permanent)

        if temporary:
            log.info("temporary rejects (retry): %d", len(temporary))
        if permanent:
            log.warning("permanent rejects: %d %s", len(permanent), reasons)

        self.synced.emit(len(accepted))
        return True
Now db.py additions. Let me write it out. Actually rather than give the whole file again (it's long), let me give a minimal patch:
Add to client/db.py after existing functions:
python
def get_active_session_uid():
    return get_meta("active_session") or None


def get_session_start(uid: str):
    row = get_conn().execute(
        "SELECT session_start FROM sessions WHERE session_uid=?", (uid,)
    ).fetchone()
    return row["session_start"] if row else None
But actually — the user wanted whole files to avoid mistakes. Let me just give the whole db.py. It's long but safe.
Actually, the original db.py from the document is quite complete. Let me just include it verbatim + 2 new functions.
Let me count — the original db.py ends with enforce_size_limit. I'll add the 2 functions there.
OK let me produce all files.
Also autostart.py — I gave it before, let me include it fully.
Let me now put everything together in a response. I'll present:
Short explanation of what's changing
Full client/db.py
Full client/sync.py
Full client/autostart.py
Full client/main.py
Instructions
Given the length, I'll be concise with explanations.
Let me make sure I don't have bugs.
In main.py:
_on_start_work — check self.session_uid is not None
Uses db.get_session_start which I'm adding
Uses self.sync.trigger() — added to sync worker
_stop_collector — safe to call even if no collector
One issue: in _on_stop_work, after closing session I trigger sync. But the sync worker is running in another thread — calling self.sync.trigger() from main thread is fine (it just sets an Event).
Another issue: CollectorWorker emits error signal via pyqtSignal(str). Connected with a lambda — fine.
Another: self.collector_thread.started.connect(self.collector.run) — worker runs in worker thread. Good.
Wait, when we stop the collector via self.collector.stop(), the worker's run method loop ends. Then self.collector_thread.quit() stops the QThread's event loop. Should work.
Another consideration: the CollectorWorker uses time.sleep(0.2) inside loop; that's fine, we just set _running = False and it exits within 200ms.
OK. One more: on _on_start_work I don't check if db.start_session is safe to call twice — it uses INSERT OR IGNORE so it's fine.
But set_meta("active_session", uid) — overwrites any previous. Fine.
Let me also handle the tray "Начать работу"/"Конец работы" — they call the same methods. The buttons should get disabled/enabled accordingly. Since tray actions call methods, and methods check session_uid, it's fine.
I think the code is good. Let me write the response.
One more thing: config.py in client doesn't have SYNC_INTERVAL? Let me check. Yes, original config has:
text
SYNC_INTERVAL = 30
Good.
Also, BASE_DIR — exists in config.
OK writing final response.
Length concerns — this is going to be long. I'll format it clearly.
Also I want to be careful — the user asked "как для чайника". So I'll give clear file-by-file instructions.
Let me also add: after these changes, the user should restart the client to see buttons.
Also: user may need to test that on server, sessions with employee_id work. Since the client's computer may not be assigned to employee yet, the session will have employee_id=None. User can assign later via admin panel.
OK writing now.
Кнопки «Начать работу» / «Конец работы» — полные файлы
Что изменится в поведении
Было: сессия создавалась автоматически при запуске приложения.
Станет:
При запуске приложение работает, sync-воркер крутится всегда, но сессия не создаётся.
Кнопка «? Начать работу» — создаёт сессию, запускает сбор активности и сразу отправляет на сервер session_start.
Кнопка «? Конец работы» — останавливает сбор, ставит session_end, просит sync немедленно отправить на сервер.
Если приложение было закрыто/упало с активной сессией — при следующем запуске она автоматически закрывается как аварийная.
Меняем 4 файла. Даю целиком — копируйте от первой до последней строки.
________________________________________
Файл 1 — client/db.py
Откройте D:\tracker\client\db.py, удалите всё, вставьте:
python
import sqlite3
import threading
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone

from .config import DB_PATH, MAX_DB_SIZE_MB

log = logging.getLogger("tracker.db")

_local = threading.local()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_uid TEXT PRIMARY KEY,
    session_start TEXT NOT NULL,
    session_end TEXT,
    abnormal_termination INTEGER DEFAULT 0,
    synced INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS records (
    record_uid TEXT PRIMARY KEY,
    session_uid TEXT NOT NULL,
    kind TEXT NOT NULL,
    data TEXT NOT NULL,
    client_ts TEXT NOT NULL,
    signature TEXT,
    synced INTEGER DEFAULT 0,
    poisoned INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_records_synced ON records(synced, poisoned);
CREATE INDEX IF NOT EXISTS ix_records_session ON records(session_uid);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def get_conn() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(
            str(DB_PATH), timeout=10, isolation_level=None,
            check_same_thread=False,
        )
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA journal_size_limit=67108864;")
        conn.row_factory = sqlite3.Row
        _local.conn = conn
    return conn


def close_conn():
    conn = getattr(_local, "conn", None)
    if conn is not None:
        try:
            conn.close()
        finally:
            _local.conn = None


def _migrate(conn):
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(records);")}
    if "poisoned" not in cols:
        conn.execute("ALTER TABLE records ADD COLUMN poisoned INTEGER DEFAULT 0;")


def _quarantine_corrupt_db():
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(DB_PATH) + suffix)
        if p.exists():
            try:
                p.rename(p.with_name(p.name + f".corrupt.{stamp}"))
            except OSError as e:
                log.error("rename %s failed: %s", p, e)


def init_db():
    if DB_PATH.exists():
        try:
            c = sqlite3.connect(str(DB_PATH))
            res = c.execute("PRAGMA integrity_check;").fetchone()
            c.close()
            if not res or res[0] != "ok":
                log.critical("DB integrity failed: %s. Quarantine.", res)
                _quarantine_corrupt_db()
        except sqlite3.DatabaseError as e:
            log.critical("Not a database: %s. Quarantine.", e)
            _quarantine_corrupt_db()

    conn = get_conn()
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    except sqlite3.OperationalError as e:
        log.warning("wal_checkpoint: %s", e)
    conn.executescript(SCHEMA)
    _migrate(conn)


def set_meta(key, value):
    get_conn().execute(
        "INSERT INTO meta(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


def get_meta(key, default=None):
    row = get_conn().execute(
        "SELECT value FROM meta WHERE key=?", (key,)
    ).fetchone()
    return row["value"] if row else default


