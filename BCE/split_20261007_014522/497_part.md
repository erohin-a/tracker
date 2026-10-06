<!-- Часть 497 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Календарь рабочих/нерабочих дней](496_Kalendar_rabochih_nerabochih_dney.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](498_part.md)

---

# ============================================================

def _get_calendar_map(db: Session, year: int) -> dict:
    rows = db.query(CalendarDay).filter(
        CalendarDay.day.like(f"{year:04d}-%")
    ).all()
    return {r.day: r.is_working for r in rows}


def _is_working_day(db: Session, d: date) -> bool:
    row = db.query(CalendarDay).filter(CalendarDay.day == d.isoformat()).first()
    if row is not None:
        return row.is_working
    return d.weekday() < 5


def _day_type(db: Session, d: date) -> str:
    row = db.query(CalendarDay).filter(CalendarDay.day == d.isoformat()).first()
    if row is not None:
        if not row.is_working:
            if d.weekday() >= 5:
                return "weekend"
            return "holiday"
        return "working"
    if d.weekday() >= 5:
        return "weekend"
    return "working"


@router.get("/calendar", response_class=HTMLResponse)
def calendar_page(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    now = datetime.now()
    try:
        year = int(request.query_params.get("year", str(now.year)))
        year = max(2020, min(2100, year))
    except (ValueError, TypeError):
        year = now.year

    cal = _get_calendar_map(db, year)

    months = []
    for m in range(1, 13):
        first = date(year, m, 1)
        if m == 12:
            last = date(year, 12, 31)
        else:
            last = date(year, m + 1, 1) - timedelta(days=1)

        days_in_month = (last - first).days + 1
        start_offset = first.weekday()

        cells = []
        for _ in range(start_offset):
            cells.append(None)
        for day_num in range(1, days_in_month + 1):
            d = date(year, m, day_num)
            iso = d.isoformat()
            is_working = cal.get(iso)
            if is_working is None:
                is_working = d.weekday() < 5
            cells.append({
                "date": d,
                "iso": iso,
                "is_working": is_working,
                "weekday": d.weekday(),
            })
        while len(cells) % 7 != 0:
            cells.append(None)

        weeks = [cells[i:i+7] for i in range(0, len(cells), 7)]

        months.append({
            "num": m,
            "name": RU_MONTHS[m],
            "weeks": weeks,
        })

    total_days = (date(year, 12, 31) - date(year, 1, 1)).days + 1
    working_days = sum(
        1 for i in range(total_days)
        if _is_working_day(db, date(year, 1, 1) + timedelta(days=i))
    )

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "admin": request.session.get("admin"),
        "year": year,
        "months": months,
        "weekday_names": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "working_days": working_days,
        "total_days": total_days,
        "saved": request.query_params.get("saved") == "1",
        "years": list(range(now.year - 2, now.year + 3)),
    })


@router.post("/calendar/save")
async def calendar_save(request: Request,
                        db: Session = Depends(get_db), _=Depends(current_admin)):
    form = await request.form()
    year = int(form.get("year", 0))
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")

    checked_isos = set()
    for k, v in form.multi_items():
        if k.startswith("day_") and k[4:].startswith(f"{year:04d}-"):
            checked_isos.add(k[4:])

    cur_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    while cur_date <= end_date:
        iso = cur_date.isoformat()
        is_working_default = cur_date.weekday() < 5
        is_working_new = iso in checked_isos

        row = db.query(CalendarDay).filter(CalendarDay.day == iso).first()

        if row is None and is_working_new == is_working_default:
            cur_date += timedelta(days=1)
            continue

        if row is None:
            db.add(CalendarDay(day=iso, is_working=is_working_new))
        else:
            row.is_working = is_working_new

        cur_date += timedelta(days=1)

    db.add(AuditLog(actor="admin", entity="calendar", entity_id=str(year),
                    action="save"))
    db.commit()
    return RedirectResponse(f"/admin/calendar?year={year}&saved=1", status_code=303)


