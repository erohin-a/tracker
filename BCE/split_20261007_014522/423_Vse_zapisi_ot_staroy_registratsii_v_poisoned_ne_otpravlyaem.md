<!-- Часть 423 из 1409 -->
# Все записи от старой регистрации — в poisoned (не отправляем)
*Хлебные крошки:* Все записи от старой регистрации — в poisoned (не отправляем)

[◀ Сессии от старой регистрации — помечаем synced=1 (не отправляем)](422_Sessii_ot_staroy_registratsii_pomechaem_synced_1_ne_otpravlyaem.md) | [Оглавление](00_BCE_INDEX.md) | [Чистим лог, чтобы видеть только свежее ▶](424_Chistim_log_chtoby_videt_tolko_svezhee.md)

---

# Все записи от старой регистрации — в poisoned (не отправляем)
cur.execute('UPDATE records SET synced=1, poisoned=1 WHERE synced=0')
print('  записей в poisoned:', cur.rowcount)

c.commit()

n_rec = cur.execute('SELECT COUNT(*) FROM records WHERE synced=0 AND poisoned=0').fetchone()[0]
n_ses = cur.execute('SELECT COUNT(*) FROM sessions WHERE synced=0').fetchone()[0]
print(f'После очистки: records={n_rec}, sessions={n_ses}')
c.close()
"@
Ожидаемый вывод:
text
До очистки: records=1234, sessions=7
  сессий помечено: 7
  записей в poisoned: 1234
После очистки: records=0, sessions=0
________________________________________
Скрипт 3 — пересборка сервера
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

Write-Host "--- Статус ---" -ForegroundColor Cyan
docker compose ps

Write-Host "`n--- Логи API (последние 20) ---" -ForegroundColor Cyan
docker compose logs api --tail=20
________________________________________
Скрипт 4 — запуск клиента и проверка
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

