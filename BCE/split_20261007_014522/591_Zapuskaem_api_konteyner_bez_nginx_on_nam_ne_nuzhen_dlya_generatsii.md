<!-- Часть 591 из 1409 -->
# Запускаем api-контейнер (без nginx — он нам не нужен для генерации)
*Хлебные крошки:* Запускаем api-контейнер (без nginx — он нам не нужен для генерации)

[◀ Должно быть "Did not find any relations" — БД пустая](590_Dolzhno_byt_Did_not_find_any_relations_BD_pustaya.md) | [Оглавление](00_BCE_INDEX.md) | [Запускаем api в фоне. Он упадёт, потому что миграций нет — но это ожидаемо. ▶](592_Zapuskaem_api_v_fone_On_upadet_potomu_chto_migratsiy_net_no_eto_ozhidaemo.md)

---

# Запускаем api-контейнер (без nginx — он нам не нужен для генерации)
Write-Host "`n=== Генерация baseline-миграции ===" -ForegroundColor Cyan
Write-Host "Это займёт 10-15 секунд — Alembic подключается к БД и сравнивает модели." -ForegroundColor Gray

