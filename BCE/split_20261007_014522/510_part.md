<!-- Часть 510 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ PDF-рендер отчёта](509_PDF_render_otcheta.md) | [Оглавление](00_BCE_INDEX.md) | [Создать папку ▶](511_Sozdat_papku.md)

---

# ============================================================

def _pdf_table_data(report, styles):
    group_by = report["group_by"]
    rows_data = []

    def cell(text, center=False):
        return Paragraph(str(text if text is not None else ""),
                         styles["cell_center" if center else "cell"])

    if group_by == "days":
        headers = ["Рабочий день", "Сотрудник", "1C ID", "Отдел",
                   "Сессий", "Отработано", "Эффективно"]
        for r in report["rows"]:
            d = r.get("date")
            d_str = d.strftime("%d.%m.%Y") if d else "—"
            if r.get("day_type") == "weekend":
                d_str += " (вых)"
            elif r.get("day_type") == "holiday":
                d_str += " (празд.)"
            rows_data.append([
                cell(d_str),
                cell(r.get("employee_name") or ""),
                cell(r.get("external_id") or "—"),
                cell(r.get("department_name") or "—"),
                cell(r.get("sessions_count", 0), True),
                cell(_fmt_dur(r.get("worked_duration", 0)), True),
                cell(_fmt_dur(r.get("effective_duration", 0)), True),
            ])
    elif group_by == "months":
        headers = ["Месяц", "Сотрудник", "1C ID", "Отдел",
                   "Дней", "Отработано", "Эффективно"]
        for r in report["rows"]:
            rows_data.append([
                cell(f"{r.get('month_name','')} {r.get('year','')}"),
                cell(r.get("employee_name") or ""),
                cell(r.get("external_id") or "—"),
                cell(r.get("department_name") or "—"),
                cell(r.get("days_count", 0), True),
                cell(_fmt_dur(r.get("worked_duration", 0)), True),
                cell(_fmt_dur(r.get("effective_duration", 0)), True),
            ])
    elif group_by == "employees":
        headers = ["Сотрудник", "1C ID", "Отдел", "Дней", "Сессий",
                   "Отработано", "Эффективно"]
        for r in report["rows"]:
            rows_data.append([
                cell(r.get("employee_name") or ""),
                cell(r.get("external_id") or "—"),
                cell(r.get("department_name") or "—"),
                cell(r.get("days_count", 0), True),
                cell(r.get("sessions_count", 0), True),
                cell(_fmt_dur(r.get("worked_duration", 0)), True),
                cell(_fmt_dur(r.get("effective_duration", 0)), True),
            ])
    elif group_by == "departments":
        headers = ["Отдел", "Сотрудников", "Дней", "Отработано", "Эффективно"]
        for r in report["rows"]:
            rows_data.append([
                cell(r.get("department_name") or ""),
                cell(r.get("employees_count", 0), True),
                cell(r.get("days_count", 0), True),
                cell(_fmt_dur(r.get("worked_duration", 0)), True),
                cell(_fmt_dur(r.get("effective_duration", 0)), True),
            ])
    elif group_by == "computers":
        headers = ["Компьютер", "Дней", "Сессий", "Отработано", "Эффективно"]
        for r in report["rows"]:
            rows_data.append([
                cell(r.get("computer_name") or ""),
                cell(r.get("days_count", 0), True),
                cell(r.get("sessions_count", 0), True),
                cell(_fmt_dur(r.get("worked_duration", 0)), True),
                cell(_fmt_dur(r.get("effective_duration", 0)), True),
            ])
    else:  # sessions
        headers = ["Рабочий день", "Сотрудник", "1C ID", "Компьютер",
                   "Начало", "Конец", "Отработано", "Эффективно"]
        for r in report["rows"]:
            d = r.get("date")
            sl = r.get("start_local")
            el = r.get("end_local")
            rows_data.append([
                cell(d.strftime("%d.%m.%Y") if d else ""),
                cell(r.get("employee_name") or ""),
                cell(r.get("external_id") or "—"),
                cell(r.get("computer_name") or ""),
                cell(sl.strftime("%H:%M:%S") if sl else ""),
                cell(el.strftime("%H:%M:%S") if el else ""),
                cell(_fmt_dur(r.get("worked_duration", 0)), True),
                cell(_fmt_dur(r.get("effective_duration", 0)), True),
            ])

    return headers, rows_data