@router.post("/calendar/generate")
def calendar_generate(year: int = Form(...), db: Session = Depends(get_db),
                      _=Depends(current_admin)):
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")
    cur = date(year, 1, 1)
    end = date(year, 12, 31)
    while cur <= end:
        iso = cur.isoformat()
        row = db.query(CalendarDay).filter(CalendarDay.day == iso).first()
        is_working = cur.weekday() < 5
        if row is None:
            db.add(CalendarDay(day=iso, is_working=is_working))
        else:
            row.is_working = is_working
        cur += timedelta(days=1)
    db.add(AuditLog(actor="admin", entity="calendar", entity_id=str(year),
                    action="generate"))
    db.commit()
    return RedirectResponse(f"/admin/calendar?year={year}&saved=1", status_code=303)


@router.post("/calendar/reset")
def calendar_reset(year: int = Form(...), db: Session = Depends(get_db),
                   _=Depends(current_admin)):
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")
    db.query(CalendarDay).filter(CalendarDay.day.like(f"{year:04d}-%")).delete(
        synchronize_session=False)
    db.add(AuditLog(actor="admin", entity="calendar", entity_id=str(year),
                    action="reset"))
    db.commit()
    return RedirectResponse(f"/admin/calendar?year={year}&saved=1", status_code=303)
'@

$content = $content.TrimEnd() + $calendarBlock

