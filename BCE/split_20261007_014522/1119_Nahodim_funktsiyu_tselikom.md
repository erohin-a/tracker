<!-- Часть 1119 из 1409 -->
# Находим функцию целиком
*Хлебные крошки:* Находим функцию целиком

[◀ ============================================================](1118_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1120_part.md)

---

# Находим функцию целиком
m = re.search(
    r"def _aggregate_group\(sessions: list, extra_fields: dict\) -> dict:.*?(?=\ndef |\n# ============)",
    content, re.DOTALL)
if not m:
    print("ERROR: _aggregate_group не найдена")
    raise SystemExit(1)

new_aggregate = '''def _aggregate_group(sessions: list, extra_fields: dict) -> dict:
    """
    Универсальная агрегация сессий в группу (день, сотрудник, отдел и т.д.).

    Возвращает 6 ключевых метрик + производные:
      worked_span_duration — табель: сумма daily spans
      worked_duration      — union интервалов (без двойного счёта 2 ПК)
      effective_duration   — сумма времени работы активных программ
      intensive_seconds    — 5 сек ? активные activity-события
      pause_seconds_total  — сумма нажатий кнопки «Пауза»
      break_duration       — кнопка + перерывы между сессиями
                           = pause_seconds_total + (span ? union)
    """
    if not sessions:
        return {
            **extra_fields,
            "sessions_count": 0,
            "worked_span_duration": 0,
            "worked_duration": 0,
            "effective_duration": 0,
            "intensive_seconds": 0,
            "pause_seconds_total": 0,
            "break_duration": 0,
            "keyboard": 0,
            "mouse": 0,
            "abnormal": False,
            "top_apps": [],
            "sessions": [],
        }

    app_stats = defaultdict(lambda: {"seconds": 0, "keyboard": 0, "mouse": 0})
    for s in sessions:
        _merge_apps(app_stats, s["top_apps"])

    span = _aggregate_spans(sessions)
    union = _aggregate_unions(sessions)
    effective = sum(s.get("effective_duration", 0) for s in sessions)
    intensive = sum(s.get("intensive_seconds", 0) for s in sessions)
    pause_btn = sum(s.get("pause_seconds", 0) for s in sessions)
    # Пауза = нажатие кнопки + перерывы между сессиями
    break_dur = pause_btn + max(0, span - union)

    return {
        **extra_fields,
        "sessions_count": len(sessions),
        "worked_span_duration": span,
        "worked_duration": union,
        "effective_duration": effective,
        "intensive_seconds": intensive,
        "pause_seconds_total": pause_btn,
        "break_duration": break_dur,
        "keyboard": sum(s.get("keyboard", 0) for s in sessions),
        "mouse": sum(s.get("mouse", 0) for s in sessions),
        "abnormal": any(s.get("abnormal") for s in sessions),
        "top_apps": _apps_to_list(app_stats),
        "sessions": sessions,
    }

'''
content = content[:m.start()] + new_aggregate + content[m.end():]
print("OK: _aggregate_group переписан")

