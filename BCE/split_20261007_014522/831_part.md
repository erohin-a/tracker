<!-- Часть 831 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Приём изменений настроек от клиента](830_Priem_izmeneniy_nastroek_ot_klienta.md) | [Оглавление](00_BCE_INDEX.md) | [Проверки ▶](832_Proverki.md)

---

# ============================================================
@app.put("/api/v1/client-settings")
def update_client_settings(
    payload: ClientSettingsIn,
    comp: Computer = Depends(get_computer),
    db: Session = Depends(get_db),
):
    """
    Клиент отправляет свои локальные изменения настроек.
    
    Логика приоритета (server wins):
    - Если сервер недавно менял настройки (updated_at < 5 минут назад)
      и updated_by != "client" — отклоняем клиентские изменения, возвращаем
      то, что на сервере.
    - Иначе — применяем клиентские изменения, пишем в audit_log.
    
    Требует X-Computer-Uid. Если ПК не привязан к сотруднику — 400.
    """
    from datetime import timedelta as _td
    from .models import EmployeeSettings as _ES
    from .schemas import ClientSettingsOut as _Out

    if not comp.employee_id:
        raise HTTPException(
            400,
            "Компьютер не привязан к сотруднику. Обратитесь к администратору.",
        )

    es = db.query(_ES).filter(_ES.employee_id == comp.employee_id).first()

    # Проверка приоритета: если сервер менял недавно — server wins
    now = _now()
    server_recently = False
    if es and es.updated_at:
        updated = es.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if (now - updated) < _td(minutes=5) and (es.updated_by or "") != "client":
            server_recently = True

    if not server_recently:
        # Создаём запись, если её нет
        if not es:
            es = _ES(employee_id=comp.employee_id, updated_by="client")
            db.add(es)

        # Применяем только те поля, что пришли (не None)
        changed = []
        for field in [
            "reminder_enabled",
            "reminder_threshold_minutes",
            "reminder_repeat_minutes",
            "reminder_max_per_day",
            "end_of_day_hour",
            "end_of_day_minute",
        ]:
            new_val = getattr(payload, field, None)
            if new_val is not None:
                old_val = getattr(es, field, None)
                if old_val != new_val:
                    setattr(es, field, new_val)
                    changed.append({"field": field, "old": old_val, "new": new_val})

        es.updated_at = now
        es.updated_by = "client"

        if changed:
            db.add(AuditLog(
                actor=f"client:{comp.computer_uid}",
                entity="employee_settings",
                entity_id=str(comp.employee_id),
                action="client_update",
                new_value=json.dumps(changed, ensure_ascii=False, default=str),
            ))
        db.commit()
        log.info(
            "client-settings applied for emp=%s from comp=%s, changed=%d",
            comp.employee_id, comp.computer_uid, len(changed),
        )
    else:
        log.info(
            "client-settings rejected (server_recently_changed) emp=%s",
            comp.employee_id,
        )

    # Возвращаем эффективные настройки (как в GET)
    # Переиспользуем логику — вызовем get_client_config через внутренний расчёт
    from .models import AppSetting as _AppSetting

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
        "reminder_enabled": getstr("reminder_enabled", "1") == "1",
        "reminder_threshold_minutes": getv("reminder_threshold_minutes", 15, 1, 480),
        "reminder_repeat_minutes": getv("reminder_repeat_minutes", 10, 1, 480),
        "reminder_max_per_day": getv("reminder_max_per_day", 5, 1, 100),
        "end_of_day_hour": getv("end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": getv("end_of_day_minute", 0, 0, 59),
        "source_reminder": "global",
        "source_end_of_day": "global",
    }
    if es:
        for field in ["reminder_enabled", "reminder_threshold_minutes",
                      "reminder_repeat_minutes", "reminder_max_per_day"]:
            val = getattr(es, field, None)
            if val is not None:
                eff[field] = val
                eff["source_reminder"] = "personal"
        for field in ["end_of_day_hour", "end_of_day_minute"]:
            val = getattr(es, field, None)
            if val is not None:
                eff[field] = val
                eff["source_end_of_day"] = "personal"

    return eff


'''

new_content = content[:insert_at] + new_endpoint + content[insert_at:]

with open(MAIN, "w", encoding="utf-8") as f:
    f.write(new_content)

print("OK: /api/v1/client-settings добавлен")

try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)