[System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  календарь дописан в web_admin.py" -ForegroundColor Green

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Проверьте, что уже сделано из прошлых скриптов
Перед тем как продолжать, убедимся, что C1 (модель) и C4 (шаблон calendar.html) прошли.
powershell
Write-Host "--- models.py ---" -ForegroundColor Cyan
Select-String -Path D:\tracker\server\models.py -Pattern "class CalendarDay"

Write-Host "`n--- calendar.html ---" -ForegroundColor Cyan
if (Test-Path D:\tracker\server\templates\calendar.html) {
    "  OK, размер: $((Get-Item D:\tracker\server\templates\calendar.html).Length) байт"
} else {
    Write-Host "  НЕТ ШАБЛОНА" -ForegroundColor Red
}

Write-Host "`n--- base.html ссылка на календарь ---" -ForegroundColor Cyan
Select-String -Path D:\tracker\server\templates\base.html -Pattern "/admin/calendar"

Write-Host "`n--- таблица в БД ---" -ForegroundColor Cyan
cd D:\tracker
docker compose exec -T db psql -U tracker -d tracker -c "\dt calendar_days"
Если чего-то не хватает — доделаем.
________________________________________
Если модель CalendarDay не появилась в models.py
Выполните C1 из прошлого сообщения. Повторяю его отдельно (короткая версия без ошибок PowerShell):
powershell
$ErrorActionPreference = "Stop"
$modelsPath = "D:\tracker\server\models.py"
$content = [System.IO.File]::ReadAllText($modelsPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("class CalendarDay")) {
    Write-Host "Модель уже есть" -ForegroundColor Yellow
} else {
    $addition = @'


class CalendarDay(Base):
    __tablename__ = "calendar_days"

    day = Column(String(10), primary_key=True)
    is_working = Column(Boolean, nullable=False, default=True)
    note = Column(String(255))
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
'@
    $content = $content.TrimEnd() + $addition
    [System.IO.File]::WriteAllText($modelsPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  CalendarDay добавлен" -ForegroundColor Green
}

python -c "import ast; ast.parse(open(r'$modelsPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Если calendar.html не появился
Повторите C4 из прошлого сообщения — там был большой блок с шаблоном.
Если что-то из этого уже сделано — не выполняйте повторно, скрипты проверяют наличие.
________________________________________
Если ссылка на календарь не появилась в base.html
powershell
$ErrorActionPreference = "Stop"
$basePath = "D:\tracker\server\templates\base.html"
$content = [System.IO.File]::ReadAllText($basePath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("/admin/calendar")) {
    Write-Host "Ссылка уже есть" -ForegroundColor Yellow
} else {
    $old = '<a class="nav-link {% if ''/settings'' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>'
    $new = $old + "`n        " + '<a class="nav-link {% if ''/calendar'' in request.url.path %}active{% endif %}" href="/admin/calendar">Календарь</a>'
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($basePath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  ссылка добавлена" -ForegroundColor Green
}
________________________________________
Пересборка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

docker compose ps
docker compose logs api --tail=20

Write-Host "`nОткройте https://127.0.0.1/admin/calendar" -ForegroundColor Green
________________________________________
Если снова будет ошибка в скрипте
Чтобы избежать проблем с кавычками PowerShell (как в этот раз), все скрипты дальше я буду давать в одинарных кавычках для строк — например '@router.get("/calendar")' — это устраняет проблему с \".
Пришлите:
Вывод проверки «что уже сделано из прошлых скриптов»
Результат после пересборки: открывается ли /admin/calendar
Если откроется — сразу идём к PDF-отчёту (Часть 2 подблока C).
Вс открылось работаем дальше
The user has confirmed the calendar is working. Now I need to give them the PDF report - Part 2 of Subblock C.
Let me plan what needs to be done:
PDF generation using reportlab
Font with Cyrillic support (DejaVuSans.ttf already downloaded in C2)
Add "PDF" option to reports form
Add PDF rendering function to web_admin.py
Add "Скачать PDF" button to report_result.html
Let me write scripts carefully, avoiding PowerShell quoting issues that bit us before. I'll use single quotes for strings containing double quotes and be careful with here-strings.
Key components:
PDF generation function using reportlab with cyrillic font
Modify reports form to include PDF option
Modify report_result to have PDF download button
Make sure font file is available in container
The Dockerfile needs to copy the fonts directory. Let me check - the Dockerfile currently does COPY server/ ./server/ which should copy the fonts folder too if it's inside server/.
Wait, in C2 I created $fontsDir = "$serverDir\fonts" = D:\tracker\server\fonts\DejaVuSans.ttf. Since Dockerfile copies entire server/ folder, the fonts will be at /app/server/fonts/DejaVuSans.ttf.
Let me build the PDF generation carefully. I need:
SimpleTable or Table from reportlab.platypus
Paragraph for wrapping
Font registration
Landscape orientation for wide tables
Cyrillic support
Let me structure the PDF generator to handle all the same groupings as HTML/XLSX.
I'll structure the scripts:
Script C9 - add PDF rendering function to web_admin.py (append at end)
Script C10 - update reports.html to add PDF option
Script C11 - update report_result.html to add PDF download button
Script C12 - rebuild and test
For the report_result.html PDF download button, I need a form that submits with current params. Better to pass through URL or make a simple form.
Actually simpler: in report_result.html, add a POST form with all the report params hidden that submits to /reports/generate with fmt=pdf. This preserves the filter state.
Let me write the code.
For reportlab, I need:
python
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
Font path: /app/server/fonts/DejaVuSans.ttf
Need to handle the case where the report is large - A4 landscape should fit 8-10 columns.
Let me write it carefully.
Actually, in the PDF I'll produce a landscape table with these columns for the main data:
Рабочий день / Месяц / Сотрудник / Отдел / Сессий / Отработано / Эффективно
Should handle group_by days/months/employees/departments/computers/sessions.
For each: pick appropriate columns.
Let me be pragmatic and just include the essential columns.
Now let me write the PDF function:
python
def _render_pdf(report, date_from, date_to):
    import os
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, 
                                     Paragraph, Spacer)
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    # Регистрация шрифта
    font_name = 'DejaVu'
    font_path = '/app/server/fonts/DejaVuSans.ttf'
    if not os.path.exists(font_path):
        # Fallback
        for p in ['/app/server/fonts/arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
            if os.path.exists(p):
                font_path = p
                break
    
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    ...
Let me write the full thing.
Actually, I realize I should keep the PDF generation reasonable but not too long. Let me focus on:
Landscape A4
Header with title
Summary table
Main table
Simple styling
Total width available in landscape A4: 297mm - 2*15mm = 267mm.
For days grouping: Рабочий день (25mm), Сотрудник (50mm), 1C ID (25mm), Отдел (40mm), Сессий (18mm), Отработано (30mm), Эффективно (30mm) = 218mm, ok.
Let me write it now, being careful with PowerShell quoting.
I'll use single quotes for strings in PowerShell when they contain double quotes, and use @'...'@ here-strings (literal, no variable interpolation) for the Python code.
Wait, actually the problem was:
powershell
if ($content.Contains("@router.get(\"/calendar\"")) {
This is a double-quoted PowerShell string with escaped \" which doesn't work in PS.
Correct: use single quotes:
powershell
if ($content.Contains('@router.get("/calendar")')) {
Or use here-string:
powershell
if ($content.Contains(@'
@router.get("/calendar")
'@)) {
For safety, I'll use single quotes where possible.
OK let me write the full scripts now.
For the PDF generation, the cleanest approach:
Read data from the report dict that already exists
Build a reportlab flowable
Return StreamingResponse with BytesIO
Let me structure the PDF layout:
Title: "Отчёт: Tracker"
Subtitle: period, TZ, grouping
Summary: sessions, worked, effective, abnormal
Main table with columns based on group_by
Optional: top apps section
Footer: date of generation
Let me write it.
python
def _render_pdf(report: dict, date_from: str, date_to: str):
    import io as _io
    import os as _os
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, 
                                     Paragraph, Spacer)
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    
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
        FONT_BOLD = FONT_REGULAR  # fallback
    
    buf = _io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=12*mm, rightMargin=12*mm,
        topMargin=12*mm, bottomMargin=12*mm,
        title=f"Отчёт {date_from} — {date_to}",
        author="Tracker",
    )
    
    styles = {
        'title': ParagraphStyle('title', fontName=FONT_BOLD, fontSize=14, 
                                alignment=TA_LEFT, spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', fontName=FONT_REGULAR, fontSize=9,
                                   alignment=TA_LEFT, textColor=colors.grey,
                                   spaceAfter=10),
        'cell': ParagraphStyle('cell', fontName=FONT_REGULAR, fontSize=8,
                               alignment=TA_LEFT),
        'cell_center': ParagraphStyle('cell_center', fontName=FONT_REGULAR, fontSize=8,
                                      alignment=TA_CENTER),
        'header': ParagraphStyle('header', fontName=FONT_BOLD, fontSize=8,
                                 alignment=TA_CENTER, textColor=colors.white),
    }
    
    elements = []
    
    # Title
    elements.append(Paragraph("Отчёт по учёту рабочего времени", styles['title']))
    
    group_label = {
        'days': 'Рабочие дни ? Сотрудник',
        'months': 'Месяц ? Сотрудник',
        'employees': 'По сотрудникам',
        'departments': 'По отделам',
        'computers': 'По компьютерам',
        'sessions': 'Детально — каждая сессия',
    }.get(report['group_by'], report['group_by'])
    
    elements.append(Paragraph(
        f"Период: {report['date_from'].strftime('%d.%m.%Y')} — {report['date_to'].strftime('%d.%m.%Y')} "
        f"&nbsp;•&nbsp; Группировка: {group_label} "
        f"&nbsp;•&nbsp; TZ: {report['tz_name']}",
        styles['subtitle']
    ))
    
    # Summary
    t = report['totals']
    summary_data = [
        ['Сессий', 'Отработано', 'Эффективно', 'Аварийных'],
        [str(t['sessions']), _fmt_dur(t['worked_duration']),
         _fmt_dur(t['effective_duration']), str(t['abnormal'])],
    ]
    summary_table = Table(summary_data, colWidths=[35*mm]*4)
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), FONT_REGULAR),
        ('FONTNAME', (0,0), (-1,0), FONT_BOLD),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#343A40')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 6*mm))
    
    # Main table
    # Определяем заголовки и данные в зависимости от группировки
    headers, rows = _pdf_table_data(report, styles)
    
    data = [headers] + rows
    # Равномерно распределяем ширину
    n_cols = len(headers)
    available = 273*mm  # landscape A4 297 - 2*12
    col_widths = [available / n_cols] * n_cols
    
    t2 = Table(data, colWidths=col_widths, repeatRows=1)
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), FONT_BOLD),
        ('FONTNAME', (0,1), (-1,-1), FONT_REGULAR),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#343A40')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    # Подсветка выходных
    if report['group_by'] == 'days':
        for i, r in enumerate(report['rows'], start=1):
            dt = r.get('day_type')
            if dt == 'weekend':
                t2.setStyle(TableStyle([('BACKGROUND', (0,i), (0,i), colors.HexColor('#fff3cd'))]))
            elif dt == 'holiday':
                t2.setStyle(TableStyle([('BACKGROUND', (0,i), (0,i), colors.HexColor('#f8d7da'))]))
    
    elements.append(t2)
    
    # Footer
    elements.append(Spacer(1, 4*mm))
    from datetime import datetime as _dt
    elements.append(Paragraph(
        f"Сформировано: {_dt.now().strftime('%d.%m.%Y %H:%M')}",
        styles['subtitle']
    ))
    
    doc.build(elements)
    buf.seek(0)
    
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.pdf"},
    )


