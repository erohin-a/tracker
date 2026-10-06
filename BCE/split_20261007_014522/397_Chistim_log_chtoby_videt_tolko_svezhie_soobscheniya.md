<!-- Часть 397 из 1409 -->
# Чистим лог, чтобы видеть только свежие сообщения
*Хлебные крошки:* Чистим лог, чтобы видеть только свежие сообщения

[◀ 3) Поправить _on_synced: не перезаписывать last_sync_ts при n=0](396_3_Popravit_on_synced_ne_perezapisyvat_last_sync_ts_pri_n_0.md) | [Оглавление](00_BCE_INDEX.md) | [Запускаем ▶](398_Zapuskaem.md)

---

# Чистим лог, чтобы видеть только свежие сообщения
Remove-Item "$env:APPDATA\Tracker\client.log" -ErrorAction SilentlyContinue

