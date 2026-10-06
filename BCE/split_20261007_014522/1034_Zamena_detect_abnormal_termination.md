<!-- Часть 1034 из 1409 -->
# ---------- Замена detect_abnormal_termination ----------
*Хлебные крошки:* ---------- Замена detect_abnormal_termination ----------

[◀ close_session не меняем, оставляем для ручного закрытия](1033_close_session_ne_menyaem_ostavlyaem_dlya_ruchnogo_zakrytiya.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1035_part.md)

---

# ---------- Замена detect_abnormal_termination ----------
if "closing at last activity" in content:
    print("SKIP: detect_abnormal_termination уже пропатчен")
else:
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
    Закрывает «висящую» сессию от прошлого запуска клиента.

    Ключевое отличие от старой версии: session_end ставится НЕ «сейчас»,
    а временем последней реальной активности. Это исправляет баг
    «17 часов работы за ночь» — когда сотрудник ушёл в 18:00, ПК
    выключили, а утром клиент запускается и закрывает сессию.

    Приоритет источников времени последней активности:
      1. MAX(client_ts) из таблицы records — самый надёжный
         (данные в БД, не зависят от meta-ключей).
      2. meta.last_activity — если по какой-то причине records пусты.
      3. session_start — крайний случай (длительность = 0 секунд).

    Если с последней активности прошло меньше 12 часов — ничего
    не делаем. Возможно, это тот же рабочий день и клиент просто
    перезапустился. Дадим пользователю решить через UnclosedSessionDialog.
    """
    active = get_meta("active_session")
    if not active:
        return

    # Источник 1: последняя запись в records
    last_record_ts = get_last_session_record_ts(active)

    # Источник 2: meta.last_activity
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

    # Источник 3: session_start
    if not last_record_ts:
        last_record_ts = get_session_start(active) or _now_iso()

    # Проверка давности
    try:
        end_dt = datetime.fromisoformat(last_record_ts)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        end_dt = datetime.now(timezone.utc)

    if datetime.now(timezone.utc) - end_dt < timedelta(hours=12):
        return

    log.warning(
        "Abnormal termination of %s — closing at last activity %s",
        active, last_record_ts,
    )
    close_session_at(active, last_record_ts, abnormal=True)
'''

    if old in content:
        content = content.replace(old, new, 1)
        print("OK: detect_abnormal_termination переписан")
    else:
        print("ERROR: старый detect_abnormal_termination не найден")
        raise SystemExit(1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

try:
    ast.parse(content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    raise SystemExit(1)
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_db_abnormal.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Запуск патчера db.py ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_db_abnormal.py
Что ожидаем:
text
OK: detect_abnormal_termination переписан
SYNTAX OK
________________________________________
Шаг 2 — Патч client/main.py
Два места:
_quit() — при выходе закрываем сессию временем last_activity.
_handle_unclosed_session() — в аварийном случае (если диалог упал) используем close_last_activity, а не close_now.
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

PATH = r"D:\tracker\client\main.py"
with open(PATH, encoding="utf-8") as f:
    content = f.read()