def _render_pdf(report: dict, date_from: str, date_to: str):
    import io as _io
    import os as _os
    import traceback as _tb

    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors as _c
        from reportlab.lib.units import mm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer)
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        FONT_REGULAR = "DejaVuSans"
        FONT_BOLD = "DejaVuSans-Bold"

        base_dir = "/app/server/fonts"
        regular_path = _os.path.join(base_dir, "DejaVuSans.ttf")
        bold_path = _os.path.join(base_dir, "DejaVuSans-Bold.ttf")

        if not _os.path.exists(regular_path):
            raise RuntimeError(f"Шрифт не найден: {regular_path}")

        pdfmetrics.registerFont(TTFont(FONT_REGULAR, regular_path))
        if _os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont(FONT_BOLD, bold_path))
        else:
            FONT_BOLD = FONT_REGULAR

        buf = _io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=landscape(A4),
            leftMargin=10 * mm, rightMargin=10 * mm,
            topMargin=10 * mm, bottomMargin=10 * mm,
        )

        styles = {
            "title": ParagraphStyle("title", fontName=FONT_BOLD, fontSize=14,
                                    spaceAfter=4),
            "subtitle": ParagraphStyle("subtitle", fontName=FONT_REGULAR, fontSize=9,
                                       textColor=_c.grey, spaceAfter=10, leading=12),
            "cell": ParagraphStyle("cell", fontName=FONT_REGULAR, fontSize=8,
                                   leading=10),
            "cell_center": ParagraphStyle("cell_center", fontName=FONT_REGULAR,
                                          fontSize=8, leading=10),
        }

        elements = []
        elements.append(Paragraph("Отчёт по учёту рабочего времени", styles["title"]))

        group_label = {
            "days": "Рабочие дни ? Сотрудник",
            "months": "Месяц ? Сотрудник",
            "employees": "По сотрудникам",
            "departments": "По отделам",
            "computers": "По компьютерам",
            "sessions": "Детально — каждая сессия",
        }.get(report.get("group_by"), str(report.get("group_by")))

        d_from = report["date_from"]
        d_to = report["date_to"]
        sub = "Период: {} - {} | Группировка: {} | TZ: {}".format(
            d_from.strftime("%d.%m.%Y"),
            d_to.strftime("%d.%m.%Y"),
            group_label,
            report.get("tz_name", ""),
        )
        elements.append(Paragraph(sub, styles["subtitle"]))

        t = report["totals"]
        summary_data = [
            ["Сессий", "Отработано", "Эффективно", "Аварийных"],
            [str(t.get("sessions", 0)),
             _fmt_dur(t.get("worked_duration", 0)),
             _fmt_dur(t.get("effective_duration", 0)),
             str(t.get("abnormal", 0))],
        ]
        summary_table = Table(summary_data, colWidths=[40 * mm] * 4)
        summary_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), FONT_REGULAR),
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("BACKGROUND", (0, 0), (-1, 0), _c.HexColor("#343A40")),
            ("TEXTCOLOR", (0, 0), (-1, 0), _c.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.3, _c.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 6 * mm))

        headers, rows = _pdf_table_data(report, styles)
        data = [headers] + rows

        n_cols = len(headers)
        available = 277 * mm
        col_widths = [available / n_cols] * n_cols

        t2 = Table(data, colWidths=col_widths, repeatRows=1)
        style_cmds = [
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
            ("BACKGROUND", (0, 0), (-1, 0), _c.HexColor("#343A40")),
            ("TEXTCOLOR", (0, 0), (-1, 0), _c.white),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, _c.lightgrey),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_c.white, _c.HexColor("#f8f9fa")]),
        ]

        if report.get("group_by") == "days":
            for i, r in enumerate(report["rows"], start=1):
                dt = r.get("day_type")
                if dt == "weekend":
                    style_cmds.append(("BACKGROUND", (0, i), (0, i),
                                       _c.HexColor("#fff3cd")))
                elif dt == "holiday":
                    style_cmds.append(("BACKGROUND", (0, i), (0, i),
                                       _c.HexColor("#f8d7da")))

        t2.setStyle(TableStyle(style_cmds))
        elements.append(t2)

        elements.append(Spacer(1, 4 * mm))
        from datetime import datetime as _dt
        elements.append(Paragraph(
            "Сформировано: " + _dt.now().strftime("%d.%m.%Y %H:%M"),
            styles["subtitle"],
        ))

        doc.build(elements)
        buf.seek(0)

    except Exception as e:
        log.exception("PDF render failed")
        raise HTTPException(
            status_code=500,
            detail="PDF render failed: " + str(e),
        )

    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition":
                 "attachment; filename=report_{}_{}.pdf".format(date_from, date_to)},
    )
