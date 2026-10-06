<!-- Часть 1363 из 1409 -->
# точнее: применяем и считаем удаления
*Хлебные крошки:* точнее: применяем и считаем удаления

[◀ n = кол-во форм всего. Мы не знаем, сколько удалено. Считаем разницу.](1362_n_kol_vo_form_vsego_My_ne_znaem_skolko_udaleno_Schitaem_raznitsu.md) | [Оглавление](00_BCE_INDEX.md) | [Очистим лишние пустые строки ▶](1364_Ochistim_lishnie_pustye_stroki.md)

---

# точнее: применяем и считаем удаления
removed = 0
def repl_form2(m):
    global removed
    block = m.group(0)
    if 'name="fmt" value="pdf"' in block:
        removed += 1
        return ''
    return block

c = re.sub(r'<form\b[^>]*>.*?</form>', repl_form2, c, flags=re.DOTALL)
