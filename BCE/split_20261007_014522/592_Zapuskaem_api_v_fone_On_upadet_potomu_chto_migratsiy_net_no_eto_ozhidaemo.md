<!-- Часть 592 из 1409 -->
# Запускаем api в фоне. Он упадёт, потому что миграций нет — но это ожидаемо.
*Хлебные крошки:* Запускаем api в фоне. Он упадёт, потому что миграций нет — но это ожидаемо.

[◀ Запускаем api-контейнер (без nginx — он нам не нужен для генерации)](591_Zapuskaem_api_konteyner_bez_nginx_on_nam_ne_nuzhen_dlya_generatsii.md) | [Оглавление](00_BCE_INDEX.md) | [Генерируем автогенерацию — Alembic не запустит апгрейд, а только создаст файл миграции ▶](593_Generiruem_avtogeneratsiyu_Alembic_ne_zapustit_apgreyd_a_tolko_sozdast_fayl_migr.md)

---

# Запускаем api в фоне. Он упадёт, потому что миграций нет — но это ожидаемо.
docker compose up -d api
Start-Sleep -Seconds 6

