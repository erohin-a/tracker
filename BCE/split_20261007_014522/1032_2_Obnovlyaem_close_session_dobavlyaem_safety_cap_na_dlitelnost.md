<!-- Часть 1032 из 1409 -->
# 2. Обновляем close_session — добавляем safety cap на длительность
*Хлебные крошки:* 2. Обновляем close_session — добавляем safety cap на длительность

[◀ 1. Заменяем detect_abnormal_termination на правильную версию](1031_1_Zamenyaem_detect_abnormal_termination_na_pravilnuyu_versiyu.md) | [Оглавление](00_BCE_INDEX.md) | [close_session не меняем, оставляем для ручного закрытия ▶](1033_close_session_ne_menyaem_ostavlyaem_dlya_ruchnogo_zakrytiya.md)

---

# 2. Обновляем close_session — добавляем safety cap на длительность
old_close = '''def close_session(uid: str, abnormal: bool = False):
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?",
        (_now_iso(), 1 if abnormal else 0, uid),
    )
    if get_meta("active_session") == uid:
        set_meta("active_session", "")'''

new_close = '''def close_session(uid: str, abnormal: bool = False):
    """
    Закрывает сессию текущим временем UTC.
    Для аварийного закрытия правильнее использовать close_session_at —
    передать время последней активности, а не «сейчас».
    """
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=?, synced=0 "
        "WHERE session_uid=?",
        (_now_iso(), 1 if abnormal else 0, uid),
    )
    if get_meta("active_session") == uid:
        set_meta("active_session", "")'''

