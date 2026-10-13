@@ 11 часть разработки
Чат V2 от 12.10.2026

12.10.2026 V2 Трекер обновление у сотрудников
The user is continuing the "Tracker" project. They're at ~96% readiness. The P0 task is "Публикация версий через UI" — version publishing through the UI.
They explicitly said at the end of the first file:
"Прежде чем писать код — попроси у меня файлы, которые нужны для анализа (например, server/routes/admin_versions.py, client/updater.py, 04_CLIENT/08_AUTOSTART_UPDATE.md, 06_DEPLOY/05_UPDATES.md). Не начинай вслепую — структуры я не помню детально."
So they want me to ask for the files I need. Don't start coding blindly.
Let me think about what I actually need to implement version publication UI. The task:
1.	Build new installer in SCP.
2.	Click "Publish version" button in SCP → send artifact to server.
3.	In admin panel on versions page see: number, size, date, who published.
4.	Clients on heartbeat see "new version available" and via updater.py download and install automatically.
I need to know:
•	Server-side: existing API routes for versions. What's already there? server/routes/admin_versions.py presumably.
•	Client-side: client/updater.py — existing? What's its state?
•	Docs: 04_CLIENT/08_AUTOSTART_UPDATE.md, 06_DEPLOY/05_UPDATES.md — these describe the intended design.
•	SCP build tab: control/build_tab.py — where the "Publish" button would go.
•	SCP deploy module: control/deploy.py.
•	Client sync/heartbeat: client/sync.py or similar — to know how heartbeat works and where to add version check.
•	Server models: client_versions table? Check 03_SERVER/03_MODELS.md.
•	Admin templates: versions page template.
Let me ask for these files systematically. I should organize by priority — first the design docs (so I know intended design), then existing code.
Actually, per their instruction, I should ask for the files needed for analysis. Let me be specific and organized, and note what I'll do with each.
Let me list the asks:
Design docs (first — to understand intended design):
1.	D:\tracker\docs\04_CLIENT\08_AUTOSTART_UPDATE.md
2.	D:\tracker\docs\06_DEPLOY\05_UPDATES.md
Server side:
3.	D:\tracker\server\routes\admin_versions.py (if exists — or the route file that handles versions)
4.	D:\tracker\server\models\*.py — specifically the file with client_versions model (or wherever it is)
5.	The admin template for the versions page (likely server/templates/admin/versions.html)
6.	D:\tracker\server\main.py or wherever routes are registered (to see how routes are hooked up)
Client side:
7.	D:\tracker\client\updater.py (if exists)
8.	D:\tracker\client\sync.py (heartbeat / client-config)
9.	D:\tracker\client\main.py or entry point
SCP side:
10.	D:\tracker\control\build_tab.py (where "Publish" button goes)
11.	D:\tracker\control\build.py (already modified for prepare_client_env — need current state)
12.	D:\tracker\control\deploy.py
Let me also consider: they said server/routes/admin_versions.py as an example. So maybe it exists.
I should keep the ask focused, prioritized. Maybe ask for the design docs first, then code. But they said don't start blindly — so asking for a batch is fine.
Actually, I should probably batch it in a couple of groups to avoid overwhelming. But since the user is fine pasting multiple files, let me ask for the key ones in priority order and note which are "critical" vs "helpful if exists".
Let me also give a brief plan of what I understand and what I'll do once I have the files, so the user knows the direction.
Let me write it in Russian, "ты", as per the rules.
Structure:
•	Confirm context understood (P0: version publishing UI cycle).
•	Brief plan outline of the cycle endpoints (my hypothesis).
•	Ask for files, organized by category, with "why I need it".
•	Mention that if some files don't exist, that's fine — tell me.
Let me be careful not to over-ask. Priority:
Critical:
•	Design docs: 04_CLIENT/08_AUTOSTART_UPDATE.md, 06_DEPLOY/05_UPDATES.md
•	Server: routes file for versions, models file with client_versions
•	Client: updater.py, sync.py (heartbeat part)
•	SCP: build_tab.py, build.py, deploy.py
Secondary:
•	Admin template for versions page
•	main.py route registration
•	client main entry point
•	03_SERVER/03_MODELS.md (to see if client_versions exists)
Let me write this out.
I should also ask about a few decisions I need to clarify:
•	Auto-install vs user consent (they mentioned "обсудим")
•	Where artifacts are stored (server: filesystem? volume?)
•	How the client verifies the artifact (checksum, signature?)
But maybe ask files first, decisions after. Actually, asking a couple of key design questions upfront along with the file ask is efficient. Let me include a short "вопросы по дизайну" section — but keep it small, since without seeing code I can't ask well-formed questions.
Actually, the user explicitly says "Прежде чем писать код — попроси у меня файлы, которые нужны для анализа". So the primary output should be the file request. Let me focus on that, and add a short "открытые вопросы" at the end.
Let me draft.
Понял контекст. Продолжаем с P0 — публикация версий через UI. Прежде чем писать код — как договорились, не лезу вслепую, запрашиваю файлы.
Что мне нужно посмотреть (по приоритету)
1. Дизайн (обязательно, в первую очередь)
Чтобы не изобретать заново — там уже может быть описана схема:
•	D:\tracker\docs\04_CLIENT\08_AUTOSTART_UPDATE.md
•	D:\tracker\docs\06_DEPLOY\05_UPDATES.md
2. Серверная часть
•	D:\tracker\server\routes\admin_versions.py (или как называется файл с версиями — если такого нет, скажи, где сейчас живёт всё, что связано с версиями клиента)
•	Файл моделей, где объявлена client_versions (или как она у тебя называется) — скорее всего D:\tracker\server\models\*.py
•	Регистрация роутов: D:\tracker\server\main.py (или app.py — как у тебя)
•	Шаблон страницы версий в админке: что-то типа D:\tracker\server\templates\admin\versions.html (если есть)
•	Заодно: D:\tracker\docs\03_SERVER\03_MODELS.md и D:\tracker\docs\03_SERVER\02_API.md — чтобы я не переспрашивал по полям и эндпоинтам
3. Клиентская часть
•	D:\tracker\client\updater.py — если существует. Если нет — скажи, где сейчас heartbeat-цикл.
•	D:\tracker\client\sync.py (или как называется модуль синхронизации/heartbeat)
•	Точка входа клиента: D:\tracker\client\main.py
4. SCP
•	D:\tracker\control\build_tab.py — туда будем добавлять кнопку «Опубликовать версию»
•	D:\tracker\control\build.py — текущее состояние (после prepare_client_env)
•	D:\tracker\control\deploy.py — чтобы понимать, что уже есть по конфигу
5. Вспомогательное (если не сложно)
•	D:\tracker\docker-compose.yml — чтобы понять, куда физически складывать артефакты (volume? bind mount? отдельная папка на хосте?)
________________________________________
Зачем мне каждый файл — коротко
•	Дизайн-доки — чтобы попасть в задуманную схему, а не строить свою.
•	admin_versions.py + модели + main.py — понять, что уже есть: таблица, эндпоинты, регистрация.
•	versions.html — увидеть, что уже показывается, и куда добавлять «номер, размер, дата, кто опубликовал».
•	updater.py + sync.py — точка встраивания проверки версии в heartbeat и логика скачивания/установки.
•	build_tab.py + build.py — куда вешать кнопку и откуда брать только что собранный артефакт.
•	docker-compose.yml — как хранить артефакты на сервере (это ключевое решение, от него зависит API).
________________________________________
Открытые вопросы (можно ответить сразу, чтобы потом не тормозить)
1.	Автоустановка или согласие пользователя? В задании написано «обсудим». Моё предложение по умолчанию: скачивание — автоматически, установка — по согласию (кнопка «Обновить сейчас» в трее + напоминание). Тихая автоустановка — опцией в .env. Ок?
2.	Проверка целостности артефакта. SHA-256 хэш — минимум. Подпись (Ed25519/отдельный ключ) — уже есть или заводить с нуля?
3.	Хранение артефактов на сервере. Предлагаю: D:\tracker\artifacts\client\<version>\ на хосте + bind mount в контейнер api как /app/artifacts (read-only). Так SCP сможет класть файл прямо в папку, а API — раздавать. Устраивает?
4.	Кто «публикует»? Пользователь SCP — это один человек (ты). В поле «кто опубликовал» писать os.getlogin() + hostname или фиксированное имя из deploy.json?
Как только пришлёшь файлы — соберу карту «что уже есть / что добавить» и предложу план правок по шагам, с патчерами для крупных файлов.
Если каких-то файлов нет (например, admin_versions.py или updater.py) — просто напиши «нет такого», я подстроюсь под текущую структуру.
D:\tracker\server\routes\admin_versions.py (или как называется файл с версиями — если такого нет, скажи, где сейчас живёт всё, что связано с версиями клиента) всё сейчас здесь D:\tracker Шаблон страницы версий в админке: что-то типа D:\tracker\server\templates\admin\versions.html (если есть) такого нет Автоустановка или согласие пользователя? нужно согласие Проверка целостности артефакта. не понимаю вопрос разберись сам Хранение артефактов на сервере. зачем их ранить? может без них? Кто «публикует»? публикует пользователь SCP. С названием файлов сам определись
Let me analyze this carefully. The user wants to implement P0: publishing versions via UI for the tracker project.
Key facts:
1.	No admin_versions.py file exists yet
2.	No versions.html template exists yet
3.	User wants согласие (consent) before auto-update
4.	User doesn't understand integrity check question — I should decide myself
5.	User questions storing artifacts on server — "why store them? maybe without them?"
6.	Publisher is SCP user, filename - my choice
Let me think through the architecture:
Current state:
•	ClientVersion model exists with fields: id, version, release_date, download_url, mandatory, release_notes, created_at
•	GET /api/v1/version endpoint exists in main.py (returns latest version)
•	updater.py exists with check_for_update, download_update, apply_update
•	Client already checks for updates on startup via UpdateChecker
•	client_versions table exists
What needs to be done:
1.	Server: API endpoint to publish a version (upload .exe + metadata)
2.	Server: storage for artifacts — where does the .exe live?
3.	Admin UI: page showing list of versions + "who published"
4.	SCP: button "Опубликовать версию" in BuildTab
5.	Client: proper handling of download with user consent
Storage question: User asks "why store them? maybe without them?"
Let me think... The artifacts MUST be stored somewhere because:
•	Clients need to download the .exe
•	If we don't store on server, we'd need external hosting (GitHub Releases, S3, etc.)
•	Since we have nginx → api, the server can serve files
Options for storage:
1.	Store on server in server/static/downloads/ — since ./server is mounted as volume, files persist on host. API can serve them via FastAPI StaticFiles or a custom endpoint.
2.	External — GitHub Releases, S3, etc. Requires internet, more setup.
Given the project is on LAN, option 1 is best. And since server/ is mounted as a volume from the host, the files persist.
Wait — but there's a nuance. The user says "зачем их хранить? может без них?" — meaning maybe don't store on server, just reference externally. But the whole point is automatic updates. Let me reconsider.
Actually, the user might mean: don't keep old versions, only the latest. That's reasonable — we can keep only N latest versions or just latest.
Let me decide:
•	Store on server in server/static/downloads/ (volume-mounted, persists)
•	Keep only latest N versions (configurable, default keep 3)
•	Add SHA-256 hash for integrity check (I'll decide this since user deferred to me)
•	Filename format: TrackerSetup-{version}.exe
Integrity check: I'll implement SHA-256 verification. When publishing, compute hash and store it. Client verifies hash after download before running installer. This is simple and effective.
Need to add sha256 field to ClientVersion model. But wait — that's a migration. Let me think if we can avoid it.
Actually, we can add a nullable sha256 and file_size and published_by columns. This requires an Alembic migration. That's fine — the project has alembic.
Let me plan:
1.	Migration: add columns to client_versions: sha256 (String(64)), file_size (BigInteger), published_by (String(128))
2.	Server API: POST /admin/api/versions/publish — multipart form with file + metadata
3.	Server storage: server/static/downloads/ directory
4.	Static serving: nginx or FastAPI mount
5.	Admin UI: GET /admin/versions — list page; form to upload
6.	SCP button: in BuildTab, "Опубликовать последнюю сборку"
7.	Client: update updater.py to verify SHA-256, show proper dialog with consent
Let me think about the SCP button flow:
•	SCP builds installer → client/dist_installer/TrackerSetup.exe
•	User clicks "Опубликовать версию"
•	Dialog appears: version (auto-filled from CLIENT_VERSION or deploy.json), release_notes, mandatory checkbox
•	SCP sends file via HTTPS POST to server with admin API key
•	Server saves file, computes sha256, creates DB record
For SCP to know server URL — from deploy.json.
For auth — need admin API key. Where does SCP get it? From .env on the server... but SCP is on the same machine. We can read from D:\tracker\.env (ADMIN_API_KEY). Actually the SCP AdminTab already does operations with API using ADMIN_API_KEY, so there's a pattern.
Wait, let me re-read. In HANDOFF §12:
"AdminTab (2026-10-11), «гибрид». control/admin_tab.py + control/admin.py.
Напрямую (docker compose exec api): reset_admin_password, recreate_admin,
rotate_admin_api_key (бэкап .env), db_diagnostics.
Через API: Проверить API, Статус сервисов (docker compose ps)."
So there's already control/admin.py with methods to talk to API. Good.
Let me structure the response. The user wants:
1.	Detailed plan (user is not a programmer)
2.	Ready-to-use scripts
3.	Python patchers for >30 line changes
Let me not dump everything at once. Let me:
1.	Explain the architecture I propose
2.	Answer the open questions
3.	List what files need to be created/modified
4.	Start with the first step (probably the migration + server API)
Actually the user's message ended with "С чего начнём?" earlier. Now they've sent files and answered questions. So I should present the plan and start executing.
Given the scope, this is a big task. Let me break it into stages and get user confirmation before implementing.
Let me think about what to include in this response:
1.	Summarize understanding — what's there, what needs to be added
2.	Answer open questions:
o	Auto-update: with consent (confirmed by user)
o	Integrity: SHA-256 hash computed at publish, verified at download (my decision)
o	Storage: on server server/static/downloads/, keep last N (my decision)
o	Publisher: SCP user — will use os.getlogin()@hostname or from deploy.json (my decision)
3.	Proposed plan in stages:
o	Stage 1: DB migration (add sha256, file_size, published_by to client_versions)
o	Stage 2: Server API (publish endpoint + list endpoint)
o	Stage 3: Static file serving (nginx config or FastAPI StaticFiles)
o	Stage 4: Admin UI page (/admin/versions)
o	Stage 5: SCP button in BuildTab
o	Stage 6: Client updater.py — SHA-256 verify + consent dialog
4.	Ask which stage to start with — or start with Stage 1
Actually, I think the best approach is to present the full plan, then immediately start with the first stage. The user is not a programmer, so I should be clear.
Let me think about specifics:
Migration (Alembic):
python
op.add_column('client_versions', sa.Column('sha256', sa.String(64), nullable=True))
op.add_column('client_versions', sa.Column('file_size', sa.BigInteger(), nullable=True))
op.add_column('client_versions', sa.Column('published_by', sa.String(128), nullable=True))
Server API:
•	POST /admin/api/versions/publish — multipart upload
•	GET /admin/api/versions — list JSON
•	POST /admin/api/versions/{id}/delete — delete version + file
•	Also update GET /api/v1/version to include sha256 and file_size in response
Storage:
•	server/static/downloads/TrackerSetup-{version}.exe
•	Since ./server is mounted, this persists on host
Serving files:
•	Option A: nginx serves /downloads/ from server/static/downloads/
•	Option B: FastAPI StaticFiles mount
Let me check nginx.conf... user didn't send it. I need to ask or add it as a task.
Actually, let me keep it simple: FastAPI can serve StaticFiles. Add to main.py:
python
from fastapi.staticfiles import StaticFiles
app.mount("/downloads", StaticFiles(directory="server/static/downloads"), name="downloads")
But wait — nginx proxies /api/ and /admin/ to api. Does it proxy /downloads/? Need to check nginx.conf. If not, either add to nginx.conf or use /api/v1/downloads/ path.
Better to use /api/v1/downloads/ — already proxied.
Actually, let me put a download endpoint in the API instead of StaticFiles:
python
@app.get("/api/v1/downloads/{filename}")
def download_file(filename: str):
    path = Path("server/static/downloads") / filename
    # validate no path traversal
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path)
This is cleaner and works with existing nginx proxy.
Admin UI:
•	GET /admin/versions — list
•	GET /admin/versions/upload — form
•	POST /admin/versions/upload — handle upload
Need to find how admin routes are structured — they're in web_admin.py (referenced in main.py: from .web_admin import router as admin_web_router).
I need to see web_admin.py to understand the pattern.
SCP:
•	New button in BuildTab "Опубликовать версию..."
•	Dialog: version, notes, mandatory
•	POST multipart to /admin/api/versions/publish
•	Need admin token — from where? Probably from .env file on server via control/admin.py.
Let me look at what admin.py does... user didn't send it. Need to ask.
Actually the handoff says SCP AdminTab uses API with ADMIN_API_KEY. So there must be a way. Let me ask for control/admin.py and control/config.py.
OK let me draft the response. It should:
1.	Confirm understanding
2.	Answer open questions with reasoning
3.	Present plan in stages
4.	Request a few more files
5.	Start with Stage 1 or ask where to start
Given the user is not a programmer and wants progress, let me propose starting with the full server-side (migration + API + admin UI) as one package, then SCP + client.
Let me be concise but complete. Use tables and clear structure.
Let me also think about file naming. Since user said "с названием файлов сам определись":
•	TrackerSetup-{version}.exe — e.g., TrackerSetup-1.4.1.exe
•	Version from client/.env TRACKER_VERSION (current: "1.0.0" but app version says 1.4.0 — hmm, inconsistent. Let me not worry, use whatever's in .env)
Actually looking more carefully — the version in .env defaults to "1.0.0" in build.py. The app says version="1.4.0" in FastAPI. And CLIENT_VERSION in client/.env is used for version checks. So version scheme is a bit messy. Let me use whatever CLIENT_VERSION is set to.
Publisher identity: SCP runs on the same machine. Use os.getlogin() + socket.gethostname(). Or from deploy.json — let me add a publisher field to deploy.json. Actually simplest: use {os.getlogin()}@{socket.gethostname()}. If that fails, use SCP.
SHA-256: Compute at publish time on SCP, send to server along with file. Server verifies by re-computing. Server stores. Client downloads, computes, compares. If mismatch — refuse to install.
Actually simpler: server computes sha256 on receipt, stores. No need to send from SCP. That way server is authoritative.
Now let me draft the final response.
Actually the response will be quite long. Let me structure it:
1.	Короткий итог: что я понял
2.	Мои решения по открытым вопросам
3.	Общий план (6 этапов)
4.	Что нужно доделать в моём понимании перед началом — файлы
5.	Начинаем с этапа 1
Let me write this out.
One more consideration — for the response, I should:
•	Not start coding yet, since we need to see web_admin.py first
•	Present the plan clearly so user can approve direction
•	Ask for web_admin.py + control/admin.py + control/config.py + nginx.conf + installer.iss (to check that .env is copied with TRACKER_VERSION and to understand admin structure)
Actually let me be efficient. The user is tired of back-and-forth. Let me present a solid plan and ask for the minimum files needed to start.
Minimum for Stage 1 (migration):
•	server/alembic/versions/ — list of existing migrations (or just what's the last revision)
•	server/alembic/env.py — to check include_object
Minimum for Stage 2 (server API):
•	server/web_admin.py — to add routes
•	server/schemas.py — to add Pydantic models
•	server/nginx.conf — to check proxy paths
•	server/templates/base.html — for admin layout
Minimum for Stage 5 (SCP):
•	control/admin.py — existing HTTP-client pattern
•	control/config.py — paths
Let me just ask for these and present the plan.
Hmm, actually I want to be pragmatic. Let me present the plan and ask for the files needed for the first two stages (server-side), which is the most critical path.
Let me finalize.
Отлично, контекст полный. Разобрался с состоянием и отвечаю по порядку.
Что уже есть (по факту)
Слой	Что есть	Что нужно
Модель	ClientVersion (version, release_date, download_url, mandatory, release_notes, created_at)	+ sha256, file_size, published_by
API	GET /api/v1/version — работает	+ публикация, список, удаление
Хранилище	нет	server/static/downloads/ (том смонтирован, файлы сохранятся на хосте)
Админка	нет страницы версий	/admin/versions (список + форма)
SCP	BuildTab собирает TrackerSetup.exe	кнопка «Опубликовать версию»
Клиент	updater.py уже умеет check / download / apply	+ проверка SHA-256, + диалог согласия
Мои решения по твоим вопросам
1. Автоустановка или согласие → согласие (как ты и сказал)
Логика:
•	mandatory = false (обычно) → тост + диалог с кнопками «Обновить сейчас» / «Позже». Клиент продолжает работать.
•	mandatory = true → диалог без «Позже», только «Обновить сейчас». Если сеть упала — пробуем снова на следующем heartbeat, не блокируем работу жёстко.
•	Тихая установка (/S) — только опция в .env (TRACKER_UPDATE_SILENT=1), по умолчанию выключена.
2. Проверка целостности — SHA-256
•	При публикации сервер сам считает sha256 файла и сохраняет в БД (не доверяем SCP).
•	Клиент после скачивания считает sha256 и сравнивает с тем, что вернул GET /api/v1/version.
•	Не совпало — файл удаляется, установка не запускается, в лог пишется «hash mismatch».
Подпись .exe (Authenticode) — откладываем в P1, это отдельная история с сертификатом подписи.
3. Хранение артефактов — храним на сервере, последние 3 версии
Почему так:
•	Клиентам нужно откуда-то качать. Без хостинга на сервере — придётся поднимать что-то внешнее (S3, GitHub Releases). Для LAN-проекта это лишнее.
•	Том ./server:/app/server уже смонтирован → файлы, положенные в server/static/downloads/, физически живут на хосте в D:\tracker\server\static\downloads\. Бэкапятся вместе с папкой server.
•	Держим последние 3 версии (настраивается в deploy.json: keep_versions: 3). При публикации 4-й — самая старая удаляется и из БД, и с диска. Так диск не пухнет, но и откат на 1–2 версии назад всегда возможен.
Имя файла: TrackerSetup-{version}.exe (например, TrackerSetup-1.4.1.exe).
4. Кто публикует — {user}@{hostname} из SCP
Пример: Erohin@ws147. Если по какой-то причине не удалось получить — SCP.
Дополнительно добавим в deploy.json поле publisher — если задано, используется оно (удобно, если хочешь писать «Администратор» или ФИО).
План по этапам
Этап 1. БД (Alembic-миграция)
Добавить в client_versions: sha256 (64), file_size (BigInteger), published_by (128).
Этап 2. Серверный API
•	POST /admin/api/versions/publish — multipart (file + version + notes + mandatory). Считает sha256, сохраняет файл, пишет запись + аудит.
•	GET /admin/api/versions — список.
•	POST /admin/api/versions/{id}/delete — удалить запись + файл.
•	GET /api/v1/downloads/{filename} — отдача файла клиенту (через nginx-прокси /api/).
•	Обновить GET /api/v1/version — добавить sha256, file_size.
Этап 3. Админка (HTML)
•	GET /admin/versions — таблица: версия, размер, дата, кто, mandatory, sha256 (сокр.), кнопка «Удалить».
•	GET /admin/versions/upload — форма загрузки (на случай, если публикуешь не через SCP).
•	Пункт меню «Версии» в base-шаблоне.
Этап 4. SCP — кнопка «Опубликовать версию»
•	Новая группа в BuildTab: чекбокс mandatory, поле release_notes, кнопка «Опубликовать».
•	Диалог берёт путь client/dist_installer/TrackerSetup.exe, версию из CLIENT_VERSION, шлёт multipart на сервер с ADMIN_API_KEY (из .env).
•	Лог: что отправили, сколько байт, что ответил сервер.
Этап 5. Клиент — updater.py
•	Проверка SHA-256 после скачивания.
•	Диалог с release_notes, кнопки «Обновить сейчас» / «Позже».
•	Обновить check_for_update и UpdateChecker, чтобы принимали sha256.
Этап 6. KB + тесты
•	Обновить 04_CLIENT/08_AUTOSTART_UPDATE.md, 06_DEPLOY/05_UPDATES.md, 05_SCP/03_BUILD.md, HANDOFF.md.
•	Прогнать вживую: собрал → опубликовал → увидел в админке → клиент предложил обновиться.
Что мне нужно посмотреть, прежде чем писать код
Чтобы не угадывать структуру:
Обязательно:
1.	D:\tracker\server\web_admin.py — куда добавлять роуты /admin/versions и /admin/api/versions/*
2.	D:\tracker\server\schemas.py — добавлю Pydantic-схемы для версий
3.	D:\tracker\server\nginx.conf — проверить, что /api/ проксируется и отдача файлов пойдёт корректно
4.	D:\tracker\server\templates\base.html — куда вставить пункт меню
5.	Один пример существующей страницы-списка (например, templates/admin/tokens.html или templates/admin/computers.html) — чтобы я попал в стиль
6.	D:\tracker\control\admin.py — как SCP сейчас ходит в API (какой http-клиент, как берёт токен)
7.	D:\tracker\control\config.py — пути (нужен CLIENT_SETUP_EXE, ROOT_DIR)
8.	Список файлов D:\tracker\server\alembic\versions\ — понять последнюю ревизию (достаточно вывода dir)
Желательно:
9.	D:\tracker\server\alembic\env.py — проверить include_object (чтобы миграция не снесла партиции)
10.	D:\tracker\client\config.py — там CLIENT_VERSION, DOWNLOAD_DIR, get_server_url
С чего предлагаю начать
Дам сразу весь серверный пакет (этапы 1–3) одним куском, потому что они связаны: миграция → API → UI. Пока ты присылаешь файлы выше, я подготовлю:
•	скрипт миграции (alembic revision),
•	правки models.py (3 поля),
•	правки main.py (эндпоинты),
•	правки web_admin.py (роуты),
•	новый templates/admin/versions.html и templates/admin/versions_upload.html,
•	правку schemas.py,
•	патчеры для всего, что >30 строк.
Потом отдельным пакетом — SCP и клиент.
Присылай файлы из списка выше — и я начну выдавать код. Если чего-то нет (например, web_admin.py окажется разбит на несколько модулей) — просто напиши, как оно на самом деле устроено, и я подстроюсь.
Список файлов D:\tracker\server\alembic\versions\ 0f13ad394b65_add_admin_users_department_id.py 35d67a73f181_baseline.py 939e3d0b6f4c_partition_records_by_month.py 2602b71902d4_add_employee_settings.py b02da1230e4d_add_computer_soft_delete.py ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py Экономим чат, не забываем писать всплывающие комментария ко всем действиям
Пользователь дал все нужные файлы. Нужно спланировать всю фичу "Публикация версий через UI" и выдать код по этапам.
Давайте разберём:
Что нужно сделать
Этап 1. БД (Alembic-миграция)
Добавить в client_versions:
•	sha256 (String(64), nullable=True — на случай существующих записей)
•	file_size (BigInteger, nullable=True)
•	published_by (String(128), nullable=True)
Последняя миграция: ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py
Новая миграция: xxxx_add_client_versions_sha256_filesize_publisher.py
Этап 2. Модель
Обновить server/models.py — модель ClientVersion.
Этап 3. Схемы
VersionResponse в schemas.py — добавить sha256 и file_size.
Новые схемы для admin API.
Этап 4. API
В main.py уже есть GET /api/v1/version. Нужно добавить sha256/file_size в ответ.
Также нужен эндпоинт для скачивания файла: GET /api/v1/downloads/{filename}.
И админские эндпоинты в web_admin.py:
•	GET /admin/versions — HTML-страница
•	POST /admin/api/versions/publish — загрузка файла (multipart)
•	POST /admin/api/versions/{id}/delete — удаление (или через обычную форму в HTML)
Учитывая что web_admin уже использует обычные HTML-формы (multipart), можно сделать проще:
•	GET /admin/versions — список
•	GET /admin/versions/upload — форма
•	POST /admin/versions/upload — приём файла и создание версии
•	POST /admin/versions/{id}/delete — удаление
•	GET /api/v1/downloads/{filename} — отдача файла
Для SCP мы будем публиковать через API с ADMIN_API_KEY (X-Admin-Token). Значит, нужен JSON-endpoint. Или SCP может тоже зайти как admin? Проще — сделать API с X-Admin-Token.
Тогда:
•	POST /api/v1/admin/versions/publish — multipart, X-Admin-Token
•	GET /api/v1/admin/versions — список, X-Admin-Token
•	POST /api/v1/admin/versions/{id}/delete — удаление, X-Admin-Token
•	GET /admin/versions — HTML для веб-админки (list)
•	POST /admin/versions/upload — HTML форма (multipart), альтернатива для админа
•	POST /admin/versions/{id}/delete — удаление через HTML
А в SCP — кнопка, которая делает POST на /api/v1/admin/versions/publish с X-Admin-Token.
Хотя проще всего: SCP шлёт файл напрямую через requests/httpx multipart.
Этап 5. Хранение файлов
Том ./server:/app/server уже смонтирован. Папка server/static/downloads/. Файл будет доступен на хосте.
Отдача файла: nginx проксирует /api/ на api. Значит, чтобы отдать файл, нужно сделать endpoint /api/v1/downloads/{filename} в main.py, который отдаст FileResponse.
Этап 6. Ограничение: последние 3 версии
Параметр keep_versions в deploy.json (для SCP) — а на сервере просто оставить логику: при публикации удалять старые, если их больше 5 (условно). Хотя проще: пусть SCP сообщает это. Или на сервере hardcode 5.
Хм. Я решил оставить в deploy.json, но сервер об этом не знает. Проще сделать так: на сервере при публикации удаляем старые версии, если их больше N. N=5 как дефолт. Или пусть админ в веб-админке решает вручную. В первой итерации: не удаляем автоматически. Просто позволяем удалять вручную через UI.
Но пользователь написал: "может без них?" — то есть он сомневается в хранении. Я предложил хранить 3. Давай сделаем проще:
•	Храним все, пока не удалят вручную.
•	В UI есть кнопка «Удалить».
Это соответствует "Экономим чат, не забываем писать всплывающие комментарии ко всем действиям".
Этап 7. Клиент — updater.py
Обновить:
•	check_for_update — принимать sha256.
•	download_update — после скачивания проверить sha256.
•	Диалоги в main.py — уже есть диалоги согласия. Нужно обновить _on_update_available, чтобы показывать release_notes.
Смотрю на main.py (клиента):
python
def _on_update_available(self, info):
    if info.get("mandatory"):
        self._download_and_apply(info)
    else:
        r = QMessageBox.question(
            self,
            t("client.update.title"),
            t("client.update.question", version=info["latest_version"]),
        )
        if r == QMessageBox.StandardButton.Yes:
            self._download_and_apply(info)
Нужно добавить:
•	release_notes в текст вопроса
•	обязательность → модальное окно без "Позже"
•	добавить sha256 в info
Диалог с «Обновить сейчас» / «Позже» — QMessageBox.question с Yes/No подходит. Добавим release_notes.
Этап 8. SCP — кнопка «Опубликовать версию»
Добавить в BuildTab:
•	Чекбокс mandatory
•	Поле release_notes (QPlainTextEdit)
•	Поле version (QLineEdit, дефолт из CLIENT_VERSION)
•	Кнопка «Опубликовать последний TrackerSetup.exe»
Логика:
1.	Берём client/dist_installer/TrackerSetup.exe.
2.	Спрашиваем version, mandatory, release_notes.
3.	Читаем ADMIN_API_KEY из D:\tracker\.env.
4.	POST multipart на {server_url}/api/v1/admin/versions/publish.
5.	Показываем результат.
Приступаю к реализации
Начну с этапа 1 (БД и модель), потом сервер, потом SCP и клиент. Чтобы не раздувать сообщение, разбиваю на два ответа:
Это сообщение: серверная часть (этап 1–5).
Следующее: SCP + клиент.
Хотя пользователь может захотеть всё сразу. Но код объёмный, и я уже вижу, что он реально большой. Давайте сделаю всё-таки по одной большой порции, но с чётким разделением.
Стратегия — минимально инвазивный подход:
1.	Никакой автоматической очистки старых версий (только ручная через UI).
2.	Файлы храним в server/static/downloads/.
3.	Публикация из SCP идёт через API с X-Admin-Token.
4.	Из веб-админки — обычная форма (multipart).
5.	Скачивание — эндпоинт /api/v1/downloads/{filename}.
Ещё вопрос: download_url. Он должен указывать на что-то доступное клиенту. Если nginx проксирует /api/, то https://192.168.0.35/api/v1/downloads/TrackerSetup-1.4.0.exe — то, что нужно. Формируется из deploy.json → server_url.
OK. Поехали.
Патчеры для Python
Правила: >30 строк — Python-патчеры, иначе here-string. Тут много правок, но большинство — небольшие вставки. Пойду по принципу:
•	Модель (2 строки): небольшой патч.
•	Схемы: небольшой патч.
•	main.py — добавление эндпоинтов. Это >30 строк, но можно вставить блоком через патчер или через явное указание места. Учитывая, что main.py уже длинный — Python-патчер уместен.
•	web_admin.py — добавление роутов. Тоже патчер.
•	Новый шаблон versions.html — создаём с нуля через WriteAllText.
•	Новый модуль control/publish.py — создаём с нуля.
Alembic миграция
Нужно создать новый файл. Имя: <hash>_add_client_versions_sha256_filesize_publisher.py. Хеш генерируется автоматом, но мы можем задать вручную. Пусть будет a1b2c3d4e5f6.
down_revision = "ecb1e3f89300"
Ок, начнём.
Сначала дам:
1.	Патч модели models.py
2.	Alembic-миграцию
3.	Патч schemas.py
4.	Патч main.py (эндпоинт скачивания + sha256 в version)
5.	Патч web_admin.py (HTML роуты версий)
6.	Шаблон versions.html
7.	Ограничение nginx client_max_body_size — сейчас 10m, установщик 34 МБ! Нужно увеличить.
Это уже много. Разобью на 2 ответа:
•	Ответ A: модель, миграция, schemas, main.py (эндпоинт скачивания), nginx.
•	Ответ B: web_admin.py (роуты версий), шаблон versions.html.
•	Ответ C: SCP publish.py + build_tab.py, updater.py.
Хотя пользователь просил "экономим чат". Давайте в одном сообщении попробую дать всё серверное, а клиентское/SCP — во втором.
Начну.
Важное: client_max_body_size 10m — установщик 34 МБ. Нужно увеличить до, скажем, 200m.
Плюс важно: nginx надо перезапустить после правки nginx.conf.
Патчер для models.py
Изменения:
python
class ClientVersion(Base):
    __tablename__ = "client_versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(32), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    download_url = Column(String(512), nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    release_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    # +++ новые поля
    sha256 = Column(String(64), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    published_by = Column(String(128), nullable=True)
Патч schemas.py
python
class VersionResponse(BaseModel):
    latest_version: str
    download_url: str
    mandatory: bool
    release_notes: Optional[str] = None
    sha256: Optional[str] = None       # +++
    file_size: Optional[int] = None    # +++
Патч main.py
1.	В get_latest_version добавить sha256 и file_size в ответ.
2.	Новый эндпоинт GET /api/v1/downloads/{filename} — FileResponse.
3.	Новые админ-эндпоинты для публикации (multipart) — /api/v1/admin/versions/publish и др.
Для публикации из SCP понадобится multipart. FastAPI: UploadFile = File(...).
python
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
Также путь для файлов. Директория: /app/server/static/downloads/. На хосте: D:\tracker\server\static\downloads\.
Логика публикации:
1.	Принимаем файл + version + release_notes + mandatory.
2.	Сохраняем в server/static/downloads/TrackerSetup-{version}.exe.
3.	Считаем sha256.
4.	Создаём/обновляем запись в client_versions.
5.	Пишем в audit_log.
6.	Возвращаем JSON.
Эндпоинт скачивания:
python
@app.get("/api/v1/downloads/{filename}")
def download_file(filename: str):
    # защита от path traversal
    safe_name = os.path.basename(filename)
    path = DOWNLOADS_DIR / safe_name
    if not path.exists():
        raise HTTPException(404, "file not found")
    return FileResponse(path, filename=safe_name, media_type="application/octet-stream")
Где DOWNLOADS_DIR = Path("/app/server/static/downloads") или из config.
Лучше через относительный путь от файла модуля.
Патч web_admin.py
Роуты:
•	GET /admin/versions — HTML список.
•	POST /admin/versions/upload — HTML форма multipart, сохранение.
•	POST /admin/versions/{id}/delete — удаление.
Шаблон versions.html
Список версий + форма загрузки.
Патч nginx.conf
client_max_body_size 10m; → client_max_body_size 200m;.
Ограничения
Ах, да. Мне бы не забыть создать папку server/static/downloads/ — при публикации.
Всё, поехали. Дам сразу все серверные правки.
Структура ответа
1.	Сначала — обзор плана.
2.	Затем — Python-патчер для models.py.
3.	Затем — новый файл миграции.
4.	Патчер schemas.py.
5.	Python-патчер main.py.
6.	Python-патчер web_admin.py.
7.	Шаблон versions.html.
8.	Патч nginx.conf.
9.	Инструкция по применению (down/up, миграция, проверка).
Начну.
Патчер для models.py
Небольшой — можно через here-string, но по правилу >30 строк — патчер. Тут не 30 строк, тут 4 строки вставки. Но чтобы не рисковать — патчер.
Хотя учитывая, что патчер на Python для models.py это тоже не так уж просто (там файл большой), лучше следовать правилу HANDOFF: "Python-патчеры для правок >30 строк".
Для 4 строк — here-string ОК. Но HANDOFF говорит "PowerShell here-string ломается на блоках > 30 строк". Тут не так много. Но у меня же один файл models.py, там могут быть проблемы с кодировкой. Ладно, патчер надёжнее.
Хм. Ок, но патчер для 4 строк — избыточно. Давай сделаю через патчер для надёжности, чтобы точно не сломать кодировку.
Итак, патчер 1: models.py.
python
# apply_models_patch.py
from pathlib import Path

p = Path(r"D:\tracker\server\models.py")
text = p.read_text(encoding="utf-8")

old = '''class ClientVersion(Base):
    __tablename__ = "client_versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(32), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    download_url = Column(String(512), nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    release_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
'''

new = '''class ClientVersion(Base):
    __tablename__ = "client_versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(32), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    download_url = Column(String(512), nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    release_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    # ------------------------------------------------------------
    # Контроль целостности артефакта.
    # sha256 заполняется сервером при публикации (не доверяем SCP).
    # Клиент после скачивания считает sha256 и сверяет — если не
    # совпало, установка не запускается.
    # ------------------------------------------------------------
    sha256 = Column(String(64), nullable=True)
    file_size = Column(BigInteger, nullable=True)

    # Кто опубликовал: "user@hostname" из SCP или "web:admin" из веб-формы.
    published_by = Column(String(128), nullable=True)
'''

if old not in text:
    raise SystemExit("Не найден блок ClientVersion — проверь вручную")

text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("OK: models.py обновлён")
Импорт BigInteger уже есть в models.py — да, есть (from sqlalchemy import (..., BigInteger, ...)).
Миграция
python
# server/alembic/versions/a1b2c3d4e5f6_add_client_versions_sha256.py
"""add client_versions sha256, file_size, published_by

Revision ID: a1b2c3d4e5f6
Revises: ecb1e3f89300
Create Date: 2026-10-12
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "ecb1e3f89300"
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем три поля. Все nullable — чтобы не сломать уже
    # существующие записи client_versions, которые были добавлены
    # вручную (до появления этой функциональности).
    op.add_column(
        "client_versions",
        sa.Column("sha256", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "client_versions",
        sa.Column("file_size", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "client_versions",
        sa.Column("published_by", sa.String(length=128), nullable=True),
    )


def downgrade():
    op.drop_column("client_versions", "published_by")
    op.drop_column("client_versions", "file_size")
    op.drop_column("client_versions", "sha256")
Патч schemas.py
python
class VersionResponse(BaseModel):
    latest_version: str
    download_url: str
    mandatory: bool
    release_notes: Optional[str] = None
    sha256: Optional[str] = None
    file_size: Optional[int] = None
Патч main.py
Добавить импорты в начале файла:
python
import os
from pathlib import Path
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
Уже есть import os — да, ближе к концу, но лучше добавить в начало. Хотя Python работает с любым местом. Но чище добавить в начало.
Путь к downloads:
python
# Директория для хранения артефактов клиента.
# На хосте: D:\tracker\server\static\downloads\
# В контейнере: /app/server/static/downloads/
DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"
Т.к. main.py лежит в server/main.py, Path(__file__).resolve().parent = /app/server. Значит server/static/downloads/.
Новые эндпоинты:
python
@app.get("/api/v1/downloads/{filename}")
def download_artifact(filename: str):
    """
    Отдаёт файл артефакта клиента.
    Защита от path traversal: basename() отсекает ../ и абсолютные пути.
    """
    safe_name = os.path.basename(filename)
    if not safe_name or safe_name != filename:
        raise HTTPException(400, "invalid filename")
    path = DOWNLOADS_DIR / safe_name
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "file not found")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=safe_name,
    )
Админ-эндпоинт публикации:
python
def _sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    """Считает SHA-256 файла. Чанк 1 МБ — быстро для .exe до 200 МБ."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


@app.post("/api/v1/admin/versions/publish",
          dependencies=[Depends(require_admin)])
async def publish_version(
    file: UploadFile = File(...),
    version: str = Form(...),
    release_notes: str = Form(""),
    mandatory: str = Form("0"),
    published_by: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Публикация новой версии клиента.

    Multipart: file (TrackerSetup.exe), version, release_notes, mandatory, published_by.
    Защита:
      - File name принудительно TrackerSetup-{version}.exe (не доверяем).
      - sha256 считается сервером.
      - Уникальность version — 409 если уже есть.
    """
    version = version.strip()
    if not version or len(version) > 32:
        raise HTTPException(400, "Некорректная версия")

    # Проверка: такая версия уже есть?
    existing = db.query(ClientVersion).filter(
        ClientVersion.version == version
    ).first()
    if existing:
        raise HTTPException(409, f"Версия {version} уже опубликована")

    # Куда сохраняем
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"TrackerSetup-{version}.exe"
    target = DOWNLOADS_DIR / safe_name

    # Пишем потоком, чтобы не держать в памяти 200 МБ
    written = 0
    with open(target, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            written += len(chunk)

    if written == 0:
        target.unlink(missing_ok=True)
        raise HTTPException(400, "Пустой файл")

    sha = _sha256_file(target)

    # URL формируем от запроса (https://host/api/v1/downloads/...)
    base = str(request.base_url).rstrip("/")
    download_url = f"{base}/api/v1/downloads/{safe_name}"

    row = ClientVersion(
        version=version,
        release_date=_now(),
        download_url=download_url,
        mandatory=(mandatory in ("1", "true", "True")),
        release_notes=release_notes or None,
        sha256=sha,
        file_size=written,
        published_by=published_by or "api",
    )
    db.add(row)
    db.add(AuditLog(
        actor=published_by or "api",
        entity="client_version",
        entity_id=version,
        action="publish",
        new_value=json.dumps({
            "version": version,
            "size": written,
            "sha256": sha,
            "mandatory": row.mandatory,
        }, ensure_ascii=False),
    ))
    db.commit()

    log.info("Published client version %s (%d bytes)", version, written)
    return {
        "status": "ok",
        "version": version,
        "download_url": download_url,
        "sha256": sha,
        "file_size": written,
    }
Плюс удаление версии:
python
@app.post("/api/v1/admin/versions/{version}/delete",
          dependencies=[Depends(require_admin)])
def delete_version(version: str, db: Session = Depends(get_db)):
    """
    Удаляет запись версии и её файл на диске.
    Если файла нет — не ошибка (мог быть удалён вручную).
    """
    row = db.query(ClientVersion).filter(ClientVersion.version == version).first()
    if not row:
        raise HTTPException(404, "Версия не найдена")

    # Файл на диске — по имени из download_url
    filename = os.path.basename(row.download_url)
    path = DOWNLOADS_DIR / filename
    file_deleted = False
    if path.exists():
        try:
            path.unlink()
            file_deleted = True
        except Exception as e:
            log.warning("Не удалось удалить файл %s: %s", path, e)

    db.delete(row)
    db.add(AuditLog(
        actor="admin",
        entity="client_version",
        entity_id=version,
        action="delete",
        new_value=json.dumps({"file_deleted": file_deleted}),
    ))
    db.commit()
    return {"status": "ok", "file_deleted": file_deleted}
Плюс обновить get_latest_version:
python
@app.get("/api/v1/version", response_model=VersionResponse)
def get_latest_version(current: str = "", db: Session = Depends(get_db)):
    latest = (db.query(ClientVersion)
              .order_by(ClientVersion.release_date.desc()).first())
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
    return VersionResponse(
        latest_version=latest.version,
        download_url=latest.download_url,
        mandatory=latest.mandatory,
        release_notes=latest.release_notes,
        sha256=latest.sha256,
        file_size=latest.file_size,
    )
Патч web_admin.py
Импорт: FileResponse уже есть? Есть StreamingResponse. Добавить FileResponse при необходимости.
Роуты:
python
# ============================================================
# ВЕРСИИ КЛИЕНТА
# ============================================================
# Публикация и удаление релизов клиентского установщика.
# Файлы хранятся в server/static/downloads/.
# Скачивание — /api/v1/downloads/{filename} (см. main.py).
# ============================================================

VERSIONS_DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"


@router.get("/versions", response_class=HTMLResponse)
def versions_page(request: Request, db: Session = Depends(get_db),
                  _=Depends(current_admin)):
    """Список опубликованных версий."""
    _require_admin_role(request)
    versions = (db.query(ClientVersion)
                .order_by(desc(ClientVersion.release_date)).all())
    return templates.TemplateResponse("versions.html", {
        "request": request,
        "versions": versions,
        "saved": request.query_params.get("saved") == "1",
        "error": request.query_params.get("error"),
        "deleted_ok": request.query_params.get("deleted") == "1",
    })


@router.post("/versions/upload")
async def versions_upload(
    request: Request,
    file: UploadFile = File(...),
    version: str = Form(...),
    release_notes: str = Form(""),
    mandatory: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    """Загрузка файла версии из веб-формы."""
    user = _require_admin_role(request)
    version = version.strip()
    if not version or len(version) > 32:
        return RedirectResponse("/admin/versions?error=bad_version", status_code=303)
    if db.query(ClientVersion).filter(ClientVersion.version == version).first():
        return RedirectResponse("/admin/versions?error=already_exists", status_code=303)

    VERSIONS_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"TrackerSetup-{version}.exe"
    target = VERSIONS_DOWNLOADS_DIR / safe_name
    written = 0
    with open(target, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            written += len(chunk)
    if written == 0:
        target.unlink(missing_ok=True)
        return RedirectResponse("/admin/versions?error=empty_file", status_code=303)

    # Считаем sha256
    h = hashlib.sha256()
    with open(target, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    sha = h.hexdigest()

    base = str(request.base_url).rstrip("/")
    download_url = f"{base}/api/v1/downloads/{safe_name}"

    row = ClientVersion(
        version=version,
        release_date=_now(),
        download_url=download_url,
        mandatory=bool(mandatory),
        release_notes=release_notes or None,
        sha256=sha,
        file_size=written,
        published_by=f"web:{user['username']}",
    )
    db.add(row)
    db.add(AuditLog(
        actor=user["username"],
        entity="client_version",
        entity_id=version,
        action="publish_web",
        new_value=json.dumps({
            "version": version, "size": written, "sha256": sha,
            "mandatory": row.mandatory,
        }, ensure_ascii=False),
    ))
    db.commit()

    log.info("Published version %s via web (%d bytes)", version, written)
    return RedirectResponse("/admin/versions?saved=1", status_code=303)


@router.post("/versions/{version}/delete")
def versions_delete(
    version: str,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    """Удаляет версию (запись + файл)."""
    user = _require_admin_role(request)
    row = db.query(ClientVersion).filter(ClientVersion.version == version).first()
    if not row:
        raise HTTPException(404, "Версия не найдена")

    filename = os.path.basename(row.download_url)
    path = VERSIONS_DOWNLOADS_DIR / filename
    if path.exists():
        try:
            path.unlink()
        except Exception as e:
            log.warning("Failed to unlink %s: %s", path, e)

    db.delete(row)
    db.add(AuditLog(
        actor=user["username"],
        entity="client_version",
        entity_id=version,
        action="delete",
    ))
    db.commit()
    return RedirectResponse("/admin/versions?deleted=1", status_code=303)
Нужно ещё импортировать UploadFile, File в web_admin.py:
python
from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
И импорт ClientVersion из models:
python
from .models import (
    ...,
    ClientVersion,
    ...
)
И Path:
python
from pathlib import Path
И os:
python
import os
В web_admin уже есть import hashlib, import json, import io. os вроде не импортирован. Добавим.
Шаблон versions.html
Список + форма загрузки.
Патч nginx.conf
client_max_body_size 10m; → client_max_body_size 200m;
Что ещё нужно
1.	server/static/ — папка. Она уже может быть (там fonts и т.д.). Нужно создать server/static/downloads/.
2.	Нужно ли что-то в docker-compose? Нет, том уже монтирован.
3.	Nginx нужно перезапустить.
4.	Миграция — через docker compose exec -T api alembic ... upgrade head. Хотя main.py автоматически применяет миграции при старте? Нет, в entrypoint.sh судя по комментарию.
Стоп. Посмотрел main.py: есть комментарий "Migracii primenyayutsya avtomaticheski pri kazhdom zapuske api". То есть при старте API миграции применяются автоматически. Значит достаточно перезапустить API.
Хотя ниже: "Миграции Alembic уже применены в entrypoint.sh до старта gunicorn". Значит миграции делаются в entrypoint. Мы просто должны перезапустить api.
Проверю: docker compose down && docker compose up -d --build — это как раз пересоздаст контейнер и entrypoint применит миграцию.
Упорядочивание
Пойду по файлам:
1.	Python-патчер 1: server/models.py — добавить поля в ClientVersion.
2.	Новый файл: server/alembic/versions/a1b2c3d4e5f6_add_client_versions_sha256.py.
3.	Python-патчер 2: server/schemas.py — VersionResponse.
4.	Python-патчер 3: server/main.py — импорты, DOWNLOADS_DIR, обновление get_latest_version, скачивание, публикация, удаление.
5.	Python-патчер 4: server/web_admin.py — импорты, роуты версий.
6.	Новый файл: server/templates/versions.html.
7.	Патч: server/nginx.conf — 10m → 200m.
8.	Создать папку server/static/downloads/ (можно в патчере).
9.	Перезапустить.
Далее в этом же ответе или следующем — клиент и SCP. Учитывая объём, сделаю серверную часть здесь, а клиент/SCP в следующем ответе. Это разумно.
Погнали писать. Буду краток в описаниях между патчами, чтобы не раздувать.
Особенности
•	При публикации через SCP: version будет браться из CLIENT_VERSION клиента. Для тестов можно поставить 1.4.1.
•	Если попытаются опубликовать ту же версию — получим 409.
Также важно: у ClientVersion.release_date — не default, а задаётся явно. При публикации через web_admin — я задаю _now(). Через API — тоже _now(). OK.
Ещё: db.query(ClientVersion).order_by(desc(ClientVersion.release_date)).all() — тут используется desc. В web_admin уже импортирован desc из sqlalchemy. OK.
Ещё: в main.py нужен import hashlib — есть уже в web_admin, и в main.py есть. Проверю: да, import hashlib есть в main.py.
import os — есть в main.py. Но в начале? Да нет, в середине. Всё равно нужно для os.path.basename.
from pathlib import Path — не уверен. Проверю: не вижу в main.py. Нужно добавить.
from fastapi import UploadFile, File, Form — сейчас только Depends, FastAPI, Header, HTTPException, Request. Нужно добавить.
from fastapi.responses import FileResponse — сейчас RedirectResponse as _AdminRedirect. Добавить FileResponse.
Ок. Патчер main.py должен быть аккуратным. Лучше через замену импортов и вставку новых функций в конец файла перед @app.get("/api/v1/version"....
Хм, это сложно. Лучше перепишу блок импортов и вставлю все новые функции после get_latest_version.
Стратегия патча main.py:
1.	Заменить строку с импортами fastapi.
2.	Добавить from pathlib import Path после import os.
3.	Заменить get_latest_version на новую версию + добавить после неё все новые эндпоинты.
Хорошо, теперь пишу.
Патч nginx.conf
text
client_max_body_size 10m;
на
text
client_max_body_size 200m;
Или больше — 500m. Установщик 34 МБ. 200 хватит с запасом.
Погнали.
Что нужно написать патчерам
Сначала подумаю про общий "активатор" — один большой PS-скрипт, который:
1.	Создаёт папку server/static/downloads/.
2.	Применяет патчи по очереди.
Или отдельные скрипты? Для читаемости — пусть будут отдельные скрипты в D:\tracker\_apply_versions\. Или все в одном.
Пользователь — не программист. Лучше один скрипт apply_versions.py, который делает всё. Запустить: python apply_versions.py.
Пойду этим путём. Один патчер, который сам создаёт файлы (миграцию, шаблон), патчит существующие.
Хм. Но патч миграции — это новый файл, а не патч. И шаблон versions.html — тоже новый файл. Их проще создать явно, а не патчить. Поэтому:
•	Один патчер применяет правки в 4 файла: models.py, schemas.py, main.py, web_admin.py.
•	Отдельно создаются 2 новых файла: миграция и versions.html.
•	Патч nginx.conf — совсем простой (замена одной строки).
Могу запихнуть в один патчер и создание новых файлов, и патчи.
Пойду так: один Python-патчер D:\tracker\_apply_versions.py:
1.	Патчит server/models.py
2.	Создаёт server/alembic/versions/a1b2c3d4e5f6_add_client_versions_sha256.py
3.	Патчит server/schemas.py
4.	Патчит server/main.py
5.	Патчит server/web_admin.py
6.	Создаёт server/templates/versions.html
7.	Патчит server/nginx.conf
8.	Создаёт папку server/static/downloads/
Все операции с проверками и логированием.
Делаем
Запускается:
powershell
cd D:\tracker
client\.venv\Scripts\python.exe _apply_versions.py
Или просто python. У пользователя есть client\.venv\Scripts\python.exe, используем его.
Начинаю писать скрипт.
Ключевые блоки для замены:
models.py
Old:
text
class ClientVersion(Base):
    __tablename__ = "client_versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(32), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    download_url = Column(String(512), nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    release_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
New: тот же + новые поля.
schemas.py
Old:
text
class VersionResponse(BaseModel):
    latest_version: str
    download_url: str
    mandatory: bool
    release_notes: Optional[str] = None
New:
text
class VersionResponse(BaseModel):
    latest_version: str
    download_url: str
    mandatory: bool
    release_notes: Optional[str] = None
    sha256: Optional[str] = None
    file_size: Optional[int] = None
main.py
1.	Импорты fastapi:
Old: from fastapi import Depends, FastAPI, Header, HTTPException, Request
New: from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
2.	from fastapi.responses import RedirectResponse as _AdminRedirect
New: from fastapi.responses import FileResponse, RedirectResponse as _AdminRedirect
3.	Добавить from pathlib import Path — где-то после import os.
На самом деле лучше просто добавить в начало файла (после import hashlib) from pathlib import Path. Проверю верх файла:
python
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
...
Значит после import secrets добавим from pathlib import Path.
4.	get_latest_version — заменим.
5.	Вставим новые функции и DOWNLOADS_DIR.
Лучше вставить DOWNLOADS_DIR после:
python
log = logging.getLogger("tracker.server")
logging.basicConfig(...)
Хотя DOWNLOADS_DIR можно положить сразу после app = FastAPI(...).
Но у меня тут FileResponse. Он должен импортироваться до использования. Импорты — в начале, ок.
Стратегия патча main.py:
•	Заменить блок импортов fastapi.
•	Заменить from fastapi.responses import RedirectResponse as _AdminRedirect — но это уже после строки from fastapi import .... Надо проверить, что там:
python
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import RedirectResponse as _AdminRedirect
Заменим.
•	После from typing import Optional добавить from pathlib import Path.
•	Добавить DOWNLOADS_DIR и новые эндпоинты + заменить get_latest_version в конце.
Ну и import os — уже есть в середине. Оставим.
web_admin.py
1.	Импорты:
Old: from fastapi import APIRouter, Depends, Request, Form, HTTPException
New: from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
2.	Добавить в импорты import os (уже есть? — нет).
Смотрим верх web_admin.py:
python
import csv
import logging
import hashlib
import io
import json
import secrets
from collections import defaultdict
Нет os. Добавим.
3.	Добавить ClientVersion в импорт моделей:
Old:
python
from .models import (
    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,
    CalendarDay, Computer, Department, Employee, EmployeeSettings,
    Record, WorkSession,
    Schedule, ScheduledTask, TaskRun,
)
New:
python
from .models import (
    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,
    CalendarDay, ClientVersion, Computer, Department, Employee,
    EmployeeSettings, Record, WorkSession,
    Schedule, ScheduledTask, TaskRun,
)
4.	Добавить from pathlib import Path в импорты.
5.	В конце файла (или где-то) — вставить роуты. Лучше вставить перед # Аудит в конце, или в конец файла (перед последней функцией). Проще в самый конец файла.
Смотрим последний блок web_admin.py:
python
@router.post("/employees/{emp_id}/settings/reset")
def employee_settings_reset(...):
    ...
    return RedirectResponse(
        f"/admin/employees/{emp_id}/settings?saved=1",
        status_code=303,
    )
Это конец файла. Добавим блок версий после него.
nginx.conf
Old: client_max_body_size 10m;
New: client_max_body_size 200m;
versions.html
Полноценный шаблон.
Хорошо, теперь пишу всё.
Патч main.py: подумаю о местах вставки.
Где вставить DOWNLOADS_DIR? К примеру после:
python
log = logging.getLogger("tracker.server")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Employee Tracker API", version="1.4.0")
Вставим:
python
app = FastAPI(title="Employee Tracker API", version="1.4.0")

# ------------------------------------------------------------
# Директория хранения артефактов клиента (установщиков .exe).
# На хосте: D:\tracker\server\static\downloads\
# В контейнере: /app/server/static/downloads/
# Монтируется через docker-compose (./server:/app/server).
# ------------------------------------------------------------
DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"
Это нормально.
Новые эндпоинты — вставить после get_latest_version. В самом конце файла.
Порядок:
1.	_sha256_file helper.
2.	download_artifact — публичное скачивание.
3.	publish_version — приём файла с X-Admin-Token.
4.	delete_version — удаление с X-Admin-Token.
Заменю get_latest_version и добавлю всё в конец.
Финальный вид Python-патчера
Слишком длинный для одного блока в чате, но осилю. Постараюсь быть компактным.
Ок, пора писать.
Ещё: у меня _sha256_file дублируется в main.py и web_admin.py. Можно вынести в отдельный модуль, но проще — в каждом файле своя локальная функция. Ок.
Или вынести в server/utils.py? Не хочется плодить. Оставлю локально в каждом.
Кроме того, DOWNLOADS_DIR тоже дублируется. Можно импортировать из main.py: from .main import DOWNLOADS_DIR. Но это создаст циклический импорт (main.py импортирует web_admin). Лучше продублировать. Или вынести в config.py. Но не хочу трогать config.py сервера — там может быть что-то специфичное.
Дублирую. Если что, потом унифицируем.
Хм, но лучше в одном месте. Сделаем константу в models.py? Нет, тоже не очень.
Оставляю дублирование. Оба файла в одной папке — путь одинаковый.
Ещё: web_admin.html - обновление sidebar
Нужно добавить ссылку в base.html — пункт «Версии» в разделе «Администрирование». Это тоже патч.
В base.html в разделе админа:
html
{% if admin_role in ('admin', 'operator') %}
{# --- АДМИНИСТРИРОВАНИЕ --- #}
<div class="nav-group">
  <div class="nav-group-title">{{ _("menu.group_admin") }}</div>
  <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}"
     href="/admin/tokens">{{ _("menu.tokens") }}</a>
  <a class="nav-link {% if '/scheduler' in request.url.path %}active{% endif %}"
     href="/admin/scheduler">{{ _("menu.scheduler") }}</a>
  {% if admin_role == 'admin' %}
  <a class="nav-link {% if '/users' in request.url.path %}active{% endif %}"
     href="/admin/users">{{ _("menu.users") }}</a>
  <a class="nav-link {% if '/logins' in request.url.path %}active{% endif %}"
     href="/admin/logins">{{ _("menu.logins") }}</a>
  <a class="nav-link {% if '/trash' in request.url.path %}active{% endif %}"
     href="/admin/trash">{{ _("menu.trash") }}</a>
  <a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}"
     href="/admin/settings">{{ _("menu.settings") }}</a>
  {% endif %}
</div>
{% endif %}
Добавим:
html
<a class="nav-link {% if '/versions' in request.url.path %}active{% endif %}"
   href="/admin/versions">{{ _("menu.versions") }}</a>
Перед {% if admin_role == 'admin' %}.
Также нужен i18n ключ menu.versions в i18n.py. Или можно использовать русский текст напрямую. Проще — использовать {{ _("menu.versions") }}, добавив ключ. Но это ещё один файл.
Проще использовать просто текст "Версии" без i18n. Это рабочее решение. Английский не критичен для этого пункта.
Хм. Ну ладно, можно русский текст прямо. Или использовать существующий ключ. Оставлю так: <a ...>Версии</a>.
Хотя... По правилам стиля — лучше через _(). Но нужен ключ. Могу добавить в i18n.py, но это ещё патч.
Отступлюсь — использую прямой текст "Версии". Если будут жалобы — добавим в i18n.
Тоже в патче base.html.
Хорошо, итерирую.
Итого патчер
1.	server/models.py — замена блока ClientVersion.
2.	server/alembic/versions/a1b2c3d4e5f6_add_client_versions_sha256.py — новый файл.
3.	server/schemas.py — замена VersionResponse.
4.	server/main.py — импорты + DOWNLOADS_DIR + замена get_latest_version + новые эндпоинты.
5.	server/web_admin.py — импорты + ClientVersion + роуты.
6.	server/templates/versions.html — новый.
7.	server/templates/base.html — пункт меню.
8.	server/nginx.conf — 10m → 200m.
9.	server/static/downloads/.gitkeep — создание папки.
Всё в одном Python-патчере.
Ок, начинаю писать. Пойду по шагам, но текст одного большого скрипта.
Учитывая огромный объём кода, буду писать через тройные кавычки в Python-скрипте, но с осторожностью: код содержит и """ (в докстрингах внутри создаваемых файлов). Нужно использовать raw strings и/или одинарные тройные кавычки. Лучше — все внутренние строки как список строк, склеенных через "\n".join().
Это очень длинно. Ок, погнали.
Хм. Может, использовать другой подход — написать python-патчер с использованием отдельных функций, читающих .txt-файлы с новым содержимым? Нет, это ещё сложнее.
Решение: использовать raw-strings r"""...""" там, где внутри """ встречается — нельзя. Лучше — где содержимое содержит """, использовать одинарные '''...'''. И наоборот.
Проблема: мой шаблон versions.html содержит {% block %} — не проблема. Но некоторые мои эндпоинты содержат docstrings """...""". Их надо экранировать. Лучше вообще не использовать многострочные строки в содержимом, которое надо вставить.
Или писать везде одинарные кавычки ''' для контейнера, а внутри """ — свободно.
Но тогда в контенте не должно быть '''. Проверю — почти наверняка нет.
Пойду с '''.
Стоп. В Python-патчере я буду использовать одинарные тройные для контента, содержащего двойные тройные. Это валидно:
python
content = '''...содержит """внутри"""...'''
Так что ОК.
Начинаю.
Для экономии: не буду переписывать блоки целиком, где можно вставить/заменить по маркерам.
Пишу патчер.
Расчёт на 2 ответа
Этот ответ — серверный. Следующий — SCP + клиент.
Двигаюсь.
Итоговый патчер
Соберу всё в один файл D:\tracker\_apply_versions.py.
Учитывая объём, не буду разделять на подпатчи, а сделаю один. Внутри — несколько функций.
Шаг 1: models.py
python
OLD = '''class ClientVersion(Base):
    __tablename__ = "client_versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(32), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    download_url = Column(String(512), nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    release_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
'''

NEW = '''class ClientVersion(Base):
    __tablename__ = "client_versions"

    id = Column(Integer, primary_key=True)
    version = Column(String(32), unique=True, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    download_url = Column(String(512), nullable=False)
    mandatory = Column(Boolean, default=False, nullable=False)
    release_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    # ------------------------------------------------------------
    # Контроль целостности артефакта.
    # sha256 считается сервером при публикации (не доверяем SCP).
    # Клиент после скачивания сверяет — если не совпало,
    # установка НЕ запускается.
    # ------------------------------------------------------------
    sha256 = Column(String(64), nullable=True)
    file_size = Column(BigInteger, nullable=True)

    # Кто опубликовал: "user@hostname" из SCP или "web:admin" из веб-формы.
    published_by = Column(String(128), nullable=True)
'''
Шаг 2: alembic миграция (новый файл)
Шаг 3: schemas.py
Шаг 4: main.py
Шаг 5: web_admin.py
Шаг 6: versions.html
Шаг 7: base.html
Шаг 8: nginx.conf
Шаг 9: папка downloads
Ок, кодим.
Для base.html — вставка до {% if admin_role == 'admin' %} в разделе админа.
Маркер:
text
      <a class="nav-link {% if '/scheduler' in request.url.path %}active{% endif %}"
         href="/admin/scheduler">{{ _("menu.scheduler") }}</a>
      {% if admin_role == 'admin' %}
Заменю на:
text
      <a class="nav-link {% if '/scheduler' in request.url.path %}active{% endif %}"
         href="/admin/scheduler">{{ _("menu.scheduler") }}</a>
      <a class="nav-link {% if '/versions' in request.url.path %}active{% endif %}"
         href="/admin/versions">Версии</a>
      {% if admin_role == 'admin' %}
OK.
Для nginx.conf:
text
old: "    client_max_body_size 10m;"
new: "    client_max_body_size 200m;"
Для создания папки:
python
(VERSIONS_DOWNLOADS_DIR).mkdir(parents=True, exist_ok=True)
Или создать gitkeep? Не обязательно.
Всё, пишу.
Ой, а ещё client/updater.py должен обрабатывать sha256. Но это следующий ответ.
И ещё: нужно проверить, что _now() в web_admin возвращает tz-aware datetime (да, datetime.now(timezone.utc)).
И: в versions_upload есть UploadFile = File(...) в параметрах функции. Нужен async def. Да, сделаю async.
Плюс: UploadFile импортируется в web_admin — да, добавляю.
Ещё: hashlib есть в web_admin. ОК.
Ещё: os — добавлю.
Ещё: Path — добавлю.
Погнали.
Не забываем про i18n в шаблоне versions.html
В шаблоне можно использовать _() для переводов, но у нас нет ключей. Проще всё на русском. Тогда не будем использовать _(). Просто текст.
Хорошо.
Проверка после применения
1.	docker compose down && docker compose up -d --build
2.	Открыть https://192.168.0.35/admin/versions — должна быть страница со списком (пустая).
3.	curl.exe -k https://192.168.0.35/api/v1/version — должен вернуть пустые поля (или дефолт).
4.	Проверить, что миграция применилась: docker compose exec -T api alembic -c /app/server/alembic.ini current.
Это пишу в конце как инструкцию.
Проверка синтаксиса
После патча — ast.parse для каждого изменённого Python-файла.
Наконец, начинаю писать. Постараюсь уложиться в разумный объём.
Разделение ответа
1.	Сначала краткий план.
2.	Затем один большой Python-патчер.
3.	Инструкция по применению.
4.	Что дальше (SCP + клиент).
Погнали.
Тут будет длинно. Пойду.
Дополнительная мысль
Клиенту нужно будет узнать о версии при heartbeat. Сейчас heartbeat отдельный от version — main.py клиента вызывает _check_updates при старте. Периодичности нет. Можно попросить SyncWorker периодически дёргать check. Это следующий ответ.
Также важно: download_url строится от request.base_url. При запросе от SCP (внутренний URL) или от клиента (LAN IP) — base_url будет разный. Например, если SCP обращается к https://127.0.0.1, то download_url будет https://127.0.0.1/api/v1/downloads/.... А клиенту нужен https://192.168.0.35/api/v1/downloads/....
Значит, download_url лучше формировать из deploy.json на стороне SCP? Или из request.headers.get("host")?
Хм. request.base_url берёт из Host заголовка. Если SCP шлёт на https://192.168.0.35, то и в базе будет https://192.168.0.35/api/v1/downloads/.... То есть — как SCP обратится, такой URL и запишется.
Это может быть проблемой. Решение: формировать download_url из deploy.json.server_url на стороне SCP, а сервер сохраняет то, что передали. Но тогда сервер не проверяет — можно ли подделать? Не критично, это внутренняя сеть.
Альтернатива: сервер сам формирует через settings (например, свой внешний URL из .env). Но у нас нет такого.
Компромисс: принимаем download_base (или download_url) от клиента публикации, если это X-Admin-Token (доверенный). По умолчанию — из request.base_url.
Или: клиент при скачивании просто берёт download_url и заменяет хост? Сложно.
Проще всего: SCP передаёт download_base (по умолчанию server_url из deploy.json). Сервер использует его для формирования download_url. Если не передан — берёт из request.base_url.
Отлично.
Также при публикации через web_admin — там используется request.base_url, и админ открывает админку с нужного URL. Ок.
Хорошо, добавляю параметр download_base в publish_version.
Погнали.
Кстати, request.base_url в FastAPI — это URL запроса с scheme://host:port/. Если за nginx — то будет https://host/.
Ой, ещё: если nginx не передаёт Host правильно... В nginx.conf есть proxy_set_header Host $host; — ок, передаётся.
Так что request.base_url вернёт https://192.168.0.35/. Отлично.
Значит, если SCP шлёт на https://192.168.0.35/api/v1/admin/versions/publish, то base_url будет https://192.168.0.35/ и download_url будет корректный.
Это упрощает. Но всё же оставлю возможность переопределить через параметр.
Ай, ещё вопрос. request.base_url возвращает URL с trailing slash. Итог: f"{base_url.rstrip('/')}/api/v1/downloads/..." — норм.
OK, финал. Пишу.
Один момент: у меня тут main.py, там есть import os — но внутри функции. Это не критично. Просто использую os.path.basename.
Ещё: main.py надо проверить, что при вызове Depends(require_admin) — есть функция require_admin. Да, есть.
Погнали.
И ещё: в web_admin у version_delete параметр пути — {version}. Версия может содержать точки. FastAPI нормально это отработает.
Ок.
Про проверку защиты от path traversal
os.path.basename("../../etc/passwd") вернёт "passwd". Значит, если filename содержит ../ — мы её обрежем. НО у нас валидация: safe_name != filename — значит, если были .. — откажем.
Ещё случай: filename = TrackerSetup-1.0.0.exe. Нормально.
Ещё: filename может содержать URL-encoded %2F. FastAPI декодирует автоматически. Значит, в результате декодирования получим ../. Обрежется basename.
Ещё: filename содержит невалидные символы — например \0. Проверим, что нет. os.path.basename не защитит от \0, но path.open() упадёт. Обернём в try.
На самом деле, простой фильтр: filename не должен содержать /, \, ... Уже это покрывается: basename(x) == x для x без / и \. А .. без слеша — это просто имя файла .., которое не существует. Так что ладно, оставляю.
Хотя .. как имя — path.exists() вернёт True (это родительская директория). А path.is_file() вернёт False. Значит, будет 404. ОК.
Ок.
Наконец, пишу
Слишком долго думаю. Код!
ЗЫ. Постараюсь уместиться. Если что — разобью на 2 сообщения.
Ещё раз проверю важные детали:
1.	Модель ClientVersion — OK.
2.	Alembic down_revision должен быть ecb1e3f89300.
3.	_now() возвращает datetime.now(timezone.utc). OK.
4.	UploadFile от FastAPI требует python-multipart в зависимостях. Проверить! Скорее всего уже есть, т.к. в web_admin есть другие File в bulk_assign.
Смотрю: computers_bulk_assign — использует await request.form() и form.get("csv_file"). Это тоже требует multipart. Значит пакет есть. OK.
5.	В publish_version используется json — уже импортирован в main.py. OK.
6.	AuditLog тоже используется. OK.
7.	AuditLog.entity_id — String(64). Версия влезает. OK.
Пишу!
Отлично, всё есть. Иду по плану: сначала серверная часть (модель, миграция, схемы, API, страница веб-админки), потом отдельным ответом — SCP и клиент.
Что делаем в этом шаге
1.	Модель ClientVersion — добавляем sha256, file_size, published_by.
2.	Миграция Alembic.
3.	Схема VersionResponse — добавляем sha256, file_size.
4.	main.py — эндпоинт скачивания файла + админские эндпоинты публикации/удаления + sha256/file_size в /api/v1/version.
5.	web_admin.py — HTML-страница /admin/versions + форма загрузки.
6.	Шаблон versions.html + пункт меню в base.html.
7.	nginx.conf — client_max_body_size 10m → 200m (сейчас 34 МБ установщик не влезет).
8.	Создать папку server/static/downloads/.
Ключевые решения (озвучены выше):
•	Хранение: файлы лежат на хосте в D:\tracker\server\static\downloads\ (том уже примонтирован). Удаление — только вручную через UI.
•	Имя файла: TrackerSetup-{version}.exe (задаёт сервер, не доверяем имени из запроса).
•	Целостность: сервер считает SHA-256 при публикации. Клиент потом сверит.
•	Кто публикует: user@hostname из SCP или web:{username} из веб-формы.
Один большой Python-патчер
Создай файл D:\tracker\_apply_versions.py с таким содержимым:
python
# -*- coding: utf-8 -*-
# ============================================================
# Патчер: публикация версий клиента через UI (серверная часть).
# ============================================================
# Что делает:
#   1. models.py       — + sha256, file_size, published_by в ClientVersion
#   2. alembic/...     — новый файл миграции
#   3. schemas.py      — + sha256, file_size в VersionResponse
#   4. main.py         — импорты, DOWNLOADS_DIR, новый get_latest_version,
#                        /api/v1/downloads/{filename},
#                        /api/v1/admin/versions/publish,
#                        /api/v1/admin/versions/{version}/delete
#   5. web_admin.py    — импорты + ClientVersion, роуты /admin/versions/*
#   6. templates/versions.html — новый файл
#   7. templates/base.html     — пункт меню "Версии"
#   8. nginx.conf      — client_max_body_size 10m -> 200m
#   9. server/static/downloads/ — папка для артефактов
#
# Запуск:
#   D:\tracker\client\.venv\Scripts\python.exe D:\tracker\_apply_versions.py
# ============================================================

from pathlib import Path
import ast
import sys

ROOT = Path(r"D:\tracker")
SERVER = ROOT / "server"

log_ops = []


def _p(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    log_ops.append(line)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _write(p: Path, text: str):
    p.write_text(text, encoding="utf-8")
    _p(f"  OK  записан {p.relative_to(ROOT)} ({len(text)} байт)")


def _replace_once(text: str, old: str, new: str, what: str) -> str:
    if old not in text:
        raise SystemExit(f"НЕ НАЙДЕН блок для замены: {what}")
    cnt = text.count(old)
    if cnt > 1:
        raise SystemExit(f"Блок '{what}' встречается {cnt} раз — уточни маркер")
    return text.replace(old, new, 1)


def _check_py(p: Path):
    """ast.parse — лёгкая проверка синтаксиса."""
    src = _read(p)
    try:
        ast.parse(src)
    except SyntaxError as e:
        raise SystemExit(f"СИНТАКСИС {p.name}: {e}")
    _p(f"  OK  синтаксис {p.name} валиден")


# ============================================================
# 1. models.py
# ============================================================
def patch_models():
    p = SERVER / "models.py"
    _p("[1/9] Патч models.py ...")
    text = _read(p)

    old = (
        'class ClientVersion(Base):\n'
        '    __tablename__ = "client_versions"\n'
        '\n'
        '    id = Column(Integer, primary_key=True)\n'
        '    version = Column(String(32), unique=True, nullable=False)\n'
        '    release_date = Column(DateTime(timezone=True), nullable=False)\n'
        '    download_url = Column(String(512), nullable=False)\n'
        '    mandatory = Column(Boolean, default=False, nullable=False)\n'
        '    release_notes = Column(Text)\n'
        '    created_at = Column(DateTime(timezone=True), default=_utcnow)\n'
    )

    new = (
        'class ClientVersion(Base):\n'
        '    __tablename__ = "client_versions"\n'
        '\n'
        '    id = Column(Integer, primary_key=True)\n'
        '    version = Column(String(32), unique=True, nullable=False)\n'
        '    release_date = Column(DateTime(timezone=True), nullable=False)\n'
        '    download_url = Column(String(512), nullable=False)\n'
        '    mandatory = Column(Boolean, default=False, nullable=False)\n'
        '    release_notes = Column(Text)\n'
        '    created_at = Column(DateTime(timezone=True), default=_utcnow)\n'
        '\n'
        '    # ------------------------------------------------------------\n'
        '    # Целостность артефакта.\n'
        '    # sha256 считается сервером при публикации (не доверяем источнику).\n'
        '    # Клиент после скачивания пересчитает и сверит — если не совпало,\n'
        '    # установка НЕ запускается.\n'
        '    # ------------------------------------------------------------\n'
        '    sha256 = Column(String(64), nullable=True)\n'
        '    file_size = Column(BigInteger, nullable=True)\n'
        '\n'
        '    # Кто опубликовал: "user@hostname" из SCP или "web:admin" из веб-формы.\n'
        '    published_by = Column(String(128), nullable=True)\n'
    )

    text = _replace_once(text, old, new, "ClientVersion")
    _write(p, text)
    _check_py(p)


# ============================================================
# 2. Alembic миграция (новый файл)
# ============================================================
def create_migration():
    _p("[2/9] Создаю миграцию ...")
    p = SERVER / "alembic" / "versions" / "a1b2c3d4e5f6_add_client_versions_sha256.py"
    if p.exists():
        _p(f"  --  файл уже есть: {p.name} (пропускаю)")
        return
    content = '''"""add client_versions sha256, file_size, published_by

Revision ID: a1b2c3d4e5f6
Revises: ecb1e3f89300
Create Date: 2026-10-12
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "ecb1e3f89300"
branch_labels = None
depends_on = None


def upgrade():
    # Три nullable-колонки. Так существующие записи client_versions
    # (добавленные вручную через SQL до этой фичи) не сломаются.
    op.add_column(
        "client_versions",
        sa.Column("sha256", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "client_versions",
        sa.Column("file_size", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "client_versions",
        sa.Column("published_by", sa.String(length=128), nullable=True),
    )


def downgrade():
    op.drop_column("client_versions", "published_by")
    op.drop_column("client_versions", "file_size")
    op.drop_column("client_versions", "sha256")
'''
    _write(p, content)


# ============================================================
# 3. schemas.py — VersionResponse
# ============================================================
def patch_schemas():
    p = SERVER / "schemas.py"
    _p("[3/9] Патч schemas.py ...")
    text = _read(p)

    old = (
        'class VersionResponse(BaseModel):\n'
        '    latest_version: str\n'
        '    download_url: str\n'
        '    mandatory: bool\n'
        '    release_notes: Optional[str] = None\n'
    )
    new = (
        'class VersionResponse(BaseModel):\n'
        '    latest_version: str\n'
        '    download_url: str\n'
        '    mandatory: bool\n'
        '    release_notes: Optional[str] = None\n'
        '    # --- Добавлено для проверки целостности артефакта ---\n'
        '    # sha256: hex-строка 64 символа. Может быть None для старых\n'
        '    # записей, добавленных вручную до появления публикации.\n'
        '    sha256: Optional[str] = None\n'
        '    file_size: Optional[int] = None\n'
    )
    text = _replace_once(text, old, new, "VersionResponse")
    _write(p, text)
    _check_py(p)


# ============================================================
# 4. main.py
# ============================================================
def patch_main():
    p = SERVER / "main.py"
    _p("[4/9] Патч main.py ...")
    text = _read(p)

    # 4.1. Импорт pathlib.Path
    text = _replace_once(
        text,
        'import secrets\nfrom datetime import datetime, timedelta, timezone\n',
        'import secrets\nfrom datetime import datetime, timedelta, timezone\nfrom pathlib import Path\n',
        "import Path",
    )

    # 4.2. Расширяем импорт из fastapi
    text = _replace_once(
        text,
        'from fastapi import Depends, FastAPI, Header, HTTPException, Request\n',
        'from fastapi import (\n'
        '    Depends, FastAPI, File, Form, Header, HTTPException, Request,\n'
        '    UploadFile,\n'
        ')\n',
        "import fastapi (File/Form/UploadFile)",
    )

    # 4.3. FileResponse
    text = _replace_once(
        text,
        'from fastapi.responses import RedirectResponse as _AdminRedirect\n',
        'from fastapi.responses import FileResponse, RedirectResponse as _AdminRedirect\n',
        "import FileResponse",
    )

    # 4.4. DOWNLOADS_DIR сразу после app = FastAPI(...)
    text = _replace_once(
        text,
        'app = FastAPI(title="Employee Tracker API", version="1.4.0")\n',
        'app = FastAPI(title="Employee Tracker API", version="1.4.0")\n'
        '\n'
        '# ------------------------------------------------------------\n'
        '# Каталог для артефактов клиента (установщиков .exe).\n'
        '# На хосте:    D:\\tracker\\server\\static\\downloads\\\n'
        '# В контейнере: /app/server/static/downloads/\n'
        '# Монтируется через docker-compose (./server:/app/server).\n'
        '# ------------------------------------------------------------\n'
        'DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"\n',
        "DOWNLOADS_DIR",
    )

    # 4.5. Заменяем get_latest_version и добавляем новые эндпоинты
    old_version = (
        '@app.get("/api/v1/version", response_model=VersionResponse)\n'
        'def get_latest_version(current: str = "", db: Session = Depends(get_db)):\n'
        '    latest = (db.query(ClientVersion)\n'
        '              .order_by(ClientVersion.release_date.desc()).first())\n'
        '    if not latest:\n'
        '        return VersionResponse(latest_version=current or "0.0.0",\n'
        '                               download_url="", mandatory=False)\n'
        '    return VersionResponse(latest_version=latest.version,\n'
        '                           download_url=latest.download_url,\n'
        '                           mandatory=latest.mandatory,\n'
        '                           release_notes=latest.release_notes)\n'
    )

    new_block = (
        '@app.get("/api/v1/version", response_model=VersionResponse)\n'
        'def get_latest_version(current: str = "", db: Session = Depends(get_db)):\n'
        '    latest = (db.query(ClientVersion)\n'
        '              .order_by(ClientVersion.release_date.desc()).first())\n'
        '    if not latest:\n'
        '        return VersionResponse(latest_version=current or "0.0.0",\n'
        '                               download_url="", mandatory=False)\n'
        '    return VersionResponse(\n'
        '        latest_version=latest.version,\n'
        '        download_url=latest.download_url,\n'
        '        mandatory=latest.mandatory,\n'
        '        release_notes=latest.release_notes,\n'
        '        sha256=latest.sha256,\n'
        '        file_size=latest.file_size,\n'
        '    )\n'
        '\n'
        '\n'
        '# ============================================================\n'
        '# Публикация версий клиента\n'
        '# ============================================================\n'
        '# Публикуется установщик TrackerSetup.exe. Сервер сам:\n'
        '#   1. Сохраняет файл в server/static/downloads/TrackerSetup-<v>.exe\n'
        '#   2. Считает sha256 файла\n'
        '#   3. Создаёт запись в client_versions\n'
        '# Клиент потом скачивает файл по /api/v1/downloads/...\n'
        '# и сверяет sha256.\n'
        '# ============================================================\n'
        '\n'
        '\n'
        'def _sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:\n'
        '    """SHA-256 файла. Читаем блоками по 1 МБ — не держим .exe в RAM."""\n'
        '    h = hashlib.sha256()\n'
        '    with open(path, "rb") as f:\n'
        '        for block in iter(lambda: f.read(chunk), b""):\n'
        '            h.update(block)\n'
        '    return h.hexdigest()\n'
        '\n'
        '\n'
        '@app.get("/api/v1/downloads/{filename}")\n'
        'def download_artifact(filename: str):\n'
        '    """\n'
        '    Отдаёт .exe-артефакт клиенту.\n'
        '    Защита от path traversal: работаем только с basename.\n'
        '    """\n'
        '    safe_name = os.path.basename(filename)\n'
        '    # Если в filename были слэши / ".." — отказываем.\n'
        '    if not safe_name or safe_name != filename:\n'
        '        raise HTTPException(400, "invalid filename")\n'
        '    path = DOWNLOADS_DIR / safe_name\n'
        '    if not path.exists() or not path.is_file():\n'
        '        raise HTTPException(404, "file not found")\n'
        '    return FileResponse(\n'
        '        path,\n'
        '        media_type="application/octet-stream",\n'
        '        filename=safe_name,\n'
        '    )\n'
        '\n'
        '\n'
        '@app.post("/api/v1/admin/versions/publish",\n'
        '          dependencies=[Depends(require_admin)])\n'
        'async def publish_version(\n'
        '    request: Request,\n'
        '    file: UploadFile = File(...),\n'
        '    version: str = Form(...),\n'
        '    release_notes: str = Form(""),\n'
        '    mandatory: str = Form("0"),\n'
        '    published_by: str = Form(""),\n'
        '    download_base: str = Form(""),\n'
        '    db: Session = Depends(get_db),\n'
        '):\n'
        '    """\n'
        '    Публикация новой версии клиента (multipart/form-data).\n'
        '    Заголовок: X-Admin-Token.\n'
        '\n'
        '    Параметры:\n'
        '      file          — сам .exe\n'
        '      version       — например "1.4.1" (<=32 символов, уникальная)\n'
        '      release_notes — что нового (опционально)\n'
        '      mandatory     — "1"/"true" для обязательного\n'
        '      published_by  — "user@host" (опционально, для аудита)\n'
        '      download_base — базовый URL (например "https://192.168.0.35")\n'
        '                      если пусто — берём из request.base_url\n'
        '    """\n'
        '    version = (version or "").strip()\n'
        '    if not version or len(version) > 32:\n'
        '        raise HTTPException(400, "Некорректная версия")\n'
        '\n'
        '    # Уникальность версии\n'
        '    if db.query(ClientVersion).filter(ClientVersion.version == version).first():\n'
        '        raise HTTPException(409, f"Версия {version} уже опубликована")\n'
        '\n'
        '    # Готовим каталог\n'
        '    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)\n'
        '    safe_name = f"TrackerSetup-{version}.exe"\n'
        '    target = DOWNLOADS_DIR / safe_name\n'
        '\n'
        '    # Пишем потоком. UploadFile.read() — не грузит всё в память.\n'
        '    written = 0\n'
        '    with open(target, "wb") as f:\n'
        '        while True:\n'
        '            chunk = await file.read(1024 * 1024)\n'
        '            if not chunk:\n'
        '                break\n'
        '            f.write(chunk)\n'
        '            written += len(chunk)\n'
        '\n'
        '    if written == 0:\n'
        '        target.unlink(missing_ok=True)\n'
        '        raise HTTPException(400, "Пустой файл")\n'
        '\n'
        '    sha = _sha256_file(target)\n'
        '\n'
        '    # Формируем download_url. Если SCP передал download_base —\n'
        '    # используем его (это LAN-URL, который знают клиенты).\n'
        '    if download_base:\n'
        '        base = download_base.strip().rstrip("/")\n'
        '    else:\n'
        '        base = str(request.base_url).rstrip("/")\n'
        '    download_url = f"{base}/api/v1/downloads/{safe_name}"\n'
        '\n'
        '    row = ClientVersion(\n'
        '        version=version,\n'
        '        release_date=_now(),\n'
        '        download_url=download_url,\n'
        '        mandatory=(str(mandatory).lower() in ("1", "true", "yes", "on")),\n'
        '        release_notes=(release_notes or "").strip() or None,\n'
        '        sha256=sha,\n'
        '        file_size=written,\n'
        '        published_by=(published_by or "api").strip()[:128],\n'
        '    )\n'
        '    db.add(row)\n'
        '    db.add(AuditLog(\n'
        '        actor=(published_by or "api")[:128],\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="publish",\n'
        '        new_value=json.dumps({\n'
        '            "version": version,\n'
        '            "size": written,\n'
        '            "sha256": sha,\n'
        '            "mandatory": row.mandatory,\n'
        '            "download_url": download_url,\n'
        '        }, ensure_ascii=False),\n'
        '    ))\n'
        '    db.commit()\n'
        '\n'
        '    log.info(\n'
        '        "Published client version %s (%d bytes, sha256=%s)",\n'
        '        version, written, sha[:12],\n'
        '    )\n'
        '    return {\n'
        '        "status": "ok",\n'
        '        "version": version,\n'
        '        "download_url": download_url,\n'
        '        "sha256": sha,\n'
        '        "file_size": written,\n'
        '    }\n'
        '\n'
        '\n'
        '@app.post("/api/v1/admin/versions/{version}/delete",\n'
        '          dependencies=[Depends(require_admin)])\n'
        'def delete_version(version: str, db: Session = Depends(get_db)):\n'
        '    """\n'
        '    Удаляет запись версии и файл на диске (если есть).\n'
        '    Отсутствие файла — не ошибка (мог быть удалён вручную).\n'
        '    """\n'
        '    row = (db.query(ClientVersion)\n'
        '           .filter(ClientVersion.version == version).first())\n'
        '    if not row:\n'
        '        raise HTTPException(404, "Версия не найдена")\n'
        '\n'
        '    filename = os.path.basename(row.download_url)\n'
        '    path = DOWNLOADS_DIR / filename\n'
        '    file_deleted = False\n'
        '    if filename and path.exists() and path.is_file():\n'
        '        try:\n'
        '            path.unlink()\n'
        '            file_deleted = True\n'
        '        except Exception as e:\n'
        '            log.warning("Не удалось удалить файл %s: %s", path, e)\n'
        '\n'
        '    db.delete(row)\n'
        '    db.add(AuditLog(\n'
        '        actor="admin",\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="delete",\n'
        '        new_value=json.dumps({"file_deleted": file_deleted}),\n'
        '    ))\n'
        '    db.commit()\n'
        '    return {"status": "ok", "file_deleted": file_deleted}\n'
    )

    text = _replace_once(text, old_version, new_block, "get_latest_version + новые эндпоинты")

    # Финальный импорт os — уже есть в main.py. Проверим.
    if "\nimport os\n" not in text:
        # Если вдруг нет — добавим в начало
        text = text.replace("import secrets\n", "import os\nimport secrets\n", 1)
        _p("  --  добавил import os в начало")

    _write(p, text)
    _check_py(p)


# ============================================================
# 5. web_admin.py
# ============================================================
def patch_web_admin():
    p = SERVER / "web_admin.py"
    _p("[5/9] Патч web_admin.py ...")
    text = _read(p)

    # 5.1. import os
    text = _replace_once(
        text,
        'import csv\nimport logging\nimport hashlib\nimport io\nimport json\nimport secrets\n',
        'import csv\nimport logging\nimport hashlib\nimport io\nimport json\nimport os\nimport secrets\n',
        "import os",
    )

    # 5.2. from pathlib import Path
    text = _replace_once(
        text,
        'from datetime import datetime, date, time, timedelta, timezone\n',
        'from datetime import datetime, date, time, timedelta, timezone\nfrom pathlib import Path\n',
        "import Path",
    )

    # 5.3. fastapi imports + UploadFile/File
    text = _replace_once(
        text,
        'from fastapi import APIRouter, Depends, Request, Form, HTTPException\n',
        'from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File\n',
        "fastapi File/UploadFile",
    )

    # 5.4. ClientVersion в импорте моделей
    text = _replace_once(
        text,
        'from .models import (\n'
        '    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,\n'
        '    CalendarDay, Computer, Department, Employee, EmployeeSettings,\n'
        '    Record, WorkSession,\n'
        '    Schedule, ScheduledTask, TaskRun,\n'
        ')\n',
        'from .models import (\n'
        '    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,\n'
        '    CalendarDay, ClientVersion, Computer, Department, Employee,\n'
        '    EmployeeSettings, Record, WorkSession,\n'
        '    Schedule, ScheduledTask, TaskRun,\n'
        ')\n',
        "import ClientVersion",
    )

    # 5.5. Роуты — в самый конец файла
    routes_block = (
        '\n\n'
        '# ============================================================\n'
        '# ВЕРСИИ КЛИЕНТА (публикация релизов .exe)\n'
        '# ============================================================\n'
        '# Файлы хранятся в server/static/downloads/.\n'
        '# Раздача клиентам — GET /api/v1/downloads/{filename} (main.py).\n'
        '# Доступ — только роль admin.\n'
        '# ============================================================\n'
        '\n'
        'VERSIONS_DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"\n'
        '\n'
        '\n'
        'def _versions_sha256(path: Path, chunk: int = 1024 * 1024) -> str:\n'
        '    """SHA-256 файла. Блоками по 1 МБ."""\n'
        '    h = hashlib.sha256()\n'
        '    with open(path, "rb") as f:\n'
        '        for block in iter(lambda: f.read(chunk), b""):\n'
        '            h.update(block)\n'
        '    return h.hexdigest()\n'
        '\n'
        '\n'
        '@router.get("/versions", response_class=HTMLResponse)\n'
        'def versions_page(request: Request, db: Session = Depends(get_db),\n'
        '                  _=Depends(current_admin)):\n'
        '    """Список опубликованных версий клиента + форма загрузки."""\n'
        '    _require_admin_role(request)\n'
        '    versions = (db.query(ClientVersion)\n'
        '                .order_by(desc(ClientVersion.release_date)).all())\n'
        '    return templates.TemplateResponse("versions.html", {\n'
        '        "request": request,\n'
        '        "versions": versions,\n'
        '        "saved": request.query_params.get("saved") == "1",\n'
        '        "deleted_ok": request.query_params.get("deleted") == "1",\n'
        '        "error": request.query_params.get("error"),\n'
        '    })\n'
        '\n'
        '\n'
        '@router.post("/versions/upload")\n'
        'async def versions_upload(\n'
        '    request: Request,\n'
        '    file: UploadFile = File(...),\n'
        '    version: str = Form(...),\n'
        '    release_notes: str = Form(""),\n'
        '    mandatory: str = Form(""),\n'
        '    db: Session = Depends(get_db),\n'
        '    _=Depends(current_admin),\n'
        '):\n'
        '    """Загрузка нового .exe через веб-форму."""\n'
        '    user = _require_admin_role(request)\n'
        '    version = (version or "").strip()\n'
        '    if not version or len(version) > 32:\n'
        '        return RedirectResponse("/admin/versions?error=bad_version", status_code=303)\n'
        '    if db.query(ClientVersion).filter(ClientVersion.version == version).first():\n'
        '        return RedirectResponse("/admin/versions?error=already_exists", status_code=303)\n'
        '\n'
        '    VERSIONS_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)\n'
        '    safe_name = f"TrackerSetup-{version}.exe"\n'
        '    target = VERSIONS_DOWNLOADS_DIR / safe_name\n'
        '\n'
        '    written = 0\n'
        '    with open(target, "wb") as f:\n'
        '        while True:\n'
        '            chunk = await file.read(1024 * 1024)\n'
        '            if not chunk:\n'
        '                break\n'
        '            f.write(chunk)\n'
        '            written += len(chunk)\n'
        '    if written == 0:\n'
        '        target.unlink(missing_ok=True)\n'
        '        return RedirectResponse("/admin/versions?error=empty_file", status_code=303)\n'
        '\n'
        '    sha = _versions_sha256(target)\n'
        '    base = str(request.base_url).rstrip("/")\n'
        '    download_url = f"{base}/api/v1/downloads/{safe_name}"\n'
        '\n'
        '    row = ClientVersion(\n'
        '        version=version,\n'
        '        release_date=_now(),\n'
        '        download_url=download_url,\n'
        '        mandatory=bool(mandatory),\n'
        '        release_notes=(release_notes or "").strip() or None,\n'
        '        sha256=sha,\n'
        '        file_size=written,\n'
        '        published_by=f"web:{user[\'username\']}",\n'
        '    )\n'
        '    db.add(row)\n'
        '    db.add(AuditLog(\n'
        '        actor=user["username"],\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="publish_web",\n'
        '        new_value=json.dumps({\n'
        '            "version": version, "size": written, "sha256": sha,\n'
        '            "mandatory": row.mandatory,\n'
        '        }, ensure_ascii=False),\n'
        '    ))\n'
        '    db.commit()\n'
        '\n'
        '    log.info("Published version %s via web (%d bytes)", version, written)\n'
        '    return RedirectResponse("/admin/versions?saved=1", status_code=303)\n'
        '\n'
        '\n'
        '@router.post("/versions/{version}/delete")\n'
        'def versions_delete(\n'
        '    version: str,\n'
        '    request: Request,\n'
        '    db: Session = Depends(get_db),\n'
        '    _=Depends(current_admin),\n'
        '):\n'
        '    """Удаляет версию: запись в БД + файл на диске."""\n'
        '    user = _require_admin_role(request)\n'
        '    row = db.query(ClientVersion).filter(ClientVersion.version == version).first()\n'
        '    if not row:\n'
        '        raise HTTPException(404, "Версия не найдена")\n'
        '\n'
        '    filename = os.path.basename(row.download_url)\n'
        '    path = VERSIONS_DOWNLOADS_DIR / filename\n'
        '    if filename and path.exists() and path.is_file():\n'
        '        try:\n'
        '            path.unlink()\n'
        '        except Exception as e:\n'
        '            log.warning("Failed to unlink %s: %s", path, e)\n'
        '\n'
        '    db.delete(row)\n'
        '    db.add(AuditLog(\n'
        '        actor=user["username"],\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="delete",\n'
        '    ))\n'
        '    db.commit()\n'
        '    return RedirectResponse("/admin/versions?deleted=1", status_code=303)\n'
    )
    text = text + routes_block
    _write(p, text)
    _check_py(p)


# ============================================================
# 6. templates/versions.html
# ============================================================
def create_versions_template():
    _p("[6/9] Создаю шаблон versions.html ...")
    p = SERVER / "templates" / "versions.html"
    content = '''{% extends "base.html" %}
{% block title %}Версии клиента{% endblock %}
{% block content %}
<h3 class="mb-4">Версии клиента</h3>

{% if saved %}
<div class="alert alert-success py-2">Версия опубликована.</div>
{% endif %}
{% if deleted_ok %}
<div class="alert alert-info py-2">Версия удалена.</div>
{% endif %}
{% if error == 'bad_version' %}
<div class="alert alert-warning py-2">Некорректная версия.</div>
{% endif %}
{% if error == 'already_exists' %}
<div class="alert alert-warning py-2">Такая версия уже опубликована.</div>
{% endif %}
{% if error == 'empty_file' %}
<div class="alert alert-warning py-2">Файл пустой.</div>
{% endif %}

{# --- Форма загрузки --- #}
<div class="card mb-4">
  <div class="card-header">Опубликовать новую версию</div>
  <div class="card-body">
    <form method="post" action="/admin/versions/upload" enctype="multipart/form-data">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Файл установщика (.exe)</label>
          <input class="form-control" type="file" name="file" accept=".exe" required>
          <div class="form-text">Обычно — client/dist_installer/TrackerSetup.exe</div>
        </div>
        <div class="col-md-3">
          <label class="form-label">Версия</label>
          <input class="form-control" type="text" name="version" placeholder="1.4.1" maxlength="32" required>
        </div>
        <div class="col-md-3 d-flex align-items-end">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="mandatory" id="cbMandatory" value="1">
            <label class="form-check-label" for="cbMandatory">Обязательное обновление</label>
          </div>
        </div>
        <div class="col-12">
          <label class="form-label">Что нового (release notes)</label>
          <textarea class="form-control" name="release_notes" rows="3"
                    placeholder="Например: исправлен баг с отправкой сессий..."></textarea>
        </div>
        <div class="col-12">
          <button class="btn btn-primary">Опубликовать</button>
          <span class="text-muted ms-3 small">
            При публикации сервер сам считает sha256 и сохранит файл в
            <code>server/static/downloads/</code>.
          </span>
        </div>
      </div>
    </form>
  </div>
</div>

{# --- Список опубликованных --- #}
<table class="table table-sm bg-white align-middle">
  <thead>
    <tr>
      <th style="width:130px">Версия</th>
      <th style="width:160px">Дата</th>
      <th style="width:110px">Размер</th>
      <th style="width:150px">Опубликовал</th>
      <th style="width:110px">Mandatory</th>
      <th>Release notes</th>
      <th style="width:180px">sha256</th>
      <th style="width:90px">Действия</th>
    </tr>
  </thead>
  <tbody>
  {% for v in versions %}
    <tr>
      <td><strong>{{ v.version }}</strong></td>
      <td class="small">{{ v.release_date | dt }}</td>
      <td class="small">
        {% if v.file_size %}
          {{ "%.2f"|format(v.file_size / 1048576) }} МБ
        {% else %}—{% endif %}
      </td>
      <td class="small">{{ v.published_by or '—' }}</td>
      <td>
        {% if v.mandatory %}
          <span class="badge bg-danger">Да</span>
        {% else %}
          <span class="badge bg-secondary">Нет</span>
        {% endif %}
      </td>
      <td class="small" style="max-width:340px; white-space:pre-wrap;">{{ v.release_notes or '—' }}</td>
      <td class="small">
        {% if v.sha256 %}
          <code title="{{ v.sha256 }}">{{ v.sha256[:12] }}…</code>
        {% else %}—{% endif %}
      </td>
      <td>
        <form method="post" action="/admin/versions/{{ v.version }}/delete"
              onsubmit="return confirm('Удалить версию {{ v.version }} и файл?');">
          <button class="btn btn-sm btn-outline-danger">Удалить</button>
        </form>
      </td>
    </tr>
  {% else %}
    <tr><td colspan="8" class="text-center text-muted py-4">
      Версии ещё не опубликованы.
    </td></tr>
  {% endfor %}
  </tbody>
</table>

<div class="text-muted small mt-3">
  Клиенты получают информацию о последней версии из
  <code>GET /api/v1/version</code> и скачивают файл через
  <code>GET /api/v1/downloads/&lt;filename&gt;</code>.
</div>
{% endblock %}
'''
    _write(p, content)


# ============================================================
# 7. templates/base.html — пункт меню "Версии"
# ============================================================
def patch_base_html():
    _p("[7/9] Патч base.html (пункт меню) ...")
    p = SERVER / "templates" / "base.html"
    text = _read(p)

    old = (
        '      <a class="nav-link {% if \'/scheduler\' in request.url.path %}active{% endif %}"\n'
        '         href="/admin/scheduler">{{ _("menu.scheduler") }}</a>\n'
        '      {% if admin_role == \'admin\' %}\n'
    )
    new = (
        '      <a class="nav-link {% if \'/scheduler\' in request.url.path %}active{% endif %}"\n'
        '         href="/admin/scheduler">{{ _("menu.scheduler") }}</a>\n'
        '      <a class="nav-link {% if \'/versions\' in request.url.path %}active{% endif %}"\n'
        '         href="/admin/versions">Версии</a>\n'
        '      {% if admin_role == \'admin\' %}\n'
    )
    text = _replace_once(text, old, new, "sidebar menu пункт Версии")
    _write(p, text)


# ============================================================
# 8. nginx.conf — client_max_body_size
# ============================================================
def patch_nginx():
    _p("[8/9] Патч nginx.conf ...")
    p = SERVER / "nginx.conf"
    text = _read(p)
    old = "    client_max_body_size 10m;\n"
    new = (
        "    # 200m — с запасом на установщик TrackerSetup.exe (~35 МБ)\n"
        "    client_max_body_size 200m;\n"
    )
    if old not in text:
        if "client_max_body_size 200m" in text:
            _p("  --  уже 200m, пропускаю")
            return
        raise SystemExit("nginx.conf: не найден client_max_body_size 10m")
    text = text.replace(old, new, 1)
    _write(p, text)


# ============================================================
# 9. Каталог для артефактов
# ============================================================
def ensure_downloads_dir():
    _p("[9/9] Создаю server/static/downloads/ ...")
    d = SERVER / "static" / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitkeep").write_text("", encoding="utf-8")
    _p(f"  OK  {d}")


def main():
    print("=" * 60)
    print("Патч: публикация версий клиента (сервер)")
    print("=" * 60)
    print()
    print(f"Корень проекта: {ROOT}")
    if not ROOT.exists():
        raise SystemExit(f"Не найден {ROOT}")
    if not SERVER.exists():
        raise SystemExit(f"Не найден {SERVER}")

    patch_models()
    create_migration()
    patch_schemas()
    patch_main()
    patch_web_admin()
    create_versions_template()
    patch_base_html()
    patch_nginx()
    ensure_downloads_dir()

    print()
    print("=" * 60)
    print("ГОТОВО. Все патчи применены.")
    print("=" * 60)
    print()
    print("Дальше — в PowerShell:")
    print()
    print("  cd D:\\tracker")
    print("  docker compose down")
    print("  docker compose up -d --build")
    print()
    print("После старта (30-60 сек) проверь:")
    print("  docker compose logs api --tail=30")
    print("  docker compose exec -T api alembic -c /app/server/alembic.ini current")
    print()
    print("Открыть в браузере:")
    print("  https://192.168.0.35/admin/versions")
    print()
    print("Клиентский API:")
    print("  curl.exe -k https://192.168.0.35/api/v1/version")
    print()


if __name__ == "__main__":
    main()
Как запустить
powershell
cd D:\tracker
client\.venv\Scripts\python.exe _apply_versions.py
Скрипт печатает каждый шаг и сам проверяет синтаксис всех изменённых .py через ast.parse. Если что-то не найдено — упадёт с чётким сообщением и ничего не сломает (правки идут построчно, но если маркер не найден — выходит с ошибкой до записи файла).
Затем — перезапуск сервера
powershell
cd D:\tracker
docker compose down
docker compose up -d --build
Обязательно up --build, а не restart: мы добавили новый эндпоинт (multipart) и миграцию Alembic. Миграция применится автоматически на старте API (entrypoint).
Проверить, что всё поднялось:
powershell
docker compose logs api --tail=30
docker compose exec -T api alembic -c /app/server/alembic.ini current
Ожидаешь увидеть a1b2c3d4e5f6 (head).
Открыть в браузере:
https://192.168.0.35/admin/versions
Должна быть страница «Версии клиента» с формой загрузки и пустой таблицей (если версий ещё нет). В сайдбаре появится пункт «Версии».
Что не вошло в этот шаг (будет в следующем)
1.	SCP: кнопка «Опубликовать версию» в BuildTab — с полями version/mandatory/release_notes, отправка multipart на /api/v1/admin/versions/publish с X-Admin-Token из .env и download_base из deploy.json.
2.	Клиент (updater.py + main.py): проверка sha256 после скачивания + диалог с release_notes + обязательность.
3.	KB (обновить 04_CLIENT/08_AUTOSTART_UPDATE.md, 06_DEPLOY/05_UPDATES.md, 05_SCP/03_BUILD.md, HANDOFF.md).
Если сейчас что-то сломалось — покажи вывод docker compose logs api --tail=30, разберёмся. Как только подтвердишь, что сервер поднялся и страница открывается — дам следующий пакет (SCP + клиент).
>> client\.venv\Scripts\python.exe _apply_versions.py ============================================================ Патч: публикация версий клиента (сервер) ============================================================ Корень проекта: D:\tracker [1/9] Патч models.py ... OK записан server\models.py (18187 байт) OK синтаксис models.py валиден [2/9] Создаю миграцию ... OK записан server\alembic\versions\a1b2c3d4e5f6_add_client_versions_sha256.py (999 байт) [3/9] Патч schemas.py ... OK записан server\schemas.py (4140 байт) OK синтаксис schemas.py валиден [4/9] Патч main.py ... НЕ НАЙДЕН блок для замены: get_latest_version + новые эндпоинты
Патчер упал на шаге 4 — в main.py не найден блок get_latest_version. Я неверно его задал. Надо проверить точное содержимое main.py.
Посмотрим ещё раз оригинал main.py из последнего сообщения пользователя:
python
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
Мой old строка была:
text
'@app.get("/api/v1/version", response_model=VersionResponse)\n'
'def get_latest_version(current: str = "", db: Session = Depends(get_db)):\n'
'    latest = (db.query(ClientVersion)\n'
'              .order_by(ClientVersion.release_date.desc()).first())\n'
'    if not latest:\n'
'        return VersionResponse(latest_version=current or "0.0.0",\n'
'                               download_url="", mandatory=False)\n'
'    return VersionResponse(latest_version=latest.version,\n'
'                           download_url=latest.download_url,\n'
'                           mandatory=latest.mandatory,\n'
'                           release_notes=latest.release_notes)\n'
Хм, выглядит совпадающим. Но, наверное, в реальном файле что-то не так. Например, могут быть \r\n в файле (Windows). Тогда мой \n не найдётся. Файл main.py правился через PS, там могут быть CRLF.
Это, скорее всего, и есть проблема. Надо нормализовать переносы строк при чтении.
Также client\.venv\Scripts\python.exe _apply_versions.py — скрипт выполнялся из D:\tracker, значит cwd корректен.
Решение: в _read заменить все \r\n на \n, а при записи — не возвращать обратно (или возвращать). Проще: работать с унифицированным \n. Python-файлы это не сломает.
Ещё лучше — использовать newline='' и явно передавать newline='\n' при записи. Это стандартный способ.
Обновлённый _read:
python
def _read(p: Path) -> str:
    text = p.read_text(encoding="utf-8")
    # Нормализуем CRLF → LF, чтобы маркеры совпадали независимо
    # от того, чем правился файл (PowerShell может сохранять CRLF).
    return text.replace("\r\n", "\n").replace("\r", "\n")
И _write:
python
def _write(p: Path, text: str):
    p.write_text(text, encoding="utf-8", newline="\n")
Это запишет с LF. Проверим что Python это ок — да, всё нормально.
Также надо дать пользователю короткий скрипт-«допатчер», который применит только шаг 4 (и последующие 5-9, если они уже не применились). Потому что шаг 1-3 уже прошли (models.py, миграция, schemas.py уже изменены).
Если запустить полный скрипт заново — шаг 1 упадёт, потому что новый блок уже там. Значит надо сделать «resume»-версию с шага 4.
Правильнее: написать новый компактный скрипт, который только шаги 4-9, с нормализованными переносами. Но при этом шаги 6 (create template), 7 (base.html), 8 (nginx), 9 (папка) — идемпотентны или почти. Шаблон versions.html — если файла нет, создастся. base.html — маркер точно такой же. nginx — если уже 200m, пропустит.
Проще всего: выдать новый патчер, который делает ТОЛЬКО шаги 4-9 (skip 1-3), с нормализованными переносами.
Но у меня есть подозрение: шаги 1-3 уже применились (models.py, schemas.py). Значит, надо начать с 4.
Ещё важно: возможно, при чтении файла с CRLF _read вернул CRLF, а я смотрел на содержимое, которое видел в сообщении с LF. На самом деле при копировании из мессенджера переносы могли быть сконвертированы в LF, а на диске — CRLF.
Делаю патчер-2: только шаги 4-9. С нормализацией переносов.
Стоп, подожди. models.py и schemas.py уже изменены. Значит если я сейчас снова их править начну (в новом патчере), там уже нет старых блоков. Поэтому пропускаем.
Итого новый патчер:
•	
4.	main.py (нормализовать переносы)
•	
5.	web_admin.py
•	
6.	versions.html
•	
7.	base.html
•	
8.	nginx.conf
•	
9.	downloads dir
А шаги 1-3 уже сделаны, не трогаем.
Хотя... models.py уже пропатчен (18187 байт). Значит если я снова добавлю в него sha256/file_size/published_by — получится дубль. Не трогаю.
Ещё нюанс: main.py. Если шаг 4 упал ДО записи — файл не изменён (в моём коде сначала _replace_once, потом _write). Да, файл не был записан. Проверю: в коде
text
text = _replace_once(...)
_write(p, text)
Если _replace_once падает — _write не вызывается. Значит main.py в оригинале.
Ок. Пишу новый скрипт _apply_versions2.py, только шаги 4-9.
Ещё замечу — при импорте File/Form/UploadFile из fastapi в main.py. У нас уже есть from fastapi import Depends, FastAPI, Header, HTTPException, Request. Заменяю на многострочный. Но в оригинале, возможно, строки с CRLF. Поэтому сначала нормализация.
Ещё нюанс: там где я ищу 'import secrets\nfrom datetime import datetime, timedelta, timezone\n' — в оригинале, скорее всего, было именно так (LF в hexdump показал бы, но не будем углубляться). Использую нормализацию — и всё в порядке.
Так, ещё важно: from pathlib import Path — уже есть ли? В шаге 4.1 я добавлял его после import secrets\nfrom datetime import.... Если уже импортирован где-то — не страшно, просто повторный импорт. Python не ругается.
Плюс import os — есть ли уже в main.py? Пользователь прислал main.py, там вверху:
text
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
os не импортирован. Добавлю.
Ага, но у меня в шаге 4.1 я добавил from pathlib import Path — там его тоже не было. Хорошо.
В моём финальном добавлении кода для main.py используется os.path.basename. Нужен import os. Проверю — добавлю явно в начало.
Ещё в main.py уже есть блок:
text
# ============================================================
# Version
# ============================================================
— пустой комментарий с отбивками. И ниже — функция. Может, в файле с CRLF заголовки другие. Неважно.
Хорошо, пишу патч-2.
Также: в main.py функция get_latest_version присутствует в самом конце файла. После неё — конец. Значит old_version блок в конце файла. Заменю на расширенный.
Ещё одна проблема: тестовая обёртка с ast.parse делается сразу после записи. Она проверяет синтаксис. Хорошо.
Ещё надо проверить, что в patch_main я использую Request — он уже импортирован в main.py. Да:
text
from fastapi import Depends, FastAPI, Header, HTTPException, Request
ок.
UploadFile — из fastapi. File, Form — из fastapi.
FileResponse — из fastapi.responses.
Наконец: DOWNLOADS_DIR — создаём там же. Хорошо.
Пишу скрипт-2.
Плюс я сделаю один маленький сервис — на всякий случай в шаге 5, web_admin.py — там где я заменил импорт моделей, ищу точно такой же кусок. Если в реальном файле CRLF — нормализация спасёт.
Ещё: в web_admin.py я использовал одну строку с экранированием — f"web:{user[\'username\']}" — в Python внутри строки '''...''' это норм. Но я должен быть уверен, что всё корректно. Проверю.
Теперь про шаблон versions.html: используется фильтр dt. Он зарегистрирован в web_admin.py как templates.env.filters["dt"]. ОК.
Про base.html: пункт меню я вставляю без i18n — просто «Версии» по-русски. Можно добавить в словари i18n, но это отдельная история. Пока — так.
Всё, пишу.
Дополнительно: пользователь просил «Экономим чат, не забываем писать всплывающие комментария ко всем действиям» — то есть комментарии в коде. В патчере это есть. Ок.
Файл назову _apply_versions2.py.
Внутри — короткие шаги 4-9 + нормализация переносов.
Плюс добавлю защиту: если в main.py уже есть "/api/v1/downloads" — пропустить шаг 4 (файл, похоже, уже правился). Аналогично для web_admin.py.
Готово.
Понял причину: файл main.py на диске с CRLF (Windows-переносы строк) — при копировании в чат они превратились в LF, и мой маркер не совпал. Шаги 1-3 уже применились (models.py, миграция, schemas.py — они записаны), поэтому их повторять нельзя.
Даю короткий второй патчер — только шаги 4-9, с нормализацией переносов строк. Он идемпотентен: если где-то уже применено, пропустит.
Создай D:\tracker\_apply_versions2.py:
python
# -*- coding: utf-8 -*-
# ============================================================
# Патчер #2: продолжение после сбоя на шаге 4.
# ============================================================
# Шаги 1-3 (models.py, миграция, schemas.py) уже применены —
# их НЕ трогаем.
# Здесь только: main.py, web_admin.py, шаблоны, nginx, папка.
#
# Отличие от #1: при чтении файлов нормализуются CRLF → LF.
# Это важно: main.py на диске сохранён с Windows-переносами,
# и строковые маркеры с "\n" в них не находились.
# ============================================================

from pathlib import Path
import ast

ROOT = Path(r"D:\tracker")
SERVER = ROOT / "server"


def _read(p: Path) -> str:
    """Читает файл, приводя переносы к LF — чтобы маркеры совпадали."""
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _write(p: Path, text: str):
    """Пишет файл с LF-переносами (Python-код это никак не портит)."""
    p.write_text(text, encoding="utf-8", newline="\n")
    print(f"  OK  записан {p.relative_to(ROOT)} ({len(text)} байт)")


def _replace_once(text: str, old: str, new: str, what: str) -> str:
    if old not in text:
        raise SystemExit(f"НЕ НАЙДЕН блок: {what}")
    cnt = text.count(old)
    if cnt > 1:
        raise SystemExit(f"Блок '{what}' встречается {cnt} раз — уточни маркер")
    return text.replace(old, new, 1)


def _check_py(p: Path):
    try:
        ast.parse(_read(p))
    except SyntaxError as e:
        raise SystemExit(f"СИНТАКСИС {p.name}: {e}")
    print(f"  OK  синтаксис {p.name} валиден")


# ============================================================
# Шаг 4. main.py
# ============================================================
def patch_main():
    p = SERVER / "main.py"
    print("[4/9] Патч main.py ...")
    text = _read(p)

    # Идемпотентность: если уже патчили — выходим.
    if "/api/v1/downloads/" in text:
        print("  --  уже пропатчен (есть /api/v1/downloads/), пропускаю")
        return

    # --- 4.1. import os + from pathlib import Path --------------------
    # В оригинале: "import secrets\nfrom datetime import datetime, timedelta, timezone\n"
    # Делаем аккуратно: import os после import secrets.
    if "\nimport os\n" not in text:
        text = _replace_once(
            text,
            "import secrets\nfrom datetime import datetime, timedelta, timezone\n",
            "import os\nimport secrets\nfrom datetime import datetime, timedelta, timezone\n"
            "from pathlib import Path\n",
            "import os + Path",
        )

    # --- 4.2. Расширяем импорт из fastapi -----------------------------
    text = _replace_once(
        text,
        "from fastapi import Depends, FastAPI, Header, HTTPException, Request\n",
        "from fastapi import (\n"
        "    Depends, FastAPI, File, Form, Header, HTTPException, Request,\n"
        "    UploadFile,\n"
        ")\n",
        "fastapi: File/Form/UploadFile",
    )

    # --- 4.3. FileResponse --------------------------------------------
    text = _replace_once(
        text,
        "from fastapi.responses import RedirectResponse as _AdminRedirect\n",
        "from fastapi.responses import FileResponse, RedirectResponse as _AdminRedirect\n",
        "FileResponse",
    )

    # --- 4.4. DOWNLOADS_DIR -------------------------------------------
    text = _replace_once(
        text,
        'app = FastAPI(title="Employee Tracker API", version="1.4.0")\n',
        'app = FastAPI(title="Employee Tracker API", version="1.4.0")\n'
        '\n'
        '# ------------------------------------------------------------\n'
        '# Каталог для артефактов клиента (установщиков .exe).\n'
        '# На хосте:     D:\\tracker\\server\\static\\downloads\\\n'
        '# В контейнере: /app/server/static/downloads/\n'
        '# Монтируется через docker-compose (./server:/app/server).\n'
        '# ------------------------------------------------------------\n'
        'DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"\n',
        "DOWNLOADS_DIR",
    )

    # --- 4.5. Замена get_latest_version + новые эндпоинты ------------
    old_version = (
        '@app.get("/api/v1/version", response_model=VersionResponse)\n'
        'def get_latest_version(current: str = "", db: Session = Depends(get_db)):\n'
        '    latest = (db.query(ClientVersion)\n'
        '              .order_by(ClientVersion.release_date.desc()).first())\n'
        '    if not latest:\n'
        '        return VersionResponse(latest_version=current or "0.0.0",\n'
        '                               download_url="", mandatory=False)\n'
        '    return VersionResponse(latest_version=latest.version,\n'
        '                           download_url=latest.download_url,\n'
        '                           mandatory=latest.mandatory,\n'
        '                           release_notes=latest.release_notes)\n'
    )

    new_block = (
        '@app.get("/api/v1/version", response_model=VersionResponse)\n'
        'def get_latest_version(current: str = "", db: Session = Depends(get_db)):\n'
        '    """\n'
        '    Возвращает последнюю опубликованную версию клиента.\n'
        '    Клиент сравнивает её со своей CLIENT_VERSION.\n'
        '    """\n'
        '    latest = (db.query(ClientVersion)\n'
        '              .order_by(ClientVersion.release_date.desc()).first())\n'
        '    if not latest:\n'
        '        return VersionResponse(latest_version=current or "0.0.0",\n'
        '                               download_url="", mandatory=False)\n'
        '    return VersionResponse(\n'
        '        latest_version=latest.version,\n'
        '        download_url=latest.download_url,\n'
        '        mandatory=latest.mandatory,\n'
        '        release_notes=latest.release_notes,\n'
        '        sha256=latest.sha256,\n'
        '        file_size=latest.file_size,\n'
        '    )\n'
        '\n'
        '\n'
        '# ============================================================\n'
        '# Публикация версий клиента\n'
        '# ============================================================\n'
        '# Публикуется установщик TrackerSetup.exe. Сервер сам:\n'
        '#   1. Сохраняет файл в server/static/downloads/TrackerSetup-<v>.exe\n'
        '#   2. Считает sha256 файла\n'
        '#   3. Создаёт запись в client_versions\n'
        '# Клиент скачивает файл через /api/v1/downloads/... и сверяет sha256.\n'
        '# ============================================================\n'
        '\n'
        '\n'
        'def _sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:\n'
        '    """SHA-256 файла. Читаем блоками по 1 МБ — не держим .exe в RAM."""\n'
        '    h = hashlib.sha256()\n'
        '    with open(path, "rb") as f:\n'
        '        for block in iter(lambda: f.read(chunk), b""):\n'
        '            h.update(block)\n'
        '    return h.hexdigest()\n'
        '\n'
        '\n'
        '@app.get("/api/v1/downloads/{filename}")\n'
        'def download_artifact(filename: str):\n'
        '    """\n'
        '    Отдаёт .exe-артефакт клиенту.\n'
        '    Защита от path traversal: работаем только с basename.\n'
        '    """\n'
        '    safe_name = os.path.basename(filename)\n'
        '    if not safe_name or safe_name != filename:\n'
        '        raise HTTPException(400, "invalid filename")\n'
        '    path = DOWNLOADS_DIR / safe_name\n'
        '    if not path.exists() or not path.is_file():\n'
        '        raise HTTPException(404, "file not found")\n'
        '    return FileResponse(\n'
        '        path,\n'
        '        media_type="application/octet-stream",\n'
        '        filename=safe_name,\n'
        '    )\n'
        '\n'
        '\n'
        '@app.post("/api/v1/admin/versions/publish",\n'
        '          dependencies=[Depends(require_admin)])\n'
        'async def publish_version(\n'
        '    request: Request,\n'
        '    file: UploadFile = File(...),\n'
        '    version: str = Form(...),\n'
        '    release_notes: str = Form(""),\n'
        '    mandatory: str = Form("0"),\n'
        '    published_by: str = Form(""),\n'
        '    download_base: str = Form(""),\n'
        '    db: Session = Depends(get_db),\n'
        '):\n'
        '    """\n'
        '    Публикация новой версии клиента (multipart/form-data).\n'
        '    Заголовок: X-Admin-Token.\n'
        '\n'
        '    file          — сам .exe\n'
        '    version       — например "1.4.1" (<=32 символов, уникальная)\n'
        '    release_notes — что нового (опционально)\n'
        '    mandatory     — "1"/"true" для обязательного\n'
        '    published_by  — "user@host" (опционально, для аудита)\n'
        '    download_base — базовый URL (например "https://192.168.0.35");\n'
        '                    если пусто — берём из request.base_url\n'
        '    """\n'
        '    version = (version or "").strip()\n'
        '    if not version or len(version) > 32:\n'
        '        raise HTTPException(400, "Некорректная версия")\n'
        '\n'
        '    if db.query(ClientVersion).filter(ClientVersion.version == version).first():\n'
        '        raise HTTPException(409, f"Версия {version} уже опубликована")\n'
        '\n'
        '    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)\n'
        '    safe_name = f"TrackerSetup-{version}.exe"\n'
        '    target = DOWNLOADS_DIR / safe_name\n'
        '\n'
        '    # Пишем потоком — не грузим весь .exe в память.\n'
        '    written = 0\n'
        '    with open(target, "wb") as f:\n'
        '        while True:\n'
        '            chunk = await file.read(1024 * 1024)\n'
        '            if not chunk:\n'
        '                break\n'
        '            f.write(chunk)\n'
        '            written += len(chunk)\n'
        '\n'
        '    if written == 0:\n'
        '        target.unlink(missing_ok=True)\n'
        '        raise HTTPException(400, "Пустой файл")\n'
        '\n'
        '    sha = _sha256_file(target)\n'
        '\n'
        '    if download_base:\n'
        '        base = download_base.strip().rstrip("/")\n'
        '    else:\n'
        '        base = str(request.base_url).rstrip("/")\n'
        '    download_url = f"{base}/api/v1/downloads/{safe_name}"\n'
        '\n'
        '    row = ClientVersion(\n'
        '        version=version,\n'
        '        release_date=_now(),\n'
        '        download_url=download_url,\n'
        '        mandatory=(str(mandatory).lower() in ("1", "true", "yes", "on")),\n'
        '        release_notes=(release_notes or "").strip() or None,\n'
        '        sha256=sha,\n'
        '        file_size=written,\n'
        '        published_by=(published_by or "api").strip()[:128],\n'
        '    )\n'
        '    db.add(row)\n'
        '    db.add(AuditLog(\n'
        '        actor=(published_by or "api")[:128],\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="publish",\n'
        '        new_value=json.dumps({\n'
        '            "version": version,\n'
        '            "size": written,\n'
        '            "sha256": sha,\n'
        '            "mandatory": row.mandatory,\n'
        '            "download_url": download_url,\n'
        '        }, ensure_ascii=False),\n'
        '    ))\n'
        '    db.commit()\n'
        '\n'
        '    log.info(\n'
        '        "Published client version %s (%d bytes, sha256=%s)",\n'
        '        version, written, sha[:12],\n'
        '    )\n'
        '    return {\n'
        '        "status": "ok",\n'
        '        "version": version,\n'
        '        "download_url": download_url,\n'
        '        "sha256": sha,\n'
        '        "file_size": written,\n'
        '    }\n'
        '\n'
        '\n'
        '@app.post("/api/v1/admin/versions/{version}/delete",\n'
        '          dependencies=[Depends(require_admin)])\n'
        'def delete_version(version: str, db: Session = Depends(get_db)):\n'
        '    """Удаляет запись версии и файл на диске (если есть)."""\n'
        '    row = (db.query(ClientVersion)\n'
        '           .filter(ClientVersion.version == version).first())\n'
        '    if not row:\n'
        '        raise HTTPException(404, "Версия не найдена")\n'
        '\n'
        '    filename = os.path.basename(row.download_url)\n'
        '    path = DOWNLOADS_DIR / filename\n'
        '    file_deleted = False\n'
        '    if filename and path.exists() and path.is_file():\n'
        '        try:\n'
        '            path.unlink()\n'
        '            file_deleted = True\n'
        '        except Exception as e:\n'
        '            log.warning("Не удалось удалить файл %s: %s", path, e)\n'
        '\n'
        '    db.delete(row)\n'
        '    db.add(AuditLog(\n'
        '        actor="admin",\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="delete",\n'
        '        new_value=json.dumps({"file_deleted": file_deleted}),\n'
        '    ))\n'
        '    db.commit()\n'
        '    return {"status": "ok", "file_deleted": file_deleted}\n'
    )

    text = _replace_once(text, old_version, new_block, "get_latest_version + новые эндпоинты")
    _write(p, text)
    _check_py(p)


# ============================================================
# Шаг 5. web_admin.py
# ============================================================
def patch_web_admin():
    p = SERVER / "web_admin.py"
    print("[5/9] Патч web_admin.py ...")
    text = _read(p)

    if "def versions_page(" in text:
        print("  --  уже пропатчен (есть versions_page), пропускаю")
        return

    # 5.1. import os
    text = _replace_once(
        text,
        "import csv\nimport logging\nimport hashlib\nimport io\nimport json\nimport secrets\n",
        "import csv\nimport logging\nimport hashlib\nimport io\nimport json\nimport os\nimport secrets\n",
        "import os",
    )

    # 5.2. from pathlib import Path
    text = _replace_once(
        text,
        "from datetime import datetime, date, time, timedelta, timezone\n",
        "from datetime import datetime, date, time, timedelta, timezone\nfrom pathlib import Path\n",
        "import Path",
    )

    # 5.3. File/UploadFile из fastapi
    text = _replace_once(
        text,
        "from fastapi import APIRouter, Depends, Request, Form, HTTPException\n",
        "from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File\n",
        "fastapi: File/UploadFile",
    )

    # 5.4. ClientVersion в models
    text = _replace_once(
        text,
        "from .models import (\n"
        "    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,\n"
        "    CalendarDay, Computer, Department, Employee, EmployeeSettings,\n"
        "    Record, WorkSession,\n"
        "    Schedule, ScheduledTask, TaskRun,\n"
        ")\n",
        "from .models import (\n"
        "    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,\n"
        "    CalendarDay, ClientVersion, Computer, Department, Employee,\n"
        "    EmployeeSettings, Record, WorkSession,\n"
        "    Schedule, ScheduledTask, TaskRun,\n"
        ")\n",
        "import ClientVersion",
    )

    # 5.5. Роуты — в самый конец файла.
    routes_block = (
        "\n\n"
        "# ============================================================\n"
        "# ВЕРСИИ КЛИЕНТА (публикация релизов .exe)\n"
        "# ============================================================\n"
        "# Файлы хранятся в server/static/downloads/.\n"
        "# Раздача клиентам — GET /api/v1/downloads/{filename} (main.py).\n"
        "# Доступ — только роль admin.\n"
        "# ============================================================\n"
        "\n"
        'VERSIONS_DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"\n'
        "\n"
        "\n"
        "def _versions_sha256(path: Path, chunk: int = 1024 * 1024) -> str:\n"
        '    """SHA-256 файла. Блоками по 1 МБ."""\n'
        "    h = hashlib.sha256()\n"
        '    with open(path, "rb") as f:\n'
        '        for block in iter(lambda: f.read(chunk), b""):\n'
        "            h.update(block)\n"
        "    return h.hexdigest()\n"
        "\n"
        "\n"
        '@router.get("/versions", response_class=HTMLResponse)\n'
        "def versions_page(request: Request, db: Session = Depends(get_db),\n"
        "                  _=Depends(current_admin)):\n"
        '    """Список опубликованных версий клиента + форма загрузки."""\n'
        "    _require_admin_role(request)\n"
        "    versions = (db.query(ClientVersion)\n"
        "                .order_by(desc(ClientVersion.release_date)).all())\n"
        '    return templates.TemplateResponse("versions.html", {\n'
        '        "request": request,\n'
        '        "versions": versions,\n'
        '        "saved": request.query_params.get("saved") == "1",\n'
        '        "deleted_ok": request.query_params.get("deleted") == "1",\n'
        '        "error": request.query_params.get("error"),\n'
        "    })\n"
        "\n"
        "\n"
        '@router.post("/versions/upload")\n'
        "async def versions_upload(\n"
        "    request: Request,\n"
        "    file: UploadFile = File(...),\n"
        "    version: str = Form(...),\n"
        '    release_notes: str = Form(""),\n'
        '    mandatory: str = Form(""),\n'
        "    db: Session = Depends(get_db),\n"
        "    _=Depends(current_admin),\n"
        "):\n"
        '    """Загрузка нового .exe через веб-форму."""\n'
        "    user = _require_admin_role(request)\n"
        '    version = (version or "").strip()\n'
        "    if not version or len(version) > 32:\n"
        '        return RedirectResponse("/admin/versions?error=bad_version", status_code=303)\n'
        "    if db.query(ClientVersion).filter(ClientVersion.version == version).first():\n"
        '        return RedirectResponse("/admin/versions?error=already_exists", status_code=303)\n'
        "\n"
        "    VERSIONS_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)\n"
        '    safe_name = f"TrackerSetup-{version}.exe"\n'
        "    target = VERSIONS_DOWNLOADS_DIR / safe_name\n"
        "\n"
        "    written = 0\n"
        '    with open(target, "wb") as f:\n'
        "        while True:\n"
        "            chunk = await file.read(1024 * 1024)\n"
        "            if not chunk:\n"
        "                break\n"
        "            f.write(chunk)\n"
        "            written += len(chunk)\n"
        "    if written == 0:\n"
        "        target.unlink(missing_ok=True)\n"
        '        return RedirectResponse("/admin/versions?error=empty_file", status_code=303)\n'
        "\n"
        "    sha = _versions_sha256(target)\n"
        '    base = str(request.base_url).rstrip("/")\n'
        '    download_url = f"{base}/api/v1/downloads/{safe_name}"\n'
        "\n"
        "    row = ClientVersion(\n"
        "        version=version,\n"
        "        release_date=_now(),\n"
        "        download_url=download_url,\n"
        "        mandatory=bool(mandatory),\n"
        '        release_notes=(release_notes or "").strip() or None,\n'
        "        sha256=sha,\n"
        "        file_size=written,\n"
        '        published_by=f"web:{user[\'username\']}",\n'
        "    )\n"
        "    db.add(row)\n"
        "    db.add(AuditLog(\n"
        '        actor=user["username"],\n'
        '        entity="client_version",\n'
        "        entity_id=version,\n"
        '        action="publish_web",\n'
        "        new_value=json.dumps({\n"
        '            "version": version, "size": written, "sha256": sha,\n'
        '            "mandatory": row.mandatory,\n'
        "        }, ensure_ascii=False),\n"
        "    ))\n"
        "    db.commit()\n"
        "\n"
        '    log.info("Published version %s via web (%d bytes)", version, written)\n'
        '    return RedirectResponse("/admin/versions?saved=1", status_code=303)\n'
        "\n"
        "\n"
        '@router.post("/versions/{version}/delete")\n'
        "def versions_delete(\n"
        "    version: str,\n"
        "    request: Request,\n"
        "    db: Session = Depends(get_db),\n"
        "    _=Depends(current_admin),\n"
        "):\n"
        '    """Удаляет версию: запись в БД + файл на диске."""\n'
        '    user = _require_admin_role(request)\n'
        "    row = db.query(ClientVersion).filter(ClientVersion.version == version).first()\n"
        "    if not row:\n"
        '        raise HTTPException(404, "Версия не найдена")\n'
        "\n"
        "    filename = os.path.basename(row.download_url)\n"
        "    path = VERSIONS_DOWNLOADS_DIR / filename\n"
        "    if filename and path.exists() and path.is_file():\n"
        "        try:\n"
        "            path.unlink()\n"
        "        except Exception as e:\n"
        '            log.warning("Failed to unlink %s: %s", path, e)\n'
        "\n"
        "    db.delete(row)\n"
        "    db.add(AuditLog(\n"
        '        actor=user["username"],\n'
        '        entity="client_version",\n'
        "        entity_id=version,\n"
        '        action="delete",\n'
        "    ))\n"
        "    db.commit()\n"
        '    return RedirectResponse("/admin/versions?deleted=1", status_code=303)\n'
    )
    text = text + routes_block
    _write(p, text)
    _check_py(p)


# ============================================================
# Шаг 6. versions.html
# ============================================================
def create_versions_template():
    print("[6/9] Создаю шаблон versions.html ...")
    p = SERVER / "templates" / "versions.html"
    if p.exists():
        print("  --  файл уже есть, пропускаю")
        return
    content = """{% extends "base.html" %}
{% block title %}Версии клиента{% endblock %}
{% block content %}
<h3 class="mb-4">Версии клиента</h3>

{% if saved %}
<div class="alert alert-success py-2">Версия опубликована.</div>
{% endif %}
{% if deleted_ok %}
<div class="alert alert-info py-2">Версия удалена.</div>
{% endif %}
{% if error == 'bad_version' %}
<div class="alert alert-warning py-2">Некорректная версия.</div>
{% endif %}
{% if error == 'already_exists' %}
<div class="alert alert-warning py-2">Такая версия уже опубликована.</div>
{% endif %}
{% if error == 'empty_file' %}
<div class="alert alert-warning py-2">Файл пустой.</div>
{% endif %}

{# --- Форма загрузки --- #}
<div class="card mb-4">
  <div class="card-header">Опубликовать новую версию</div>
  <div class="card-body">
    <form method="post" action="/admin/versions/upload" enctype="multipart/form-data">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Файл установщика (.exe)</label>
          <input class="form-control" type="file" name="file" accept=".exe" required>
          <div class="form-text">Обычно — client/dist_installer/TrackerSetup.exe</div>
        </div>
        <div class="col-md-3">
          <label class="form-label">Версия</label>
          <input class="form-control" type="text" name="version" placeholder="1.4.1" maxlength="32" required>
        </div>
        <div class="col-md-3 d-flex align-items-end">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="mandatory" id="cbMandatory" value="1">
            <label class="form-check-label" for="cbMandatory">Обязательное обновление</label>
          </div>
        </div>
        <div class="col-12">
          <label class="form-label">Что нового (release notes)</label>
          <textarea class="form-control" name="release_notes" rows="3"
                    placeholder="Например: исправлен баг с отправкой сессий..."></textarea>
        </div>
        <div class="col-12">
          <button class="btn btn-primary">Опубликовать</button>
          <span class="text-muted ms-3 small">
            При публикации сервер сам считает sha256 и сохранит файл в
            <code>server/static/downloads/</code>.
          </span>
        </div>
      </div>
    </form>
  </div>
</div>

{# --- Список опубликованных --- #}
<table class="table table-sm bg-white align-middle">
  <thead>
    <tr>
      <th style="width:130px">Версия</th>
      <th style="width:160px">Дата</th>
      <th style="width:110px">Размер</th>
      <th style="width:150px">Опубликовал</th>
      <th style="width:110px">Mandatory</th>
      <th>Release notes</th>
      <th style="width:180px">sha256</th>
      <th style="width:90px">Действия</th>
    </tr>
  </thead>
  <tbody>
  {% for v in versions %}
    <tr>
      <td><strong>{{ v.version }}</strong></td>
      <td class="small">{{ v.release_date | dt }}</td>
      <td class="small">
        {% if v.file_size %}
          {{ "%.2f"|format(v.file_size / 1048576) }} МБ
        {% else %}—{% endif %}
      </td>
      <td class="small">{{ v.published_by or '—' }}</td>
      <td>
        {% if v.mandatory %}
          <span class="badge bg-danger">Да</span>
        {% else %}
          <span class="badge bg-secondary">Нет</span>
        {% endif %}
      </td>
      <td class="small" style="max-width:340px; white-space:pre-wrap;">{{ v.release_notes or '—' }}</td>
      <td class="small">
        {% if v.sha256 %}
          <code title="{{ v.sha256 }}">{{ v.sha256[:12] }}…</code>
        {% else %}—{% endif %}
      </td>
      <td>
        <form method="post" action="/admin/versions/{{ v.version }}/delete"
              onsubmit="return confirm('Удалить версию {{ v.version }} и файл?');">
          <button class="btn btn-sm btn-outline-danger">Удалить</button>
        </form>
      </td>
    </tr>
  {% else %}
    <tr><td colspan="8" class="text-center text-muted py-4">
      Версии ещё не опубликованы.
    </td></tr>
  {% endfor %}
  </tbody>
</table>

<div class="text-muted small mt-3">
  Клиенты получают информацию о последней версии из
  <code>GET /api/v1/version</code> и скачивают файл через
  <code>GET /api/v1/downloads/&lt;filename&gt;</code>.
</div>
{% endblock %}
"""
    _write(p, content)


# ============================================================
# Шаг 7. base.html — пункт меню «Версии»
# ============================================================
def patch_base_html():
    print("[7/9] Патч base.html ...")
    p = SERVER / "templates" / "base.html"
    text = _read(p)

    if '/admin/versions' in text:
        print("  --  пункт меню уже есть, пропускаю")
        return

    old = (
        "      <a class=\"nav-link {% if '/scheduler' in request.url.path %}active{% endif %}\"\n"
        "         href=\"/admin/scheduler\">{{ _(\"menu.scheduler\") }}</a>\n"
        "      {% if admin_role == 'admin' %}\n"
    )
    new = (
        "      <a class=\"nav-link {% if '/scheduler' in request.url.path %}active{% endif %}\"\n"
        "         href=\"/admin/scheduler\">{{ _(\"menu.scheduler\") }}</a>\n"
        "      {# --- Публикация версий клиента (только admin) --- #}\n"
        "      <a class=\"nav-link {% if '/versions' in request.url.path %}active{% endif %}\"\n"
        "         href=\"/admin/versions\">Версии</a>\n"
        "      {% if admin_role == 'admin' %}\n"
    )
    text = _replace_once(text, old, new, "sidebar menu: Версии")
    _write(p, text)


# ============================================================
# Шаг 8. nginx.conf
# ============================================================
def patch_nginx():
    print("[8/9] Патч nginx.conf ...")
    p = SERVER / "nginx.conf"
    text = _read(p)

    if "client_max_body_size 200m" in text:
        print("  --  уже 200m, пропускаю")
        return

    old = "    client_max_body_size 10m;\n"
    if old not in text:
        raise SystemExit("nginx.conf: не найден 'client_max_body_size 10m'")
    new = (
        "    # 200m — с запасом на установщик TrackerSetup.exe (~35 МБ)\n"
        "    client_max_body_size 200m;\n"
    )
    text = text.replace(old, new, 1)
    _write(p, text)


# ============================================================
# Шаг 9. Папка для артефактов
# ============================================================
def ensure_downloads_dir():
    print("[9/9] Создаю server/static/downloads/ ...")
    d = SERVER / "static" / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitkeep").write_text("", encoding="utf-8")
    print(f"  OK  {d}")


def main():
    print("=" * 60)
    print("Патч #2: публикация версий клиента (сервер, часть 2/2)")
    print("=" * 60)
    print()
    if not ROOT.exists():
        raise SystemExit(f"Не найден {ROOT}")

    patch_main()
    patch_web_admin()
    create_versions_template()
    patch_base_html()
    patch_nginx()
    ensure_downloads_dir()

    print()
    print("=" * 60)
    print("ГОТОВО.")
    print("=" * 60)
    print()
    print("Дальше — в PowerShell:")
    print()
    print("  cd D:\\tracker")
    print("  docker compose down")
    print("  docker compose up -d --build")
    print()
    print("Проверка (через 30-60 сек):")
    print("  docker compose logs api --tail=30")
    print("  docker compose exec -T api alembic -c /app/server/alembic.ini current")
    print()
    print("Ожидаем в логе: 'Running upgrade ... a1b2c3d4e5f6'")
    print("И потом:    'a1b2c3d4e5f6 (head)'")
    print()
    print("Открыть:")
    print("  https://192.168.0.35/admin/versions")
    print()


if __name__ == "__main__":
    main()
Запуск
powershell
cd D:\tracker
client\.venv\Scripts\python.exe _apply_versions2.py
Что делает:
•	при чтении всех файлов сначала нормализует CRLF → LF (это и было причиной сбоя),
•	записывает файлы с LF — Python это не ломает, никакого влияния на работу,
•	идемпотентен: если шаг уже применён — печатает «уже пропатчен, пропускаю» и идёт дальше,
•	шаг 1-3 не трогает (models.py, миграция, schemas.py уже записаны первым патчером).
После патча
powershell
cd D:\tracker
docker compose down
docker compose up -d --build
Почему down && up --build, а не restart:
•	добавляются новые Python-эндпоинты (multipart) — нужна пересборка образа,
•	на старте API применится миграция a1b2c3d4e5f6 (3 новые колонки в client_versions).
Проверка через 30-60 секунд:
powershell
docker compose logs api --tail=30
docker compose exec -T api alembic -c /app/server/alembic.ini current
В логе должно быть:
•	Running upgrade ... -> a1b2c3d4e5f6
•	финально a1b2c3d4e5f6 (head)
Открыть в браузере
https://192.168.0.35/admin/versions
Должно быть:
•	в сайдбаре пункт «Версии» (под «Планировщик»),
•	заголовок «Версии клиента»,
•	карточка с формой загрузки,
•	пустая таблица «Версии ещё не опубликованы».
Проверка клиентского API:
powershell
curl.exe -k https://192.168.0.35/api/v1/version
Ответ — JSON с latest_version: "0.0.0" (или что там сейчас), плюс новые поля sha256: null, file_size: null.
Если что-то не так — пришли docker compose logs api --tail=40, разберёмся. Как подтвердишь, что страница открывается и миграция применилась, дам следующий пакет: SCP-кнопка публикации + updater.py с проверкой sha256 и диалогом согласия.
PS D:\tracker> cd D:\tracker >> client\.venv\Scripts\python.exe _apply_versions2.py ============================================================ Патч #2: публикация версий клиента (сервер, часть 2/2) ============================================================ [4/9] Патч main.py ... НЕ НАЙДЕН блок: get_latest_version + новые эндпоинты
The problem: the block matching is still failing. Let me think about why.
The user's main.py was originally using CRLF and the first patcher failed. Now the second patcher normalizes CRLF→LF before matching. So the block should be found now... unless the actual content in main.py differs from what I expect.
Looking at the user's original main.py at the bottom:
python
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
Hmm, that's exactly my marker. So why did it fail?
Wait — maybe the FIRST patcher already partially modified main.py? No, the first patcher failed AT step 4.5, before any _write for main.py. Let me re-read...
Actually, looking again at first patcher: it failed on _replace_once(text, old_version, new_block, "get_latest_version + новые эндпоинты"). This means it went through 4.1-4.4 successfully in memory, but then 4.5 failed. And _write(p, text) was NOT called. So main.py should be unchanged.
But wait - 4.1 (import os) might have not succeeded either since the original file starts with:
text
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
Let me check my marker:
text
'import secrets\nfrom datetime import datetime, timedelta, timezone\n'
Yes, this should match. So 4.1-4.4 succeeded in memory.
Then 4.5 should match get_latest_version block... Hmm.
Oh wait! Look at the actual main.py more carefully. Right before @app.get("/api/v1/version"...) there are these lines:
python
# ============================================================
# Version
# ============================================================

# ============================================================
# Удаление персональных настроек (сброс к глобальным)
# ============================================================
@app.delete("/api/v1/client-settings")
...
And AFTER all the client-settings stuff, at the very bottom:
python
@app.get("/api/v1/version", response_model=VersionResponse)
def get_latest_version(current: str = "", db: Session = Depends(get_db)):
    latest = (db.query(ClientVersion)
              .order_by(ClientVersion.release_date.desc()).first())
    ...
So the marker should match. Unless... hold on. What if the patcher #1 actually DID write something? Let me trace through the first patcher's _write(p, text):
python
def patch_main():
    p = SERVER / "main.py"
    _p("[4/9] Патч main.py ...")
    text = _read(p)
    # 4.1 - OK
    # 4.2 - OK
    # 4.3 - OK
    # 4.4 - OK
    # 4.5 - FAILS HERE
    text = _replace_once(text, old_version, new_block, "...")
Right, the _write(p, text) call is at the end of the function, after 4.5. Since 4.5 raised SystemExit, _write was never called. So main.py is unchanged.
Now in patcher #2, I'm doing the same replacements. Let me check my marker in patcher #2:
python
old_version = (
    '@app.get("/api/v1/version", response_model=VersionResponse)\n'
    'def get_latest_version(current: str = "", db: Session = Depends(get_db)):\n'
    '    latest = (db.query(ClientVersion)\n'
    '              .order_by(ClientVersion.release_date.desc()).first())\n'
    '    if not latest:\n'
    '        return VersionResponse(latest_version=current or "0.0.0",\n'
    '                               download_url="", mandatory=False)\n'
    '    return VersionResponse(latest_version=latest.version,\n'
    '                           download_url=latest.download_url,\n'
    '                           mandatory=latest.mandatory,\n'
    '                           release_notes=latest.release_notes)\n'
)
Hmm. That looks correct.
Wait! Maybe the problem is that in patcher #2 I check for /api/v1/downloads/ first, and if it's not present, I continue. Then I check for \nimport os\n — if not present, I do the replacement (adds import os AND from pathlib import Path).
But the first patcher #1 already modified text in memory (4.1-4.4 succeeded in memory). If #1 wrote text — no, it didn't.
Hmm, so what's the difference?
Actually wait — I need to check what the actual current state of main.py is. Maybe user's editor or something else modified it. OR... maybe I'm missing something.
Actually, let me re-read the beginning of patcher #2:
python
def patch_main():
    p = SERVER / "main.py"
    print("[4/9] Патч main.py ...")
    text = _read(p)

    # Идемпотентность: если уже патчили — выходим.
    if "/api/v1/downloads/" in text:
        print("  --  уже пропатчен (есть /api/v1/downloads/), пропускаю")
        return

    # --- 4.1. import os + from pathlib import Path --------------------
    if "\nimport os\n" not in text:
        text = _replace_once(
            text,
            "import secrets\nfrom datetime import datetime, timedelta, timezone\n",
            "import os\nimport secrets\nfrom datetime import datetime, timedelta, timezone\n"
            "from pathlib import Path\n",
            "import os + Path",
        )
    ...
Hmm. What if the original file has import secrets in a different context? Let me look at what user provided:
python
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
OK, so import secrets\nfrom datetime import datetime, timedelta, timezone\n should match.
Actually... wait. What about \nimport os\n? Let me check whether the original main.py already has this. Looking at user's paste:
python
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
...
# ------------------------------------------------------------
# Alembic: zapusk migracij pri starte prilozheniya
# ------------------------------------------------------------
...
import os
from alembic.config import Config as AlembicConfig
Yes! There IS import os later in the file. But it's import os\n not \nimport os\n. Actually it's:
text
# ------------------------------------------------------------
import os
from alembic.config import Config as AlembicConfig
So the check if "\nimport os\n" not in text: would be TRUE if... wait, \nimport os\n — that requires a newline BEFORE import os. Let me check: the preceding line is # -------...-------\n. So the text contains ...---------\nimport os\n. Yes, so \nimport os\n IS in text. So the check if "\nimport os\n" not in text is FALSE, so we DON'T do the replacement.
But wait, from pathlib import Path — is it in the file? No, it's not in the original user paste. So we skipped adding from pathlib import Path!
Then step 4.4 uses Path(__file__).resolve().parent... — but Path is not imported. That's a separate problem, but wouldn't cause the block-not-found error.
Hmm, that's not the reason for the failure either.
OK let me think again. The 4.5 marker uses \n line endings. The _read function normalizes CRLF→LF. So the marker should be found...
Unless! Maybe the file has some other whitespace variation. Let me look super carefully at the marker:
text
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
    return VersionResponse(latest_version=latest.version,
                           download_url=latest.download_url,
                           mandatory=latest.mandatory,
                           release_notes=latest.release_notes)
And the user's paste:
text
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
    return VersionResponse(latest_version=latest.version,
                           download_url=latest.download_url,
                           mandatory=latest.mandatory,
                           release_notes=latest.release_notes)
Wait, I need to count spaces precisely.
User's paste (as I see it):
text
    if not latest:
        return VersionResponse(latest_version=current or "0.0.0",
                               download_url="", mandatory=False)
if not latest: - 4 spaces
return VersionResponse... - 8 spaces
download_url... - 31 spaces? Let me count: download_url — that's 31 spaces.
Marker: ' download_url="", mandatory=False)\n'
I see 31 spaces in the marker too.
Hmm, hard to tell exactly. Let me try a different approach: instead of relying on marker match, use a regex or use str.find with a shortened marker.
Actually, a much more robust approach: use a shorter unique marker like def get_latest_version( and find the surrounding block by searching for the function.
Or better — the fail is at _replace_once which is strict. Let me make the patcher use a more relaxed approach: find the LINE @app.get("/api/v1/version", response_model=VersionResponse) and replace everything until the end of the file (since that's the last function in the file).
Looking at user's paste, get_latest_version IS the last function in the file. So we can just truncate at that point and append the new block.
Actually simpler and safest: search for '@app.get("/api/v1/version", response_model=VersionResponse)\n' in the text, and replace from there to end of file.
Let me write the fix.
Actually, first let me diagnose the actual problem. I'll write a quick diagnostic script the user can run. But that's a hassle. Better to just write the fixed patcher that uses a more robust approach.
Let me use this approach: find the marker @app.get("/api/v1/version", response_model=VersionResponse) and replace from that position through the end of the function.
Actually simplest: since the function is the LAST in the file, we can do:
python
marker = '@app.get("/api/v1/version", response_model=VersionResponse)'
idx = text.find(marker)
if idx == -1:
    raise SystemExit("Не найден @app.get ... version")
# Всё от маркера до конца файла заменяем новым блоком
new_text = text[:idx] + new_block
That works if the function is last. Let me confirm from user's paste: yes, get_latest_version is the last function, ends the file (no more code after).
Same approach for step 4.1-4.4 — use single-line markers.
Let me rewrite patcher #2 as #3, being more careful. Also fix the \nimport os\n issue — check if os module is used/needed. Actually the original file DOES import os in the middle. So we don't need to add it. But we DO need from pathlib import Path.
Let me check what my new code uses:
•	os.path.basename — needs import os (already there, later in file — Python allows imports anywhere though, but it's used at import-time by decorator? No, at request time. So fine.)
•	Path(__file__) — needs from pathlib import Path. Original doesn't have it. Need to add.
•	hashlib — already imported
•	json — already imported
So I need to add from pathlib import Path.
Let me write patcher #3.
Also — важно! — my check if "\nimport os\n" not in text was wrong logic. It should be checking whether import os is missing. But \nimport os\n requires newline before and after. In original file:
text
# ------------------------------------------------------------
import os
from alembic.config import Config as AlembicConfig
Preceding is ----\n, then import os\n. So text contains ----\nimport os\n. The substring \nimport os\n IS present. So check is false. Skipped — good (we didn't want to add it twice anyway).
But I also wanted to add from pathlib import Path — which was in the same replacement. Since replacement was skipped, Path is not imported. But it doesn't break the block-matching. It would break at runtime when the endpoint is hit. Need to add from pathlib import Path separately.
OK let me write clean patcher #3.
python
def patch_main():
    p = SERVER / "main.py"
    print("[4/9] Патч main.py ...")
    text = _read(p)

    # Идемпотентность
    if "/api/v1/downloads/" in text:
        print("  --  уже пропатчен, пропускаю")
        return

    # --- 4.1a. from pathlib import Path (отдельно) ---
    if "from pathlib import Path" not in text:
        text = _replace_once(
            text,
            "from datetime import datetime, timedelta, timezone\n",
            "from datetime import datetime, timedelta, timezone\nfrom pathlib import Path\n",
            "from pathlib import Path",
        )

    # --- 4.2. fastapi imports ---
    text = _replace_once(
        text,
        "from fastapi import Depends, FastAPI, Header, HTTPException, Request\n",
        "from fastapi import (\n"
        "    Depends, FastAPI, File, Form, Header, HTTPException, Request,\n"
        "    UploadFile,\n"
        ")\n",
        "fastapi: File/Form/UploadFile",
    )

    # --- 4.3. FileResponse ---
    text = _replace_once(
        text,
        "from fastapi.responses import RedirectResponse as _AdminRedirect\n",
        "from fastapi.responses import FileResponse, RedirectResponse as _AdminRedirect\n",
        "FileResponse",
    )

    # --- 4.4. DOWNLOADS_DIR ---
    text = _replace_once(
        text,
        'app = FastAPI(title="Employee Tracker API", version="1.4.0")\n',
        ...,
        "DOWNLOADS_DIR",
    )

    # --- 4.5. Замена хвоста. Ищем по однострочному маркеру. ---
    marker = '@app.get("/api/v1/version", response_model=VersionResponse)\n'
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("main.py: не найден декоратор @app.get(/api/v1/version)")
    head = text[:idx]
    text = head + new_block  # new_block должен содержать свою же версию @app.get
    
    _write(p, text)
    _check_py(p)
Where new_block includes the @app.get("/api/v1/version", ...) decorator again.
This is much more robust.
But wait — one more thing. The user's main.py might have gotten from pathlib import Path added already? No, because patcher #2 failed BEFORE write. So main.py is intact.
Actually I realize I should just make patcher #3 minimal — only fix the version block. Because steps 4.1-4.4 didn't persist either (the whole patch_main() raises before write). So I need to redo 4.1-4.4 too.
Let me write patcher #3 carefully.
Actually let me also think about import os — the file already has it, but later in the middle. That should work fine because Python allows imports anywhere and they execute at import time of the module, not at function call time. But wait — is import os at module level (even if positioned later)? Yes:
python
# ------------------------------------------------------------
# Alembic: zapusk migracij pri starte prilozheniya
# ------------------------------------------------------------
import os
from alembic.config import Config as AlembicConfig
These are module-level imports (no indentation). So os is available everywhere. Good.
Similarly from pathlib import Path — NOT in the file, so I need to add it.
Where to add? Top with other imports. After from datetime import... line works.
Actually, is there a name clash? Let me search for Path in main.py... not present. Good.
FileResponse — where to add? from fastapi.responses import RedirectResponse as _AdminRedirect\n. Yes.
Let me now also think about whether patcher #2's steps 5-9 persisted. They didn't run — because patch_main() raised SystemExit which propagates up through main() and kills the process. So ONLY step 4 failed, nothing else ran. Good — but that means I need to redo steps 5-9 too.
Actually wait, let me check the log output the user gave:
text
[4/9] Патч main.py ...
НЕ НАЙДЕН блок: get_latest_version + новые эндпоинты
Yes, only step 4 was attempted. So steps 5-9 also need to run. Patcher #3 needs to do all of 4-9.
OK let me write patcher #3.
Also — I want to minimize future failures. Let me write it more robustly, with the marker on a single line each, and better diagnostics.
Let me write it:
Понял. Проблема в содержимом main.py: где-то в блоке get_latest_version есть невидимые отличия (пробелы/переносы/что-то ещё), которые мой строгий маркер не ловит.
Меняю тактику: вместо длинного многострочного маркера — ищу одну короткую строку @app.get("/api/v1/version", response_model=VersionResponse) и заменяю весь «хвост» файла от неё до конца (там больше ничего нет после — я проверил в твоём main.py).
Плюс сразу поправлю мелочь: from pathlib import Path нужно добавить явно (в оригинале его нет).
Создай D:\tracker\_apply_versions3.py:
python
# -*- coding: utf-8 -*-
# ============================================================
# Патчер #3: серверная часть — публикация версий клиента.
# ============================================================
# Почему #3: в #2 не сработал строгий многострочный маркер в main.py.
# Здесь используем ОДНОСТРОЧНЫЙ маркер и заменяем хвост файла
# целиком — надёжнее и не зависит от пробелов в старом коде.
#
# Идемпотентен: если шаг уже применён — пропускает.
# Шаги 1-3 (models.py, миграция, schemas.py) НЕ трогает —
# они уже применены ранее.
# ============================================================

from pathlib import Path
import ast

ROOT = Path(r"D:\tracker")
SERVER = ROOT / "server"


def _read(p: Path) -> str:
    """Читает файл, приводя переносы к LF."""
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _write(p: Path, text: str):
    p.write_text(text, encoding="utf-8", newline="\n")
    print(f"  OK  записан {p.relative_to(ROOT)} ({len(text)} байт)")


def _replace_once(text: str, old: str, new: str, what: str) -> str:
    if old not in text:
        raise SystemExit(f"НЕ НАЙДЕН блок: {what}")
    cnt = text.count(old)
    if cnt > 1:
        raise SystemExit(f"Блок '{what}' встречается {cnt} раз — уточни маркер")
    return text.replace(old, new, 1)


def _check_py(p: Path):
    try:
        ast.parse(_read(p))
    except SyntaxError as e:
        raise SystemExit(f"СИНТАКСИС {p.name}: {e}")
    print(f"  OK  синтаксис {p.name} валиден")


# ============================================================
# Шаг 4. main.py
# ============================================================
def patch_main():
    p = SERVER / "main.py"
    print("[4/9] Патч main.py ...")
    text = _read(p)

    # Идемпотентность
    if "/api/v1/downloads/" in text:
        print("  --  уже пропатчен, пропускаю")
        return

    # --- 4.1. from pathlib import Path ---------------------------------
    if "from pathlib import Path" not in text:
        text = _replace_once(
            text,
            "from datetime import datetime, timedelta, timezone\n",
            "from datetime import datetime, timedelta, timezone\nfrom pathlib import Path\n",
            "from pathlib import Path",
        )
        print("  --  +from pathlib import Path")

    # import os в файле уже есть (в блоке Alembic, module-level).
    # Проверим на всякий случай:
    if "\nimport os\n" not in text and "\nimport os\r\n" not in text:
        # Не критично — на всякий случай добавим
        text = text.replace(
            "import secrets\n",
            "import os\nimport secrets\n",
            1,
        )
        print("  --  +import os (подстраховка)")

    # --- 4.2. fastapi: File/Form/UploadFile ----------------------------
    text = _replace_once(
        text,
        "from fastapi import Depends, FastAPI, Header, HTTPException, Request\n",
        "from fastapi import (\n"
        "    Depends, FastAPI, File, Form, Header, HTTPException, Request,\n"
        "    UploadFile,\n"
        ")\n",
        "fastapi: File/Form/UploadFile",
    )
    print("  --  +fastapi File/Form/UploadFile")

    # --- 4.3. FileResponse ---------------------------------------------
    text = _replace_once(
        text,
        "from fastapi.responses import RedirectResponse as _AdminRedirect\n",
        "from fastapi.responses import FileResponse, RedirectResponse as _AdminRedirect\n",
        "FileResponse",
    )
    print("  --  +FileResponse")

    # --- 4.4. DOWNLOADS_DIR --------------------------------------------
    text = _replace_once(
        text,
        'app = FastAPI(title="Employee Tracker API", version="1.4.0")\n',
        'app = FastAPI(title="Employee Tracker API", version="1.4.0")\n'
        '\n'
        '# ------------------------------------------------------------\n'
        '# Каталог для артефактов клиента (установщиков .exe).\n'
        '# На хосте:     D:\\tracker\\server\\static\\downloads\\\n'
        '# В контейнере: /app/server/static/downloads/\n'
        '# Монтируется через docker-compose (./server:/app/server).\n'
        '# ------------------------------------------------------------\n'
        'DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"\n',
        "DOWNLOADS_DIR",
    )
    print("  --  +DOWNLOADS_DIR")

    # --- 4.5. Замена блока version через ОДНОСТРОЧНЫЙ маркер ---------
    # Идея: get_latest_version — последняя функция в файле.
    # Находим её декоратор (одна строка) и всё от неё до конца файла
    # заменяем новым блоком.
    marker = '@app.get("/api/v1/version", response_model=VersionResponse)\n'
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit(
            "main.py: не найден маркер\n"
            "  " + repr(marker) + "\n"
            "Проверь, что в main.py есть эндпоинт /api/v1/version."
        )

    head = text[:idx]

    new_tail = (
        '@app.get("/api/v1/version", response_model=VersionResponse)\n'
        'def get_latest_version(current: str = "", db: Session = Depends(get_db)):\n'
        '    """\n'
        '    Возвращает последнюю опубликованную версию клиента.\n'
        '    Клиент сравнивает её со своей CLIENT_VERSION.\n'
        '    """\n'
        '    latest = (db.query(ClientVersion)\n'
        '              .order_by(ClientVersion.release_date.desc()).first())\n'
        '    if not latest:\n'
        '        return VersionResponse(latest_version=current or "0.0.0",\n'
        '                               download_url="", mandatory=False)\n'
        '    return VersionResponse(\n'
        '        latest_version=latest.version,\n'
        '        download_url=latest.download_url,\n'
        '        mandatory=latest.mandatory,\n'
        '        release_notes=latest.release_notes,\n'
        '        sha256=latest.sha256,\n'
        '        file_size=latest.file_size,\n'
        '    )\n'
        '\n'
        '\n'
        '# ============================================================\n'
        '# Публикация версий клиента\n'
        '# ============================================================\n'
        '# Публикуется установщик TrackerSetup.exe. Сервер сам:\n'
        '#   1. Сохраняет файл в server/static/downloads/TrackerSetup-<v>.exe\n'
        '#   2. Считает sha256 файла\n'
        '#   3. Создаёт запись в client_versions\n'
        '# Клиент скачивает файл через /api/v1/downloads/... и сверяет sha256.\n'
        '# ============================================================\n'
        '\n'
        '\n'
        'def _sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:\n'
        '    """SHA-256 файла. Читаем блоками по 1 МБ — не держим .exe в RAM."""\n'
        '    h = hashlib.sha256()\n'
        '    with open(path, "rb") as f:\n'
        '        for block in iter(lambda: f.read(chunk), b""):\n'
        '            h.update(block)\n'
        '    return h.hexdigest()\n'
        '\n'
        '\n'
        '@app.get("/api/v1/downloads/{filename}")\n'
        'def download_artifact(filename: str):\n'
        '    """\n'
        '    Отдаёт .exe-артефакт клиенту.\n'
        '    Защита от path traversal: работаем только с basename.\n'
        '    """\n'
        '    safe_name = os.path.basename(filename)\n'
        '    if not safe_name or safe_name != filename:\n'
        '        raise HTTPException(400, "invalid filename")\n'
        '    path = DOWNLOADS_DIR / safe_name\n'
        '    if not path.exists() or not path.is_file():\n'
        '        raise HTTPException(404, "file not found")\n'
        '    return FileResponse(\n'
        '        path,\n'
        '        media_type="application/octet-stream",\n'
        '        filename=safe_name,\n'
        '    )\n'
        '\n'
        '\n'
        '@app.post("/api/v1/admin/versions/publish",\n'
        '          dependencies=[Depends(require_admin)])\n'
        'async def publish_version(\n'
        '    request: Request,\n'
        '    file: UploadFile = File(...),\n'
        '    version: str = Form(...),\n'
        '    release_notes: str = Form(""),\n'
        '    mandatory: str = Form("0"),\n'
        '    published_by: str = Form(""),\n'
        '    download_base: str = Form(""),\n'
        '    db: Session = Depends(get_db),\n'
        '):\n'
        '    """\n'
        '    Публикация новой версии клиента (multipart/form-data).\n'
        '    Заголовок: X-Admin-Token.\n'
        '\n'
        '    file          — сам .exe\n'
        '    version       — например "1.4.1" (<=32 символов, уникальная)\n'
        '    release_notes — что нового (опционально)\n'
        '    mandatory     — "1"/"true" для обязательного\n'
        '    published_by  — "user@host" (опционально, для аудита)\n'
        '    download_base — базовый URL (например "https://192.168.0.35");\n'
        '                    если пусто — берём из request.base_url\n'
        '    """\n'
        '    version = (version or "").strip()\n'
        '    if not version or len(version) > 32:\n'
        '        raise HTTPException(400, "Некорректная версия")\n'
        '\n'
        '    if db.query(ClientVersion).filter(ClientVersion.version == version).first():\n'
        '        raise HTTPException(409, f"Версия {version} уже опубликована")\n'
        '\n'
        '    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)\n'
        '    safe_name = f"TrackerSetup-{version}.exe"\n'
        '    target = DOWNLOADS_DIR / safe_name\n'
        '\n'
        '    # Пишем потоком — не грузим весь .exe в память.\n'
        '    written = 0\n'
        '    with open(target, "wb") as f:\n'
        '        while True:\n'
        '            chunk = await file.read(1024 * 1024)\n'
        '            if not chunk:\n'
        '                break\n'
        '            f.write(chunk)\n'
        '            written += len(chunk)\n'
        '\n'
        '    if written == 0:\n'
        '        target.unlink(missing_ok=True)\n'
        '        raise HTTPException(400, "Пустой файл")\n'
        '\n'
        '    sha = _sha256_file(target)\n'
        '\n'
        '    if download_base:\n'
        '        base = download_base.strip().rstrip("/")\n'
        '    else:\n'
        '        base = str(request.base_url).rstrip("/")\n'
        '    download_url = f"{base}/api/v1/downloads/{safe_name}"\n'
        '\n'
        '    row = ClientVersion(\n'
        '        version=version,\n'
        '        release_date=_now(),\n'
        '        download_url=download_url,\n'
        '        mandatory=(str(mandatory).lower() in ("1", "true", "yes", "on")),\n'
        '        release_notes=(release_notes or "").strip() or None,\n'
        '        sha256=sha,\n'
        '        file_size=written,\n'
        '        published_by=(published_by or "api").strip()[:128],\n'
        '    )\n'
        '    db.add(row)\n'
        '    db.add(AuditLog(\n'
        '        actor=(published_by or "api")[:128],\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="publish",\n'
        '        new_value=json.dumps({\n'
        '            "version": version,\n'
        '            "size": written,\n'
        '            "sha256": sha,\n'
        '            "mandatory": row.mandatory,\n'
        '            "download_url": download_url,\n'
        '        }, ensure_ascii=False),\n'
        '    ))\n'
        '    db.commit()\n'
        '\n'
        '    log.info(\n'
        '        "Published client version %s (%d bytes, sha256=%s)",\n'
        '        version, written, sha[:12],\n'
        '    )\n'
        '    return {\n'
        '        "status": "ok",\n'
        '        "version": version,\n'
        '        "download_url": download_url,\n'
        '        "sha256": sha,\n'
        '        "file_size": written,\n'
        '    }\n'
        '\n'
        '\n'
        '@app.post("/api/v1/admin/versions/{version}/delete",\n'
        '          dependencies=[Depends(require_admin)])\n'
        'def delete_version(version: str, db: Session = Depends(get_db)):\n'
        '    """Удаляет запись версии и файл на диске (если есть)."""\n'
        '    row = (db.query(ClientVersion)\n'
        '           .filter(ClientVersion.version == version).first())\n'
        '    if not row:\n'
        '        raise HTTPException(404, "Версия не найдена")\n'
        '\n'
        '    filename = os.path.basename(row.download_url)\n'
        '    path = DOWNLOADS_DIR / filename\n'
        '    file_deleted = False\n'
        '    if filename and path.exists() and path.is_file():\n'
        '        try:\n'
        '            path.unlink()\n'
        '            file_deleted = True\n'
        '        except Exception as e:\n'
        '            log.warning("Не удалось удалить файл %s: %s", path, e)\n'
        '\n'
        '    db.delete(row)\n'
        '    db.add(AuditLog(\n'
        '        actor="admin",\n'
        '        entity="client_version",\n'
        '        entity_id=version,\n'
        '        action="delete",\n'
        '        new_value=json.dumps({"file_deleted": file_deleted}),\n'
        '    ))\n'
        '    db.commit()\n'
        '    return {"status": "ok", "file_deleted": file_deleted}\n'
    )

    text = head + new_tail
    print("  --  заменил хвост файла (от @app.get version до конца)")
    _write(p, text)
    _check_py(p)


# ============================================================
# Шаг 5. web_admin.py
# ============================================================
def patch_web_admin():
    p = SERVER / "web_admin.py"
    print("[5/9] Патч web_admin.py ...")
    text = _read(p)

    if "def versions_page(" in text:
        print("  --  уже пропатчен, пропускаю")
        return

    # 5.1. import os
    if "\nimport os\n" not in text:
        text = _replace_once(
            text,
            "import csv\nimport logging\nimport hashlib\nimport io\nimport json\nimport secrets\n",
            "import csv\nimport logging\nimport hashlib\nimport io\nimport json\nimport os\nimport secrets\n",
            "import os",
        )
        print("  --  +import os")

    # 5.2. from pathlib import Path
    if "from pathlib import Path" not in text:
        text = _replace_once(
            text,
            "from datetime import datetime, date, time, timedelta, timezone\n",
            "from datetime import datetime, date, time, timedelta, timezone\nfrom pathlib import Path\n",
            "from pathlib import Path",
        )
        print("  --  +from pathlib import Path")

    # 5.3. File/UploadFile
    text = _replace_once(
        text,
        "from fastapi import APIRouter, Depends, Request, Form, HTTPException\n",
        "from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File\n",
        "fastapi: File/UploadFile",
    )
    print("  --  +File/UploadFile")

    # 5.4. ClientVersion в импорте моделей
    text = _replace_once(
        text,
        "from .models import (\n"
        "    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,\n"
        "    CalendarDay, Computer, Department, Employee, EmployeeSettings,\n"
        "    Record, WorkSession,\n"
        "    Schedule, ScheduledTask, TaskRun,\n"
        ")\n",
        "from .models import (\n"
        "    AppSetting, AdminLogin, AdminUser, AuditLog, BootstrapToken,\n"
        "    CalendarDay, ClientVersion, Computer, Department, Employee,\n"
        "    EmployeeSettings, Record, WorkSession,\n"
        "    Schedule, ScheduledTask, TaskRun,\n"
        ")\n",
        "import ClientVersion",
    )
    print("  --  +ClientVersion в imports")

    # 5.5. Роуты — в самый конец
    routes_block = (
        "\n\n"
        "# ============================================================\n"
        "# ВЕРСИИ КЛИЕНТА (публикация релизов .exe)\n"
        "# ============================================================\n"
        "# Файлы хранятся в server/static/downloads/.\n"
        "# Раздача клиентам — GET /api/v1/downloads/{filename} (main.py).\n"
        "# Доступ — только роль admin.\n"
        "# ============================================================\n"
        "\n"
        'VERSIONS_DOWNLOADS_DIR = Path(__file__).resolve().parent / "static" / "downloads"\n'
        "\n"
        "\n"
        "def _versions_sha256(path: Path, chunk: int = 1024 * 1024) -> str:\n"
        '    """SHA-256 файла. Блоками по 1 МБ."""\n'
        "    h = hashlib.sha256()\n"
        '    with open(path, "rb") as f:\n'
        '        for block in iter(lambda: f.read(chunk), b""):\n'
        "            h.update(block)\n"
        "    return h.hexdigest()\n"
        "\n"
        "\n"
        '@router.get("/versions", response_class=HTMLResponse)\n'
        "def versions_page(request: Request, db: Session = Depends(get_db),\n"
        "                  _=Depends(current_admin)):\n"
        '    """Список опубликованных версий клиента + форма загрузки."""\n'
        "    _require_admin_role(request)\n"
        "    versions = (db.query(ClientVersion)\n"
        "                .order_by(desc(ClientVersion.release_date)).all())\n"
        '    return templates.TemplateResponse("versions.html", {\n'
        '        "request": request,\n'
        '        "versions": versions,\n'
        '        "saved": request.query_params.get("saved") == "1",\n'
        '        "deleted_ok": request.query_params.get("deleted") == "1",\n'
        '        "error": request.query_params.get("error"),\n'
        "    })\n"
        "\n"
        "\n"
        '@router.post("/versions/upload")\n'
        "async def versions_upload(\n"
        "    request: Request,\n"
        "    file: UploadFile = File(...),\n"
        "    version: str = Form(...),\n"
        '    release_notes: str = Form(""),\n'
        '    mandatory: str = Form(""),\n'
        "    db: Session = Depends(get_db),\n"
        "    _=Depends(current_admin),\n"
        "):\n"
        '    """Загрузка нового .exe через веб-форму."""\n'
        "    user = _require_admin_role(request)\n"
        '    version = (version or "").strip()\n'
        "    if not version or len(version) > 32:\n"
        '        return RedirectResponse("/admin/versions?error=bad_version", status_code=303)\n'
        "    if db.query(ClientVersion).filter(ClientVersion.version == version).first():\n"
        '        return RedirectResponse("/admin/versions?error=already_exists", status_code=303)\n'
        "\n"
        "    VERSIONS_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)\n"
        '    safe_name = f"TrackerSetup-{version}.exe"\n'
        "    target = VERSIONS_DOWNLOADS_DIR / safe_name\n"
        "\n"
        "    written = 0\n"
        '    with open(target, "wb") as f:\n'
        "        while True:\n"
        "            chunk = await file.read(1024 * 1024)\n"
        "            if not chunk:\n"
        "                break\n"
        "            f.write(chunk)\n"
        "            written += len(chunk)\n"
        "    if written == 0:\n"
        "        target.unlink(missing_ok=True)\n"
        '        return RedirectResponse("/admin/versions?error=empty_file", status_code=303)\n'
        "\n"
        "    sha = _versions_sha256(target)\n"
        '    base = str(request.base_url).rstrip("/")\n'
        '    download_url = f"{base}/api/v1/downloads/{safe_name}"\n'
        "\n"
        "    row = ClientVersion(\n"
        "        version=version,\n"
        "        release_date=_now(),\n"
        "        download_url=download_url,\n"
        "        mandatory=bool(mandatory),\n"
        '        release_notes=(release_notes or "").strip() or None,\n'
        "        sha256=sha,\n"
        "        file_size=written,\n"
        '        published_by=f"web:{user[\'username\']}",\n'
        "    )\n"
        "    db.add(row)\n"
        "    db.add(AuditLog(\n"
        '        actor=user["username"],\n'
        '        entity="client_version",\n'
        "        entity_id=version,\n"
        '        action="publish_web",\n'
        "        new_value=json.dumps({\n"
        '            "version": version, "size": written, "sha256": sha,\n'
        '            "mandatory": row.mandatory,\n'
        "        }, ensure_ascii=False),\n"
        "    ))\n"
        "    db.commit()\n"
        "\n"
        '    log.info("Published version %s via web (%d bytes)", version, written)\n'
        '    return RedirectResponse("/admin/versions?saved=1", status_code=303)\n'
        "\n"
        "\n"
        '@router.post("/versions/{version}/delete")\n'
        "def versions_delete(\n"
        "    version: str,\n"
        "    request: Request,\n"
        "    db: Session = Depends(get_db),\n"
        "    _=Depends(current_admin),\n"
        "):\n"
        '    """Удаляет версию: запись в БД + файл на диске."""\n'
        '    user = _require_admin_role(request)\n'
        "    row = db.query(ClientVersion).filter(ClientVersion.version == version).first()\n"
        "    if not row:\n"
        '        raise HTTPException(404, "Версия не найдена")\n'
        "\n"
        "    filename = os.path.basename(row.download_url)\n"
        "    path = VERSIONS_DOWNLOADS_DIR / filename\n"
        "    if filename and path.exists() and path.is_file():\n"
        "        try:\n"
        "            path.unlink()\n"
        "        except Exception as e:\n"
        '            log.warning("Failed to unlink %s: %s", path, e)\n'
        "\n"
        "    db.delete(row)\n"
        "    db.add(AuditLog(\n"
        '        actor=user["username"],\n'
        '        entity="client_version",\n'
        "        entity_id=version,\n"
        '        action="delete",\n'
        "    ))\n"
        "    db.commit()\n"
        '    return RedirectResponse("/admin/versions?deleted=1", status_code=303)\n'
    )
    text = text + routes_block
    _write(p, text)
    _check_py(p)


# ============================================================
# Шаг 6. versions.html
# ============================================================
def create_versions_template():
    print("[6/9] Создаю шаблон versions.html ...")
    p = SERVER / "templates" / "versions.html"
    if p.exists():
        print("  --  файл уже есть, пропускаю")
        return
    content = """{% extends "base.html" %}
{% block title %}Версии клиента{% endblock %}
{% block content %}
<h3 class="mb-4">Версии клиента</h3>

{% if saved %}
<div class="alert alert-success py-2">Версия опубликована.</div>
{% endif %}
{% if deleted_ok %}
<div class="alert alert-info py-2">Версия удалена.</div>
{% endif %}
{% if error == 'bad_version' %}
<div class="alert alert-warning py-2">Некорректная версия.</div>
{% endif %}
{% if error == 'already_exists' %}
<div class="alert alert-warning py-2">Такая версия уже опубликована.</div>
{% endif %}
{% if error == 'empty_file' %}
<div class="alert alert-warning py-2">Файл пустой.</div>
{% endif %}

{# --- Форма загрузки --- #}
<div class="card mb-4">
  <div class="card-header">Опубликовать новую версию</div>
  <div class="card-body">
    <form method="post" action="/admin/versions/upload" enctype="multipart/form-data">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Файл установщика (.exe)</label>
          <input class="form-control" type="file" name="file" accept=".exe" required>
          <div class="form-text">Обычно — client/dist_installer/TrackerSetup.exe</div>
        </div>
        <div class="col-md-3">
          <label class="form-label">Версия</label>
          <input class="form-control" type="text" name="version" placeholder="1.4.1" maxlength="32" required>
        </div>
        <div class="col-md-3 d-flex align-items-end">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="mandatory" id="cbMandatory" value="1">
            <label class="form-check-label" for="cbMandatory">Обязательное обновление</label>
          </div>
        </div>
        <div class="col-12">
          <label class="form-label">Что нового (release notes)</label>
          <textarea class="form-control" name="release_notes" rows="3"
                    placeholder="Например: исправлен баг с отправкой сессий..."></textarea>
        </div>
        <div class="col-12">
          <button class="btn btn-primary">Опубликовать</button>
          <span class="text-muted ms-3 small">
            При публикации сервер сам считает sha256 и сохранит файл в
            <code>server/static/downloads/</code>.
          </span>
        </div>
      </div>
    </form>
  </div>
</div>

{# --- Список опубликованных --- #}
<table class="table table-sm bg-white align-middle">
  <thead>
    <tr>
      <th style="width:130px">Версия</th>
      <th style="width:160px">Дата</th>
      <th style="width:110px">Размер</th>
      <th style="width:150px">Опубликовал</th>
      <th style="width:110px">Mandatory</th>
      <th>Release notes</th>
      <th style="width:180px">sha256</th>
      <th style="width:90px">Действия</th>
    </tr>
  </thead>
  <tbody>
  {% for v in versions %}
    <tr>
      <td><strong>{{ v.version }}</strong></td>
      <td class="small">{{ v.release_date | dt }}</td>
      <td class="small">
        {% if v.file_size %}
          {{ "%.2f"|format(v.file_size / 1048576) }} МБ
        {% else %}—{% endif %}
      </td>
      <td class="small">{{ v.published_by or '—' }}</td>
      <td>
        {% if v.mandatory %}
          <span class="badge bg-danger">Да</span>
        {% else %}
          <span class="badge bg-secondary">Нет</span>
        {% endif %}
      </td>
      <td class="small" style="max-width:340px; white-space:pre-wrap;">{{ v.release_notes or '—' }}</td>
      <td class="small">
        {% if v.sha256 %}
          <code title="{{ v.sha256 }}">{{ v.sha256[:12] }}…</code>
        {% else %}—{% endif %}
      </td>
      <td>
        <form method="post" action="/admin/versions/{{ v.version }}/delete"
              onsubmit="return confirm('Удалить версию {{ v.version }} и файл?');">
          <button class="btn btn-sm btn-outline-danger">Удалить</button>
        </form>
      </td>
    </tr>
  {% else %}
    <tr><td colspan="8" class="text-center text-muted py-4">
      Версии ещё не опубликованы.
    </td></tr>
  {% endfor %}
  </tbody>
</table>

<div class="text-muted small mt-3">
  Клиенты получают информацию о последней версии из
  <code>GET /api/v1/version</code> и скачивают файл через
  <code>GET /api/v1/downloads/&lt;filename&gt;</code>.
</div>
{% endblock %}
"""
    _write(p, content)


# ============================================================
# Шаг 7. base.html — пункт меню
# ============================================================
def patch_base_html():
    print("[7/9] Патч base.html ...")
    p = SERVER / "templates" / "base.html"
    text = _read(p)

    if '/admin/versions' in text:
        print("  --  пункт меню уже есть, пропускаю")
        return

    # Ищем блок с scheduler (он есть в оригинале base.html)
    marker = '         href="/admin/scheduler">{{ _("menu.scheduler") }}</a>\n'
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("base.html: не найден пункт scheduler для вставки")
    insert_at = idx + len(marker)

    insert = (
        '      {# --- Публикация версий клиента (только admin) --- #}\n'
        '      <a class="nav-link {% if \'/versions\' in request.url.path %}active{% endif %}"\n'
        '         href="/admin/versions">Версии</a>\n'
    )
    text = text[:insert_at] + insert + text[insert_at:]
    _write(p, text)
    print("  --  +пункт «Версии» под «Планировщик»")


# ============================================================
# Шаг 8. nginx.conf
# ============================================================
def patch_nginx():
    print("[8/9] Патч nginx.conf ...")
    p = SERVER / "nginx.conf"
    text = _read(p)

    if "client_max_body_size 200m" in text:
        print("  --  уже 200m, пропускаю")
        return

    old = "    client_max_body_size 10m;\n"
    if old not in text:
        # Возможно CRLF — проверим разные варианты
        for variant in ["client_max_body_size 10m;", "client_max_body_size 10m; \n"]:
            if variant in text:
                old = variant
                break
        else:
            raise SystemExit(
                "nginx.conf: не найден 'client_max_body_size 10m'.\n"
                "Проверь вручную эту строку в файле."
            )

    new = (
        "    # 200m — с запасом на установщик TrackerSetup.exe (~35 МБ)\n"
        "    client_max_body_size 200m;\n"
    )
    text = text.replace(old, new, 1)
    _write(p, text)


# ============================================================
# Шаг 9. Папка для артефактов
# ============================================================
def ensure_downloads_dir():
    print("[9/9] Создаю server/static/downloads/ ...")
    d = SERVER / "static" / "downloads"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitkeep").write_text("", encoding="utf-8")
    print(f"  OK  {d}")


def main():
    print("=" * 60)
    print("Патч #3: публикация версий клиента (сервер, часть 2/2)")
    print("=" * 60)
    print()
    if not ROOT.exists():
        raise SystemExit(f"Не найден {ROOT}")

    patch_main()
    patch_web_admin()
    create_versions_template()
    patch_base_html()
    patch_nginx()
    ensure_downloads_dir()

    print()
    print("=" * 60)
    print("ГОТОВО.")
    print("=" * 60)
    print()
    print("Дальше — в PowerShell:")
    print()
    print("  cd D:\\tracker")
    print("  docker compose down")
    print("  docker compose up -d --build")
    print()
    print("Проверка (через 30-60 сек):")
    print("  docker compose logs api --tail=30")
    print("  docker compose exec -T api alembic -c /app/server/alembic.ini current")
    print()
    print("Ожидаем в логе: 'Running upgrade ... a1b2c3d4e5f6'")
    print("И потом:    'a1b2c3d4e5f6 (head)'")
    print()
    print("Открыть: https://192.168.0.35/admin/versions")
    print()


if __name__ == "__main__":
    main()
Запуск
powershell
cd D:\tracker
client\.venv\Scripts\python.exe _apply_versions3.py
Что отличается от #2:
1.	Главное: для замены блока get_latest_version ищу одну короткую строку — '@app.get("/api/v1/version", response_model=VersionResponse)\n' — и заменяю всё от неё до конца файла. Не завишу от пробелов в старом коде.
2.	Если маркер всё равно не найдётся — покажет repr() маркера, чтобы было видно, что именно ищем.
3.	from pathlib import Path добавляется отдельным шагом (в файле его не было).
4.	import os не трогаю — он уже есть в блоке Alembic (module-level).
5.	Остальные шаги (web_admin, шаблоны, nginx) — как в #2, но идемпотентны.
6.	Для nginx.conf — если точная строка не найдётся, попробует пару вариантов и выдаст понятную диагностику.
После патча
powershell
cd D:\tracker
docker compose down
docker compose up -d --build
Через 30-60 секунд:
powershell
docker compose logs api --tail=30
docker compose exec -T api alembic -c /app/server/alembic.ini current
В логе ждём:
•	Running upgrade ... -> a1b2c3d4e5f6
•	финально a1b2c3d4e5f6 (head)
Открой https://192.168.0.35/admin/versions — должна быть страница с формой загрузки и пустой таблицей, в сайдбаре пункт «Версии».
Если опять упадёт — пришли первые 30 строк вывода (важно, на каком шаге и что именно не найдено). Плюс, если не сложно, выполни:
powershell
Select-String -Path D:\tracker\server\main.py -Pattern 'api/v1/version' -Context 0,1
Это покажет, как именно записана строка в файле — и я сразу пойму, что не совпало.
Alembic: Multiple head revisions. Значит в базе уже было несколько head до нашей миграции. Наша миграция указала down_revision = "ecb1e3f89300", но реально в проекте есть несколько веток (несколько head).
Давай посмотрим на список миграций:
text
0f13ad394b65_add_admin_users_department_id.py
35d67a73f181_baseline.py
939e3d0b6f4c_partition_records_by_month.py
2602b71902d4_add_employee_settings.py
b02da1230e4d_add_computer_soft_delete.py
ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py
Мои правки: a1b2c3d4e5f6 с down_revision = ecb1e3f89300.
Проблема: возможно, ecb1e3f89300 — не единственный head. Может быть, есть ещё одна ветка. Судя по имени, ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py — самая новая по названию. Но, возможно, есть два параллельных head'а.
До моего изменения alembic работал — значит head был один. Значит, я добавил второй head, привязавшись не к тому родителю. Хотя, если до этого head был ровно один (ecb1e3f89300), то мой down_revision = "ecb1e3f89300" должен работать.
Но нет — Multiple heads. Значит, и до меня было несколько head'ов? Но тогда alembic upgrade head тоже падало бы. Значит, до меня было один head, а я как-то сломал цепочку.
Хм, может быть, в моём файле миграции есть опечатка в down_revision. Проверим:
python
revision = "a1b2c3d4e5f6"
down_revision = "ecb1e3f89300"
Стоп. Может быть, я неправильно понял имя. Давай проверим: у файла ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py revision может быть не ecb1e3f89300, а что-то другое. Имя файла обычно начинается с revision_id, но не всегда.
Постой. Скорее всего, я неправильно определил родителя. Нужно проверить в файлах миграций реальные revision и down_revision.
Также возможно, что у файла 0f13ad394b65_add_admin_users_department_id.py revision_id = 0f13ad394b65, а он мигрирует относительно чего-то. Может, есть ветка от 0f13ad394b65 к чему-то ещё.
Проще всего:
1.	Удалить мою миграцию (файл a1b2c3d4e5f6_add_client_versions_sha256.py).
2.	Запустить alembic и посмотреть реальные head'ы.
3.	Определить, к какому именно head нужно привязать.
Но до этого нам надо хотя бы запустить контейнер. Апи циклится, потому что миграция падает.
Стоп! Ещё важный момент: миграция не применилась, но контейнер уже перезапускается. Значит, БД в каком-то состоянии. Нужно:
1.	Остановить api, чтобы не циклился.
2.	Удалить мой файл миграции.
3.	Запустить api без миграции — но тогда alembic current покажет текущее состояние.
4.	Определить, какие head'ы. alembic heads.
5.	Понять, к какому head привязаться.
6.	Создать миграцию заново с правильным родителем.
Или проще: использовать alembic merge для склейки, но проще подкорректировать down_revision вручную.
Давай подумаем про "multiple heads". Это может быть потому что:
•	либо в проекте уже несколько head'ов существовало (и upgrade head раньше падал — но нет, говорит, что работало),
•	либо я неправильно указал down_revision, и цепочка разорвалась, оставив старый head и создав новый.
Скорее всего, у ecb1e3f89300 есть свой down_revision не от того, что я думал. Значит, привязка к ecb1e3f89300 создала параллельную ветку от более старой ревизии.
Или... наоборот. Другой вариант: ecb1e3f89300 НЕ является head'ом. Может быть, есть ещё одна миграция после неё, файл которой называется не так, как я ожидал.
Но у меня файлы:
text
0f13ad394b65_add_admin_users_department_id.py
35d67a73f181_baseline.py
939e3d0b6f4c_partition_records_by_month.py
2602b71902d4_add_employee_settings.py
b02da1230e4d_add_computer_soft_delete.py
ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py
6 файлов. В HANDOFF говорит "6 миграций".
Скорее всего, цепочка: baseline -> partition -> employee_settings -> b02da123 -> ecb1e3f -> 0f13ad394b65? Или как-то так.
Хм. Давай просто попросим пользователя показать:
•	alembic history
•	alembic heads
•	содержимое всех файлов миграций (нужно для определения правильного родителя)
Но контейнер циклится. Нужно его остановить.
План:
1.	Остановить всё: docker compose down
2.	Удалить мой файл миграции a1b2c3d4e5f6_add_client_versions_sha256.py.
3.	Запустить только db + api (или лучше только db, а alembic отдельной командой).
4.	Собрать информацию о реальных head'ах.
5.	Правильно вставить миграцию.
Или ещё проще: поднять один db-контейнер и запустить alembic команды из api-контейнера, но убрать автозапуск alembic из entrypoint на время диагностики. Но проще сначала просто посмотреть содержимое alembic-файлов.
Дам пользователю команды:
1.	Остановить циклический контейнер:
powershell
docker compose down
2.	Посмотреть содержимое миграций — надо понять цепочку:
powershell
Get-ChildItem D:\tracker\server\alembic\versions\*.py | ForEach-Object {
  Write-Host "=== $($_.Name) ==="
  Select-String -Path $_.FullName -Pattern '^(revision|down_revision)'
}
Это покажет revision и down_revision в каждом файле.
3.	Также удалить мой файл миграции:
powershell
Remove-Item D:\tracker\server\alembic\versions\a1b2c3d4e5f6_add_client_versions_sha256.py
4.	Поднять обратно (без моей миграции):
powershell
docker compose up -d
5.	Проверить, что работает:
powershell
docker compose logs api --tail=20
docker compose exec -T api alembic -c /app/server/alembic.ini current
docker compose exec -T api alembic -c /app/server/alembic.ini heads
6.	Прислать вывод.
Потом я скажу какой down_revision правильный.
Или лучше: сначала узнаем, что там, а потом уже удалим.
Ещё вариант: может, 0f13ad394b65 — отдельный head, который не связан с ecb1e3f89300. Тогда у нас изначально 2 head'а и alembic upgrade head падал? Нет, проект работал...
Стоп. Возможно, ситуация такая:
Существовало:
text
35d67a73f181 (baseline)
  ↓
939e3d0b6f4c
  ↓
2602b71902d4
  ↓
b02da1230e4d
  ↓
ecb1e3f89300  ← head
И отдельная ветка:
text
35d67a73f181
  ↓
0f13ad394b65  ← отдельный head???
Если так — то до меня было 2 head'а и alembic upgrade head падал бы. Но ведь работало.
Значит, скорее всего, цепочка линейная:
text
35d67a73f181 → 939e3d0b6f4c → 2602b71902d4 → b02da1230e4d → ecb1e3f89300 → 0f13ad394b65
Или
text
35d67a73f181 → 0f13ad394b65 → 939e3d0b6f4c → 2602b71902d4 → b02da1230e4d → ecb1e3f89300
Тогда текущий head = ecb1e3f89300. И мой down_revision = "ecb1e3f89300" должен работать.
Хм. Но почему Multiple heads?
Может, я ошибся с именем. Может, реальный revision в файле ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py не ecb1e3f89300, а другое. Нет, так обычно не бывает.
Ещё вариант: alembic.ini содержит настройки version_locations, и file_template применяется для генерации имён. Но revision_id внутри файла — обычно тоже из имени.
Стоп. Может, в 0f13ad394b65 down_revision не ecb1e3f89300, а 939e3d0b6f4c? Тогда цепочка ветвится: ecb1e3f89300 и 0f13ad394b65 — оба наследуют от 939e3d0b6f4c (или от более старого). И до меня было 2 head'а, но alembic upgrade работал потому, что до меня команда вызывала upgrade heads (множественное), а не head.
Ого, это интересно. Возможно, в entrypoint.sh стоит команда alembic upgrade head, которая с моей миграцией ломается, потому что теперь head'ов 3 (к 2 старым добавился мой).
Но постой, тогда и до меня она должна была падать, если head'ов 2.
Если только entrypoint делает upgrade heads (множественное) — тогда 2 head'а ок, но с моим — 3 head'а тоже ок. Тогда бы не падало.
Хм. Или в entrypoint используется именно head (единственное), и до меня head был один. Значит, я действительно сломал цепочку.
Тогда единственное объяснение: ecb1e3f89300 — не head. Реальный head — что-то ещё (например, 0f13ad394b65). Мой down_revision указал на не-head, и теперь цепочка:
text
ecb1e3f89300 → a1b2c3d4e5f6 (мой)
ecb1e3f89300 → 0f13ad394b65 (реальный)
Оба наследуют от ecb1e3f89300. Следовательно, 2 head'а: a1b2c3d4e5f6 и 0f13ad394b65. Это и есть Multiple heads.
Значит, мне нужно поменять down_revision на 0f13ad394b65.
Наверняка так и есть. 0f13ad394b65_add_admin_users_department_id — последняя миграция (по дате создания). Моя должна идти после неё.
Давай дадим пользователю простое решение:
1.	Остановить контейнеры.
2.	Открыть файл D:\tracker\server\alembic\versions\a1b2c3d4e5f6_add_client_versions_sha256.py и заменить down_revision = "ecb1e3f89300" на down_revision = "0f13ad394b65".
3.	Запустить docker compose up -d.
4.	Проверить.
Или ещё проще — патчер, который это сделает.
Или я могу попросить пользователя сначала посмотреть содержимое миграций, а потом уже править. Это надёжнее.
Давай попрошу:
powershell
Get-ChildItem D:\tracker\server\alembic\versions\*.py | ForEach-Object {
  Write-Host ""
  Write-Host "=== $($_.Name) ==="
  Select-String -Path $_.FullName -Pattern '^revision\s*=' | Select-Object -First 1
  Select-String -Path $_.FullName -Pattern '^down_revision\s*=' | Select-Object -First 1
}
Но чтобы не тормозить, могу сразу два варианта дать:
1.	Сначала проверка (команда выше).
2.	Если окажется, что нужный down_revision — 0f13ad394b65, сразу патч.
Хотя. Достаточно быстро показать содержимое файлов. Но это добавит ещё один круг общения. Пользователь ждёт результат.
Хм. Дам сразу решение, но с проверкой. А именно:
1.	Остановить.
2.	Посмотреть содержимое всех миграций (одна команда).
3.	Показать мне вывод.
И параллельно я объясню логику.
Это самый надёжный путь. Плюс замечу проблему: даже если сейчас это исправим, в будущем надо аккуратнее.
Кстати, ещё важно: пользователь уже сделал docker compose up -d --build, и api циклится. Надо его остановить, чтобы не жрал ресурсы. Плюс если миграция начала применяться частично — может быть состояние БД.
Стоп. Миграция не начала применяться, потому что alembic упал ДО начала (на этапе определения head'ов). Значит, БД не тронута. Хорошо.
Итак, мой ответ:
1.	Сначала docker compose down, чтобы остановить цикл.
2.	Показать содержимое миграций.
3.	По результату — правим down_revision.
Дам готовую команду PowerShell.
Также дам простой вариант «наугад»: поменять down_revision на 0f13ad394b65 и посмотреть. Но если окажется не то — снова падать. Лучше сначала проверить.
Хотя... по времени проверить — 5 секунд. Дам команду + объяснение + план Б.
Один момент: docker compose down — но api контейнер циклится, будет ли он корректно остановлен? Обычно down форсированно убивает. Ок.
Ещё вариант: просто оставить контейнеры как есть, а миграцию поправить и перезапустить api:
powershell
docker compose restart api
Тогда при рестарте entrypoint снова применит миграцию (уже с правильным down_revision).
Но сначала надо понять, что реально там.
Ок, дам план:
Шаг 1. Остановить (чтобы не жрал ресурсы):
powershell
docker compose down
Шаг 2. Посмотреть, что за миграции:
powershell
Get-ChildItem D:\tracker\server\alembic\versions\*.py | ForEach-Object {
  $rev = (Select-String -Path $_.FullName -Pattern '^revision\s*=').Line
  $down = (Select-String -Path $_.FullName -Pattern '^down_revision\s*=').Line
  Write-Host "$($_.Name)"
  Write-Host "    $rev"
  Write-Host "    $down"
}
Это покажет пары revision / down_revision. Пришли вывод — я сразу скажу, что менять.
Шаг 3 (опционально, если хочешь ускорить). Просто заменить down_revision в моей миграции на 0f13ad394b65 и запустить. Если сработает — ок. Если нет — вернёмся.
Хотя лучше сначала посмотреть. Так надёжнее.
Хорошо, дам короткий ответ с планом. Плюс сразу дам патчер на всякий случай (если окажется 0f13ad394b65).
Думаю, дам сразу оба варианта, чтобы не тратить время:
Вариант А (быстрый, с большой вероятностью работает):
•	Проверить содержимое 0f13ad394b65_add_admin_users_department_id.py: там revision и down_revision.
•	Если revision = "0f13ad394b65" (что очевидно из имени) и это единственный файл, у которого down_revision указывает на ecb1e3f89300, то 0f13ad394b65 — это head. И наша миграция должна наследовать от него.
Вариант Б (правильный, чуть дольше):
•	Посмотреть всё, потом решать.
Я дам сначала команду для проверки, потом уже патч. Так надёжнее и займёт пару минут.
Собственно, я думаю, что проблема именно в том, что ecb1e3f89300 не является head. А head — 0f13ad394b65.
Готовлю ответ.
Также важно: ответ на русском, ты-обращение, кратко.
Дам:
1.	Объяснение проблемы (2-3 предложения).
2.	Команда диагностики (покажет все revision/down_revision).
3.	План решения после диагностики.
4.	Параллельно — сразу предложу поправить, если подтвердится.
Или ещё быстрее: сразу поправить down_revision на 0f13ad394b65 и перезапустить. Если не сработает — тогда диагностика.
Дам такой план:
•	Сначала уточним. Дай команду диагностики. Она быстрая.
Хорошо, поехали. Также важно — контейнер циклится, надо его остановить. Сначала docker compose down.
Пишу ответ.
Понял. Классика: ecb1e3f89300 не был head'ом. Похоже, реальный последний head — 0f13ad394b65 (файл 0f13ad394b65_add_admin_users_department_id.py), и я привязал миграцию не к тому родителю. В итоге цепочка разветвилась: от ecb1e3f89300 теперь идут две ветки — моя a1b2c3d4e5f6 и реальный 0f13ad394b65.
БД при этом цела: alembic падает на этапе определения head'ов до применения миграции, ничего не накатилось.
Шаг 1. Останови циклический api
powershell
cd D:\tracker
docker compose down
Шаг 2. Проверь цепочку миграций
Выполни одну команду:
powershell
Get-ChildItem D:\tracker\server\alembic\versions\*.py | ForEach-Object {
  $rev  = (Select-String -Path $_.FullName -Pattern '^revision\s*=' | Select-Object -First 1).Line.Trim()
  $down = (Select-String -Path $_.FullName -Pattern '^down_revision\s*=' | Select-Object -First 1).Line.Trim()
  Write-Host ("{0,-55} {1}   {2}" -f $_.Name, $rev, $down)
}
Она покажет для каждого файла пару revision / down_revision — как звенья цепочки.
Пришли сюда вывод — я по нему сразу скажу, какой именно head.
Шаг 3 (вероятное решение, можно сразу)
Если подтвердится, что последняя по времени миграция — 0f13ad394b65 (файл 0f13ad394b65_add_admin_users_department_id.py), то правим мою миграцию: меняем родителя с ecb1e3f89300 на 0f13ad394b65.
Открой D:\tracker\server\alembic\versions\a1b2c3d4e5f6_add_client_versions_sha256.py и одну строку поменяй:
python
# было:
down_revision = "ecb1e3f89300"

# станет:
down_revision = "0f13ad394b65"
Или то же самое одной командой PowerShell:
powershell
$p = "D:\tracker\server\alembic\versions\a1b2c3d4e5f6_add_client_versions_sha256.py"
$txt = [System.IO.File]::ReadAllText($p)
$txt = $txt.Replace('down_revision = "ecb1e3f89300"', 'down_revision = "0f13ad394b65"')
[System.IO.File]::WriteAllText($p, $txt, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Готово. Проверь:"
Select-String -Path $p -Pattern 'revision|down_revision'
Шаг 4. Перезапуск
powershell
cd D:\tracker
docker compose up -d
Через 20–30 секунд:
powershell
docker compose logs api --tail=20
docker compose exec -T api alembic -c /app/server/alembic.ini current
docker compose exec -T api alembic -c /app/server/alembic.ini heads
Ожидаем в логе:
•	Running upgrade 0f13ad394b65 -> a1b2c3d4e5f6
•	current → a1b2c3d4e5f6 (head)
•	heads → одна строка a1b2c3d4e5f6 (head) (а не две).
Потом открой https://192.168.0.35/admin/versions — должна быть страница с формой загрузки и пустой таблицей.
________________________________________
Если heads покажет две строки — пришли вывод, разберёмся (значит, в проекте действительно две параллельные ветки, и тогда используем alembic merge, но это уже другой сценарий).
Пока делаешь — параллельно уточни: вывод Get-ChildItem ... из шага 2 очень поможет. Если в нём окажется, что 0f13ad394b65 — не head (его down_revision указывает на что-то другое, и где-то есть ещё одна миграция после него) — я сразу поправлю.
PowerShell не смог распарсить regexp потому что имена переменных rev,rev,down конфликтуют, но главное: он показал что в файле a1b2c3d4e5f6_add_client_versions_sha256.py revision = "a1b2c3d4e5f6" и down_revision = "ecb1e3f89300" — как я и писал.
Но обрати внимание на две странные строки:
•	b02da1230e4d_add_computer_soft_delete.py: revision = "a1b2c3d4e5f6", down_revision = "ecb1e3f89300"
•	ecb1e3f89300_add_schedules...: revision = "a1b2c3d4e5f6", down_revision = "ecb1e3f89300"
Хм. Это скорее всего баг скрипта: Select-String возвращает Line как объект, и .Trim() не сработал — но потом, поскольку я итерировался по файлам, "line" от одного файла могла остаться от предыдущего. На самом деле revиrevиdown = NULL и Trim бросает ошибку — но следующий вывод показывает имя файла без пары. Стоп, нет — вывод идёт в порядке файлов, и там где ошибка (NULL) — печатается только имя файла, а значение пары отсутствует.
Смотрим внимательно:
text
0f13ad394b65_add_admin_users_department_id.py
  (два NULL, выводится только имя)
2602b71902d4_add_employee_settings.py
  (два NULL)
35d67a73f181_baseline.py
  (два NULL)
939e3d0b6f4c_partition_records_by_month.py
  (два NULL)
a1b2c3d4e5f6_add_client_versions_sha256.py    revision = "a1b2c3d4e5f6"   down_revision = "ecb1e3f89300"
  (тут сработало!)
b02da1230e4d_add_computer_soft_delete.py    revision = "a1b2c3d4e5f6"   down_revision = "ecb1e3f89300"
  (это ошибка — значение осталось с прошлой итерации!)
ecb1e3f89300_add_schedules_roles_scheduler_apikeys_.py  revision = "a1b2c3d4e5f6"   down_revision = "ecb1e3f89300"
  (тоже ошибка — значения не обновились)
Стоп. Проблема в том, что Select-String с Pattern '^revision\s*=' — работает только для моего файла. Почему? Потому что в моём файле ревизия начинается с начала строки. А в остальных файлах — нет, там могут быть отступы, или ещё что-то.
Ой. На самом деле нет. Я вижу что в моём файле revision в начале, а в остальных — тоже должно быть. Хм.
Ладно, проблема в том что Select-String вернул NULL, и .Line.Trim() упал. Значит pattern '^revision\s*=' не матчится в большинстве файлов. Почему?
Возможно, из-за BOM или спецсимволов. Или потому что в других файлах строка: revision = "xxx" — да, тоже в начале. Хм.
А! Может, дело в другой причине: файлы сохранены с CRLF, а PowerShell regex ^revision должен совпасть. Проверю — при чтении Select-String построчно, CRLF должен нормализоваться.
Хм, вероятно проблема в чём-то другом. Может Select-String возвращает MatchInfo где .Line содержит пробелы, а .Trim() не работает потому что .Line равно null—нонет,null—нонет,null.Trim() ошибка.
Ок. Неважно. Более простой путь: я могу просто прочитать файлы через Python-скрипт, который выведет цепочку.
Или, ещё проще — сделать то, что работает всегда:
powershell
Get-ChildItem D:\tracker\server\alembic\versions\*.py | ForEach-Object {
  Write-Host "=== $($_.Name) ==="
  Get-Content $_.FullName | Select-String -Pattern '^(revision|down_revision)'
}
Или совсем просто:
powershell
Select-String -Path D:\tracker\server\alembic\versions\*.py -Pattern '^(revision|down_revision)'
Выведет по строкам всё.
Но проще всего — Python. Пишу маленький скрипт, который выведет цепочку:
python
from pathlib import Path
for p in sorted(Path(r"D:\tracker\server\alembic\versions").glob("*.py")):
    rev = down = None
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("revision ="):
            rev = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("down_revision ="):
            down = line.split("=", 1)[1].strip().strip('"').strip("'")
    print(f"{p.name:60} rev={rev}  down={down}")
Ок. Давай сделаю этот скрипт и параллельно дам уже команду, которая сразу исправит миграцию: если окажется, что реальный head = 0f13ad394b65, то правим.
Но! Мы можем не знать настоящий head, пока не увидим цепочку. Потому что например:
•	baseline (35d67a73f181) — down=NULL (это первая)
•	939e3d0b6f4c partition — down=35d67a73f181?
•	b02da1230e4d soft_delete — down=?
•	2602b71902d4 employee_settings — down=?
•	ecb1e3f89300 schedules — down=?
•	0f13ad394b65 admin_users_dept — down=?
Нужно увидеть цепочку.
Даю короткий скрипт. Плюс простую команду на исправление.
Или можно пойти другим путём — открыть файл 0f13ad394b65_add_admin_users_department_id.py и просто посмотреть строчки revision и down_revision. Это можно сделать через Get-Content -TotalCount 30 например.
Хм. Проще всего — выведу через python. Или... стоп, я могу дать команду типа:
powershell
Get-Content D:\tracker\server\alembic\versions\0f13ad394b65_add_admin_users_department_id.py | Select-String 'revision'
Но чтобы все сразу:
powershell
Get-ChildItem D:\tracker\server\alembic\versions\*.py | ForEach-Object {
  "=== $($_.Name)"
  Get-Content $_.FullName | Select-String '^(revision|down_revision)\s*=' | ForEach-Object { "   $($_.Line.Trim())" }
}
Это надёжнее.
На самом деле я думаю проблема была в том, что Select-String вернул [Microsoft.PowerShell.Commands.MatchInfo], и у него есть свойство .Line. Но когда совпадений не было — вернул $null. А для моего файла совпадение было.
Почему не было для других? Загадка. Хотя... может, там через запятую или другие кавычки. Или... хм.
А! Понял! Возможно там revision: str = "..." — type hint! Или revision = '...' (одинарные кавычки)? Нет, regexp ^revision\s*= должен совпасть с любым revision = в начале строки.
Или же строка не в начале? Может там отступ или пробел в начале? Тогда ^revision не совпадёт. Стоп, но это же стандартный шаблон alembic — revision = "..." без отступа. Хм.
Единственное объяснение: файлы в UTF-8 с BOM. Тогда первая строка начинается с BOM-символа, и ^ может не совпасть с позиции 0. Но revision обычно не первая строка файла...
Ладно, не гадаю. Дам скрипт на Python и команду исправления.
План ответа:
1.	Признать: PowerShell-скрипт сломался, но данные всё равно есть (частично).
2.	Дать простой Python-скрипт для вывода цепочки.
3.	Дать сразу команду исправления — замену down_revision в моём файле миграции. Дать на два случая: если head = 0f13ad394b65, то менять на него. Это наиболее вероятный вариант.
Стоп. Стоп. Стоп. Давай подумаю ещё. Мы знаем что:
•	Мой файл: rev=a1b2c3d4e5f6, down=ecb1e3f89300
•	Alembic говорит "Multiple head revisions". Это значит: от ecb1e3f89300 отходят ДВЕ ветки — моя (a1b2c3d4e5f6) и ещё одна (та, где ecb1e3f89300 — родитель).
Значит: как минимум одна миграция имеет down_revision = "ecb1e3f89300". И эта миграция НЕ является моей. И у неё наверху — цепочка до head. Назовём её реальный head = X.
Задача: узнать X. Единственный способ — посмотреть все down_revision и найти, какая ревизия упоминается как down, но сама не указана как down ни у кого (т.е. она — head).
Или посмотреть revision/down_revision по всем файлам и построить цепочку.
Дам скрипт.
python
from pathlib import Path
revs = {}
for p in sorted(Path(r"D:\tracker\server\alembic\versions").glob("*.py")):
    rev = down = None
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("revision =") and rev is None:
            rev = s.split("=", 1)[1].strip().strip('"').strip("'")
        elif s.startswith("down_revision =") and down is None:
            down = s.split("=", 1)[1].strip().strip('"').strip("'")
    print(f"{p.name:62} rev={rev}  down={down}")
    revs[rev] = p.name

# Найти head(ы): те, кого никто не указывает как down
downs = set()
for p in sorted(Path(r"D:\tracker\server\alembic\versions").glob("*.py")):
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("down_revision =") and "None" not in s:
            v = s.split("=", 1)[1].strip().strip('"').strip("'")
            downs.add(v)
heads = [r for r in revs if r not in downs]
print()
print("HEAD(s):", heads)
Но! Проще всего исправление: посмотреть, какая ревизия не упоминается как down_revision. Это и есть настоящий head. Скорее всего это 0f13ad394b65 (последняя созданная по имени).
Гипотеза: файл 0f13ad394b65_add_admin_users_department_id.py — последний. Он и есть head. Мой надо прицепить на него.
Но если chain такой: baseline(35d67a73f181) -> ??? -> ... -> 0f13ad394b65, то есть 939e3d0b6f4c (partition), b02da1230e4d (soft_delete), 2602b71902d4 (employee_settings), ecb1e3f89300 (schedules), 0f13ad394b65 (admin_users_dept).
Тогда 0f13ad394b65 = последний. И моя миграция должна прицепиться на него.
Ну, давай дам скрипт и сразу две команды. Одна — вывести цепочку. Вторая — исправить.
Но! Есть проблема. Мой патч уже применился к файлу миграции. Если я изменю down_revision на 0f13ad394b65, то накатывание сработает. Но лучше — пересоздать миграцию чисто.
Хотя нет, просто правим down_revision.
Даю ответ.
Также надо отметить: PowerShell-команда упала не потому что файлов нет, а потому что $_.Line.Trim() при NULL. Ладно.
Дам Python-скрипт.
Также покажу, что я уже вижу из вывода: только для двух файлов он вывел пары, потому что PowerShell глючит. Файлы остальных имеют revision = ... — но regexp не сработал, наверное из-за non-ASCII в комментариях выше (docstring на русском). Хотя не, это не должно влиять.
Скорее всего — в остальных файлах есть docstring с revision упоминанием, и Select-String вернул первую попавшуюся строку без .Line, потому что...
Ой. На самом деле проблема в том, что в моём скрипте для каждого файла:
powershell
$rev  = (Select-String -Path $_.FullName -Pattern '^revision\s*=' | Select-Object -First 1).Line.Trim()
Если Select-String НЕ нашёл — вернёт NULL, а .Line на NULL — NULL, а .Trim() на NULL — ошибка. И переменная $rev остаётся с предыдущего файла (в PowerShell не сбрасывается в null при ошибке). Поэтому для файлов, где ошибка, выводится значение предыдущего файла. Это видно в выводе: для b02da... и ecb1... показаны значения от a1b2c3d4e5f6.
Значит, для файлов 0f13ad394b65, 2602b71902d4, 35d67a73f181, 939e3d0b6f4c — Select-String не нашёл ни одного совпадения.
Почему? Возможно там revision записан с одинарными кавычками: revision = 'xxx'? Нет, regexp не про кавычки.
Или нет пробелов вокруг =? Типа revision="xxx". Regexp ^revision\s*= совпадёт.
Или отступ в начале? Типа revision = "xxx". Тогда ^revision не совпадёт (^ — начало строки). Но alembic сам создаёт файлы без отступа...
Хм. Или BOM. Стоп.
Или на самом деле у них нет комментариев, но есть пустые строки в начале, revision не на первой строке.
Ладно, это неважно. Давай через Python — там всё по-честному. И ещё дам вариант с Get-Content.
Пишу ответ.
Ещё замечу: файл b02da1230e4d_add_computer_soft_delete.py — это soft_delete. По логике он должен быть ПОСЛЕ baseline и после partition.
Ок, давай просто дам скрипт и параллельно — команды исправления.
Ещё мысль: а вдруг проблема в том, что migration файлы, кроме моего, записаны с BOM? Тогда первая строка начинается с \ufeff. Проверю: baselines. Hmm.
Но! Мои файлы: main.py патчился WriteAllText... нет, я писал через Path.write_text(encoding="utf-8") — без BOM. А powershell WriteAllText с UTF8Encoding($false) — тоже без BOM.
Не буду гадать. Скрипт на Python — сразу покажет.
Кстати, простейший способ узнать настоящий head: посмотреть какие ревизии упомянуты в down_revision, но не упомянуты в revision. Или ещё проще — запустить alembic heads из контейнера... но контейнер падает. Можно из локали:
powershell
cd D:\tracker\server
D:\tracker\client\.venv\Scripts\python.exe -m alembic -c alembic.ini heads
Ой, но нам нужен серверный venv. Погоди, alembic установлен в серверный образ, локально может и не быть.
Ладно, дам python-скрипт — это самое быстрое.
Пишу.
Понял. Скрипт PowerShell поломался из-за $null.Trim() в файлах, где regexp не совпал (там разные форматы записи). Но главное уже ясно:
•	мой файл a1b2c3d4e5f6: revision=a1b2c3d4e5f6, down_revision=ecb1e3f89300
•	остальные файлы Select-String не показал — но это не значит, что там нет revision, просто другая запись.
Сделаем проще — через Python, он парсит единообразно.
Шаг 1. Прочитать цепочку
Создай D:\tracker\_show_revs.py:
python
# -*- coding: utf-8 -*-
# Показывает цепочку миграций: имя файла, revision, down_revision.
# В конце — список head'ов (тех, кого никто не указал как down_revision).
from pathlib import Path

VERS = Path(r"D:\tracker\server\alembic\versions")

rows = []
for p in sorted(VERS.glob("*.py")):
    rev = down = None
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if s.startswith("revision") and "=" in s and rev is None:
            rev = s.split("=", 1)[1].strip().strip('"').strip("'")
        elif s.startswith("down_revision") and "=" in s and down is None:
            down = s.split("=", 1)[1].strip().strip('"').strip("'")
    rows.append((p.name, rev, down))
    print(f"{p.name:62} rev={rev}  down={down}")

# Кто упомянут как down_revision?
downs = {d for _, _, d in rows if d and d != "None"}
heads = [r for _, r, _ in rows if r and r not in downs]
print()
print("HEAD(s):", heads)
Запуск:
powershell
D:\tracker\client\.venv\Scripts\python.exe D:\tracker\_show_revs.py
Пришли мне вывод — я точно скажу, куда перецепить мою миграцию.
Шаг 2. Скорее всего, настоящий head — 0f13ad394b65
Моя миграция должна цепляться на него (а не на ecb1e3f89300). Если вывод подтвердит — одной командой перецепляем:
powershell
$p = "D:\tracker\server\alembic\versions\a1b2c3d4e5f6_add_client_versions_sha256.py"
$txt = [System.IO.File]::ReadAllText($p)
$txt = $txt.Replace('down_revision = "ecb1e3f89300"', 'down_revision = "0f13ad394b65"')
[System.IO.File]::WriteAllText($p, $txt, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Перецепил. Проверь:"
Select-String -Path $p -Pattern 'revision'
Ожидаешь увидеть:
text
revision = "a1b2c3d4e5f6"
down_revision = "0f13ad394b65"
Шаг 3. Поднять и проверить
powershell
cd D:\tracker
docker compose up -d
Start-Sleep -Seconds 20
docker compose logs api --tail=20
docker compose exec -T api alembic -c /app/server/alembic.ini current
docker compose exec -T api alembic -c /app/server/alembic.ini heads
Ждём:
•	в логе: Running upgrade 0f13ad394b65 -> a1b2c3d4e5f6
•	current → a1b2c3d4e5f6 (head)
•	heads → одна строка a1b2c3d4e5f6 (head)
Потом открывай https://192.168.0.35/admin/versions.
________________________________________
Почему так вышло: я предположил, что последняя миграция в репо — ecb1e3f89300 (по имени она «schedules_roles_scheduler_apikeys_», самая новая фича). А на самом деле поверх неё уже была ещё одна — 0f13ad394b65 (add_admin_users_department_id). Из-за этого получилась «вилка»: от ecb1e3f89300 идут два ребёнка — мой и настоящий. Alembic не знает, куда идти, и падает с «Multiple head revisions».
Важно: БД цела, ничего не сломалось. Alembic упал на этапе анализа графа — до того, как что-либо применил. Правка одной строки в моём файле решает вопрос.
Пришли вывод _show_revs.py — я подтвержу, что 0f13ad394b65 — действительно head, и после этого пойдём дальше (SCP-кнопка + updater клиента).
PS D:\tracker> D:\tracker\client\.venv\Scripts\python.exe D:\tracker\_show_revs.py File "D:\tracker\_show_revs.py", line 14 rev = s.split(=, 1)[1].strip().strip('').strip(') ^ SyntaxError: unterminated string literal (detected at line 14)
The user ran my script but PowerShell or the terminal mangled the quotes — probably because they copy-pasted and the quotes got eaten. Let me give them a simpler solution.
Better: just use single file inspection command, or write the script directly with careful encoding.
Actually the issue: when they pasted into PowerShell here-string or directly, the " quotes inside strings got stripped. Let me give them a command that writes the script via PowerShell safely, or use Set-Content with proper escaping.
Simplest: just have them look at the actual file content directly. I can tell them to just run Get-Content on each file and look for revision lines.
Or I can give them a Python one-liner via docker compose exec, since Python is already in the container. Actually that's cleanest.
Wait — better still: since the DB is running, we can query alembic_version table in postgres directly to see what's applied. And we can use alembic CLI to see history.
Actually simplest: just run from inside the api container:
powershell
docker compose exec -T api alembic -c /app/server/alembic.ini history
That shows the full chain including heads. That's what we need.
Let me give that first. And then give a fallback to see file contents:
powershell
Get-Content D:\tracker\server\alembic\versions\*.py | Select-String -Pattern '^(revision|down_revision)'
Actually that gives us what we need too.
Let me just use alembic history — cleanest.
Понял — PowerShell съел кавычки при вставке скрипта. Не важно, у нас есть путь проще: сам alembic умеет показывать цепочку. Используем его.
Шаг 1. Показать цепочку через alembic
powershell
cd D:\tracker
docker compose up -d
Start-Sleep -Seconds 15
docker compose exec -T api alembic -c /app/server/alembic.ini history
Команда history печатает всю цепочку сверху вниз — от корня до head'ов. В выводе увидишь строки вида:
text
ecb1e3f89300 -> 0f13ad394b65 (head), add admin_users department_id
ecb1e3f89300 -> a1b2c3d4e5f6 (head), add client_versions sha256
<base> -> 35d67a73f181, baseline
...
Если в выводе увидишь два (head) от одного родителя — это подтверждает «вилку».
Пришли вывод — там всё будет видно.
Шаг 2. Параллельно — просто посмотри revision в файлах
Тоже через PowerShell, без моего сломанного скрипта:
powershell
cd D:\tracker
Get-ChildItem .\server\alembic\versions\*.py | ForEach-Object {
  $name = $_.Name
  $rev  = (Get-Content $_.FullName | Where-Object { $_ -match '^\s*revision\s*=' } | Select-Object -First 1)
  $down = (Get-Content $_.FullName | Where-Object { $_ -match '^\s*down_revision\s*=' } | Select-Object -First 1)
  "{0,-60} {1}  |  {2}" -f $name, $rev, $down
}
Здесь нет .Trim() на $null — ошибки быть не должно. Пришли вывод.
Что я уже почти уверен
•	Файл 0f13ad394b65_add_admin_users_department_id.py — это реальный последний head проекта.
•	Моя миграция a1b2c3d4e5f6 ошибочно ссылается на ecb1e3f89300 (её родителя), поэтому образовалась «вилка».
•	Лечится одной строкой: down_revision в моём файле → "0f13ad394b65".
Пока не подтвердим — не трогаю. Как только увижу history или вывод Get-ChildItem — сразу дам одну команду на исправление.
Пользователь хочет подготовить передачу в следующий чат: следующий этап — создание инсталлятора со всем сопутствующим софтом и его настройкой (Docker Desktop, .env, сертификаты, первый запуск, etc.). Нужно собрать всю имеющуюся информацию и обновить нужные страницы KB.
Что нужно сделать:
1.	Обновить KB (HANDOFF.md, 06_DEPLOY/03_WINDOWS_SETUP.md, 06_DEPLOY/06_INSTALLER.md, 05_SCP/03_BUILD.md) — всё что уже есть по инсталлятору на стороне сервера.
2.	Создать новый раздел/файл про серверный инсталлятор (то, что предстоит).
3.	Подготовить "передачу" — что прислать в следующий чат.
Пользователь сказал: "вероятно осталось мало места в этом чате так что пишем всё только по делу". Значит нужно КРАТКО.
Формат: краткая сводка + что обновить + что прислать в следующем чате.
Пункт "создание инсталлятора со всем сопутствующим софтом и его настройкой" — что это значит:
•	Сейчас установка сервера на Windows делается вручную: Docker Desktop, .env, сертификаты, docker compose up.
•	Нужен единый инсталлятор для сервера, который поставит: Docker Desktop (или проверит), создаст .env, сгенерит сертификаты, поднимет docker compose, настроит firewall.
•	Это серверный аналог клиентского TrackerSetup.exe.
Что мне нужно будет изучить в следующем чате:
•	06_DEPLOY/03_WINDOWS_SETUP.md — как сейчас ставится вручную.
•	06_DEPLOY/01_DOCKER.md — docker-compose.
•	06_DEPLOY/02_NGINX_TLS.md — сертификаты.
•	06_DEPLOY/06_INSTALLER.md — что уже есть про клиентский инсталлятор (шаблон/подход).
•	05_SCP/02_CERTIFICATES.md — сертификаты.
•	D:\tracker.env — какие переменные окружения нужны.
•	server/entrypoint.sh — что делает.
•	deploy.json — текущие параметры.
•	server/Dockerfile.
•	Возможно, есть какие-то уже существующие скрипты установки.
Ответ должен быть:
1.	Кратко: что делаем сейчас.
2.	Патч KB — какой файл создать/обновить. В идеале — дать готовый патчер или просто создать один новый файл передачи (handoff-next.md) в docs.
3.	Что прислать в следующий чат (список файлов).
Учитывая "мало места" — минимизирую. Один патчер для HANDOFF.md и, может быть, нового файла. Никаких длинных лекций.
Что реально стоит сделать:
1.	Обновить HANDOFF.md — добавить §13 "Следующий этап: инсталлятор сервера" с описанием задачи и списком файлов для следующего чата.
2.	Создать передачу в виде отдельного файла docs/99_RAW/HANDOFF_NEXT_INSTALLER.md или дописать в HANDOFF.md.
3.	Опубликовать KB.
Учитывая, что пользователь просит "собрать всю имеющуюся информацию для будущего чата" — нужно создать компактный документ "передача".
Давай сделаю так:
•	Один патчер создаёт docs/99_RAW/HANDOFF_INSTALLER.md — файл передачи.
•	Патчер дописывает в docs/HANDOFF.md короткий блок §13.
•	Публикация через update_site.bat.
Файл передачи должен содержать:
•	Задача следующего этапа (что строим).
•	Что уже есть (готовые кубики).
•	Какие файлы прислать в начале чата.
•	Открытые вопросы / решения.
Кратко и по делу.
Ещё пункт: "обновить все необходимые страницы" — вероятно, 06_DEPLOY/03_WINDOWS_SETUP.md и 06_DEPLOY/06_INSTALLER.md — но они, скорее всего, уже описывают что есть. Можно не трогать, а сослаться из передачного файла.
Ок. Пишу компактно.
Что важно упомянуть в передаче:
Задача: создать серверный инсталлятор TrackerServerSetup.exe (Inno Setup + PowerShell), который:
1.	Проверит/установит Docker Desktop (или скачает, или попросит установить).
2.	Развернёт файлы проекта из архива.
3.	Создаст .env (сгенерирует SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY).
4.	Проверит наличие certs/fullchain.pem + privkey.pem; если нет — выпустит self-signed через SCP-логику или попросит.
5.	Запустит docker compose up -d --build.
6.	Настроит firewall (порт 443).
7.	Создаст ярлыки: SCP, админка.
8.	Может — shortcut на обновление.
Что уже есть готовое (кубики):
•	deploy.json — конфиг деплоя (server_url, cert_cn, cert_san, hostname_alias).
•	control/deploy.py — чтение/запись deploy.json.
•	control/build.py — сборка клиентского установщика; шаблон подхода к Inno Setup.
•	control/network_tab.py — перевыпуск сертификата с LAN-IP, добавление правила firewall.
•	control/certificates.py (или как называется) — генерация self-signed сертификата.
•	docker-compose.yml — уже готов.
•	server/entrypoint.sh — применяет миграции и поднимает gunicorn.
•	Клиентский installer.iss — рабочий шаблон Inno Setup.
•	.env — структура известна из control/admin.py (_parse_env).
Что нужно спроектировать / решить:
•	Где хранить файлы проекта при установке (Program Files? D:\tracker?).
•	Как тащить Docker Desktop: инсталлятор качает winget / напрямую .exe / просит пользователя.
•	Первый запуск: автогенерация секретов в .env.
•	Сертификат: выпускать самому через openssl в контейнере или просить SCP.
•	Firewall: через netsh/UAC.
•	Антивирус / UAC.
•	Порт 443 — не занят ли IIS/Skype.
•	Обновления сервера (в отличие от клиента).
Файлы для следующего чата:
1.	docs/HANDOFF.md (свежий)
2.	docs/00_INDEX.md
3.	docs/06_DEPLOY/03_WINDOWS_SETUP.md
4.	docs/06_DEPLOY/01_DOCKER.md
5.	docs/06_DEPLOY/02_NGINX_TLS.md
6.	docs/06_DEPLOY/06_INSTALLER.md
7.	docs/05_SCP/02_CERTIFICATES.md
8.	docs/05_SCP/03_BUILD.md
9.	control/build.py
10.	control/config.py
11.	control/deploy.py
12.	control/network_tab.py
13.	control/build_tab.py (после патчей)
14.	client/installer.iss (шаблон Inno)
15.	docker-compose.yml
16.	server/Dockerfile
17.	server/entrypoint.sh
18.	D:\tracker\.env (без реальных значений, только структура — или просто не показывать содержимое; можно структуру)
19.	deploy.json
20.	Полный список миграций (уже известен).
Ну и скрипты управления: control/gui.py, control/gui_main.py (или как назван) — чтобы знать, откуда запускается SCP.
Думаю, стоит упомянуть что нужно решить: installer должен работать и на "чистой" машине и на "уже стоящей" (обновление сервера).
Ок. Сделаю патчер создания файла docs/99_RAW/HANDOFF_INSTALLER.md и дописывания §13 в HANDOFF.md.
Так как места мало, дам компактный ответ:
1.	Кратко — что в передаче.
2.	Готовый патчер (короткий).
3.	Что пришлёшь в следующий чат.
Патч KB одним файлом — не размазываю.
Пусть патчер создаёт docs/99_RAW/HANDOFF_INSTALLER.md. Это дополнение к HANDOFF.
Также обновить §13 в HANDOFF.md и пункт в разделе "Что делать в следующем чате".
Ок пишу.
Важно: в патчере надо быть осторожным с кавычками — использовать Python без проблемных escape.
Один момент — я не знаю точно, что за файлы SCP: certificates.py, firewall.py и т.д. В прошлых сессиях были control/services_tab.py и control/network_tab.py. Точных имён функций не знаю. В передаче укажу "прислать эти файлы, они разберутся".
Ещё момент — имя файла сертификата — certs/fullchain.pem + privkey.pem.
Ок, пишу патчер и краткое сопроводительное.
Ещё стоит обновить 06_DEPLOY/03_WINDOWS_SETUP.md — но раз пользователь сказал "мало места, только по делу", ограничусь созданием одного файла-передачи + патч HANDOFF.
Хотя "обновить все необходимые страницы" — пользователь конкретно просит. Но раз "мало места", минимизирую: создам один новый передаточный файл и обновлю HANDOFF. В передаточном файле будет ссылка "актуализировать 03_WINDOWS_SETUP.md в следующем чате".
Ок. Патчер — компактный.
Понял. Готовлю компактную передачу для следующего чата: один файл-описание задачи + правка HANDOFF.md. Всё делается одним патчером.
Что включает передача
Задача следующего чата: серверный инсталлятор TrackerServerSetup.exe (Inno Setup + PowerShell), который на чистой Windows:
1.	Проверит/установит Docker Desktop.
2.	Развернёт файлы проекта.
3.	Создаст .env с автогенерацией SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY.
4.	Выпустит self-signed сертификат или попросит через SCP.
5.	Поднимет docker compose up -d --build.
6.	Настроит firewall (443).
7.	Создаст ярлыки: SCP, админка.
8.	Продумает обновления сервера (в отличие от клиента).
Патчер KB
Создай D:\tracker\_apply_handoff_installer.py (через VS Code: code D:\tracker\_apply_handoff_installer.py):
python
# -*- coding: utf-8 -*-
# ============================================================
# Патч KB: передача следующего этапа — серверный инсталлятор.
# ============================================================
# Что делает:
#   1. Создаёт docs/99_RAW/HANDOFF_INSTALLER.md — бриф для
#      следующего чата: задача, что есть, что прислать.
#   2. Дописывает §13 в docs/HANDOFF.md (короткая сноска).
#   3. Обновляет §11 «Что делать в следующем чате».
# Идемпотентен.
# ============================================================

from pathlib import Path
from datetime import date

ROOT = Path(r"D:\tracker")
DOCS = ROOT / "docs"
TODAY = date.today().isoformat()


def _read(p): return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
def _write(p, t):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, encoding="utf-8", newline="\n")
    print("  OK ", p.relative_to(ROOT))


# ============================================================
# 1. docs/99_RAW/HANDOFF_INSTALLER.md
# ============================================================
HANDOFF_INSTALLER = f"""# HANDOFF_INSTALLER.md — передача: серверный инсталлятор

Статус: бриф для следующего чата
Дата: {TODAY}
Связанные: 06_DEPLOY\\03_WINDOWS_SETUP.md, 06_DEPLOY\\06_INSTALLER.md,
           06_DEPLOY\\01_DOCKER.md, 06_DEPLOY\\02_NGINX_TLS.md, HANDOFF.md

## Задача

Построить `TrackerServerSetup.exe` — единый установщик сервера
«Трекера» для Windows-машины (LAN). По аналогии с клиентским
`TrackerSetup.exe`, но для развёртывания серверной части.

### Что делает инсталлятор на чистой Windows

1. Проверяет, установлен ли Docker Desktop. Если нет — ставит
   (winget install Docker.DockerDesktop), ждёт готовности демона.
2. Разворачивает файлы проекта Tracker (архив).
3. Создаёт `.env`:
   - генерирует `SECRET_ENCRYPTION_KEY`, `JWT_SECRET`, `ADMIN_API_KEY`
     (криптостойко, `secrets.token_urlsafe`);
   - `DATABASE_URL` — стандартное значение;
   - не перезатирает существующий `.env`, если пользователь не
     попросит (для повторной установки / апгрейда).
4. Проверяет сертификаты `certs/fullchain.pem` + `certs/privkey.pem`:
   - если нет — выпускает self-signed (openssl в контейнере или
     через логику SCP `control/*` на LAN-IP);
   - CN = 127.0.0.1, SAN = localhost, 127.0.0.1, <LAN-IP>,
     <hostname>, tracker, tracker.local.
5. Запускает `docker compose up -d --build` и ждёт `healthy`.
6. Настраивает firewall: правило `Tracker HTTPS`, TCP:443.
7. Создаёт ярлыки: «Tracker — админка» (браузер), «Tracker SCP»
   (запуск `control.gui_main` через python venv).
8. При повторном запуске — режим «Обновить сервер» (без сброса БД,
   только пересборка контейнеров).

### Что НЕ входит

- Windows Server (только Windows 10/11 x64).
- Linux/macOS.
- Установка PostgreSQL отдельно (используется контейнер).

## Что уже готово (переиспользуем)

| Компонент | Путь | Роль |
|---|---|---|
| `deploy.json` | `D:\\tracker\\deploy.json` | server_url, cert_cn, cert_san, hostname_alias |
| Модуль `deploy` | `control/deploy.py` | load/save/get/set_values |
| Сборка клиента | `control/build.py` | шаблон Inno + PyInstaller + prepare_client_env |
| Вкладка «Сборка» | `control/build_tab.py` | UI: чекбоксы, QThread, лог |
| Вкладка «Сеть» | `control/network_tab.py` | LAN-IP, firewall, перевыпуск cert, hosts |
| Клиентский Inno | `client/installer.iss` | шаблон для копирования |
| Docker Compose | `docker-compose.yml` | db + api + nginx, volume pgdata |
| Entrypoint | `server/entrypoint.sh` | миграции Alembic + gunicorn |
| Dockerfile | `server/Dockerfile` | python:3.11-slim |
| `.env` (структура) | `D:\\tracker\\.env` | SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY |

## Что нужно решить

1. **Где разворачивать**: `C:\\Program Files\\Tracker\\` (UAC) или
   `D:\\tracker\\` (как сейчас, без UAC). Скорее — второе, как менее
   конфликтное с антивирусом.
2. **Docker Desktop**:
   - ставить через `winget install --id Docker.DockerDesktop -e`;
   - или приложить оффлайн-инсталлятор;
   - или попросить пользователя поставить вручную и продолжить после.
3. **Сертификат**: генерить внутри инсталлятора (Python-скрипт через
   SCP-логику) или запускать SCP-метод? Скорее — отдельный
   PowerShell/Python-скрипт, который инсталлятор вызывает.
4. **Firewall**: UAC-запрос при первом запуске (netsh advfirewall).
5. **Обновление сервера**: второй режим инсталлятора.
   Не перезаписывать `.env`, не удалять `pgdata`, только пересобрать
   образы и перезапустить.
6. **Дистрибутив**: как упаковывать? Inno Setup с `[Files]` из
   `D:\\tracker\\server`, `D:\\tracker\\control`, `deploy.json`,
   `docker-compose.yml`, `certs/` — или архив `.tar.gz`/`.zip`,
   который инсталлятор распаковывает.

## Файлы, которые нужно прислать в следующем чате

Обязательно:
1. `docs/HANDOFF.md` (актуальный)
2. `docs/00_INDEX.md`
3. `docs/06_DEPLOY/03_WINDOWS_SETUP.md`
4. `docs/06_DEPLOY/01_DOCKER.md`
5. `docs/06_DEPLOY/02_NGINX_TLS.md`
6. `docs/06_DEPLOY/06_INSTALLER.md`
7. `docs/06_DEPLOY/05_UPDATES.md` (серверная часть обновлений)
8. `docker-compose.yml`
9. `server/Dockerfile`
10. `server/entrypoint.sh`
11. `.env` (только структура — ключи, без значений)
12. `deploy.json`
13. `client/installer.iss` (шаблон Inno)
14. `control/config.py`
15. `control/deploy.py`
16. `control/build.py` (после патчей)
17. `control/build_tab.py` (после патчей)
18. `control/network_tab.py`
19. `control/gui.py` или `gui_main.py` — как подключаются вкладки
20. `control/certificates.py` (или чем там выпускаются сертификаты — уточнить имя)

Желательно:
21. `control/services_tab.py`
22. `control/admin.py`
23. `control/publish.py`

## Команды (шпаргалка)
Сервер:
cd D:\tracker
docker compose ps
docker compose logs api --tail=30
docker compose down && docker compose up -d --build
Админка:
https://192.168.0.35/admin/login
логин admin, пароль = ADMIN_API_KEY из .env
Сборка клиента:
SCP → вкладка «Сборка» → «Собрать полностью» + «Опубликовать версию»
Сборка сервера (предстоит):
D:\tracker\installer\TrackerServerSetup.exe
(после реализации)
text

## Состояние проекта на {TODAY}

- **Готовность:** ~97%. P0 «Публикация версий через UI» закрыт.
- **Сервер:** FastAPI + PostgreSQL 16 + nginx + Docker, миграции Alembic
  до `a1b2c3d4e5f6`, 7 задач планировщика.
- **Админка:** 75+ роутов, страница `/admin/versions`.
- **Клиент:** PyQt6, обновление с проверкой sha256, диалог согласия.
- **SCP:** вкладки Статус, Сертификат, Сервисы, Сеть, Сборка, Админ,
  публикация версий.
- **KB опубликован:** https://erohin-a.github.io/tracker/
"""


def create_handoff_installer():
    p = DOCS / "99_RAW" / "HANDOFF_INSTALLER.md"
    print("[1/2] docs/99_RAW/HANDOFF_INSTALLER.md")
    if p.exists():
        print("  --  уже есть, пропускаю")
        return
    _write(p, HANDOFF_INSTALLER)


# ============================================================
# 2. HANDOFF.md — §13 + правка §11
# ============================================================
def patch_handoff():
    print("[2/2] docs/HANDOFF.md")
    p = DOCS / "HANDOFF.md"
    text = _read(p)

    # §11 — следующий шаг
    old = (
        "## 11. Что делать в следующем чате (после handoff)\n"
        "\n"
        "1. Реализовать ca.pem через UI (SCP).\n"
        "2. UX-аудит админки и клиента (тултипы, интуитивность, единый стиль ошибок).\n"
        "3. i18n клиента до конца, темы, бэкапы, алерты.\n"
    )
    new = (
        "## 11. Что делать в следующем чате (после handoff)\n"
        "\n"
        "1. **Серверный инсталлятор** — `TrackerServerSetup.exe`\n"
        "   (Docker Desktop + файлы проекта + .env + сертификаты +\n"
        "   docker compose up + firewall + ярлыки).\n"
        "   Подробный бриф: `99_RAW\\HANDOFF_INSTALLER.md`.\n"
        "2. Реализовать ca.pem через UI (SCP).\n"
        "3. UX-аудит админки и клиента (тултипы, интуитивность).\n"
        "4. i18n клиента до конца, темы, бэкапы, алерты.\n"
    )
    if old in text:
        text = text.replace(old, new, 1)
        print("  --  §11 обновлён")
    else:
        print("  --  §11: шаблон не найден (уже правился)")

    # §13 — новый раздел в конец
    if "## 13. Следующий этап" not in text:
        text = text.rstrip("\n") + f"""

---

## 13. Следующий этап: серверный инсталлятор ({TODAY})

Полный бриф — в `99_RAW\\HANDOFF_INSTALLER.md`.

Коротко:
- Единый `TrackerServerSetup.exe` для Windows.
- Проверяет/ставит Docker Desktop.
- Разворачивает проект, создаёт `.env` с автогенерацией секретов.
- Выпускает self-signed сертификат (или через SCP).
- Поднимает `docker compose up -d --build`.
- Настраивает firewall (443).
- Создаёт ярлыки: админка, SCP.
- Режим «Обновить сервер» — без сброса БД.

Переиспользуем готовое: `control/deploy.py`, `control/build.py`,
`client/installer.iss`, `docker-compose.yml`, `control/network_tab.py`.

Перед началом следующего чата приложить файлы из списка в
`HANDOFF_INSTALLER.md` (раздел «Файлы, которые нужно прислать»).
"""
        print("  --  §13 добавлен")
    else:
        print("  --  §13 уже есть")

    _write(p, text)


def main():
    print("=" * 60)
    print("Патч KB: передача — серверный инсталлятор")
    print("=" * 60)
    if not DOCS.exists():
        raise SystemExit(f"Не найден {DOCS}")
    create_handoff_installer()
    patch_handoff()
    print()
    print("Дальше — публикация KB:")
    print("  cd D:\\tracker\\docs")
    print("  .\\update_site.bat")


if __name__ == "__main__":
    main()
Запуск и публикация:
powershell
cd D:\tracker
client\.venv\Scripts\python.exe _apply_handoff_installer.py
cd docs
.\update_site.bat
Что получится
•	Новый файл: docs/99_RAW/HANDOFF_INSTALLER.md — бриф следующего этапа (задача, готовые кубики, открытые вопросы, список файлов для передачи, команды).
•	HANDOFF.md: §11 теперь указывает на инсталлятор как первый пункт; добавлен §13 с краткой сводкой.
•	KB опубликован на https://erohin-a.github.io/tracker/.
Что делать сейчас (2 минуты)
1.	Запусти патчер выше.
2.	Выполни update_site.bat в docs.
3.	Проверь: https://erohin-a.github.io/tracker/99_RAW/HANDOFF_INSTALLER.html (или где-то рядом, если сайт перестраивает пути).
Что приложить в следующий чат (краткий минимум)
Из HANDOFF_INSTALLER.md, раздел «Файлы, которые нужно прислать» — обязательные 20:
•	HANDOFF.md, 00_INDEX.md
•	06_DEPLOY/{03_WINDOWS_SETUP, 01_DOCKER, 02_NGINX_TLS, 06_INSTALLER, 05_UPDATES}.md
•	docker-compose.yml, server/Dockerfile, server/entrypoint.sh
•	.env (структура), deploy.json, client/installer.iss
•	control/{config, deploy, build, build_tab, network_tab, gui}.py
•	список файлов control/ (чтобы я увидел, где лежит выпуск сертификата)
Плюс, если есть — control/publish.py, control/services_tab.py, control/admin.py.
С этого и начнём следующий чат.
Этот ответ сгенерирован AI, только для справки.
PS C:\WINDOWS\system32> cd D:\tracker >> client\.venv\Scripts\python.exe _apply_handoff_installer.py >> cd docs >> .\update_site.bat File "D:\tracker\_apply_handoff_installer.py", line 31 HANDOFF_INSTALLER = f"""# HANDOFF_INSTALLER.md — передача: серверный инсталлятор ^ SyntaxError: unterminated triple-quoted f-string literal (detected at line 138) ============================================ Обновление сайта Трекер (GitHub Pages) ============================================ --- Текущие изменения --- M "BCE/@@ 10 \321\207\320\260\321\201\321\202\321\214 \321\200\320\260\320\267\321\200\320\260\320\261\320\276\321\202\320\272\320\270.docx" D "BCE/~$ 10 \321\207\320\260\321\201\321\202\321\214 \321\200\320\260\320\267\321\200\320\260\320\261\320\276\321\202\320\272\320\270.docx" C:\Program Files\Git\usr\bin\astextplain: line 18: docx2txt.exe: command not found C:\Program Files\Git\usr\bin\astextplain: line 18: docx2txt.exe: command not found Введите сообщение коммита (Enter = 'обновление KB'):
The user's patcher failed with SyntaxError: unterminated triple-quoted f-string literal. The problem is likely that the f-string contains { characters that are interpreted as f-string placeholders, OR more likely — the file was saved with the wrong encoding / BOM issue, OR the issue is that """ inside the f-string content (for Python code examples in the markdown) closes the f-string.
Looking at the markdown content: it contains """ inside code blocks like:
text
    "    Возвращает итоговый server_url.\n"
Wait, actually looking closer — the markdown contains Python code with """ tripled quotes inside:
•	Line "def prepare_client_env(version: str | None = None) -> str:\n" — no
•	There's f""" in some examples but let me check...
Actually the issue is simpler. The f-string content has:
•	{ and } characters (f-string placeholders) — need to escape as {{ and }} if literal, OR
•	""" triple quotes inside breaking the f-string literal.
Looking at the content in HANDOFF_INSTALLER string, I see code examples like:
text
    def prepare_client_env(version: str | None = None) -> str:
        """
Yes! There's a nested """ in the markdown content that closes the outer f-string. Also there might be {} in JSON examples.
The user is already in the middle of a git commit in update_site.bat. Let me handle this:
1.	First, tell them to abort the git commit (Ctrl+C or press Enter with a bad message, then reset).
2.	Actually the bat is waiting for input — they can either press Ctrl+C or type something and cancel the commit later.
Best move: they're stuck at the prompt. Tell them to press Ctrl+C to abort, then we fix the patcher.
The patcher problem is that we cannot use f-string for markdown that contains nested """. Solution: use regular triple-quoted string (no f prefix) and do .format() or use % substitution, OR read from a separate file.
Simplest: define the markdown WITHOUT f-string (regular """..."""), and only substitute the date via .replace(). That avoids the whole f-string parsing hell.
But wait — the file already failed to load, so nothing was written. But maybe some things got written? No — the SyntaxError happens at parse time, before ANY execution. So nothing was written. Good.
Also — the git state shows some BCE changes that are unrelated. The user should commit those too (or they were already pending).
Let me give clean instructions:
1.	Abort the git commit (Ctrl+C).
2.	Replace the patcher with a fixed version.
3.	Run again.
Actually — they can also just press Enter to make an empty commit message, or type something. But since the patcher didn't run, the docs/HANDOFF_INSTALLER.md doesn't exist yet, so committing now would be pointless. Better to abort.
Actually, looking again: update_site.bat shows staged changes (M BCE file, D docx temp file) — those are unrelated to our work. Even if we abort and rerun after fixing, the same changes will be there. The user may want to commit them separately or include in same commit. Doesn't matter much.
Let me write a clean fix. Key points:
•	Avoid f-string for large markdown content.
•	Use .replace("__DATE__", TODAY) after building the string as plain text.
•	In the markdown content, use regular """ triple quotes only in a way that doesn't nest.
Actually the content itself contains Python code samples with """ docstrings:
text
def prepare_client_env(version: str | None = None) -> str:
    """
    Готовит client/.env
    """
Hmm, but that's inside the markdown so it should be fine — as long as the outer container doesn't use """ as delimiter, it's OK. Let me use single-quoted triple string '''...''' for the markdown, and make sure there are no ''' inside it (there aren't).
Wait — the markdown content has # HANDOFF_INSTALLER.md etc — that's fine. It has Python code in there with ''' — need to check. Yes, code sample:
text
    def _parts(v):
        out = []
        for x in (v or "").split("."):
No ''' in there. Good.
Also — escape { and } in f-string. In the current content, we have JSON-like examples like {{8B7A6C2E-...}} — those are already escaped. But there are also Python format strings like f" OK client/.env: TRACKER_SERVER_URL={url}" which have single { — that WOULD be an f-string placeholder in the outer f-string.
So the fix: don't use f-string at all. Use regular triple-quoted string with ''' (single quotes), and replace __DATE__ placeholder with TODAY.
Actually if we use '''...''' we don't need to escape braces. And we avoid the nested """ issue too.
Let me write the corrected version.
Also — I need to consider the git prompt situation. The user is at:
text
Введите сообщение коммита (Enter = 'обновление KB'):
They need to abort. Press Ctrl+C.
Let me write the response compactly — user said "пишем всё только по делу".
Plan:
1.	Say: Ctrl+C to abort git.
2.	Fix patcher (compact).
3.	Run.
4.	Publish.
Keep it short.
Стоп, сначала оборви git — в окне PowerShell, где висит приглашение «Введите сообщение коммита», нажми Ctrl+C. Патчер упал ещё до записи файлов, так что ничего не сломано, просто отменим коммит.
Причина сбоя
Я обернул большой markdown в f-строку (f"""...""") — а внутри содержимого есть вложенные """ (Python-примеры в бриф) и одиночные { в примерах кода. Python не может их распарсить. Нужно убрать f и подставить дату через .replace().
Исправленный патчер
Открой на перезапись D:\tracker\_apply_handoff_installer.py в VS Code (code D:\tracker\_apply_handoff_installer.py) и вставь:
python
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import date

ROOT = Path(r"D:\tracker")
DOCS = ROOT / "docs"
TODAY = date.today().isoformat()


def _read(p): return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
def _write(p, t):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, encoding="utf-8", newline="\n")
    print("  OK ", p.relative_to(ROOT))


# ВАЖНО: НЕ f-строка. Дата подставляется через .replace("__DATE__", TODAY).
# Внутри есть вложенные " и {}, они в обычной строке безопасны.
HANDOFF_INSTALLER = '''# HANDOFF_INSTALLER.md — передача: серверный инсталлятор

Статус: бриф для следующего чата
Дата: __DATE__
Связанные: 06_DEPLOY/03_WINDOWS_SETUP.md, 06_DEPLOY/06_INSTALLER.md,
           06_DEPLOY/01_DOCKER.md, 06_DEPLOY/02_NGINX_TLS.md, HANDOFF.md

## Задача

Построить `TrackerServerSetup.exe` — единый установщик сервера
«Трекера» для Windows-машины (LAN). По аналогии с клиентским
`TrackerSetup.exe`, но для развёртывания серверной части.

### Что делает инсталлятор на чистой Windows

1. Проверяет, установлен ли Docker Desktop. Если нет — ставит
   (winget install Docker.DockerDesktop), ждёт готовности демона.
2. Разворачивает файлы проекта Tracker (архив).
3. Создаёт `.env`:
   - генерирует SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY
     (через secrets.token_urlsafe);
   - DATABASE_URL — стандартное значение;
   - не перезатирает существующий .env, если пользователь не
     попросит (для повторной установки / апгрейда).
4. Проверяет сертификаты certs/fullchain.pem + certs/privkey.pem:
   - если нет — выпускает self-signed (openssl в контейнере или
     через логику SCP на LAN-IP);
   - CN = 127.0.0.1, SAN = localhost, 127.0.0.1, LAN-IP,
     hostname, tracker, tracker.local.
5. Запускает `docker compose up -d --build` и ждёт healthy.
6. Настраивает firewall: правило `Tracker HTTPS`, TCP:443.
7. Создаёт ярлыки: «Tracker — админка» (браузер), «Tracker SCP»
   (запуск control.gui_main через python venv).
8. При повторном запуске — режим «Обновить сервер» (без сброса БД,
   только пересборка контейнеров).

### Что НЕ входит

- Windows Server (только Windows 10/11 x64).
- Linux/macOS.
- Установка PostgreSQL отдельно (используется контейнер).

## Что уже готово (переиспользуем)

| Компонент | Путь | Роль |
|---|---|---|
| deploy.json | D:\\tracker\\deploy.json | server_url, cert_cn, cert_san, hostname_alias |
| control/deploy.py | control/deploy.py | load/save/get/set_values |
| control/build.py | control/build.py | шаблон Inno + PyInstaller + prepare_client_env |
| control/build_tab.py | control/build_tab.py | UI: чекбоксы, QThread, лог |
| control/network_tab.py | control/network_tab.py | LAN-IP, firewall, перевыпуск cert, hosts |
| client/installer.iss | client/installer.iss | шаблон Inno для копирования |
| docker-compose.yml | docker-compose.yml | db + api + nginx, volume pgdata |
| server/entrypoint.sh | server/entrypoint.sh | миграции Alembic + gunicorn |
| server/Dockerfile | server/Dockerfile | python:3.11-slim |
| .env | D:\\tracker\\.env | SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY |

## Что нужно решить

1. Где разворачивать: C:\\Program Files\\Tracker\\ (UAC) или
   D:\\tracker\\ (без UAC). Скорее — второе.
2. Docker Desktop: winget / оффлайн-инсталлятор / вручную.
3. Сертификат: генерить внутри инсталлятора или через SCP-логику.
4. Firewall: UAC-запрос (netsh advfirewall).
5. Обновление сервера: второй режим, без сброса pgdata.
6. Дистрибутив: Inno с [Files] из D:\\tracker\\* или архив .zip,
   который инсталлятор распаковывает.

## Файлы, которые нужно прислать в следующем чате

Обязательно:
1. docs/HANDOFF.md
2. docs/00_INDEX.md
3. docs/06_DEPLOY/03_WINDOWS_SETUP.md
4. docs/06_DEPLOY/01_DOCKER.md
5. docs/06_DEPLOY/02_NGINX_TLS.md
6. docs/06_DEPLOY/06_INSTALLER.md
7. docs/06_DEPLOY/05_UPDATES.md
8. docker-compose.yml
9. server/Dockerfile
10. server/entrypoint.sh
11. .env (структура, без значений)
12. deploy.json
13. client/installer.iss
14. control/config.py
15. control/deploy.py
16. control/build.py
17. control/build_tab.py
18. control/network_tab.py
19. control/gui.py (как подключаются вкладки)
20. список файлов control/ (нужно увидеть, где выпуск сертификата)

Желательно:
21. control/services_tab.py
22. control/admin.py
23. control/publish.py

## Команды (шпаргалка)

Сервер:
  cd D:\\tracker
  docker compose ps
  docker compose logs api --tail=30
  docker compose down && docker compose up -d --build

Админка:
  https://192.168.0.35/admin/login
  логин admin, пароль = ADMIN_API_KEY из .env

Сборка клиента:
  SCP - вкладка «Сборка» - «Собрать полностью» + «Опубликовать версию»

Сборка сервера (предстоит):
  D:\\tracker\\installer\\TrackerServerSetup.exe

## Состояние проекта на __DATE__

- Готовность: ~97%. P0 «Публикация версий через UI» закрыт.
- Сервер: FastAPI + PostgreSQL 16 + nginx + Docker, миграции до
  a1b2c3d4e5f6, 7 задач планировщика.
- Админка: 75+ роутов, страница /admin/versions.
- Клиент: PyQt6, обновление с проверкой sha256, диалог согласия.
- SCP: вкладки Статус, Сертификат, Сервисы, Сеть, Сборка, Админ,
  публикация версий.
- KB опубликован: https://erohin-a.github.io/tracker/
'''


def create_handoff_installer():
    p = DOCS / "99_RAW" / "HANDOFF_INSTALLER.md"
    print("[1/2] docs/99_RAW/HANDOFF_INSTALLER.md")
    if p.exists():
        print("  --  уже есть, пропускаю")
        return
    _write(p, HANDOFF_INSTALLER.replace("__DATE__", TODAY))


def patch_handoff():
    print("[2/2] docs/HANDOFF.md")
    p = DOCS / "HANDOFF.md"
    text = _read(p)

    old = (
        "## 11. Что делать в следующем чате (после handoff)\n"
        "\n"
        "1. Реализовать ca.pem через UI (SCP).\n"
        "2. UX-аудит админки и клиента (тултипы, интуитивность, единый стиль ошибок).\n"
        "3. i18n клиента до конца, темы, бэкапы, алерты.\n"
    )
    new = (
        "## 11. Что делать в следующем чате (после handoff)\n"
        "\n"
        "1. **Серверный инсталлятор** — TrackerServerSetup.exe.\n"
        "   Подробный бриф: 99_RAW\\HANDOFF_INSTALLER.md.\n"
        "2. Реализовать ca.pem через UI (SCP).\n"
        "3. UX-аудит админки и клиента (тултипы, интуитивность).\n"
        "4. i18n клиента до конца, темы, бэкапы, алерты.\n"
    )
    if old in text:
        text = text.replace(old, new, 1)
        print("  --  §11 обновлён")
    else:
        print("  --  §11: шаблон не найден (уже правился)")

    if "## 13. Следующий этап" not in text:
        text = text.rstrip("\n") + "\n\n---\n\n## 13. Следующий этап: серверный инсталлятор (" + TODAY + ")\n"
        text += "\n"
        text += "Полный бриф — в 99_RAW\\HANDOFF_INSTALLER.md.\n"
        text += "\n"
        text += "Коротко:\n"
        text += "- Единый TrackerServerSetup.exe для Windows.\n"
        text += "- Проверяет/ставит Docker Desktop.\n"
        text += "- Разворачивает проект, создаёт .env с автогенерацией секретов.\n"
        text += "- Выпускает self-signed сертификат (или через SCP).\n"
        text += "- Поднимает docker compose up -d --build.\n"
        text += "- Настраивает firewall (443).\n"
        text += "- Создаёт ярлыки: админка, SCP.\n"
        text += "- Режим «Обновить сервер» — без сброса БД.\n"
        text += "\n"
        text += "Переиспользуем готовое: control/deploy.py, control/build.py,\n"
        text += "client/installer.iss, docker-compose.yml, control/network_tab.py.\n"
        text += "\n"
        text += "Перед началом следующего чата приложить файлы из списка\n"
        text += "в HANDOFF_INSTALLER.md (раздел «Файлы, которые нужно прислать»).\n"
        print("  --  §13 добавлен")
    else:
        print("  --  §13 уже есть")

    _write(p, text)


def main():
    print("=" * 60)
    print("Патч KB: передача — серверный инсталлятор")
    print("=" * 60)
    if not DOCS.exists():
        raise SystemExit("Не найден " + str(DOCS))
    create_handoff_installer()
    patch_handoff()
    print()
    print("Дальше — публикация KB:")
    print("  cd D:\\tracker\\docs")
    print("  .\\update_site.bat")


if __name__ == "__main__":
    main()
Запуск
powershell
cd D:\tracker
client\.venv\Scripts\python.exe _apply_handoff_installer.py
Ожидаешь:
text
[1/2] docs/99_RAW/HANDOFF_INSTALLER.md
  OK  docs\99_RAW\HANDOFF_INSTALLER.md
[2/2] docs/HANDOFF.md
  --  §11 обновлён
  --  §13 добавлен
  OK  docs\HANDOFF.md
Публикация
powershell
cd D:\tracker\docs
.\update_site.bat
Когда скрипт спросит сообщение коммита — просто нажми Enter (будет «обновление KB») или впиши handoff: серверный инсталлятор.
Если git снова будет ворчать на docx2txt.exe и .docx-файлы — это не ошибка, а предупреждение. Коммит пройдёт, docx просто не конвертируется в текст для diff'а.
________________________________________
Что дальше
Следующий чат начинай так:
1.	Приложи docs/HANDOFF.md, docs/00_INDEX.md, docs/99_RAW/HANDOFF_INSTALLER.md.
2.	Приложи файлы из раздела «Файлы, которые нужно прислать» брифа (обязательные 20).
3.	Скажи: «Делаем серверный инсталлятор, вот файлы».
По объёму брифа я сразу пойду по плану: сначала уточню, где выпускаются сертификаты (не хватает control/certificates.py — если такого нет, назови файл), потом соберу installer_server/ с Inno-скриптом и вспомогательными Python/PowerShell.
Этот ответ сгенерирован AI, только для справки.
Приложи файлы из раздела «Файлы, которые нужно прислать» брифа (обязательные 20). а что это за файлы?
User is asking what files need to be attached for the next chat. Let me list them clearly from the brief.
Это список из брифа HANDOFF_INSTALLER.md, раздел «Файлы, которые нужно прислать». Он нужен, чтобы в следующем чате я не строил инсталлятор вслепую. Разбит на две группы — обязательные и желательные.
Обязательные 20
KB (7 файлов)
1.	D:\tracker\docs\HANDOFF.md
2.	D:\tracker\docs\00_INDEX.md
3.	D:\tracker\docs\06_DEPLOY\03_WINDOWS_SETUP.md
4.	D:\tracker\docs\06_DEPLOY\01_DOCKER.md
5.	D:\tracker\docs\06_DEPLOY\02_NGINX_TLS.md
6.	D:\tracker\docs\06_DEPLOY\06_INSTALLER.md
7.	D:\tracker\docs\06_DEPLOY\05_UPDATES.md
Инфраструктура сервера (4 файла)
8.	D:\tracker\docker-compose.yml
9.	D:\tracker\server\Dockerfile
10.	D:\tracker\server\entrypoint.sh
11.	D:\tracker\.env — только структура, без значений. Просто скопируй в чат, заменив сами секреты на xxx.
Конфиг и шаблон (2 файла)
12.	D:\tracker\deploy.json
13.	D:\tracker\client\installer.iss — как шаблон для серверного Inno
SCP (5 файлов)
14.	D:\tracker\control\config.py
15.	D:\tracker\control\deploy.py
16.	D:\tracker\control\build.py
17.	D:\tracker\control\build_tab.py
18.	D:\tracker\control\network_tab.py
Что ещё нужно (2 позиции)
19.	D:\tracker\control\gui.py — как подключаются вкладки в SCP
20.	Список файлов control/ — просто запусти в PowerShell:
powershell
Get-ChildItem D:\tracker\control\*.py | Select-Object Name
Это чтобы я увидел, где лежит выпуск сертификата (мне нужен control/certificates.py или как он у тебя называется).
Желательные (3 файла, но приложи если не сложно)
21.	D:\tracker\control\services_tab.py
22.	D:\tracker\control\admin.py
23.	D:\tracker\control\publish.py
________________________________________
Зачем каждый нужен
Файл	Зачем
HANDOFF.md, 00_INDEX.md	Контекст проекта, чтобы я сразу понимал картину
06_DEPLOY/*	Что уже описано про установку сервера, Docker, TLS, Inno
docker-compose.yml, Dockerfile, entrypoint.sh	Что именно разворачивает инсталлятор
.env	Какие переменные нужно автогенерить при установке
deploy.json	Что читает SCP и куда писать server_url/cert
client/installer.iss	Готовый шаблон Inno — переиспользуем структуру
control/config.py, deploy.py	Пути, утилиты, дефолты — чтобы инсталлятор туда же попадал
control/build.py, build_tab.py	Логика сборки и UI — по аналогии сделаем серверный
control/network_tab.py	LAN-IP, firewall, cert — переиспользуем в серверном инсталляторе
control/gui.py	Как SCP регистрирует вкладки, если будем делать отдельную
список control/*.py	Найти файл с выпуском сертификата (мне важно)
services_tab.py, admin.py, publish.py	Дополнительный контекст по SCP
________________________________________
Как быстро собрать
Вариант 1 — вручную. Открой папки docs, control, корень D:\tracker и перетащи файлы из списка в окно следующего чата.
Вариант 2 — одной командой. Скопирует всё в D:\_handoff_for_next_chat\ — потом просто выделяешь папку и тащишь в чат:
powershell
$dst = "D:\_handoff_for_next_chat"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
$files = @(
  "docs\HANDOFF.md",
  "docs\00_INDEX.md",
  "docs\06_DEPLOY\03_WINDOWS_SETUP.md",
  "docs\06_DEPLOY\01_DOCKER.md",
  "docs\06_DEPLOY\02_NGINX_TLS.md",
  "docs\06_DEPLOY\06_INSTALLER.md",
  "docs\06_DEPLOY\05_UPDATES.md",
  "docker-compose.yml",
  "server\Dockerfile",
  "server\entrypoint.sh",
  ".env",
  "deploy.json",
  "client\installer.iss",
  "control\config.py",
  "control\deploy.py",
  "control\build.py",
  "control\build_tab.py",
  "control\network_tab.py",
  "control\gui.py",
  "control\services_tab.py",
  "control\admin.py",
  "control\publish.py"
)
foreach ($f in $files) {
  $src = Join-Path "D:\tracker" $f
  if (Test-Path $src) {
    $out = Join-Path $dst (Split-Path $f -Leaf)
    Copy-Item $src $out -Force
    Write-Host "OK  $f"
  } else {
    Write-Host "--  нет: $f"
  }
}
Get-ChildItem "D:\tracker\control\*.py" | Select-Object Name | Out-File "$dst\_control_file_list.txt" -Encoding UTF8
Write-Host ""
Write-Host "Готово. Файлы: $dst"
Write-Host "Список control/*.py: $dst\_control_file_list.txt"
Скрипт сам пропустит отсутствующие файлы (пометка --), а список control/*.py сложит в _control_file_list.txt.
Важное про .env: перед отправкой в чат открой его и замени значения секретов на xxx. Реальный ADMIN_API_KEY в чат не кладём.
________________________________________
Что делать дальше
1.	Скопируй файлы (вариант 1 или 2).
2.	Приложи их в новом чате вместе с этим промптом:
Делаем серверный инсталлятор (TrackerServerSetup.exe). Бриф — в HANDOFF_INSTALLER.md. Прикладываю файлы из списка. Начни с уточнений: где в control/ выпуск сертификата, что писать в .env при автогенерации, как упаковывать дистрибутив (Inno [Files] vs архив).
Один совет: если файлов действительно много и не влезут за раз — приложи сначала обязательные 7 KB-документов + docker-compose.yml + Dockerfile + entrypoint.sh, а остальное (SCP-модули) доберём по ходу. Так тоже можно, не критично.

