<!-- Часть 147 из 1409 -->
# 12. Заключение
*Хлебные крошки:* Техническое задание на разработку системы учёта рабочего времени удалённых сотрудников «Трекер» (расширенная версия) / 12. Заключение

[◀ 11.3. Рекомендуемые библиотеки (полный список)](146_11_3_Rekomenduemye_biblioteki_polnyy_spisok.md) | [Оглавление](00_BCE_INDEX.md) | [Employee add columns ▶](148_Employee_add_columns.md)

---

## 12. Заключение

Данное техническое задание представляет собой расширенную и детализированную версию исходного ТЗ. Оно учитывает:

- Проблемы кроссплатформенности и пути их решения.
- Юридические требования (152-ФЗ).
- Технические риски (антивирусы, GIL, конкурентный доступ к SQLite).
- Детальную архитектуру и схему данных.
- Полный стек технологий с обоснованием выбора.
- План разработки с оценкой сроков.
- Требования к тестированию и развёртыванию.



17.09.2026
Во вложении проект Трекер. Много ещё не реализовано. Нет привязки к компьютеру нет нормальных отчётов интерфейса наверное нужно создать веб интерфейс для админа для регистрации новых сотрудников вывода отчётов. нужно создать авто установочные файлы, сделать автозапуск. проведи глубокий анализ проделанной работы. и помоги создать всё недостающие 
We need answer in Russian. User attached huge doc. They ask: "Во вложении проект Трекер. Много ещё не реализовано. Нет привязки к компьютеру нет нормальных отчётов интерфейса наверное нужно создать веб интерфейс для админа для регистрации новых сотрудников вывода отчётов. нужно создать авто установочные файлы, сделать автозапуск. проведи глубокий анализ проделанной работы. и помоги создать всё недостающие"
We need provide deep analysis and help create missing. We can't actually create files? We can outline, provide code snippets, plan, maybe complete implementation. Need be useful. Since huge context, maybe they want assistance. We need analyze current project state, gaps, propose architecture, implement missing pieces: web admin UI, reports, employee/computer binding, autoinstallers, autostart. We can provide code for FastAPI web UI with Jinja2, admin auth, CRUD employees, computers, binding, reports export CSV/Excel/PDF? Need maybe not full code but enough. We have token budget. Need craft answer.
We need understand current code. Existing server has FastAPI API, models Computer, Employee, WorkSession, Record, BootstrapToken, ClientVersion, AuditLog. Client registers computer by bootstrap token, no employee info. Records include kind/data. No employee binding. No web UI. No reports. No installer/autostart.
We should propose modifications:
Add Employee management and binding: extend Computer with employee_id? Already Employee model but Computer doesn't have employee_id. WorkSession has employee_id. Need add employee_id to Computer? Or Computer assignment via new table? Simpler: add employee_id FK to Computer, plus assigned_at. Then sessions inherit employee_id from computer at creation if not set. Registration payload should include employee info? But client currently doesn't collect employee. Could add optional employee_id/employee fields to RegisterRequest. For admin UI, admin can register employee and bind computer after registration. Better: admin UI lists computers, assign employee. Then when client creates session, server sets employee_id from computer.employee_id. Also records don't need employee.
Web admin UI:
Session-based auth with admin user. Could use simple ADMIN_API_KEY or add AdminUser model. Since existing only ADMIN_API_KEY, simplest: login page asks admin key, sets signed cookie. Or add admin users table with password hash. Better implement minimal: AdminUser model with username/password_hash/role. Use passlib, python-jose? But existing requirements lack passlib, jinja2. We can add. Or use itsdangerous for session. Simpler: use FastAPI SessionMiddleware with secret_key=JWT_SECRET, and login checks ADMIN_API_KEY. But for real roles need users. We can propose two-step: MVP use ADMIN_API_KEY login, later roles.
Pages: dashboard, employees CRUD, computers list/assign, sessions/records, reports.
Templates: base, login, employees, computers, reports, report_result.
Reports:
Endpoints: GET /admin/reports with filters employee, computer, date range, type. Generate summary from WorkSession, Record. Need parse Record data. Current records: kind activity, window, idle, idle_end. Activity data has keys/clicks/scroll. Window data has app, title. We can compute:
Session duration.
Active keyboard/mouse: sum activity counts? But no seconds. Client sends counts every 5 sec? Actually CollectorWorker flushes every 5 sec? It emits activity with counts of keys/clicks/scroll in interval. So each activity record represents 5 sec interval with some counts. We can count intervals with any activity? Or estimate active seconds = count of activity records where keys+clicks+scroll > 0 * ACTIVE_WINDOW_INTERVAL (5 sec). Better to store duration in data? Current doesn't. We can modify client to include interval_seconds. For now, report by number of activity events.
Program usage: window records are edge-triggered when window changes. Need compute duration between window records per session. Could do in SQL? Easier in Python: fetch window records ordered by client_ts, compute durations until next window/idle/session_end. This gives time per app/title.
Idle: idle records mark start, idle_end marks end. Compute idle duration.
Export CSV, Excel via openpyxl, PDF via reportlab. Add requirements.
Autoinstallers:
Client: PyInstaller onedir, Inno Setup script for Windows. Provide build.bat, installer.iss. Autostart via registry or Startup folder. Already client has autostart toggle not implemented. Implement autostart in client config/main? Could add functions in client/autostart.py. On first run, if config autostart_enabled true, create shortcut/bat in Startup. Also installer can add to startup optionally.
Server: docker compose already. Could add docker-compose.prod.yml, .env.example, scripts for backup.
Auto-update: existing updater. Need publish versions via admin UI.
We need "помоги создать всё недостающие". We can provide concrete code snippets and structure. Given answer length, we can give a complete roadmap and key code. Maybe ask what to start? But likely need answer. We can provide code for:
Server modifications: models employee_id on Computer, admin web router, templates, report service, export.
Client autostart module and integration.
Inno Setup script.
Build scripts.
Admin UI code.
Need be careful not to produce too massive unreadable. Desired oververbosity 5. But user wants deep analysis and help create. We can structure:
Глубокий анализ текущего состояния: что готово, что критично.
Целевая архитектура доработки.
Пошаговый план внедрения.
Код:
server/web_admin.py with FastAPI APIRouter, Jinja2Templates, login, dashboard, employees, computers, bind, reports.
templates/base.html, login.html, employees.html, computers.html, reports.html, report_result.html.
server/reports.py for report generation.
server/models.py changes: Computer.employee_id, AdminUser? Use existing.
client/autostart.py.
installer.iss.
Как внедрять.
Need mention that we can't physically create files, but provide ready-to-copy code. Since API, final should be answer.
Let's design code.
Server models changes:
Add to Computer: employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True); assigned_at = Column(DateTime(timezone=True))
Employee already exists. Add full_name? It has full_name, external_id, is_active. For UI, we need last_name/first_name/middle_name. Could add fields or use full_name. Simpler: add last_name, first_name, middle_name to Employee model. But existing Employee has full_name. We can add columns. Or use full_name and parse? Better add.
WorkSession already employee_id. When creating session, set employee_id from comp.employee_id.
Record: no change.
Admin web:
Use FastAPI APIRouter. Need templates dir: server/templates. Static? Use Bootstrap CDN.
Auth: simple dependency:
text
def get_current_admin(request: Request):
    if request.session.get("admin"):
        return request.session["admin"]
    raise HTTPException(401)
