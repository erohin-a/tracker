<!-- Часть 1055 из 1409 -->
# 2. В settings_save добавляем параметр
*Хлебные крошки:* 2. В settings_save добавляем параметр

[◀ 1. В get_settings_dict добавляем поле](1054_1_V_get_settings_dict_dobavlyaem_pole.md) | [Оглавление](00_BCE_INDEX.md) | [3. В new_vals добавляем обработку ▶](1056_3_V_new_vals_dobavlyaem_obrabotku.md)

---

# 2. В settings_save добавляем параметр
old_save_sig = '''    end_of_day_hour: int = Form(19),
    end_of_day_minute: int = Form(0),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):'''

new_save_sig = '''    end_of_day_hour: int = Form(19),
    end_of_day_minute: int = Form(0),
    stale_session_hours: int = Form(2),
    db: Session = Depends(get_db),
    _=Depends(current_admin),
):'''

if old_save_sig in content:
    content = content.replace(old_save_sig, new_save_sig, 1)
    print("OK: параметр stale_session_hours в settings_save")
else:
    print("ERROR: не найдена сигнатура settings_save")
    raise SystemExit(1)

