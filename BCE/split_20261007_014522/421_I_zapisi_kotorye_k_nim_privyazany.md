<!-- Часть 421 из 1409 -->
# И записи, которые к ним привязаны
*Хлебные крошки:* И записи, которые к ним привязаны

[◀ Считаем сессии с ошибкой 409 (принадлежат старому ПК) — помечаем synced=1](420_Schitaem_sessii_s_oshibkoy_409_prinadlezhat_staromu_PK_pomechaem_synced_1.md) | [Оглавление](00_BCE_INDEX.md) | [Сессии от старой регистрации — помечаем synced=1 (не отправляем) ▶](422_Sessii_ot_staroy_registratsii_pomechaem_synced_1_ne_otpravlyaem.md)

---

# И записи, которые к ним привязаны
cur.execute('UPDATE records SET synced=1 WHERE synced=0 AND poisoned=0')
print('  затронуто записей:', cur.rowcount)

c.commit()
c.close()
print('OK')
"@
После этого перезапустите клиент (правый клик на трее ? Выход, потом заново python -m client.main). Старые записи не будут заново долбить сервер.
Если после этого новые записи начнут уходить — увидим accepted=N без ошибок.
________________________________________
Пока пришлите мне
Результат Шага 1 (grep).
Последние 40–60 строк из docker compose logs api --tail=100 — особенно если там есть Traceback.
По ним точно скажу, что чинить. Скорее всего, это одна из двух причин:
A. Образ не пересобрался (в контейнере старый main.py), либо
B. В новой версии ingest_records есть тонкий баг с откатом транзакции при IntegrityError — тогда я пришлю патч db.py и main.py, где обработка идёт не построчно, а через ON CONFLICT DO NOTHING.
Если увижу Traceback — точно скажу, какой из вариантов.
Ключевая ошибка:
text
sqlalchemy.exc.DataError: (psycopg2.errors.StringDataRightTruncation) value too long for type character varying(64)
В таблице audit_log поле entity_id VARCHAR(64), но мы в ingest_records пишем туда ",".join(rejected[:20]) — это больше 64 символов.
И самое главное — эта ошибка происходит когда есть rejected с bad_signature. То есть все записи, которые шлёт клиент, имеют неправильную подпись!
Стоп. Это вторичная проблема. Первичная — почему bad_signature? Клиент подписывает client_secret, сервер проверяет тем же секретом. Секрет после перерегистрации обновился (был revoke, потом новый register) — но клиент не знал что записи со старым секретом. Хотя нет, ключ хранится в keyring и обновляется при регистрации.
Возможно проблема в том, что при перерегистрации (revoke старого ПК + register нового) сервер сгенерировал новый client_secret и secret_version=1. Но клиент в своём keyring имеет старый секрет от предыдущей регистрации — если он не удалил client_secret в keyring перед новой регистрацией... Но нет, регистрация через диалог сохраняет новый.
Хотя логи показывают:
17:04:44 ? ошибка client_secret not found; register first (было до регистрации)
17:06:51 ? Registered as ed1ef589-... (secret_version=1) — новая регистрация
Но потом 17:07+ старые записи шлются и получают bad_signature. Потому что они были подписаны старым секретом от старой регистрации (af354a84).
Клиент пытается отправить старые записи, подписанные старым client_secret, но у сервера теперь секрет от новой регистрации (ed1ef589). Соответственно подписи не сходятся.
Это классическая проблема: при перерегистрации старые локальные записи становятся невалидными. Их надо выкидывать (poisoned).
В моей реализации в sync.py:
python
permanent = [u for u in rejected if reasons.get(u) == "bad_signature"]
db.apply_sync_result(accepted, permanent)
Это правильно — они должны быть помечены как poisoned и больше не отправляться. Но! Из-за того что сервер падает 500 на этапе создания audit_log, клиент получает 500 и не помечает их poisoned. Круг замыкается.
Решение:
Исправить в ingest_records поле entity_id — обрезать или использовать entity="record" без длинного entity_id. Лучше entity_id=None, а в new_value положить список.
Восстановить обработку bad_signature ? poisoned.
Также есть проблема: если bad_signature, клиент должен пометить и не пытаться снова. Это у нас уже сделано, но сервер падает раньше ответа.
Сделаю патч:
Патч server/main.py — в блоке создания audit_log убрать/обрезать entity_id. И ещё сделать так, чтобы вся транзакция не падала из-за одной ошибки. Плюс — обязательно откатывать bad_signature в БД.
Также надо подумать: если у клиента есть старые записи с bad_signature — они идут в poisoned и больше не отправляются. Это хорошо.
Но! Клиент шлёт по 200 записей в батче. Если в батче есть хотя бы одна запись с bad_signature — сервер отвечает 200, но с принятыми/отклонёнными. И это уже работает. Проблема только в том, что сервер падает на audit_log до возврата ответа.
Так что патч ingest_records:
entity_id ? обрезать до 64 символов, либо положить туда что-то короткое (например, str(len(rejected))).
new_value — уже без проблем (Text).
И ещё — надо явно не помещать в rejected те записи, которые отличаются только подписью (bad_signature) если они уже в базе. Хотя это уже есть.
Но основная проблема клиента: старые записи. Решение на клиенте — кнопка "Сбросить очередь" или автоочистка при старте, если много bad_signature.
Дам патч:
server/main.py — фикс audit_log (не переполнять entity_id).
Опционально: в sync.py — если получили bad_signature для всей пачки — увеличить счётчик и автоматически показывать уведомление/чистить через N повторов.
Начнём с серверного патча. Дам полный main.py.
Также замечу: сообщение про 500 — это не «сервер офлайн». Это ошибка на сервере. Нужно поправить и всё пойдёт.
Ещё момент — клиент по 200 записей шлёт на сервер. Если у него скопились тысячи записей с bad_signature, они все будут падать. Нужна регенерация (или удаление). Плюс клиент должен понимать что bad_signature — это permanent и больше не пытаться. Это уже есть в sync.py.
Дам патч main.py и подскажу команду для очистки старых записей на клиенте.
Пишу.
Найдено! Ошибка в серверном audit_log
Traceback предельно ясен:
text
sqlalchemy.exc.DataError: value too long for type character varying(64)
[SQL: INSERT INTO audit_log (... entity_id ...) VALUES (...)]
entity_id: '50c5db31-09d7-4755-aee3-58069ba1a66e,9586575e-...,4349cd93-...'
Что происходит:
Клиент шлёт пачку записей, подписанных старым client_secret (после перерегистрации секрет сменился, старые записи подписаны старым).
Сервер видит bad_signature для этих записей — правильно.
Пытается записать в audit_log, кладя в entity_id список из 20 UUID через запятую — это >1000 символов, а колонка VARCHAR(64).
SQL падает, вся транзакция откатывается, эндпоинт возвращает 500.
Клиент никогда не получает ответ ? не помечает записи как poisoned ? долбит их бесконечно.
Двойной фикс:
Сервер — больше не переполнять entity_id.
Клиент — почистить очередь от старых записей (подписанных старым секретом) — они никогда не пройдут.
________________________________________
Скрипт 1 — патч server/main.py
Заменяем только блок аудита в ingest_records. Ничего больше не трогаем.
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\main.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

