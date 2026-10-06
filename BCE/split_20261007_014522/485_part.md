<!-- Часть 485 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Календарь рабочих/нерабочих дней](484_Kalendar_rabochih_nerabochih_dney.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](486_part.md)

---

# ============================================================

def _get_calendar_map(db: Session, year: int) -> dict:
    """Возвращает {date_iso: is_working} для указанного года."""
    rows = db.query(CalendarDay).filter(
        CalendarDay.day.like(f"{year:04d}-%")
    ).all()
    return {r.day: r.is_working for r in rows}


def _is_working_day(db: Session, d: date) -> bool:
    """Рабочий ли день. Если записи нет — дефолт: Пн-Пт = рабочий."""
    row = db.query(CalendarDay).filter(CalendarDay.day == d.isoformat()).first()
    if row is not None:
        return row.is_working
    return d.weekday() < 5


def _day_type(db: Session, d: date) -> str:
    """Тип дня: 'working', 'weekend', 'holiday'."""
    row = db.query(CalendarDay).filter(CalendarDay.day == d.isoformat()).first()
    if row is not None:
        if not row.is_working:
            # Если это Сб/Вс и нерабочий — 'weekend', иначе 'holiday'
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

    # Собираем 12 месяцев
    months = []
    for m in range(1, 13):
        first = date(year, m, 1)
        if m == 12:
            last = date(year, 12, 31)
        else:
            last = date(year, m + 1, 1) - timedelta(days=1)

        # Пн=0 ... Вс=6, но в отображении — Пн первый столбец
        # Находим первый понедельник (или нужный день месяца)
        days_in_month = (last - first).days + 1
        # weekday: Пн=0 … Вс=6
        start_offset = first.weekday()  # сколько пустых ячеек до 1-го числа

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
        # Добиваем до конца недели
        while len(cells) % 7 != 0:
            cells.append(None)

        # Разбиваем на недели
        weeks = [cells[i:i+7] for i in range(0, len(cells), 7)]

        months.append({
            "num": m,
            "name": RU_MONTHS[m],
            "weeks": weeks,
        })

    # Итоги года
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
    """Сохраняет отмеченные рабочие дни для указанного года."""
    form = await request.form()
    year = int(form.get("year", 0))
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")

    # Собираем: какие дни отмечены is_working
    checked_isos = set()
    for k, v in form.multi_items():
        # Имена чекбоксов: day_YYYY-MM-DD
        if k.startswith("day_") and k[4:].startswith(f"{year:04d}-"):
            checked_isos.add(k[4:])

    # Обходим все дни года и обновляем/создаём записи
    cur_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    while cur_date <= end_date:
        iso = cur_date.isoformat()
        is_working_default = cur_date.weekday() < 5
        is_working_new = iso in checked_isos

        row = db.query(CalendarDay).filter(CalendarDay.day == iso).first()

        # Оптимизация: если значение совпадает с дефолтом и записи нет — не создаём
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
    """Заполняет год по дефолту: Сб/Вс нерабочие."""
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
    """Удаляет все записи за год ? возвращаемся к дефолту."""
    if year < 2020 or year > 2100:
        raise HTTPException(400, "invalid year")
    db.query(CalendarDay).filter(CalendarDay.day.like(f"{year:04d}-%")).delete(
        synchronize_session=False)
    db.add(AuditLog(actor="admin", entity="calendar", entity_id=str(year),
                    action="reset"))
    db.commit()
    return RedirectResponse(f"/admin/calendar?year={year}&saved=1", status_code=303)