def _pdf_table_data(report, styles):
    """Возвращает (headers, rows) для PDF-таблицы."""
    group_by = report['group_by']
    rows_data = []
    
    def cell(text, center=False):
        return Paragraph(str(text or ''), styles['cell_center' if center else 'cell'])
    
    if group_by == 'days':
        headers = ['Рабочий день', 'Сотрудник', '1C ID', 'Отдел',
                   'Сессий', 'Отработано', 'Эффективно']
        for r in report['rows']:
            d = r['date']
            d_str = d.strftime('%d.%m.%Y')
            if r.get('day_type') == 'weekend':
                d_str += ' (вых)'
            elif r.get('day_type') == 'holiday':
                d_str += ' (празд.)'
            rows_data.append([
                cell(d_str), cell(r['employee_name']),
                cell(r.get('external_id') or '—'), cell(r.get('department_name') or '—'),
                cell(r['sessions_count'], True),
                cell(_fmt_dur(r['worked_duration']), True),
                cell(_fmt_dur(r['effective_duration']), True),
            ])
    elif group_by == 'months':
        headers = ['Месяц', 'Сотрудник', '1C ID', 'Отдел', 'Дней', 'Отработано', 'Эффективно']
        for r in report['rows']:
            rows_data.append([
                cell(f"{r['month_name']} {r['year']}"),
                cell(r['employee_name']), cell(r.get('external_id') or '—'),
                cell(r.get('department_name') or '—'),
                cell(r['days_count'], True),
                cell(_fmt_dur(r['worked_duration']), True),
                cell(_fmt_dur(r['effective_duration']), True),
            ])
    elif group_by == 'employees':
        headers = ['Сотрудник', '1C ID', 'Отдел', 'Дней', 'Сессий', 'Отработано', 'Эффективно']
        for r in report['rows']:
            rows_data.append([
                cell(r['employee_name']), cell(r.get('external_id') or '—'),
                cell(r.get('department_name') or '—'),
                cell(r['days_count'], True), cell(r['sessions_count'], True),
                cell(_fmt_dur(r['worked_duration']), True),
                cell(_fmt_dur(r['effective_duration']), True),
            ])
    elif group_by == 'departments':
        headers = ['Отдел', 'Сотрудников', 'Дней', 'Отработано', 'Эффективно']
        for r in report['rows']:
            rows_data.append([
                cell(r['department_name']),
                cell(r['employees_count'], True),
                cell(r['days_count'], True),
                cell(_fmt_dur(r['worked_duration']), True),
                cell(_fmt_dur(r['effective_duration']), True),
            ])
    elif group_by == 'computers':
        headers = ['Компьютер', 'Дней', 'Сессий', 'Отработано', 'Эффективно']
        for r in report['rows']:
            rows_data.append([
                cell(r['computer_name']),
                cell(r['days_count'], True),
                cell(r['sessions_count'], True),
                cell(_fmt_dur(r['worked_duration']), True),
                cell(_fmt_dur(r['effective_duration']), True),
            ])
    else:  # sessions
        headers = ['Рабочий день', 'Сотрудник', '1C ID', 'Компьютер',
                   'Начало', 'Конец', 'Отработано', 'Эффективно']
        for r in report['rows']:
            rows_data.append([
                cell(r['date'].strftime('%d.%m.%Y')),
                cell(r['employee_name']), cell(r.get('external_id') or '—'),
                cell(r['computer_name']),
                cell(r['start_local'].strftime('%H:%M:%S'), True),
                cell(r['end_local'].strftime('%H:%M:%S'), True),
                cell(_fmt_dur(r['worked_duration']), True),
                cell(_fmt_dur(r['effective_duration']), True),
            ])
    
    return headers, rows_data
