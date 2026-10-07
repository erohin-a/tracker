# ============================================================

*Часть 14 из 100. Источник: `BCE.md`.*

[◀ ============================================================](013_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](015_part.md)

---

# ============================================================
Write-Host "`n--- Пересборка Docker ---" -ForegroundColor Cyan
Set-Location D:\tracker
docker compose down
docker compose up -d --build

Start-Sleep -Seconds 25

Write-Host "`n--- Статус контейнеров ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Логи API (последние 30 строк) ---" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`nГотово. Откройте: https://localhost/admin/computers" -ForegroundColor Green
________________________________________
Что делать после запуска
Откройте https://localhost/admin/computers — должно открыться без ошибки.
Потом /admin/tokens, /admin/audit, /admin — все должны работать.
Если какая-то всё ещё падает — пришлите вывод:
powershell
docker compose logs api --tail=60
Там будет конкретная ошибка (обычно TemplateAssertionError или UndefinedError).
________________________________________
Если какой-то шаблон всё ещё падает
Наиболее вероятно, что в старых dashboard.html / computers.html / tokens.html / audit.html / employees.html используются переменные, которые я в новом web_admin.py переименовал. Если такое случится — я пришлю обновлённые версии этих шаблонов через PowerShell-скрипт (как для base.html, reports.html, report_result.html).
Напишите результат после перезапуска — заработало ли, или какая конкретно ошибка осталась.
у сотрудников есть 1С id его необходимо выводить в отчёт В отчёте мы видим сколько сотрудник пользовался мышкой сколько клавиатурой. Нужно это убрать из основного отчёта и привязать к программе что бы было понятно в какой программе. Нужно сделать настройку во сколько начинается новый рабочий день. Или посоветуй как реализовать? Если у сотрудника компьютер не выключается круглосуточно, как понять начал работать он сегодня или продолжает работать компьютер без него? как быть?
Пользователь задал важные вопросы про логику отчётов. Давайте разберёмся подробно.
1C ID в отчёт — просто добавить колонку.
Мышь/клавиатура привязать к программам — сейчас у нас активность (клавиатура/мышь) считается независимо от активной программы. Нужно связать: если в интервале X была активная клавиатура И активное окно было PyCharm ? значит клавиатура была в PyCharm.
Логика:
Клиент пишет activity события каждые 5 сек: keys/clicks/scroll за интервал.
Клиент пишет window события при смене окна.
Сейчас на сервере: keyboard += 5 за каждое activity с keys>0, mouse += 5 за clicks+scroll>0.
Нужно: смотреть, какое окно было активно в момент activity, и записывать 5 сек клавиатуры/мыши именно этой программе.
Это можно сделать на сервере: отсортировать все записи по client_ts, идти по ним, держать "текущее окно", при встрече activity — добавить к текущему окну.
Настройка начала рабочего дня — рабочий день начинается, например, в 06:00 или 04:00. Сессия, начавшаяся в 02:00, относится к предыдущему дню. Или наоборот — сессия, начавшаяся в 05:00, относится к текущему дню.
Это нужно для группировки "День ? Сотрудник".
Лучший подход: настраиваемое время начала рабочего дня (по умолчанию 00:00 или 04:00). Сессия относится к «рабочему дню», если её session_start_local >= day_start_local + day_start_hour. Иначе — к предыдущему рабочему дню.
Компьютер не выключается 24/7, как понять, начал ли сотрудник работать?
Это очень важный практический вопрос. Сейчас у нас кнопки «Начать работу» / «Конец работы». Пока сотрудник не нажал — сессии нет. То есть если сотрудник ушёл и не нажал «Конец работы», сессия тянется.
Варианты:
А) Полуавтомат: кнопки + авто-детект бездействия
Если нет активности (клавиатура/мышь) > N минут (например 30–60), сессия автоматически помечается завершённой временем последней активности, а не текущим моментом.
При следующей активности в ту же сессию — либо продолжение (если < порога), либо новая сессия (если между ними > порога или сменился рабочий день).
Б) Полный автомат: полагаться только на idle
Не нужны кнопки, всё автоматически. Но тогда менее точный учёт (не понять, что человек на обеде vs ушёл домой).
В) Гибрид (лучшее):
Сотрудник нажимает «Начать работу» утром.
Вечером нажимает «Конец работы».
Если забыл нажать — система сама закроет сессию через N минут без активности (последняя активность = конец сессии).
На сервере/в отчётах: если сессия закрыта автоматически, помечать её auto_closed=1.
При подсчёте «отработал часов» отнимаем «хвост» без активности.
Практическая реализация на сервере:
При расчёте длительности сессии не брать session_end - session_start вслепую.
Взять последнюю активность в сессии (max client_ts из records с kind in ('activity', 'window')).
Эффективная длительность = last_activity - session_start.
Или ещё строже: прибавлять по 5 секунд за каждое activity-событие, но с учётом «окна» — если между двумя activity прошло > 5 мин, этот разрыв не считаем.
Это как раз и решает проблему «компьютер работает 24/7».
Но лучше — чтобы клиент сам не писал «мусорные» сессии. Сотрудник закрыл ноутбук, не нажал «Конец» — клиент на следующей загрузке должен автоматически закрыть сессию временем последней активности, а не временем запуска.
У нас уже есть detect_abnormal_termination в db.py — он закрывает сессию, если прошло больше 12 часов. Можно усовершенствовать:
НЕ по текущему времени, а по времени последней записи в этой сессии.
Порог не 12 часов, а, скажем, 30 минут без активности ? сессия автоматически закрывается временем последней активности.
Тогда:
Сотрудник ушёл на ночь, забыл нажать «Конец работы».
В 19:00 — последняя активность.
В 19:30 клиент сам закрывает сессию с session_end = 19:00 (последняя активность).
Помечается abnormal=1 (или новое поле auto_closed=1).
Утром в 09:00 сотрудник нажимает «Начать работу» ? новая сессия.
Это правильное решение.
Также нужна настройка "начало рабочего дня" для группировки. Например, если сотрудник работает ночью с 22:00 до 06:00, и начало рабочего дня = 06:00, то сессия, начавшаяся в 22:00 — должна попасть в рабочий день Д (текущий), а сессия, начавшаяся в 05:00 — тоже в рабочий день Д, но формально это уже следующий календарный день. Тонкий момент, но обычно делают так: если время старта >= начала рабочего дня, то рабочий день = дата старта. Если < начала рабочего дня — рабочий день = дата старта - 1 день.
Пример:
Начало рабочего дня = 06:00.
Сессия 17.09 22:00 ? рабочий день = 17.09.
Сессия 18.09 02:00 ? рабочий день = 17.09 (потому что 02:00 < 06:00).
Сессия 18.09 08:00 ? рабочий день = 18.09.
Это правильная логика.
Хорошо. Теперь что реализовать:
В web_admin добавить:
Настройку workday_start_hour: int = 6 в settings (config.py).
В форме отчёта — селектор начала рабочего дня (0–23).
В группировке «дни ? сотрудник» использовать эту настройку.
В отчёте: атрибуция клавиатуры/мыши по активной программе.
В отчёте: колонка 1C ID.
Опция «Учитывать простой» — считать эффективное время как сумму активных интервалов (5 сек за каждое activity) или как session_end - session_start.
В клиенте:
Авто-закрытие сессии по бездействию (30 мин без активности).
session_end = время последней активности, а не текущее время.
Это большая задача. Давайте разобью на несколько итераций:
Итерация 1 (сейчас):
1C ID в отчёт
Атрибуция клавы/мыши по программам
Настройка начала рабочего дня
Логика закрытия сессии по бездействию на сервере + клиенте
Итерация 2:
Авто-закрытие сессий на сервере (если клиент пропал)
Более умные фильтры
Хорошо, отвечу на вопросы сначала текстом (анализ + рекомендации), потом код.
По объёму — это большой файл web_admin.py снова. Надо решить, что менять минимально.
Что нужно менять:
config.py — добавить workday_start_hour: int = 6, idle_threshold_minutes: int = 30
web_admin.py — большая переработка отчётов
reports.html — добавить селектор начала дня
report_result.html — обновить таблицу с 1C ID и программами
Дам всё через PowerShell-скрипты.
Про клиент тоже надо подумать. Но сначала — анализ.
Ключевые вопросы пользователя:
1C ID в отчёт — легко.
Мышь/клавиатура к программам — легко на сервере (пересечь timeline).
Настройка начала рабочего дня — легко.
Что делать с 24/7 компом — здесь 2 подхода:
На сервере считать "эффективное время" — только активные интервалы.
На клиенте авто-закрывать сессию.
Дам оба. Плюс объясню, что лучший подход — гибрид.
Хорошо, теперь напишу большой ответ. Сначала — анализ и рекомендации, потом код.
Структура ответа:
Анализ и рекомендации (текст)
План изменений
Скрипт 1 — config.py + db.py патчи
Скрипт 2 — web_admin.py
Скрипт 3 — шаблоны
Постараюсь быть компактным, но не в ущерб полноте.
Про алгоритм атрибуции клавы/мыши по программам:
text
records sorted by client_ts:
  window A at 10:00:00
  activity keys=3 at 10:00:05
  activity keys=5 at 10:00:10
  window B at 10:00:12
  activity keys=2 at 10:00:15
  
При обработке:
  current_window = None
  for r in records:
    if kind == "window":
      current_window = r.app
    elif kind == "activity":
      if current_window and keys>0: app_totals[current_window].keyboard += 5
      if current_window and (clicks+scroll)>0: app_totals[current_window].mouse += 5
Так у каждой программы будет своя клавиатура и мышь.
А в основном отчёте "клавиатура" = сумма по всем программам. Или вообще убрать из основного отчёта (как просит пользователь) и показывать только в детализации по программам.
Пользователь говорит: "Нужно это убрать из основного отчёта и привязать к программе". То есть в основной таблице не показывать клавиатуру/мышь отдельно. Показывать их только внутри "Топ программ" или в детализации.
Хорошо, сделаю так:
Основная таблица: день, сотрудник, 1C ID, сессий, длительность, топ-программа, аварийных.
В детализации (при expand_details): под строками — список программ с клавиатурой и мышью.
Или лучше: в топ-программах сразу показывать клавиатуру/мышь по каждой программе.
Сделаю топ-программы с колонками: программа | время | клавиатура | мышь.
Для этого нужно считать keyboard/mouse в разрезе приложений.
Модифицирую _analyze_session:
python
app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
И на выходе получим разбивку по программам с клавиатурой/мышью.
Ок, теперь про рабочее время:
workday_start_hour — от 0 до 23. По умолчанию 0 (полночь), но для ночных смен лучше 6.
Логика:
python
def _workday_date(start_local: datetime, workday_start_hour: int) -> date:
    if start_local.hour < workday_start_hour:
        return (start_local - timedelta(days=1)).date()
    return start_local.date()
Про 24/7 компьютер:
Проблема: сессия может длиться сутками, потому что компьютер не выключается, а сотрудник забыл нажать "Конец работы".
Решение на сервере: при расчёте сессии учитывать только "эффективное время":
Идём по records сессии.
Для каждой пары последовательных activity событий: если разрыв <= MAX_GAP (например 5 мин), добавляем этот интервал к эффективному времени. Иначе — не добавляем.
Опционально: это касается только "автоматически добавленного" времени.
Это уже сделано в _analyze_session — там идёт duration = session_end - session_start. Заменю на эффективное.
Решение на клиенте: автоматически закрывать сессию, если не было активности N минут:
Периодически проверяем last_activity в meta.
Если now - last_activity > idle_threshold_minutes И в сессии что-то есть — закрываем с session_end = last_activity, abnormal_termination = True (или новый флаг auto_closed).
При следующем нажатии "Начать работу" создаётся новая сессия.
Опционально: если пользователь вернулся в течение часа, можно "продолжить" ту же сессию — сложнее, отложим.
Давайте сделаем так:
Порог idle: 30 минут (настраивается).
Если сессия "висит" без активности больше 30 мин — клиент её закрывает сам.
Это решает проблему "компьютер 24/7".
Всё, приступаю к написанию ответа.
Так как ответ большой, и у меня в прошлый раз была проблема с : и -> при копипасте, буду давать через PowerShell here-string.
Начну с анализа и рекомендаций, потом код.
Учту, что web_admin.py уже правился. Перезапишу его целиком в скрипте.
Дам один большой скрипт.
Для лучшей читаемости в ответе, разделю:
Часть 1 — Анализ и рекомендации
Часть 2 — Скрипт: config.py + db.py
Часть 3 — Скрипт: web_admin.py
Часть 4 — Скрипт: шаблоны
Часть 5 — Пересборка
Хм, но у меня ограничение на длину ответа. Попробую уложиться.
На самом деле можно объединить config.py в скрипт вместе с web_admin.py — они оба в server/.
И шаблоны в отдельный скрипт.
Поехали.
Анализ и рекомендации
Разберу все 4 вопроса по порядку — сначала логика, потом код.
________________________________________
1. 1C ID в отчёте
Тривиально — добавляем колонку. Берётся из Employee.external_id.
2. Клавиатура/мышь ? привязать к программам
Как это делается правильно (не меняя клиент):
У нас уже есть два потока записей с таймстемпами:
window — смена активного окна (при смене приложения)
activity — раз в 5 сек: {keys: N, clicks: M, scroll: K}
Алгоритм: идём по записям сессии в хронологическом порядке, помним «текущее окно», и когда встречаем activity — добавляем 5 секунд клавиатуры/мыши именно этому окну.
Так получается детализация: PyCharm — 2 часа, из них клавиатура 40 мин, мышь 15 мин. Топ программ покажем с этими колонками.
В основной таблице отчёта колонки «Клавиатура» и «Мышь» убираем — остаётся только «Длительность» и «Топ программ». А клавиатура/мышь живут внутри детализации программы.
3. Настройка начала рабочего дня
Зачем нужно: если сотрудник работает ночью 22:00–06:00, куда отнести сессию? К сегодняшнему дню или вчерашнему?
Логика (стандартная для Toggl, Clockify, Jira):
text
Если время старта < начала рабочего дня ? рабочий день = вчера
Иначе ? рабочий день = дата старта
Пример при workday_start = 06:00:
Старт сессии	Рабочий день
17.09 22:00	17.09
18.09 02:00	17.09 (ещё «вчерашняя» смена)
18.09 08:00	18.09
Настройку вынесем в config.py + на страницу отчёта добавлю селектор.
4. Компьютер работает 24/7 — как понять, начал ли сотрудник работать?
Проблема: сотрудник забыл нажать «Конец работы». Сессия тянется сутками. В отчёте видим «12 часов», хотя человек ушёл через 2.
Правильное решение — двухуровневое:
Уровень A. Клиент сам закрывает «висящие» сессии
Раз в минуту проверяем: если с последней активности прошло больше 30 минут — сессия закрывается автоматически.
session_end ставится не «сейчас», а = время последней активности.
Флаг abnormal_termination = 1 (или новый auto_closed = 1).
Это решает 90% случаев: человек ушёл домой, забыл нажать кнопку — сессия через 30 минут закроется сама, причём временем реального ухода.
Уровень B. Сервер считает «эффективное время»
Даже если по какой-то причине сессия всё-таки растянулась — сервер не берёт session_end - session_start слепо. Он идёт по записям и суммирует:
промежутки, где были activity-события

окна активности (смена окон)
Разрывы больше 5 минут не считаются. Это автоматически отсекает «мёртвые» часы, когда комп работал, а человек спал.
Что это даёт:
«Сотрудник отработал 8 часов» — реально 8 часов активности, а не 24 «компьютер включён».
Если сотрудник ушёл в 18:00 и забыл нажать «Конец», утром увидим «8:00, авто-закрыто в 18:00».
План: реализуем оба уровня. Уровень A — в клиенте, уровень B — в отчётах.
________________________________________
Реализация
Что меняем
Сервер:
config.py — новые настройки workday_start_hour, idle_close_minutes
web_admin.py — новая логика отчётов (1C ID, программы с клавой/мышью, рабочее время, эффективное время)
reports.html, report_result.html — обновлённые шаблоны
Клиент:
db.py — метод auto_close_idle_session()
main.py — таймер, который периодически проверяет и закрывает «висящие» сессии
________________________________________
Скрипт 1 — сервер: config.py + web_admin.py
Скопируйте весь блок в PowerShell, Enter.
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

# ============================================================
# config.py
# ============================================================
$config_py = @'
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

_PLACEHOLDERS = {"", "CHANGE_ME", "CHANGE_ME_JWT", "CHANGE_ME_32_BYTE_BASE64_KEY"}


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://tracker:tracker@db:5432/tracker"
    secret_encryption_key: str = ""
    jwt_secret: str = ""
    admin_api_key: str = ""

    # --- Веб-интерфейс администратора ---
    admin_login: str = "admin"
    session_secret: str = ""
    web_secure_cookie: bool = False

    # --- Отчёты ---
    report_timezone: str = "Europe/Moscow"
    # Во сколько начинается рабочий день (0-23). Сессии, начавшиеся до этого часа,
    # относятся к предыдущему рабочему дню (полезно для ночных смен).
    workday_start_hour: int = 6
    # Сколько минут без активности — порог для авто-закрытия висящей сессии
    idle_close_minutes: int = 30
    # Максимальный разрыв между событиями активности, который считается «работой»
    # (в минутах). Всё что больше — считается простоем и не учитывается.
    activity_gap_minutes: int = 5

    class Config:
        env_file = ".env"


settings = Settings()


def _fail(name: str, hint: str):
    raise RuntimeError(f"{name} не задан или placeholder.\n{hint}")


if settings.secret_encryption_key in _PLACEHOLDERS:
    _fail(
        "SECRET_ENCRYPTION_KEY",
        'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"',
    )

if settings.jwt_secret in _PLACEHOLDERS:
    _fail(
        "JWT_SECRET",
        'python -c "import secrets; print(secrets.token_urlsafe(48))"',
    )

if settings.admin_api_key in _PLACEHOLDERS:
    _fail(
        "ADMIN_API_KEY",
        'python -c "import secrets; print(secrets.token_urlsafe(48))"',
    )

try:
    FERNET = Fernet(settings.secret_encryption_key.encode())
except Exception as e:
    raise RuntimeError(f"SECRET_ENCRYPTION_KEY некорректен: {e}") from e
'@
[System.IO.File]::WriteAllText("$serverDir\config.py", $config_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  config.py" -ForegroundColor Green

# ============================================================
# web_admin.py
# ============================================================
$web_admin_py = @'
"""
Веб-интерфейс администратора для проекта «Трекер».
"""
import csv
import hashlib
import io
import json
import secrets
from collections import defaultdict
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import (
    AuditLog, BootstrapToken, Computer, Employee, Record, WorkSession,
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="server/templates")


# ============================================================
# Утилиты
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_admin(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=401, detail="not authenticated")
    return request.session["admin"]


def _now():
    return datetime.now(timezone.utc)


def _hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def _resolve_tz(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, KeyError):
        try:
            return ZoneInfo(settings.report_timezone)
        except Exception:
            return ZoneInfo("UTC")


def _to_local(dt, tz: ZoneInfo):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz)


def _fmt_dur(seconds: int) -> str:
    if not seconds:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_dt_global(dt):
    if dt is None:
        return "—"
    try:
        tz = ZoneInfo(settings.report_timezone)
    except Exception:
        tz = ZoneInfo("UTC")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime("%d.%m.%Y %H:%M")


templates.env.filters["dur"] = _fmt_dur
templates.env.filters["dt"] = _fmt_dt_global


def _available_timezones():
    return [
        ("Europe/Moscow", "Москва (UTC+3)"),
        ("Europe/Kaliningrad", "Калининград (UTC+2)"),
        ("Asia/Yekaterinburg", "Екатеринбург (UTC+5)"),
        ("Asia/Novosibirsk", "Новосибирск (UTC+7)"),
        ("Asia/Krasnoyarsk", "Красноярск (UTC+7)"),
        ("Asia/Irkutsk", "Иркутск (UTC+8)"),
        ("Asia/Vladivostok", "Владивосток (UTC+10)"),
        ("UTC", "UTC"),
    ]


def _workday_date(start_local: datetime, workday_start_hour: int) -> date:
    """
    Возвращает дату «рабочего дня» для сессии.
    Если сессия началась до workday_start_hour — относится к предыдущему дню.
    """
    if start_local.hour < workday_start_hour:
        return (start_local - timedelta(days=1)).date()
    return start_local.date()


# ============================================================
# Логин / логаут
# ============================================================

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("admin"):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    ok_user = secrets.compare_digest(username, settings.admin_login)
    ok_pass = secrets.compare_digest(password, settings.admin_api_key)
    if ok_user and ok_pass:
        request.session["admin"] = username
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Неверный логин или ключ"},
        status_code=401,
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


# ============================================================
# Дашборд
# ============================================================

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    today_local = datetime.now(tz).date()
    today_start_local = datetime.combine(today_local, time.min, tzinfo=tz)
    today_start_utc = today_start_local.astimezone(timezone.utc)
    week_ago_utc = today_start_utc - timedelta(days=7)

    stats = {
        "employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "computers": db.query(Computer).filter(Computer.is_active == True).count(),
        "sessions_today": db.query(WorkSession).filter(
            WorkSession.session_start >= today_start_utc).count(),
        "sessions_week": db.query(WorkSession).filter(
            WorkSession.session_start >= week_ago_utc).count(),
        "records": db.query(Record).count(),
        "tokens_active": db.query(BootstrapToken).filter(
            BootstrapToken.used_at.is_(None),
            BootstrapToken.expires_at > _now(),
        ).count(),
    }

    recent_computers = (
        db.query(Computer).order_by(desc(Computer.registered_at)).limit(10).all()
    )
    recent_audit = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_computers": recent_computers,
        "recent_audit": recent_audit,
        "admin": request.session.get("admin"),
        "tz": tz,
    })


# ============================================================
# Сотрудники
# ============================================================

@router.get("/employees", response_class=HTMLResponse)
def employees_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).order_by(Employee.last_name, Employee.first_name).all()
    return templates.TemplateResponse("employees.html", {
        "request": request, "employees": employees, "admin": request.session.get("admin"),
    })


@router.post("/employees/create")
def employee_create(
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(""),
    external_id: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    last_name = last_name.strip()
    first_name = first_name.strip()
    middle_name = middle_name.strip()
    external_id = external_id.strip()

    if not last_name or not first_name:
        raise HTTPException(400, "Фамилия и имя обязательны")

    full_name = " ".join(x for x in [last_name, first_name, middle_name] if x)
    emp = Employee(
        full_name=full_name,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name or None,
        external_id=external_id or None,
    )
    db.add(emp)
    db.flush()
    db.add(AuditLog(
        actor="admin", entity="employee", entity_id=str(emp.id),
        action="create", new_value=json.dumps({"full_name": full_name}, ensure_ascii=False),
    ))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/edit")
def employee_edit(
    emp_id: int,
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(""),
    external_id: str = Form(""),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    emp = db.query(Employee).get(emp_id)
    if not emp:
        raise HTTPException(404)
    old = emp.full_name
    emp.last_name = last_name.strip()
    emp.first_name = first_name.strip()
    emp.middle_name = middle_name.strip() or None
    emp.external_id = external_id.strip() or None
    emp.full_name = " ".join(x for x in [emp.last_name, emp.first_name, emp.middle_name] if x)
    db.add(AuditLog(
        actor="admin", entity="employee", entity_id=str(emp_id), action="edit",
        old_value=old, new_value=emp.full_name,
    ))
    db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/deactivate")
def employee_deactivate(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.is_active = False
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="deactivate"))
        db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


@router.post("/employees/{emp_id}/activate")
def employee_activate(emp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    emp = db.query(Employee).get(emp_id)
    if emp:
        emp.is_active = True
        db.add(AuditLog(actor="admin", entity="employee", entity_id=str(emp_id), action="activate"))
        db.commit()
    return RedirectResponse("/admin/employees", status_code=303)


# ============================================================
# Компьютеры
# ============================================================

@router.get("/computers", response_class=HTMLResponse)
def computers_list(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    tz = _resolve_tz(settings.report_timezone)
    computers = db.query(Computer).order_by(desc(Computer.last_seen_at)).all()
    employees = db.query(Employee).filter(Employee.is_active == True).order_by(Employee.last_name).all()
    return templates.TemplateResponse("computers.html", {
        "request": request, "computers": computers, "employees": employees,
        "admin": request.session.get("admin"), "tz": tz,
    })


@router.post("/computers/{comp_id}/assign")
def computer_assign(
    comp_id: int,
    employee_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    comp = db.query(Computer).get(comp_id)
    if not comp:
        raise HTTPException(404)

    emp_id = int(employee_id) if employee_id else None
    old = comp.employee_id
    comp.employee_id = emp_id
    comp.assigned_at = _now()

    db.add(AuditLog(
        actor="admin", entity="computer", entity_id=str(comp_id), action="assign",
        old_value=str(old), new_value=str(emp_id),
    ))
    db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


@router.post("/computers/{comp_id}/revoke")
def computer_revoke(comp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    comp = db.query(Computer).get(comp_id)
    if comp:
        comp.is_active = False
        db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id), action="revoke"))
        db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


@router.post("/computers/{comp_id}/activate")
def computer_activate(comp_id: int, db: Session = Depends(get_db), _=Depends(current_admin)):
    comp = db.query(Computer).get(comp_id)
    if comp:
        comp.is_active = True
        db.add(AuditLog(actor="admin", entity="computer", entity_id=str(comp_id), action="activate"))
        db.commit()
    return RedirectResponse("/admin/computers", status_code=303)


# ============================================================
# Bootstrap-токены
