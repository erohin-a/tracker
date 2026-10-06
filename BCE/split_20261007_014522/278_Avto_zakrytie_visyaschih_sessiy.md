<!-- Часть 278 из 1409 -->
# --- Авто-закрытие «висящих» сессий ---
*Хлебные крошки:* --- Авто-закрытие «висящих» сессий ---

[◀ Проверяем, есть ли уже функция](277_Proveryaem_est_li_uzhe_funktsiya.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](279_Proverka_sintaksisa.md)

---

# --- Авто-закрытие «висящих» сессий ---

def auto_close_idle_session(idle_minutes: int = 30) -> str | None:
    """
    Если активная сессия не имела активности дольше idle_minutes,
    закрывает её временем последней активности и помечает abnormal=1.
    Возвращает UID закрытой сессии, либо None.
    """
    active = get_meta("active_session")
    if not active:
        return None

    last = get_meta("last_activity")
    if not last:
        return None

    try:
        last_dt = datetime.fromisoformat(last)
    except ValueError:
        return None
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if (now - last_dt).total_seconds() < idle_minutes * 60:
        return None

    # Закрываем сессию временем последней активности, а не «сейчас»
    end_iso = last_dt.isoformat()
    get_conn().execute(
        "UPDATE sessions SET session_end=?, abnormal_termination=1, synced=0 "
        "WHERE session_uid=? AND session_end IS NULL",
        (end_iso, active),
    )
    set_meta("active_session", "")
    log.warning("Auto-closed idle session %s (last activity %s)",
                active, end_iso)
    return active
'@

    # Добавляем в конец файла
    $newContent = $dbContent + $addition
    [System.IO.File]::WriteAllText($dbPath, $newContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  auto_close_idle_session добавлена в db.py" -ForegroundColor Green
}