Wait, I need to be careful — doc.build() doesn't accept styles for paragraphs from cell as strings, they need to be Paragraph objects. But actually with Table, if you pass strings, reportlab will wrap them in Paragraph automatically only if they're long. Actually no — Table cells accept strings and Paragraphs. If string is too long, it will overflow. So using Paragraph is safer for wrapping.
For TableStyle, adding style dynamically per row is a bit inefficient but works.
OK, I think this is fine. Let me also handle the case when the fonts folder doesn't get copied to the container. Actually the Dockerfile does COPY server/ ./server/ — since fonts are inside server/, they'll be copied. Good.
But wait — I need to check the Dockerfile. Let me add a defensive fix: also add fonts copy explicitly.
Actually just verify at build time. If Dockerfile is:
text
COPY server/ ./server/
then everything in server/ is copied. OK.
Let me now write the scripts. I'll be very careful with PowerShell quoting.
For appending to web_admin.py, I'll use single-quoted here-string:
powershell
$pdfBlock = @'
...python code...
'@
That's literal, no interpolation. Good.
Let me finalize.
One issue: in the PDF generation code I have f"Отчёт {date_from} — {date_to}" with — em-dash. That's fine in UTF-8.
Let me also verify that Paragraph handles the &nbsp; — yes, reportlab supports basic HTML entities.
Wait, actually &nbsp; may not be supported by reportlab. Let me use &amp;nbsp; — no. Let me just use plain spaces or | separators.
Actually reportlab supports &nbsp; as HTML entity. Let me test... actually to be safe, let me just use regular spaces or |.
Let me use · (middle dot with spaces) as separator, that's Cyrillic-safe.
OK let me finalize the scripts now.
One more thing — in reports_generate, I need to add:
python
if fmt == "pdf":
    return _render_pdf(report, date_from, date_to)
