<!-- Часть 160 из 1409 -->
# ---------- Отчёты ----------
*Хлебные крошки:* ---------- Отчёты ----------

[◀ ---------- Bootstrap-токены ----------](159_Bootstrap_tokeny.md) | [Оглавление](00_BCE_INDEX.md) | [---------- Аудит ---------- ▶](161_Audit.md)

---

# ---------- Отчёты ----------

@router.get("/reports", response_class=HTMLResponse)
def reports_form(request: Request, db: Session = Depends(get_db), _=Depends(current_admin)):
    employees = db.query(Employee).filter(Employee.is_active == True).order_by(Employee.last_name).all()
    computers = db.query(Computer).filter(Computer.is_active == True).order_by(Computer.hostname).all()
    return templates.TemplateResponse("reports.html", {
        "request": request, "employees": employees, "computers": computers,
        "admin": request.session.get("admin"),
    })


def _build_report(db: Session, employee_id: Optional[int], computer_id: Optional[int],
                  date_from: date, date_to: date) -> dict:
    dt_from = datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
    dt_to = datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc)

    q = db.query(WorkSession).filter(
        WorkSession.session_start >= dt_from,
        WorkSession.session_start <= dt_to,
    )
    if employee_id:
        q = q.filter(WorkSession.employee_id == employee_id)
    if computer_id:
        q = q.filter(WorkSession.computer_id == computer_id)

    sessions = q.order_by(WorkSession.session_start).all()

    rows = []
    total_seconds = 0
    total_keyboard = 0
    total_mouse = 0
    app_totals: dict[str, int] = {}

    for ws in sessions:
        start = ws.session_start
        end = ws.session_end or _now()
        duration = max(0, int((end - start).total_seconds()))
        total_seconds += duration

        recs = (db.query(Record)
                .filter(Record.session_uid == ws.session_uid)
                .order_by(Record.client_ts).all())

        keyboard = 0
        mouse = 0
        windows = []  # (ts, app_name)
        for r in recs:
            try:
                data = json.loads(r.data) if r.data else {}
            except Exception:
                data = {}
            if r.kind == "activity":
                keys = int(data.get("keys", 0) or 0)
                clicks = int(data.get("clicks", 0) or 0)
                scroll = int(data.get("scroll", 0) or 0)
                if keys > 0:
                    keyboard += 5
                if clicks + scroll > 0:
                    mouse += 5
            elif r.kind == "window":
                app = data.get("app") or data.get("title") or "unknown"
                windows.append((r.client_ts, app))

        for i, (ts, app) in enumerate(windows):
            next_ts = windows[i + 1][0] if i + 1 < len(windows) else end
            dur = max(0, int((next_ts - ts).total_seconds()))
            if dur > 0:
                app_totals[app] = app_totals.get(app, 0) + dur

        total_keyboard += keyboard
        total_mouse += mouse

        emp = db.query(Employee).get(ws.employee_id) if ws.employee_id else None
        comp = db.query(Computer).get(ws.computer_id)

        rows.append({
            "session_uid": ws.session_uid,
            "employee": emp.full_name if emp else "—",
            "computer": (comp.hostname or comp.computer_uid) if comp else "—",
            "start": start,
            "end": end,
            "duration": duration,
            "keyboard": keyboard,
            "mouse": mouse,
            "abnormal": ws.abnormal_termination,
        })

    top_apps = sorted(
        [{"app": k, "seconds": v} for k, v in app_totals.items()],
        key=lambda x: x["seconds"], reverse=True,
    )

    return {
        "rows": rows,
        "totals": {
            "sessions": len(sessions),
            "duration": total_seconds,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "top_apps": top_apps[:10],
        },
        "date_from": date_from,
        "date_to": date_to,
    }


@router.post("/reports/generate")
def reports_generate(
    request: Request,
    employee_id: str = Form(""),
    computer_id: str = Form(""),
    date_from: str = Form(...),
    date_to: str = Form(...),
    fmt: str = Form("html"),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):
    d_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    d_to = datetime.strptime(date_to, "%Y-%m-%d").date()
    if d_to < d_from:
        raise HTTPException(400, "date_to < date_from")

    emp_id = int(employee_id) if employee_id else None
    comp_id = int(computer_id) if computer_id else None

    report = _build_report(db, emp_id, comp_id, d_from, d_to)

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["session_uid", "employee", "computer", "start", "end",
                         "duration_sec", "keyboard_sec", "mouse_sec", "abnormal"])
        for r in report["rows"]:
            writer.writerow([
                r["session_uid"], r["employee"], r["computer"],
                r["start"].isoformat(), r["end"].isoformat(),
                r["duration"], r["keyboard"], r["mouse"], int(r["abnormal"]),
            ])
        writer.writerow([])
        writer.writerow(["ИТОГО", "", "", "", "",
                         report["totals"]["duration"],
                         report["totals"]["keyboard"],
                         report["totals"]["mouse"], ""])
        output.seek(0)
        # BOM для Excel
        data = "\ufeff" + output.getvalue()
        return StreamingResponse(
            iter([data]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.csv"},
        )

    if fmt == "xlsx":
        from openpyxl import Workbook
        from openpyxl.styles import Font

        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        headers = ["session_uid", "employee", "computer", "start", "end",
                   "duration_sec", "keyboard_sec", "mouse_sec", "abnormal"]
        ws.append(headers)
        for c in ws[1]:
            c.font = Font(bold=True)

        for r in report["rows"]:
            ws.append([
                r["session_uid"], r["employee"], r["computer"],
                r["start"].strftime("%Y-%m-%d %H:%M:%S"),
                r["end"].strftime("%Y-%m-%d %H:%M:%S"),
                r["duration"], r["keyboard"], r["mouse"], int(r["abnormal"]),
            ])

        ws.append([])
        ws.append(["ИТОГО", "", "", "", "",
                   report["totals"]["duration"],
                   report["totals"]["keyboard"],
                   report["totals"]["mouse"], ""])

        # Автоширина
        for col in ws.columns:
            length = max((len(str(c.value)) for c in col if c.value is not None), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(length + 2, 60)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=report_{date_from}_{date_to}.xlsx"},
        )

    return templates.TemplateResponse("report_result.html", {
        "request": request, "report": report, "admin": request.session.get("admin"),
    })


