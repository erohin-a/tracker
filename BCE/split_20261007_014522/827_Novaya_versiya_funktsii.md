<!-- Часть 827 из 1409 -->
# Новая версия функции
*Хлебные крошки:* Новая версия функции

[◀ Находим конец функции (следующий @app. или # ===)](826_Nahodim_konets_funktsii_sleduyuschiy_app_ili.md) | [Оглавление](00_BCE_INDEX.md) | [Проверки ▶](828_Proverki.md)

---

# Новая версия функции
new_func = '''@app.get("/api/v1/client-config")
def get_client_config(request: Request, db: Session = Depends(get_db)):
    """
    Клиент подтягивает эту конфигурацию раз в 5 минут.
    
    Если передан заголовок X-Computer-Uid и этот ПК привязан
    к сотруднику, в employee_settings есть персональные настройки —
    они перекрывают глобальные (AppSetting). Иначе — только глобальные.
    """
    from .models import AppSetting as _AppSetting, Computer as _Computer, EmployeeSettings as _ES

    # --- 1. Глобальные дефолты ---
    def getv(key, default, mn, mx):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        try:
            return max(mn, min(mx, int(row.value))) if row else default
        except (ValueError, TypeError):
            return default

    def getstr(key, default):
        row = db.query(_AppSetting).filter(_AppSetting.key == key).first()
        return row.value if row else default

    eff = {
        "idle_close_minutes": getv("idle_close_minutes", 30, 5, 480),
        "sync_interval": getv("sync_interval", 30, 5, 3600),
        "batch_size": getv("batch_size", 200, 10, 1000),
        "active_window_interval": getv("active_window_interval", 5, 1, 60),
        "idle_threshold": getv("idle_threshold", 60, 10, 3600),
        "reminder_enabled": getstr("reminder_enabled", "1") == "1",
        "reminder_threshold_minutes": getv("reminder_threshold_minutes", 15, 1, 480),
        "reminder_repeat_minutes": getv("reminder_repeat_minutes", 10, 1, 480),
        "reminder_max_per_day": getv("reminder_max_per_day", 5, 1, 100),
        "end_of_day_hour": getv("end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": getv("end_of_day_minute", 0, 0, 59),
    }
    eff["source_reminder"] = "global"
    eff["source_end_of_day"] = "global"

    # --- 2. Персональные override (если ПК привязан к сотруднику) ---
    computer_uid = request.headers.get("X-Computer-Uid")
    if computer_uid:
        comp = db.query(_Computer).filter(_Computer.computer_uid == computer_uid).first()
        if comp and comp.employee_id:
            es = db.query(_ES).filter(_ES.employee_id == comp.employee_id).first()
            if es:
                # reminder-настройки
                reminder_fields = [
                    "reminder_enabled",
                    "reminder_threshold_minutes",
                    "reminder_repeat_minutes",
                    "reminder_max_per_day",
                ]
                for field in reminder_fields:
                    val = getattr(es, field, None)
                    if val is not None:
                        eff[field] = val
                        eff["source_reminder"] = "personal"
                # end-of-day
                eod_fields = ["end_of_day_hour", "end_of_day_minute"]
                for field in eod_fields:
                    val = getattr(es, field, None)
                    if val is not None:
                        eff[field] = val
                        eff["source_end_of_day"] = "personal"

    return eff
'''

new_content = content[:start] + new_func + content[end:]

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(new_content)

print("OK: get_client_config переписан с мержем персональных")

try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

