# ============================================================

*Часть 79 из 100. Источник: `BCE.md`.*

[◀ После формирования totals добавляем break и idle](078_Posle_formirovaniya_totals_dobavlyaem_break_i_idle.md) | [Оглавление](00_BCE_INDEX.md) | [Копируем внутрь контейнера и запускаем ▶](080_Kopiruem_vnutr_konteynera_i_zapuskaem.md)

---

# ============================================================
# Генератор тестовых данных для отчётов за август 2026
# ============================================================
# Что делает:
# 1. Создаёт 3 отдела: Планово-экономический, Разработка, Бухгалтерия
# 2. В каждом 5-7 сотрудников с 1C ID (0001..0015)
# 3. Создаёт ~15 "виртуальных" ПК (hostname ws-a-01 и т.п.)
# 4. На каждый рабочий день августа 2026 (пн-пт + иногда выходные)
#    генерирует 1-3 сессии у каждого сотрудника
# 5. Каждая сессия: start/end с реалистичными паузами-обедами,
#    pause_seconds (в 30% сессий), abnormal_termination (10%)
# 6. Часть ПК оставим БЕЗ employee_id — для проверки "не привязан"
# ============================================================
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://tracker:tracker@db:5432/tracker",
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# ---------- Данные для генерации ----------
DEPARTMENTS = [
    "Планово-экономический отдел",
    "Отдел разработки",
    "Бухгалтерия",
]

# (last, first, middle, dept_idx)
EMPLOYEES = [
    ("Ерохин",   "Александр", "Владимирович",  0, "0001"),
    ("Смирнова", "Ольга",     "Ивановна",      0, "0002"),
    ("Кузнецов", "Дмитрий",   "Петрович",      0, "0003"),
    ("Попова",   "Екатерина", "Сергеевна",     0, "0004"),
    ("Волков",   "Андрей",    "Николаевич",    0, "0005"),
    ("Соколов",  "Михаил",    "Андреевич",     0, "0006"),

    ("Морозов",  "Игорь",     "Валерьевич",    1, "0007"),
    ("Лебедева", "Анна",      "Дмитриевна",    1, "0008"),
    ("Новиков",  "Сергей",    "Олегович",      1, "0009"),
    ("Фёдоров",  "Павел",     "Игоревич",      1, "0010"),
    ("Орлова",   "Мария",     "Алексеевна",    1, "0011"),
    ("Зайцев",   "Артём",     "Сергеевич",     1, "0012"),
    ("Павлов",   "Роман",     "Владимирович",  1, "0013"),

    ("Никитина", "Татьяна",   "Петровна",      2, "0014"),
    ("Белов",    "Олег",      "Николаевич",    2, "0015"),
    ("Григорьева","Светлана", "Михайловна",    2, "0016"),
    ("Тимофеев", "Виктор",    "Андреевич",     2, "0017"),
    ("Иванова",  "Наталья",   "Сергеевна",     2, "0018"),
]

# Приложения для records (вес = вероятность)
APPS = [
    ("1cv8.exe",       25),
    ("browser.exe",    20),
    ("OUTLOOK.EXE",    15),
    ("EXCEL.EXE",      15),
    ("WINWORD.EXE",    10),
    ("Code.exe",        5),
    ("max.exe",         5),
    ("explorer.exe",    3),
    ("notepad.exe",     2),
]

def weighted_choice(items):
    total = sum(w for _, w in items)
    r = random.uniform(0, total)
    upto = 0
    for name, w in items:
        if upto + w >= r:
            return name
        upto += w
    return items[-1][0]

# ---------- Очистка (только наши тестовые данные) ----------
print("Очистка прошлых тестовых данных...")
db.execute(text("DELETE FROM records WHERE client_ts >= '2026-08-01' AND client_ts < '2026-09-01'"))
db.execute(text("DELETE FROM work_sessions WHERE session_start >= '2026-08-01' AND session_start < '2026-09-01'"))
db.execute(text("DELETE FROM computers WHERE hostname LIKE 'ws-gen-%'"))
db.execute(text("DELETE FROM employees WHERE external_id LIKE '1C-%'"))
db.execute(text("DELETE FROM departments WHERE name IN :names").bindparams(
    names=tuple(DEPARTMENTS)
))
db.commit()

# ---------- Отделы ----------
print("Создаю отделы...")
dept_ids = {}
for name in DEPARTMENTS:
    row = db.execute(text(
        "INSERT INTO departments (name, is_active, created_at) "
        "VALUES (:n, true, NOW()) RETURNING id"
    ), {"n": name}).first()
    dept_ids[name] = row[0]
