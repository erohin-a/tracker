<!-- Часть 1054 из 1409 -->
# 1. В get_settings_dict добавляем поле
*Хлебные крошки:* 1. В get_settings_dict добавляем поле

[◀ Регистрируем в TASKS_REGISTRY — вставляем новый элемент](1053_Registriruem_v_TASKS_REGISTRY_vstavlyaem_novyy_element.md) | [Оглавление](00_BCE_INDEX.md) | [2. В settings_save добавляем параметр ▶](1055_2_V_settings_save_dobavlyaem_parametr.md)

---

# 1. В get_settings_dict добавляем поле
old_dict = '''        "end_of_day_hour": get_app_setting_int(db, "end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": get_app_setting_int(db, "end_of_day_minute", 0, 0, 59),
}'''

new_dict = '''        "end_of_day_hour": get_app_setting_int(db, "end_of_day_hour", 19, 0, 23),
        "end_of_day_minute": get_app_setting_int(db, "end_of_day_minute", 0, 0, 59),
        # --- Автозакрытие зависших сессий ---
        "stale_session_hours": get_app_setting_int(db, "stale_session_hours", 2, 1, 24),
}'''

if old_dict in content:
    content = content.replace(old_dict, new_dict, 1)
    print("OK: stale_session_hours в settings_dict")
else:
    print("ERROR: не найден конец settings_dict")
    raise SystemExit(1)