And in reports.html, add:
html
<option value="pdf">PDF</option>
And in report_result.html, add a button that submits with fmt=pdf.
For the button in report_result.html, I need to know what filters were used. But the template doesn't have access to them currently. Two options:
Pass them from Python
Store in session
Simpler: pass from Python via context. Let me add to context:
python
"filter_employee_ids": employee_ids,
"filter_department_ids": department_ids,
"filter_computer_ids": computer_ids,
Then in template, render a form with hidden inputs.
Actually simpler still: add a query param to the URL. Let me change reports_generate to redirect if fmt=xlsx/csv/pdf... no that's complicated.
Cleanest: pass filters to context.
Let me finalize. I'll pass:
filters: dict with employee_ids, department_ids, computer_ids, date_from, date_to, group_by
Then template builds a hidden form.
Actually I realize the current template already has report object that has date_from, date_to, group_by. But not employee_ids etc. Let me just add them.
OK let me write it all now.
Let me also handle the error if fonts missing — the endpoint should return 500 with clear message. Actually better: return a friendly error.
Actually — maybe I should just check upfront and if font not found, use default Helvetica (will show squares for Cyrillic). Better to raise clear error.
Let me write it.
I'll structure my response:
Short intro
Script C9: append PDF generation to web_admin.py
Script C10: modify reports_generate to handle fmt=pdf + pass filter params to context
Script C11: update reports.html - add PDF option
Script C12: update report_result.html - add PDF download button
Script C13: rebuild and test
Let me be careful with each script.
For C10, I need to modify the reports_generate function. The current code:
python
    if fmt == "csv":
        return _render_csv(report, date_from, date_to)
    if fmt == "xlsx":
        return _render_xlsx(report, date_from, date_to)

    return templates.TemplateResponse("report_result.html", {
        "request": request, "report": report,
        "admin": request.session.get("admin"),
        "show_apps": bool(show_apps),
        "show_abnormal": bool(show_abnormal),
        "expand_details": bool(expand_details),
    })