db.commit()
print(f"  Создано отделов: {len(dept_ids)}")

# ---------- Сотрудники ----------
print("Создаю сотрудников...")
emp_ids = {}  # (ext_id) -> employee_id
for last, first, middle, dept_idx, ext_id in EMPLOYEES:
    full_name = f"{last} {first} {middle}"
    dept_name = DEPARTMENTS[dept_idx]
    row = db.execute(text(
        "INSERT INTO employees (full_name, last_name, first_name, middle_name, "
        "external_id, department_id, is_active) "
        "VALUES (:fn, :ln, :fi, :mn, :ext, :dept, true) RETURNING id"
    ), {
        "fn": full_name, "ln": last, "fi": first, "mn": middle,
        "ext": f"1C-{ext_id}", "dept": dept_ids[dept_name],
    }).first()
    emp_ids[ext_id] = row[0]
db.commit()
print(f"  Создано сотрудников: {len(emp_ids)}")

# ---------- Компьютеры ----------
print("Создаю компьютеры...")
# Раздадим по одному ПК на сотрудника + несколько лишних БЕЗ привязки
# (для проверки блока "не привязан")
comp_info = []  # (comp_id, emp_id_or_None, hostname)
ws_counter = 100
for last, first, middle, dept_idx, ext_id in EMPLOYEES:
    ws_counter += 1
    hostname = f"ws-gen-{ws_counter:03d}"
    # 85% ПК привязаны к сотруднику, 15% — без привязки
    emp_id = emp_ids[ext_id] if random.random() < 0.85 else None
    row = db.execute(text(
        "INSERT INTO computers (computer_uid, hostname, os_info, client_version, "
        "client_secret_enc, secret_version, is_active, employee_id, assigned_at, "
        "registered_at, last_seen_at) "
        "VALUES (:uid, :h, 'Windows 10', '1.2.0', 'fake_encrypted', 1, true, "
        ":emp, :now, :now, :now) RETURNING id"
    ), {
        "uid": str(uuid.uuid4()),
        "h": hostname,
        "emp": emp_id,
        "now": datetime(2026, 8, 1, tzinfo=timezone.utc),
    }).first()
    comp_info.append((row[0], emp_id, hostname))
db.commit()
print(f"  Создано ПК: {len(comp_info)} (из них без привязки: {sum(1 for c in comp_info if c[1] is None)})")

# ---------- Сессии + Records ----------
print("Генерирую сессии и записи за август 2026...")
aug_start = datetime(2026, 8, 1, tzinfo=timezone.utc)
aug_end = datetime(2026, 9, 1, tzinfo=timezone.utc)
MSK = timezone(timedelta(hours=3))

total_sessions = 0
total_records = 0

