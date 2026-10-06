<!-- Часть 1031 из 1409 -->
# 1. Заменяем detect_abnormal_termination на правильную версию
*Хлебные крошки:* 1. Заменяем detect_abnormal_termination на правильную версию

[◀ Тогда они одинаковые будут без пауз.](1030_Togda_oni_odinakovye_budut_bez_pauz.md) | [Оглавление](00_BCE_INDEX.md) | [2. Обновляем close_session — добавляем safety cap на длительность ▶](1032_2_Obnovlyaem_close_session_dobavlyaem_safety_cap_na_dlitelnost.md)

---

# 1. Заменяем detect_abnormal_termination на правильную версию
old = '''def detect_abnormal_termination():
    active = get_meta("active_session")
    if not active:
        return
    last = get_meta("last_activity")
    try:
        last_dt = datetime.fromisoformat(last) if last else datetime.now(timezone.utc)
    except ValueError:
        last_dt = datetime.now(timezone.utc)
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - last_dt > timedelta(hours=12):
        log.warning("Abnormal termination of %s", active)
        close_session(active, abnormal=True)'''

new = '''def detect_abnormal_termination():
    """
    Если при старте клиента обнаружена незакрытая сессия — закрываем
    её временем последней активности (а не текущим временем).

    Логика: почему не "сейчас"?
    Если сотрудник ушёл домой в 18:00, а ПК упал/выключили в 18:05,
    сессия в SQLite осталась открытой. Утром при следующем запуске
    закрываем её — но не временем "сейчас" (09:00 следующего дня,
    это дало бы 15 часов работы), а временем последней реальной
    активности (18:00).

    Fallback на "сейчас" — только если записей в сессии вообще нет
    (тогда длительность = 0 секунд).
    """
    active = get_meta("active_session")
    if not active:
        return

    # Приоритет 1: последняя запись активности в этой сессии (самый надёжный источник)
    last_record_ts = get_last_session_record_ts(active)

    # Приоритет 2: meta last_activity (если записей нет)
    if not last_record_ts:
        last = get_meta("last_activity")
        if last:
            try:
                last_dt = datetime.fromisoformat(last)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
                last_record_ts = last_dt.isoformat()
            except ValueError:
                pass

    # Приоритет 3: start_time сессии (если совсем ничего нет)
    if not last_record_ts:
        last_record_ts = get_session_start(active) or _now_iso()

    # Насколько давно это было?
    try:
        end_dt = datetime.fromisoformat(last_record_ts)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        end_dt = datetime.now(timezone.utc)

    # Если прошло меньше 12 часов — ничего не делаем (может, клиент
    # просто перезапустился и это та же сессия). Мы лишь страхуем
    # действительно «висящие» сессии.
    if datetime.now(timezone.utc) - end_dt < timedelta(hours=12):
        return

    log.warning("Abnormal termination of %s — closing at last activity %s",
                active, last_record_ts)
    close_session_at(active, last_record_ts, abnormal=True)
'''

if old in content:
    content = content.replace(old, new, 1)
    print("OK: detect_abnormal_termination заменён")
else:
    print("WARN: старый detect_abnormal_termination не найден — возможно уже пропатчен")

