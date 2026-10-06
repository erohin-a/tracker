<!-- Часть 287 из 1409 -->
# ---------- Client config ----------
*Хлебные крошки:* ---------- Client config ----------

[◀ ============================================================](286_part.md) | [Оглавление](00_BCE_INDEX.md) | [in loop: ▶](288_in_loop.md)

---

# ---------- Client config ----------

@app.get("/api/v1/client-config")
def get_client_config(db: Session = Depends(get_db)):
    from .web_admin import get_app_setting
    idle = int(get_app_setting(db, "idle_close_minutes", "30"))
    return {"idle_close_minutes": idle}
Wait, circular import risk. Let me instead define the helper in a new module or in web_admin and import it lazily. Or define it inline.
Actually cleaner — define get_app_setting in models.py or a new small helper. Or just define it inline in main.py.
Let me define a small helper in main.py:
python
def _get_setting(db: Session, key: str, default: str) -> str:
    from .models import AppSetting
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    return row.value if row else default
OK. Now for web_admin.py — I'll fully replace it because there are lots of changes.
Let me be smart: keep web_admin.py as a single script but write it carefully.
Alright, writing now. Being careful with f-strings and backticks in PowerShell.
Let me plan the top programs matrix function more carefully:
python
def _build_program_employee_matrix(flat: list) -> dict:
    """
    app -> [{employee_name, external_id, seconds, keyboard, mouse}, ...]
    Отсортирован по убыванию seconds.
    """
    matrix = defaultdict(lambda: defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0}))
    for r in flat:
        emp_key = (r["employee_name"], r.get("external_id") or "")
        for a in r["top_apps"]:
            m = matrix[a["app"]][emp_key]
            m["seconds"] += a["seconds"]
            m["keyboard"] += a["keyboard"]
            m["mouse"] += a["mouse"]
    
    result = {}
    for app, emps in matrix.items():
        rows = []
        for (name, ext_id), stats in emps.items():
            rows.append({
                "employee_name": name,
                "external_id": ext_id,
                "seconds": stats["seconds"],
                "keyboard": stats["keyboard"],
                "mouse": stats["mouse"],
            })
        rows.sort(key=lambda x: x["seconds"], reverse=True)
        result[app] = rows
    return result
Then when building top_apps for totals:
python
matrix = _build_program_employee_matrix(flat)
top_apps = [...]
for a in top_apps:
    a["by_employee"] = matrix.get(a["app"], [])
Good.
Now for the "worked_duration" (span) logic in group functions:
For _split_by_day:
python
g = {..., "first_start": None, "last_end": None, ...}

