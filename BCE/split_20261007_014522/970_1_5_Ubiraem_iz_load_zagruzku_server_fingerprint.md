<!-- Часть 970 из 1409 -->
# ---------- 1.5. Убираем из _load() загрузку server/fingerprint ----------
*Хлебные крошки:* ---------- 1.5. Убираем из _load() загрузку server/fingerprint ----------

[◀ ---------- 1.4. Убираем методы _on_save_server и _on_check_connection из GeneralTab ----------](969_1_4_Ubiraem_metody_on_save_server_i_on_check_connection_iz_GeneralTab.md) | [Оглавление](00_BCE_INDEX.md) | [---------- 1.6. Убираем _wrap_row, он больше не нужен ---------- ▶](971_1_6_Ubiraem_wrap_row_on_bolshe_ne_nuzhen.md)

---

# ---------- 1.5. Убираем из _load() загрузку server/fingerprint ----------
old_load = '''        # Сервер
        self.ed_server.setText(get_server_url() or "")
        self.ed_fingerprint.setText(get_cert_fingerprint() or "")

        # Уведомления'''

new_load = '''        # Уведомления'''

if old_load in content:
    content = content.replace(old_load, new_load, 1)
    print("OK: _load() больше не читает сервер/отпечаток")
else:
    print("WARN: блок загрузки сервера не найден")


