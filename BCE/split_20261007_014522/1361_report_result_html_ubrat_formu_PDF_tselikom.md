<!-- Часть 1361 из 1409 -->
# report_result.html: убрать форму PDF целиком
*Хлебные крошки:* report_result.html: убрать форму PDF целиком

[◀ D:\tracker\tools\disable_pdf_button.py](1360_D_tracker_tools_disable_pdf_button_py.md) | [Оглавление](00_BCE_INDEX.md) | [n = кол-во форм всего. Мы не знаем, сколько удалено. Считаем разницу. ▶](1362_n_kol_vo_form_vsego_My_ne_znaem_skolko_udaleno_Schitaem_raznitsu.md)

---

# report_result.html: убрать форму PDF целиком
p = ROOT / "server" / "templates" / "report_result.html"
backup(p)
c = p.read_text(encoding="utf-8")

def repl_form(m):
    block = m.group(0)
    if 'name="fmt" value="pdf"' in block:
        return ''
    return block

new_c, n = re.subn(r'<form\b[^>]*>.*?</form>', repl_form, c, flags=re.DOTALL)
