<!-- Часть 1150 из 1409 -->
# Ищем хвост функции после _aggregate_group(all_sessions, {...})
*Хлебные крошки:* Ищем хвост функции после _aggregate_group(all_sessions, {...})

[◀ ============================================================](1149_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1151_part.md)

---

# Ищем хвост функции после _aggregate_group(all_sessions, {...})
old_override_e = '''        })
        agg["worked_duration"] = sum(d["span"] for d in days)
        # span за период = сумма spans по дням (не один общий span).
        total_span = 0
        for d in days:
            day_sessions = d["sessions"]
            d_start = min(s["start_local"] for s in day_sessions)
            d_end = max(s["end_local"] for s in day_sessions)
            total_span += max(0, int((d_end - d_start).total_seconds()))
        agg["worked_span_duration"] = total_span
        result.append(agg)'''

new_override_e = '''        })
        result.append(agg)'''

if old_override_e in content:
    content = content.replace(old_override_e, new_override_e, 1)
    changes.append("убран override в _group_by_employee")
else:
    changes.append("SKIP: override в _group_by_employee не найден")

