<!-- Часть 422 из 1409 -->
# Сессии от старой регистрации — помечаем synced=1 (не отправляем)
*Хлебные крошки:* Сессии от старой регистрации — помечаем synced=1 (не отправляем)

[◀ И записи, которые к ним привязаны](421_I_zapisi_kotorye_k_nim_privyazany.md) | [Оглавление](00_BCE_INDEX.md) | [Все записи от старой регистрации — в poisoned (не отправляем) ▶](423_Vse_zapisi_ot_staroy_registratsii_v_poisoned_ne_otpravlyaem.md)

---

# Сессии от старой регистрации — помечаем synced=1 (не отправляем)
cur.execute('UPDATE sessions SET synced=1 WHERE synced=0')
print('  сессий помечено:', cur.rowcount)