'@

[System.IO.File]::WriteAllText($mainPath, $head + $pdfBlock, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  _render_pdf заменён на защищённую версию" -ForegroundColor Green

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Шаг 3 — пересборка и попытка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

Write-Host "--- Переходим в браузер, открывайте /admin/reports и формируйте PDF ---" -ForegroundColor Cyan
Start-Sleep -Seconds 1
Write-Host "Затем ВЫПОЛНИТЕ: docker compose logs api --tail=40" -ForegroundColor Yellow
После попытки сформировать PDF:
powershell
docker compose logs api --tail=40
Теперь при ошибке в логе будет:
text
ERROR tracker.server PDF render failed
Traceback (most recent call last):
  ...
  File "/app/server/web_admin.py", line NNN, in _render_pdf
    ...
Пришлите этот traceback. По конкретной строке сразу скажу, что править.
________________________________________
Что я подозреваю (наиболее вероятное)
from reportlab.lib.enums import TA_LEFT, TA_CENTER — в некоторых сборках reportlab 4.x эти константы могут отсутствовать (переехали). Я убрал этот импорт в новой версии — использовал "CENTER" строкой и без выравнивания для cell/cell_center (они и так наследуют left).
ROWBACKGROUNDS конфликтует с явными BACKGROUND для weekend/holiday в некоторых версиях. Я оставил, но если будет ошибка — уберу.
Кириллица в title= — я убрал title=, чтобы не мучиться с кодировкой PDF metadata.
Если после правки PDF всё ещё падает — пришлите traceback, и я точно скажу, в чём дело.
Traceback clear: NameError: name 'Paragraph' is not defined в _pdf_table_data (строка 1459/1445). Функция _pdf_table_data использует Paragraph и styles, но Paragraph импортируется внутри _render_pdf, а не на уровне модуля. Нужно либо импортировать Paragraph на уровне модуля, либо передавать его в _pdf_table_data.
Проще — добавить импорт Paragraph на уровне модуля web_admin.py.
Но тут есть проблема: на уровне модуля импорт reportlab может упасть, если reportlab не установлен (тогда все эндпоинты админки упадут). Поэтому лучше сделать «отложенный» импорт внутри _pdf_table_data тоже.
Решение: в начале _pdf_table_data добавить from reportlab.platypus import Paragraph.
Даю точечный патч.
Точная причина — NameError: Paragraph
Смотрите трейсбек:
text
File "/app/server/web_admin.py", line 1445, in cell
    return Paragraph(str(text if text is not None else ""),
NameError: name 'Paragraph' is not defined
_pdf_table_data вызывает Paragraph, а импорт from reportlab.platypus import ... Paragraph ... находится внутри _render_pdf — локально для той функции. _pdf_table_data его не видит.
Лечится одной строкой: добавляем импорт в саму _pdf_table_data.
________________________________________
Скрипт — точечный патч
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$old = @'
def _pdf_table_data(report, styles):
    group_by = report["group_by"]
    rows_data = []

    def cell(text, center=False):
        return Paragraph(str(text if text is not None else ""),
                         styles["cell_center" if center else "cell"])
'@

$new = @'
def _pdf_table_data(report, styles):
    from reportlab.platypus import Paragraph as _Paragraph

    group_by = report["group_by"]
    rows_data = []

    def cell(text, center=False):
        return _Paragraph(str(text if text is not None else ""),
                          styles["cell_center" if center else "cell"])
'@

if ($content.Contains($new)) {
    Write-Host "Уже пропатчен — пропускаем" -ForegroundColor Yellow
} elseif ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  Paragraph импортирован в _pdf_table_data" -ForegroundColor Green
} else {
    Write-Host "Не найден блок _pdf_table_data — правьте вручную" -ForegroundColor Red
    Write-Host "Откройте D:\tracker\server\web_admin.py и убедитесь, что в функции _pdf_table_data" -ForegroundColor Yellow
    Write-Host "есть строка 'from reportlab.platypus import Paragraph as _Paragraph' в самом начале." -ForegroundColor Yellow
    exit 1
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Пересборка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

docker compose ps
docker compose logs api --tail=15

Write-Host "`nОткройте https://localhost/admin/reports и сформируйте PDF" -ForegroundColor Green
________________________________________
Проверка
/admin/reports ? период «Этот месяц», группировка «Месяц ? Сотрудник», формат PDF ? «Сформировать»
Скачается report_2026-09-01_2026-09-30.pdf
Откройте — кириллица, таблица, шапка со сводкой, подпись внизу
Также кнопка ?? Скачать PDF на странице «Просмотр» должна работать.
________________________________________
Если снова 500
Пришлите docker compose logs api --tail=40 — теперь в трейсбеке будут уже другие строки, если что-то ещё вылезет. Но конкретно эта ошибка (NameError) теперь устранена.
Давай подведём итоги второго дня. Новое ТЗ Все обновленные коды Полная инструкция что для чего с какой задумкой. Какие проблемы существуют и как они решаются. Что мы сделали из первичного ТЗ Что мы доработали вне ТЗ Проведи глубокий анализ функционала, решений, всего сделанного, того что есть готовое на рынке, такого что мы планируем ещё сделать, и сделай свои выводы что нам ещё нужно сделать и как всё реализовать. Также сделай сводку всего происходящего в этом чате что бы можно было скопировать и вставить в новом чате. сделай подробную инструкцию для внедрения, для администратора этой учетной системы, для кадровика, для обычного сотрудника который будет устанавливать клиентскую часть. Расписывать ответы максимально подробно на русском языке
The user wants a comprehensive summary of everything we've done, a new TZ, all updated code, full instructions, analysis of what's done, what's planned, comparison with market solutions, and detailed instructions for different user roles (admin, HR, employee).
This is a HUGE task. Let me structure it carefully. I need to be thorough but organized.
Let me plan the structure:
Итоги второго дня — краткое резюме
Сводка чата для нового чата — компактный блок для копирования
Новое ТЗ — обновленное ТЗ с учетом всего, что сделали
Глубокий анализ — что готово, что нет, что на рынке, выводы
Инструкции — для админа, кадровика, сотрудника
Все обновленные коды — перечисление файлов с кратким описанием (не весь код — он огромный, но структура)
Так как код огромный, я не могу привести его весь — места не хватит. Лучше дать:
Список файлов
Их назначение
Ключевые моменты
Или дать ссылку на структуру, а код запрашивать по частям.
Хотя пользователь просит "все обновленные коды" — это может быть мега-длинный ответ. Нужно структурировать так, чтобы было полезно, но не превратилось в нечитаемое полотно.
Подойду так:
Сводка структуры проекта
Для каждого файла: назначение + короткое описание ключевых функций
Полные коды дам только для критичных новых файлов (calendar.html, web_admin и т.д.) — но это тоже огромно
Лучше сделать по-другому: перечислить все файлы и сказать "если нужен код — скажите, пришлю целиком". Это честнее и практичнее.
Хотя пользователь конкретно просит "все обновленные коды"... Постараюсь дать максимум но структурированно.
Давайте я сделаю так:
Сводка чата (для нового чата) — компактно
Итоги дня — что сделали
Анализ функционала — что есть, что нет, сравнение с рынком
Новое ТЗ (обновленное) — структура
Все файлы — список с назначением, БЕЗ полного кода (иначе будет 500К символов)
Инструкции по внедрению — для каждой роли
Дорожная карта — что дальше
Начну.
Итоги второго дня разработки проекта «Трекер»
Проект за два дня прошёл путь от «сырой технической заготовки» до работоспособной системы учёта рабочего времени с веб-интерфейсом администратора, отчётами, календарём и клиентом с регистрацией. Ниже — полная сводка всего, что сделано, что осталось, и как этим пользоваться.
________________________________________
ЧАСТЬ 1. СВОДКА ЧАТА (для вставки в новый чат)
text
ПРОЕКТ: Трекер — учёт рабочего времени сотрудников.
Стек: FastAPI + PostgreSQL + Nginx + Docker (сервер), PyQt6 + httpx (клиент).
Расположение: D:\tracker
Админка: https://localhost/admin (логин admin, пароль = ADMIN_API_KEY)
Сервер не на localhost, а на 127.0.0.1 для клиента (Python не умеет IPv6-fallback).

=== ЧТО РЕАЛИЗОВАНО ===

СЕРВЕР:
- Модели: Computer, Employee, Department, WorkSession, Record, BootstrapToken,
  ClientVersion, AuditLog, AppSetting, CalendarDay
- API: /api/v1/computers/register, /sessions, /records/batch, /heartbeat,
  /client-config, /version, /admin/bootstrap-tokens
- HMAC-подпись записей, идемпотентность, защита от race, audit_log
- Веб-интерфейс: /admin (дашборд), /employees, /departments, /computers,
  /tokens, /reports, /settings, /calendar, /audit
- Отчёты: 6 группировок (дни, месяцы, сотрудники, отделы, ПК, сессии),
  мультифильтры с поиском, экспорт HTML/CSV/XLSX/PDF
- Календарь рабочих/нерабочих дней с автозаполнением Сб/Вс
- Настройки в БД (idle-порог, часовой пояс, начало дня, интервал синка и др.)
- Массовая привязка ПК через CSV
- Heartbeat + онлайн/оффлайн статус на дашборде

КЛИЕНТ (PyQt6):
- Диалог регистрации по bootstrap-токену при первом запуске
- Кнопки «Начать работу» / «Конец работы»
- Сбор активности (клавиатура, мышь, активное окно) с edge-triggered окнами
- Авто-закрытие «висящих» сессий по idle-порогу с сервера
- Локальная SQLite (WAL), офлайн-режим, синхронизация раз в 30 сек
- Heartbeat раз в 3 минуты
- Панель: сессия, счётчик, статус сервера, очередь, последняя синхронизация
- Автозапуск через реестр/desktop-файл
- Автообновление (проверка версии на сервере)

=== КЛЮЧЕВЫЕ ФАЙЛЫ ===

СЕРВЕР:
- server/models.py
- server/web_admin.py       (главный файл админки, ~1500 строк)
- server/main.py            (API)
- server/config.py
- server/security.py
- server/schemas.py
- server/database.py
- server/requirements.txt
- server/Dockerfile
- server/nginx.conf
- server/templates/*.html   (11 шаблонов)
- server/fonts/DejaVuSans.ttf  (для PDF)

КЛИЕНТ:
- client/main.py            (главное окно)
- client/registration.py
- client/registration_dialog.py
- client/collector.py
- client/sync.py
- client/db.py
- client/crypto.py
- client/http_client.py
- client/config.py
- client/autostart.py
- client/updater.py
- client/.env
- client/requirements.txt

КОРЕНЬ:
- docker-compose.yml
- .env                      (SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY)
- certs/fullchain.pem, privkey.pem

=== ИЗВЕСТНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ ===
1. localhost в Python ? 127.0.0.1 (IPv6 vs IPv4)
2. create_all не мигрирует схему ? ручной ALTER TABLE
3. records с bad_signature ? poisoned в SQLite, чистка через SQL
4. audit_log.entity_id переполнялся ? кладём только первый UUID
5. Порт 80 занят Windows HTTP.sys ? только 443
6. Русские буквы в PDF ? DejaVuSans.ttf в server/fonts/

=== ЧТО ГОТОВО К ВНЕДРЕНИЮ ===
Система работает end-to-end: клиент на ПК собирает данные, отправляет
на сервер, админ видит отчёты в веб-интерфейсе.

=== ЧТО ОСТАЛОСЬ (приоритеты) ===
P0 (перед выдачей сотрудникам):
- Установщик Inno Setup + PyInstaller-сборка .exe
- Публикация версий клиента через UI для автообновления
- Alembic (миграции БД)
- Бэкап PostgreSQL по расписанию
- Роли пользователей (admin/operator/viewer)

P1 (для полноценной эксплуатации):
- 152-ФЗ: согласие, приказ, уведомление РКН
- Тесты pytest
- Мониторинг (Prometheus/Grafana)
- Просмотр логов клиента в админке
- Экспорт 1С

P2 (развитие):
- Wayland-поддержка (evdev)
- macOS/Linux сборки
- Цифровая подпись .exe
- Партиционирование records при 500+ ПК
________________________________________
ЧАСТЬ 2. НОВОЕ ТЗ (что фактически построили)
1. Назначение
Система «Трекер» — автоматизированный учёт рабочего времени удалённых сотрудников с:
сбором активности на стороне ПК (клавиатура, мышь, активное окно);
передачей данных по HTTPS с HMAC-подписью;
веб-интерфейсом администратора для управления и отчётности;
формированием отчётов в HTML, CSV, XLSX, PDF.
2. Архитектура
text
?????????????????????????????????????????????????????????????????
? ПК СОТРУДНИКА (Windows)                                       ?
?  ????????????????????????                                     ?
?  ? Tracker.exe (PyQt6)  ?                                     ?
?  ?  - collector         ?  HTTPS + HMAC-SHA256                ?
?  ?  - sync worker       ?  ???????????????                    ?
?  ?  - heartbeat         ?                                     ?
?  ?  - local SQLite      ?                                     ?
?  ?  - tray icon         ?                                     ?
?  ????????????????????????                                     ?
?????????????????????????????????????????????????????????????????
                              ?
                              ?
?????????????????????????????????????????????????????????????????
? СЕРВЕР (Docker Compose)                                       ?
?  ??????????????????   ??????????????????   ???????????????? ?
?  ? nginx (443)    ????? FastAPI        ????? PostgreSQL   ? ?
?  ? TLS, proxy     ?   ? /api/v1/*      ?   ? 10 таблиц    ? ?
?  ?                ?   ? /admin/*       ?   ?              ? ?
?  ??????????????????   ??????????????????   ???????????????? ?
?                        ?                                     ?
?                        ?                                     ?
?              ??????????????????????                          ?
?              ? Веб-браузер админа ?                          ?
?              ??????????????????????                          ?
?????????????????????????????????????????????????????????????????
3. Функциональные требования (реализованные)
3.1. Сбор данных на клиенте
Счётчики нажатий клавиатуры (без содержимого)
Клики, скролл мыши
Активное окно: имя приложения + заголовок
Периоды простоя (idle)
Сбор идёт только в течение активной сессии (кнопка «Начать работу»)
3.2. Передача данных
HMAC-SHA256 подпись каждой записи и батча
Bootstrap-токен для регистрации (одноразовый)
Офлайн-буфер в SQLite, синхронизация при появлении связи
Heartbeat раз в 3 минуты
3.3. Серверная обработка
Проверка подписей, идемпотентность по record_uid
Автоматическая привязка сотрудника к сессии по employee_id компьютера
Аудит всех действий администратора
3.4. Веб-интерфейс администратора
Дашборд со статистикой и онлайн-статусом ПК
CRUD сотрудников с отделами, увольнением/восстановлением
CRUD отделов
Управление ПК: привязка, отключение, массовая привязка CSV
Выпуск bootstrap-токенов
Календарь рабочих/нерабочих дней на год с автозаполнением
Настройки приложения (idle-порог, TZ, начало дня, интервал синка)
Отчёты — 6 группировок, мультифильтры с поиском, экспорт 4 формата
Журнал аудита
3.5. Отчётность
Группировки: рабочие дни ? сотрудник, месяц ? сотрудник, по сотрудникам, по отделам, по компьютерам, детально по сессиям
Метрики: отработано (span), эффективно (без пауз), клавиатура, мышь
Разбивка по программам с привязкой к сотрудникам
Подсветка выходных/праздников
Экспорт: HTML (интерактивный), CSV, XLSX, PDF
4. Нефункциональные требования
Windows 10/11 как целевая ОС клиента
Linux Ubuntu 22.04 для сервера (Docker)
До 50 клиентов на один сервер (при большем — партиционирование)
Клиент — менее 80 МБ дистрибутив
Резервное копирование PostgreSQL
________________________________________
ЧАСТЬ 3. ГЛУБОКИЙ АНАЛИЗ
3.1. Что готово полностью
Компонент	Состояние
Регистрация ПК по bootstrap-токену	? работает
HMAC-подпись и защита от подмены	? работает
Офлайн-режим с буфером	? работает
Сессии с кнопками старт/стоп	? работает
Авто-закрытие «висящих» сессий	? работает
Heartbeat + онлайн-статус	? работает
Веб-интерфейс админа	? 11 страниц
Отчёты (6 группировок)	? работает
Мультифильтры с поиском	? работает
Экспорт CSV/XLSX/PDF/HTML	? работает
Календарь рабочих дней	? работает
Массовая привязка CSV	? работает
Аудит действий	? работает
3.2. Что готово частично
Компонент	Что не хватает
Автообновление клиента	Опубликование версий только через SQL
Роли пользователей	Только один admin
Логи клиента	Видны только локально на ПК
1С-интеграция	Поле есть, механизма нет
Миграции БД	Только ручной ALTER TABLE
Резервное копирование	Только вручную
3.3. Что не начато
Компонент	Приоритет
Установщик .exe	P0
Alembic	P0
152-ФЗ (юридическое)	P0
Тесты	P1
Мониторинг	P1
Wayland-поддержка	P2
macOS/Linux-сборки	P2
Цифровая подпись .exe	P2
3.4. Сравнение с рынком
Аналоги:
Продукт	Что есть	Стоимость
Hubstaff	Скриншоты, GPS, интеграции, team management	$7-10/чел/мес
Toggl Track	Простой тайм-трекер, отчёты, интеграции	$9/чел/мес
Clockify	Бесплатный, без скриншотов	Free / $4/чел/мес
DeskTime	Скриншоты, приложения, продуктивность	$7/чел/мес
StaffCop	DLP + мониторинг, ФСТЭК	от 1500 ?/чел
Стахановец	Учёт времени, скриншоты, ФЗ-152	от 200 ?/чел/мес
Наши преимущества:
Полный контроль над данными (у нас в БД, не у вендора)
Нет абонентской платы
Простая архитектура, легко развивать
Соблюдение 152-ФЗ при правильной настройке
Наши недостатки:
Нет скриншотов (и не планируется — по ТЗ их и не должно быть)
Нет GPS-трекинга (не нужен для офисных ПК)
Нет мобильного приложения
Нет интеграций с другими сервисами (Jira, Trello и т.п.)
Интерфейс минималистичный
Вывод: для небольшой компании до 50 человек с собственным сервером наша система эффективнее и дешевле коммерческих аналогов. Для 500+ сотрудников проще взять готовое решение.
3.5. Что можно улучшить в текущей архитектуре
Серьёзные пробелы:
Нет миграций (Alembic). Каждое изменение модели требует ручного ALTER. Это критично на проде. Решение: подключить Alembic, накатить начальную миграцию, дальше — только через alembic upgrade head.
Один администратор. ADMIN_API_KEY — единый на всех. Нет разделения на роли (admin/operator/viewer). Нет истории входов. Решение: таблица admin_users с паролями (bcrypt), роли, страница управления.
Нет установщика. Сотрудник не сможет сам поставить клиент — нужна консоль и venv. Решение: PyInstaller + Inno Setup, скрипт сборки, .exe-инсталлятор с полем для токена.
Логи клиента — только локально. Если что-то падает у сотрудника — админ не видит. Решение: эндпоинт /api/v1/client-log, клиент отправляет последние N строк при ошибках.
Нет heartbeat-истории. last_seen_at — одна точка. Решение: таблица computer_heartbeats с историей, график доступности.
Нет алертов. Если ПК молчит 2 часа — админ не узнает. Решение: APScheduler-задача, проверка раз в 10 минут, уведомление в Telegram.
SQLite не шифруется. Локальный админ ПК прочитает. Решение: SQLCipher (сложно) или хотя бы файловая система с шифрованием BitLocker.
Секрет клиента не ротируется. Если утёк — только revoke + перерегистрация. Решение: эндпоинт rotate-secret, клиент сам забирает новый.
Нет rate-limiting. API можно ддосить. Решение: slowapi в FastAPI или nginx-модуль.
Партиционирование records. При 500+ ПК таблица раздуется. Решение: партиции по месяцам (PostgreSQL native partitioning).
3.6. Что я рекомендую сделать в следующие 2-3 дня
День 3:
Установщик .exe (Inno Setup + build.bat)
Alembic (миграции)
Публикация версий клиента через UI
День 4:
Роли пользователей (admin_users)
Просмотр логов клиента в админке
Бэкап PostgreSQL по cron
День 5:
Алерты (Telegram / Email)
Тесты (pytest на критичные пути)
Документация для сдачи проекта
________________________________________
ЧАСТЬ 4. ВСЕ ОБНОВЛЕННЫЕ КОДЫ (список файлов)
Полные коды файлов — отдельные большие блоки, каждый можно запросить у меня. Ниже — структура и назначение.
4.1. Сервер
Файл	Назначение
server/main.py	FastAPI-приложение: регистрация, сессии, записи, heartbeat, версия
server/web_admin.py	Веб-интерфейс админа (~1500 строк): все страницы, отчёты, PDF
server/models.py	ORM-модели: Computer, Employee, Department, WorkSession, Record, BootstrapToken, ClientVersion, AuditLog, AppSetting, CalendarDay
server/config.py	Загрузка .env, инициализация Fernet
server/database.py	SQLAlchemy engine, SessionLocal, init_db
server/security.py	HMAC-SHA256, canonical_json, verify
server/schemas.py	Pydantic-схемы запросов/ответов
server/requirements.txt	Зависимости сервера (fastapi, sqlalchemy, jinja2, reportlab, openpyxl, tzdata)
server/Dockerfile	Сборка образа API
server/nginx.conf	Reverse-proxy на 443
server/templates/base.html	Общий шаблон с навигацией
server/templates/login.html	Страница входа
server/templates/dashboard.html	Дашборд с онлайн-статусом
server/templates/employees.html	CRUD сотрудников
server/templates/departments.html	CRUD отделов
server/templates/computers.html	ПК + массовая привязка CSV
server/templates/tokens.html	Выпуск bootstrap-токенов
server/templates/reports.html	Форма отчёта с мультифильтрами
server/templates/report_result.html	Результат отчёта (HTML)
server/templates/settings.html	Настройки приложения
server/templates/calendar.html	Календарь рабочих дней
server/templates/audit.html	Журнал аудита
server/fonts/DejaVuSans.ttf	Шрифт для PDF
4.2. Клиент
Файл	Назначение
client/main.py	Главное окно: кнопки старт/стоп, панель, трей
client/registration.py	Регистрация, keyring, fallback credentials.enc
client/registration_dialog.py	Диалог ввода bootstrap-токена
client/collector.py	Сбор клавиатуры, мыши, активного окна
client/sync.py	Отправка данных + heartbeat + client-config
client/db.py	Локальная SQLite (WAL), метаданные, авто-закрытие сессий
client/crypto.py	HMAC-подпись (идентична серверной)
client/http_client.py	httpx-клиент с pinning
client/config.py	Чтение .env, дефолты, пути
client/autostart.py	Реестр Windows / .desktop Linux
client/updater.py	Проверка версий, скачивание, установка
client/.env	TRACKER_SERVER_URL=https://127.0.0.1

client/requirements.txt	PyQt6, httpx, pynput, keyring и др.
4.3. Корень
Файл	Назначение
docker-compose.yml	Три контейнера: db, api, nginx
.env	SECRET_ENCRYPTION_KEY, JWT_SECRET, ADMIN_API_KEY
certs/fullchain.pem, certs/privkey.pem	TLS-сертификаты
________________________________________
ЧАСТЬ 5. ИНСТРУКЦИИ ПО ВНЕДРЕНИЮ
5.1. Для администратора системы (развёртывание)
Требования к серверу:
Windows 10/11 с Docker Desktop или Linux Ubuntu 22.04
4 ГБ RAM, 20 ГБ диска
Статический IP или домен (для прода)
Шаг 1. Установка Docker Desktop
Скачать с docker.com, установить, перезагрузить ПК.
Шаг 2. Установка проекта
powershell