Need SessionMiddleware in main.py: from starlette.middleware.sessions import SessionMiddleware; app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret).
Login:
text
@router.get("/login")
@router.post("/login")
async def login(request, username, password):
    if username=="admin" and secrets.compare_digest(password, settings.admin_api_key):
        request.session["admin"]="admin"
        return RedirectResponse("/admin", 303)
Logout.
Pages:
dashboard: counts.
employees: list, create, edit, deactivate.
computers: list with employee assign dropdown, revoke.
reports: form; POST generate -> render report or download.
Report service:
Functions:
text
def generate_report(db, employee_id, computer_uid, date_from, date_to, report_type):
    sessions = query WorkSession join Computer ...
    for each session:
        duration = (session_end or now) - session_start
        records = query Record where session_uid and kind in ...
        # activity: sum counts, active_intervals = count records with keys+clicks+scroll>0
        # window: compute durations per app
Need parse JSON data. Use json.loads.
Export:
CSV using csv module.
Excel using openpyxl.
PDF using reportlab. For Cyrillic need DejaVuSans. We can provide code with font registration path.
But maybe too much. We can provide core.
Client autostart:
text
def set_autostart(enabled):
    if win: import winreg; key=HKCU\Software\Microsoft\Windows\CurrentVersion\Run; set/delete "Tracker"
    elif linux: ~/.config/autostart/tracker.desktop
Integrate in main window: checkbox. But existing UI no checkbox. We can add minimal.
Installer Inno Setup:
text
[Setup]
AppName=Tracker
AppVersion=1.2.0
DefaultDirName={localappdata}\Tracker
DefaultGroupName=Tracker
OutputBaseFilename=TrackerSetup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
[Files]
Source: "dist\Tracker\*"; DestDir: "{app}"; Flags: recursesubdirs
[Icons]
Name: "{userstartup}\Tracker"; Filename: "{app}\Tracker.exe"; Parameters: "--minimized"
Name: "{group}\Tracker"; Filename: "{app}\Tracker.exe"
[Run]
Filename: "{app}\Tracker.exe"; Description: "Запустить Tracker"; Flags: nowait postinstall skipifsilent
[Code]
...
Need bootstrap token. Installer can ask for token and write to %APPDATA%\Tracker\bootstrap.txt. Use Pascal script.
Build scripts:
client/build.bat:
text
pyinstaller build.spec --clean
Inno Setup compile.
Auto-update publish: admin UI can add ClientVersion.
We should also analyze gaps:
No employee binding: fix.
No reports: fix.
No web UI: fix.
No installers/autostart: fix.
No heartbeat: optional.
No Alembic: recommend.
We need mention security: web admin over HTTPS, session cookie secure.
Let's craft answer with sections:
Глубокий анализ: что уже есть, что критично, риски.
Архитектура доработки.
Что делать по шагам.
Код (сервер: модели, веб-админка, отчёты; клиент: автозапуск; установщик).
Как внедрить и проверить.
Что дальше.
Given final answer length, we can include code snippets. Need ensure not too massive. But user wants help create. We'll provide enough.
Let's write in Russian.
Start with "Можно сделать так". Then analysis.
Detailed analysis:
Сильные стороны: сервер/клиент, HMAC, офлайн, Docker, bootstrap.
Пробелы:
Employee не связан с Computer; WorkSession.employee_id не заполняется.
Нет веб-интерфейса.
Нет отчётов.
Нет установщиков.
Нет автозапуска.
Нет миграций.
Нет ролей.
Нет heartbeat.
Нет тестов.
Приоритеты: P0 employee binding, web UI, reports, installers, autostart. P1 Alembic, roles, heartbeat, backup. P2 Wayland, macOS, 1C.
Then architecture:
Добавить employee_id в computers.
При создании сессии брать employee_id из computer.
Веб-админка на FastAPI + Jinja2 + Bootstrap, сессия через SessionMiddleware.
Отчёты: сервис, экспорт CSV/Excel/PDF.
Установщик Inno Setup, автозапуск через реестр/Startup.
Code:
models.py patch:
python