I need to:
Add if fmt == "pdf": return _render_pdf(...)
Add filters to context
New:
python
    if fmt == "csv":
        return _render_csv(report, date_from, date_to)
    if fmt == "xlsx":
        return _render_xlsx(report, date_from, date_to)
    if fmt == "pdf":
        return _render_pdf(report, date_from, date_to)

    return templates.TemplateResponse("report_result.html", {
        "request": request, "report": report,
        "admin": request.session.get("admin"),
        "show_apps": bool(show_apps),
        "show_abnormal": bool(show_abnormal),
        "expand_details": bool(expand_details),
        "filter_employee_ids": employee_ids,
        "filter_department_ids": department_ids,
        "filter_computer_ids": computer_ids,
        "filter_date_from": date_from,
        "filter_date_to": date_to,
        "filter_group_by": group_by,
    })
Let me write the PowerShell patch for that.
Now for report_result.html, add a PDF button near "? Новый отчёт":
html
<form method="post" action="/admin/reports/generate" class="d-inline">
  {% for eid in filter_employee_ids %}<input type="hidden" name="employee_ids" value="{{ eid }}">{% endfor %}
  {% for did in filter_department_ids %}<input type="hidden" name="department_ids" value="{{ did }}">{% endfor %}
  {% for cid in filter_computer_ids %}<input type="hidden" name="computer_ids" value="{{ cid }}">{% endfor %}
  <input type="hidden" name="date_from" value="{{ filter_date_from }}">
  <input type="hidden" name="date_to" value="{{ filter_date_to }}">
  <input type="hidden" name="group_by" value="{{ filter_group_by }}">
  <input type="hidden" name="fmt" value="pdf">
  {% if show_apps %}<input type="hidden" name="show_apps" value="on">{% endif %}
  {% if show_abnormal %}<input type="hidden" name="show_abnormal" value="on">{% endif %}
  <input type="hidden" name="expand_details" value="on">
  <button class="btn btn-outline-danger">?? Скачать PDF</button>
</form>
OK. Let me write the scripts.
Actually one concern: I'm using @'...'@ here-strings in PowerShell. These don't interpolate variables — perfect. But if the Python code contains '@ sequence on a line by itself, it will terminate early. Let me make sure the Python code doesn't contain '@ on its own line. Looking through it — it doesn't. Good.
Let me write the final scripts now.
I should also mention that we need DejaVuSans-Bold.ttf potentially. Let me make it optional with a fallback.
OK let me write.
I'll aim for a compact but complete response.
Подблок C — часть 2: PDF-отчёт
Шрифт DejaVuSans.ttf уже скачан в C2 (D:\tracker\server\fonts\DejaVuSans.ttf). Теперь добавим генерацию PDF через reportlab.
Что получится
В форме отчёта появится опция PDF, а на странице результата — кнопка ?? Скачать PDF, которая скачивает тот же отчёт в PDF (со всеми фильтрами и группировкой).
________________________________________
Скрипт C9 — добавляем PDF-рендерер в web_admin.py
Дописываем в конец файла функцию _render_pdf и хелпер _pdf_table_data.
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("def _render_pdf")) {
    Write-Host "PDF-рендерер уже есть" -ForegroundColor Yellow
    exit 0
}

$pdfBlock = @'


