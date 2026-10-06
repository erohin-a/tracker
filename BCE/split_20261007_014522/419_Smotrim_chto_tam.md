<!-- Часть 419 из 1409 -->
# Смотрим что там
*Хлебные крошки:* Смотрим что там

[◀ Потом заново:](418_Potom_zanovo.md) | [Оглавление](00_BCE_INDEX.md) | [Считаем сессии с ошибкой 409 (принадлежат старому ПК) — помечаем synced=1 ▶](420_Schitaem_sessii_s_oshibkoy_409_prinadlezhat_staromu_PK_pomechaem_synced_1.md)

---

# Смотрим что там
print('Записей в очереди (synced=0, poisoned=0):')
for row in cur.execute('SELECT COUNT(*) FROM records WHERE synced=0 AND poisoned=0'):
    print('  ', row[0])

print('Сессий не отправлено:')
for row in cur.execute('SELECT COUNT(*) FROM sessions WHERE synced=0'):
    print('  ', row[0])

