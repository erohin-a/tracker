<!-- Часть 348 из 1409 -->
# Employee:
*Хлебные крошки:* Employee:

[◀ ============================================================](347_part.md) | [Оглавление](00_BCE_INDEX.md) | [... ▶](349_part.md)

---

# Employee:
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    fired_at = Column(DateTime(timezone=True), nullable=True)
AppSetting keys:
idle_close_minutes (exists)
report_timezone (new)
workday_start_hour (new)
activity_gap_minutes (new)
Web_admin changes:
get_app_setting_int(db, key, default, min, max) helper.
Settings page: form with all 4 settings.
Employees page:
tabs: "Активные" (fired_at IS NULL), "Уволенные" (fired_at IS NOT NULL), "Все"
each row: ФИО, отдел, 1C ID
action: edit, fire/restore, deactivate
Departments page:
CRUD
Reports page:
employees: multi-select (use <select multiple> or checkbox list)
department filter
timezone comes from settings (global), workday_start comes from settings (global)
remove these from form (they're in settings now)
Excel formatting:
Format durations as HH:MM:SS
Format date as DD.MM.YYYY
Actually with openpyxl we can write the actual datetime.time or datetime.timedelta objects and set number format. But safest to write strings.
Actually, for Excel to "understand", better to write:
datetime.timedelta(seconds=X) with number_format [HH]:MM:SS
datetime.date with number_format DD.MM.YYYY
But that's more complex. Let me write strings that Excel understands as time — hmm, strings won't be treated as time. Better to write actual values with formats.
Let me do:
python
from datetime import timedelta, date
from openpyxl.styles import numbers
