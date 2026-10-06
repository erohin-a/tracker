<!-- Часть 661 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 2. Патчим web_admin.py — регистрируем _() и context processor](660_2_Patchim_web_admin_py_registriruem_i_context_processor.md) | [Оглавление](00_BCE_INDEX.md) | [Проверим, не пропатчен ли уже ▶](662_Proverim_ne_propatchen_li_uzhe.md)

---

# ============================================================
$webAdminPath = "$serverDir\web_admin.py"
$content = [System.IO.File]::ReadAllText($webAdminPath, [System.Text.UTF8Encoding]::new($false))

