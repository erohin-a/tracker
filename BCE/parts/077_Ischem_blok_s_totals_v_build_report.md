# Ищем блок с totals в _build_report

*Часть 77 из 100. Источник: `BCE.md`.*

[◀ 4. Итого внизу](076_4_Itogo_vnizu.md) | [Оглавление](00_BCE_INDEX.md) | [После формирования totals добавляем break и idle ▶](078_Posle_formirovaniya_totals_dobavlyaem_break_i_idle.md)

---

# Ищем блок с totals в _build_report
old = '''"totals": {
            "sessions": len(flat), "worked_duration": total_worked,
            "effective_duration": total_effective, "keyboard": total_keyboard,
            "mouse": total_mouse, "abnormal": total_abnormal, "top_apps": top_apps,
        },'''

new = '''"totals": {
            "sessions": len(flat),
            "worked_span_duration": sum(r.get("worked_span_duration", 0) for r in rows),
            "worked_duration": total_worked,
            "effective_duration": total_effective,
            "keyboard": total_keyboard,
            "mouse": total_mouse,
            "abnormal": total_abnormal,
            "top_apps": top_apps,
        },'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: добавили worked_span_duration в totals")
else:
    print("WARN: не нашли блок totals — правьте вручную")

