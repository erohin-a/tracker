<!-- Часть 493 из 1409 -->
# Импорт CalendarDay
*Хлебные крошки:* Импорт CalendarDay

[◀ Проверяем, не добавлен ли уже](492_Proveryaem_ne_dobavlen_li_uzhe.md) | [Оглавление](00_BCE_INDEX.md) | [Блок календаря — дописываем в конец файла ▶](494_Blok_kalendarya_dopisyvaem_v_konets_fayla.md)

---

# Импорт CalendarDay
if ($content -notmatch "CalendarDay") {
    $content = $content.Replace(
        "    AppSetting, AuditLog, BootstrapToken, Computer, Department,",
        "    AppSetting, AuditLog, BootstrapToken, CalendarDay, Computer, Department,"
    )
    Write-Host "OK  CalendarDay добавлен в импорты" -ForegroundColor Green
}

