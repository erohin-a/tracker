<!-- Часть 1132 из 1409 -->
# Ищем блок return с totals и дополняем
*Хлебные крошки:* Ищем блок return с totals и дополняем

[◀ ============================================================](1131_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1133_part.md)

---

# Ищем блок return с totals и дополняем
old_return = '''"totals": {
            "sessions": len(flat), "worked_duration": total_worked,
            "effective_duration": total_effective, "keyboard": total_keyboard,
            "mouse": total_mouse, "abnormal": total_abnormal, "top_apps": top_apps,
        },'''

new_return = '''"totals": {
            "sessions": len(flat),
            "worked_span_duration": total_span,
            "worked_duration": total_worked,
            "effective_duration": total_effective,
            "intensive_seconds": total_intensive,
            "pause_seconds_total": total_pause_btn,
            "break_duration": total_break,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "abnormal": total_abnormal,
            "top_apps": top_apps,
        },'''

if old_return in content:
    content = content.replace(old_return, new_return, 1)
    print("OK: totals в return обновлены")
else:
    # Возможно уже был другой формат после нашего патча — пробуем иначе
    if '"worked_span_duration": total_span' in content:
        print("SKIP: return уже обновлён")
    else:
        print("WARN: блок return с totals не найден — правьте вручную")

