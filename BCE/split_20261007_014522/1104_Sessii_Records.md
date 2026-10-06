<!-- Часть 1104 из 1409 -->
# ---------- Сессии + Records ----------
*Хлебные крошки:* ---------- Сессии + Records ----------

[◀ (для проверки блока "не привязан")](1103_dlya_proverki_bloka_ne_privyazan.md) | [Оглавление](00_BCE_INDEX.md) | [Копируем внутрь контейнера и запускаем ▶](1105_Kopiruem_vnutr_konteynera_i_zapuskaem.md)

---

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