$old = @'
    if rejected:
        db.add(AuditLog(
            actor=f"computer:{comp.computer_uid}",
            entity="record", entity_id=",".join(rejected[:20]),
            action="reject_signature",
            new_value=json.dumps({"count": len(rejected), "reasons": reasons},
                                 ensure_ascii=False),
        ))
'@

$new = @'
    if rejected:
        # entity_id ограничен 64 символами — кладём туда первое отклонённое UUID,
        # список всех отклонённых уходит в new_value (там Text, без ограничений).
        db.add(AuditLog(
            actor=f"computer:{comp.computer_uid}"[:128],
            entity="record",
            entity_id=(rejected[0] if rejected else None),
            action="reject_signature",
            new_value=json.dumps(
                {"count": len(rejected), "rejected": rejected[:50], "reasons": reasons},
                ensure_ascii=False,
            ),
        ))
'@

if ($content.Contains($new)) {
    Write-Host "Уже пропатчен — ничего не делаем" -ForegroundColor Yellow
} elseif ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK  main.py пропатчен" -ForegroundColor Green
} else {
    Write-Host "НЕ НАЙДЕН блок аудита — правьте вручную" -ForegroundColor Red
    Write-Host "Ищите: 'entity_id='',''.join(rejected[:20])'" -ForegroundColor Red
    exit 1
}

python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  SYNTAX OK')"
________________________________________
Скрипт 2 — чистим «мёртвую» очередь на клиенте
Это записи, подписанные старым секретом (сгорели при перерегистрации). Они никогда не пройдут проверку подписи — надо их удалить, иначе клиент будет их вечно долбить.
Пока клиент запущен — закройте его (трей ? Выход). Затем:
powershell
$ErrorActionPreference = "Stop"
cd D:\tracker
client\.venv\Scripts\Activate.ps1

python -c @"
import os, sqlite3
p = os.path.join(os.environ['APPDATA'], 'Tracker', 'data.db')
c = sqlite3.connect(p)
cur = c.cursor()

n_rec = cur.execute('SELECT COUNT(*) FROM records WHERE synced=0 AND poisoned=0').fetchone()[0]
n_ses = cur.execute('SELECT COUNT(*) FROM sessions WHERE synced=0').fetchone()[0]
print(f'До очистки: records={n_rec}, sessions={n_ses}')

