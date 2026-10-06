<!-- Часть 590 из 1409 -->
# Должно быть "Did not find any relations" — БД пустая
*Хлебные крошки:* Должно быть "Did not find any relations" — БД пустая

[◀ чтобы не ломать ничего.](589_chtoby_ne_lomat_nichego.md) | [Оглавление](00_BCE_INDEX.md) | [Запускаем api-контейнер (без nginx — он нам не нужен для генерации) ▶](591_Zapuskaem_api_konteyner_bez_nginx_on_nam_ne_nuzhen_dlya_generatsii.md)

---

# Должно быть "Did not find any relations" — БД пустая
Что мы сделали: сбросили всё, пересобрали образ (теперь с Alembic в pip-пакетах), но API пока не поднимаем — чтобы он не упал без миграций.
________________________________________
Скрипт D7 — генерируем baseline-миграцию
Теперь запускаем API-контейнер, но Alembic пока не накатится (миграций нет). Нам нужно сгенерировать первую миграцию по моделям.
powershell
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

