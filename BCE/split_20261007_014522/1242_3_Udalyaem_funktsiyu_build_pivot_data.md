<!-- Часть 1242 из 1409 -->
# 3. Удаляем функцию _build_pivot_data
*Хлебные крошки:* 3. Удаляем функцию _build_pivot_data

[◀ 2. Удаляем эндпоинт pivot-data](1241_2_Udalyaem_endpoint_pivot_data.md) | [Оглавление](00_BCE_INDEX.md) | [4. PDF: удаляем ветку if fmt == "pdf" ▶](1243_4_PDF_udalyaem_vetku_if_fmt_pdf.md)

---

# 3. Удаляем функцию _build_pivot_data
content, n3 = re.subn(
    r'\ndef _build_pivot_data\(.*?(?=\n\n(?:def |@router|# =))',
    '',
    content,
    count=1,
    flags=re.DOTALL,
)