cur = aug_start
while cur < aug_end:
    # Дата в Москве (для определения выходного)
    msk_date = (cur + timedelta(hours=3)).date()
    # Выходной или будний?
    is_weekend = msk_date.weekday() >= 5

    for comp_id, emp_id, hostname in comp_info:
        # В выходные работают только 20% сотрудников
        if is_weekend and random.random() > 0.20:
            continue
        # В будни прогуливают 5%
        if not is_weekend and random.random() < 0.05:
            continue

        # Стиль работы: ранний, обычный, поздний
        style = random.choice(["early", "normal", "normal", "late"])
        if style == "early":
            start_h = 7
            start_m = random.randint(0, 30)
            end_h = random.randint(15, 16)
        elif style == "late":
            start_h = random.randint(10, 11)
            start_m = random.randint(0, 30)
            end_h = random.randint(19, 20)
        else:
            start_h = random.randint(8, 9)
            start_m = random.randint(0, 45)
            end_h = random.randint(17, 18)

        # Сессия 1: утро-обед
        s1_start_msk = datetime(msk_date.year, msk_date.month, msk_date.day,
                                start_h, start_m, tzinfo=MSK)
        lunch_h = 13
        s1_end_msk = datetime(msk_date.year, msk_date.month, msk_date.day,
                              lunch_h, 0, tzinfo=MSK)
        if s1_end_msk <= s1_start_msk:
            continue

        # 20% сотрудников ещё делают вторую сессию после обеда
        has_second = random.random() < 0.80

        sessions_today = [(s1_start_msk, s1_end_msk)]

        if has_second:
            s2_start_msk = datetime(msk_date.year, msk_date.month, msk_date.day,
                                    14, 0, tzinfo=MSK)
            s2_end_msk = datetime(msk_date.year, msk_date.month, msk_date.day,
                                  end_h, random.randint(0, 59), tzinfo=MSK)
            if s2_end_msk > s2_start_msk:
                sessions_today.append((s2_start_msk, s2_end_msk))

        # Ланч между сессиями — пауза (не сессия)
        # Если нет второй сессии — то просто короткая (до 16:00)

        for sess_start_msk, sess_end_msk in sessions_today:
            sess_start = sess_start_msk.astimezone(timezone.utc)
            sess_end = sess_end_msk.astimezone(timezone.utc)

            # pause_seconds: 30% сессий содержат нажатую паузу 15-90 мин
            pause_seconds = 0
            if random.random() < 0.30:
                pause_seconds = random.randint(15, 90) * 60

            abnormal = random.random() < 0.05

            sess_uid = str(uuid.uuid4())
            db.execute(text(
                "INSERT INTO work_sessions (session_uid, computer_id, employee_id, "
                "session_start, session_end, abnormal_termination, client_version, "
                "pause_seconds, is_deleted, created_at) "
                "VALUES (:uid, :cid, :eid, :ss, :se, :abn, '1.2.0', :ps, false, NOW())"
            ), {
                "uid": sess_uid, "cid": comp_id, "eid": emp_id,
                "ss": sess_start, "se": sess_end, "abn": abnormal,
                "ps": pause_seconds,
            })
            total_sessions += 1

            # Генерируем records внутри сессии — activity каждые 5 сек
            # + window events при смене приложения
            # Экономим: не каждые 5 сек, а раз в 30 сек (достаточно для отчётов)
            t = sess_start
            current_app = weighted_choice(APPS)
            interval = timedelta(seconds=30)

            # Простой на обед внутри сессии (если сессия длинная)
            # нет — обед у нас между сессиями

            # Пауза внутри сессии
            pause_start = None
            pause_end = None
            if pause_seconds > 0:
                # Пауза начинается через случайное время от старта
                pause_offset = random.randint(30, 90) * 60  # 30-90 мин от старта
                pause_start = sess_start + timedelta(seconds=pause_offset)
                pause_end = pause_start + timedelta(seconds=pause_seconds)

            while t < sess_end:
                # Смена активного приложения
                if random.random() < 0.03:
                    current_app = weighted_choice(APPS)
                    # window event
                    db.execute(text(
                        "INSERT INTO records (record_uid, session_uid, computer_id, "
                        "kind, data, client_ts, signature, received_at) "
                        "VALUES (:uid, :sess, :cid, 'window', :data, :ts, 'fake', NOW())"
                    ), {
                        "uid": str(uuid.uuid4()), "sess": sess_uid, "cid": comp_id,
                        "data": f'{{"type":"window","app":"{current_app}","title":"{current_app}"}}',
                        "ts": t,
                    })
                    total_records += 1

                # Внутри паузы записи не пишем (или пишем idle)
                in_pause = pause_start and pause_end and pause_start <= t <= pause_end

                if not in_pause:
                    keys = random.randint(0, 20)
                    clicks = random.randint(0, 5)
                    scroll = random.randint(0, 3)
                    db.execute(text(
                        "INSERT INTO records (record_uid, session_uid, computer_id, "
                        "kind, data, client_ts, signature, received_at) "
                        "VALUES (:uid, :sess, :cid, 'activity', :data, :ts, 'fake', NOW())"
                    ), {
                        "uid": str(uuid.uuid4()), "sess": sess_uid, "cid": comp_id,
                        "data": f'{{"type":"activity","keys":{keys},"clicks":{clicks},"scroll":{scroll}}}',
                        "ts": t,
                    })
                    total_records += 1

                t += interval

    cur += timedelta(days=1)

db.commit()
db.close()

print()
print("=" * 60)
print(f"Готово!")
print(f"  Отделов:     {len(DEPARTMENTS)}")
print(f"  Сотрудников: {len(EMPLOYEES)}")
print(f"  ПК:          {len(comp_info)}")
print(f"  Сессий:      {total_sessions}")
print(f"  Записей:     {total_records}")
print("=" * 60)
'@

[System.IO.File]::WriteAllText("D:\tracker\_seed_august.py", $seedScript, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: скрипт создан" -ForegroundColor Green

