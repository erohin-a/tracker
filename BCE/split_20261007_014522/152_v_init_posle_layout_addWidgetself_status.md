<!-- Часть 152 из 1409 -->
# в __init__ после layout.addWidget(self.status):
*Хлебные крошки:* в __init__ после layout.addWidget(self.status):

[◀ ---------- Компьютеры ----------](151_Kompyutery.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Утилиты ---------- ▶](153_Utility.md)

---

# в __init__ после layout.addWidget(self.status):
self.autostart_cb = QCheckBox("Автозапуск")
self.autostart_cb.setChecked(self._load_autostart_setting())
self.autostart_cb.stateChanged.connect(self._on_autostart_changed)
layout.addWidget(self.autostart_cb)

def _load_autostart_setting(self) -> bool:
    cfg = BASE_DIR / "config.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text(encoding="utf-8")).get("autostart_enabled", False)
        except Exception:
            pass
    return False

def _on_autostart_changed(self, state):
    enabled = state == 2  # Qt.CheckState.Checked
    ok = set_autostart(enabled)
    if ok:
        cfg = BASE_DIR / "config.json"
        data = {}
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
            except Exception:
                pass
        data["autostart_enabled"] = enabled
        cfg.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
________________________________________
7. Установщик Windows (Inno Setup)
Создайте installer.iss:
ini
[Setup]
AppName=Tracker
AppVersion=1.2.0
DefaultDirName={localappdata}\Tracker
DefaultGroupName=Tracker
OutputBaseFilename=TrackerSetup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
WizardStyle=modern

[Files]
Source: "client\dist\Tracker\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\Tracker"; Filename: "{app}\Tracker.exe"
Name: "{userstartup}\Tracker"; Filename: "{app}\Tracker.exe"; Parameters: "--minimized"

[Run]
Filename: "{app}\Tracker.exe"; Description: "Запустить Tracker"; Flags: nowait postinstall skipifsilent

