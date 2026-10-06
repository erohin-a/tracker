<!-- Часть 506 из 1409 -->
# Находим начало блока _pdf_table_data
*Хлебные крошки:* Находим начало блока _pdf_table_data

[◀ Копируем Arial и Arial Bold](505_Kopiruem_Arial_i_Arial_Bold.md) | [Оглавление](00_BCE_INDEX.md) | [Отрезаем всё от _pdf_table_data до конца файла — вставим заново ▶](507_Otrezaem_vse_ot_pdf_table_data_do_kontsa_fayla_vstavim_zanovo.md)

---

# Находим начало блока _pdf_table_data
$marker = "def _pdf_table_data(report, styles):"
if (-not $content.Contains($marker)) {
    Write-Host "Не найден маркер _pdf_table_data — правьте вручную" -ForegroundColor Red
    exit 1
}

