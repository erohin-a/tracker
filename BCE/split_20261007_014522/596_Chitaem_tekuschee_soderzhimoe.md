<!-- Часть 596 из 1409 -->
# Читаем текущее содержимое
*Хлебные крошки:* Читаем текущее содержимое

[◀ client/i18n.py — тот же подход](595_client_i18n_py_tot_zhe_podhod.md) | [Оглавление](00_BCE_INDEX.md) | [Добавляем alembic, если ещё нет ▶](597_Dobavlyaem_alembic_esli_esche_net.md)

---

# Читаем текущее содержимое
$req = [System.IO.File]::ReadAllText($reqPath, [System.Text.UTF8Encoding]::new($false))