[Code]
var
  TokenPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  TokenPage := CreateInputQueryPage(wpSelectTasks,
    'Bootstrap-токен', 'Введите одноразовый токен',
    'Получите токен у администратора и вставьте сюда. Он будет сохранён в %APPDATA%\Tracker\bootstrap.txt');
  TokenPage.Add('Токен:', False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Token: String;
  Dir: String;
begin
  if CurStep = ssPostInstall then
  begin
    Token := TokenPage.Values[0];
    if Token <> '' then
    begin
      Dir := ExpandConstant('{userappdata}\Tracker');
      ForceDirectories(Dir);
      SaveStringToFile(Dir + '\bootstrap.txt', Token, False);
    end;
  end;
end;
Сборка:
powershell
cd D:\tracker\client
pyinstaller build.spec --clean
cd ..
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
________________________________________
8. Что делать по шагам
Обновить модели
Добавить employee_id в Computer, поля ФИО в Employee, поправить upsert_session.
Пересобрать сервер
docker compose down, docker compose up -d --build.
Если БД уже есть — вручную ALTER TABLE или подключить Alembic.
Добавить веб-админку
Создать server/web_admin.py, server/templates/*, подключить SessionMiddleware и роутер в main.py.
Добавить отчёты
Создать server/reports.py, добавить эндпоинты и шаблоны.
Проверить
Зайти на https://localhost/admin/login, ввести admin и ADMIN_API_KEY.
Создать сотрудника, привязать компьютер, сформировать отчёт.
Клиент: автозапуск
Добавить client/autostart.py, чекбокс в главное окно.
Собрать установщик
pyinstaller build.spec, затем Inno Setup.
Обновить requirements
Не забыть jinja2, python-multipart, itsdangerous, openpyxl, reportlab.
Alembic (следующий шаг)
Инициализировать alembic, создать миграцию на текущую схему, дальше менять только через миграции.
________________________________________
9. Что ещё стоит сделать в ближайшее время
Heartbeat-эндпоинт /api/v1/heartbeat — клиент раз в 5 минут шлёт X-Computer-Uid, сервер обновляет last_seen_at.
Роли admin/operator/viewer — таблица admin_users, хеш пароля через passlib.
Публикация версий через UI — форма добавления записи в client_versions.
Бэкап PostgreSQL — cron + pg_dump, хранение 30 дней.
Тесты — pytest для API, моки для pynput.
Если хотите, могу следующим сообщением выдать:
полный server/web_admin.py с PDF-экспортом;
Alembic-миграцию под новые поля;
готовый build.bat и installer.iss под вашу структуру;
код heartbeat и ролей.
Давай начнем с создания вэб интерфейса
The user wants to start with creating the web interface. Let me provide a complete, working implementation of the web admin interface for the Tracker project. I need to be thorough and give them everything they need to actually run this.
Let me structure this properly:
Requirements update
Server config updates for admin credentials
web_admin.py - main router
Templates (base, login, dashboard, employees, computers, reports)
Static files if needed
Integration into main.py
Testing instructions
I should be practical and give working code. Let me write it out carefully.
Key considerations:
The existing project uses ADMIN_API_KEY for API admin auth
I need a separate login for the web UI (or reuse ADMIN_API_KEY)
Session middleware needed
Jinja2 templates
Bootstrap 5 via CDN (simpler)
Need to handle the existing models (Computer, Employee, WorkSession, Record, BootstrapToken, AuditLog, ClientVersion)
Let me also think about what pages are needed:
Login
Dashboard (stats)
Employees (list, create, edit, deactivate)
Computers (list, assign to employee, revoke)
Bootstrap tokens (issue new)
Reports (list, generate, export)
Audit log
Let me write this carefully and completely.
I should be careful about:
DateTime handling (timezone-aware)
SQLAlchemy 2.0 style vs 1.x style - the existing code uses 1.x style (db.query())
The BootstrapToken issuance logic needs to be reused from main.py
Let me structure the answer well with clear sections.
Веб-интерфейс администратора «Трекер» — пошаговая реализация
Ниже — готовый к запуску код. Разбито на шаги: сначала подготовка, потом файлы, потом подключение и проверка.
________________________________________
Шаг 0. Что получится в итоге
Страницы:
/admin/login — вход по логину/паролю.
/admin — дашборд со статистикой.
/admin/employees — CRUD сотрудников.
/admin/computers — список ПК, привязка к сотрудникам, revoke.
/admin/tokens — выпуск bootstrap-токенов.
/admin/reports — форма отчёта + просмотр + экспорт CSV/XLSX.
/admin/audit — журнал аудита.
Аутентификация — сессия (cookie), логин admin + ADMIN_API_KEY из .env. Позже легко заменить на таблицу admin_users с ролями.
________________________________________
Шаг 1. Дополнить зависимости сервера
server/requirements.txt — добавьте:
txt
jinja2==3.1.4
itsdangerous==2.2.0
openpyxl==3.1.5
python-multipart==0.0.9
Пересоберёте образ позже.
________________________________________
Шаг 2. Дополнить server/config.py
Добавьте в Settings (внутри server/config.py):
python
class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tracker:tracker@db:5432/tracker"
    secret_encryption_key: str = ""
    jwt_secret: str = ""
    admin_api_key: str = ""

    # ? новые поля для веб-интерфейса
    admin_login: str = "admin"
    session_secret: str = ""   # если пусто — используем jwt_secret
    web_secure_cookie: bool = False  # True на проде с HTTPS

    class Config:
        env_file = ".env"
Ничего больше не трогаем — если session_secret пуст, в main.py подставим jwt_secret.
________________________________________
Шаг 3. Создать структуру шаблонов
text
server/
??? templates/
?   ??? base.html
?   ??? login.html
?   ??? dashboard.html
?   ??? employees.html
?   ??? computers.html
?   ??? tokens.html
?   ??? reports.html
?   ??? report_result.html
?   ??? audit.html
??? web_admin.py
________________________________________
Шаг 4. server/web_admin.py
Полностью готовый файл:
python
"""
Веб-интерфейс администратора для проекта «Трекер».
Аутентификация: сессия (cookie), логин admin + ADMIN_API_KEY.
"""
import csv
import io
import json
import secrets
from datetime import datetime, date, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from .config import FERNET, settings
from .database import SessionLocal
from .models import (
    AuditLog, BootstrapToken, ClientVersion, Computer, Employee, Record, WorkSession,
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="server/templates")


