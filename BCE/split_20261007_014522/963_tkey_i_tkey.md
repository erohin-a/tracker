<!-- Часть 963 из 1409 -->
# t("key") и t('key')
*Хлебные крошки:* t("key") и t('key')

[◀ Заменяем плейсхолдеры f-строк на реальные значения](962_Zamenyaem_pleysholdery_f_strok_na_realnye_znacheniya.md) | [Оглавление](00_BCE_INDEX.md) | [t(f"key.{var}") — f-строки ▶](964_tfkey_var_f_stroki.md)

---

# t("key") и t('key')
pattern1 = re.compile(r'''\bt\(\s*["']([a-z_][a-z_.0-9]*)["']''')
keys = set(pattern1.findall(src))

