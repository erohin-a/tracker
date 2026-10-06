<!-- Часть 799 из 1409 -->
# Скрипт	Что делает
*Хлебные крошки:* Скрипт	Что делает

[◀ revision identifiers, used by Alembic](798_revision_identifiers_used_by_Alembic.md) | [Оглавление](00_BCE_INDEX.md) | [1. Список всех миграций ▶](800_1_Spisok_vseh_migratsiy.md)

---

#	Скрипт	Что делает
1	_fix_migration.py	Убирает из 2602b71902d4 все records_*-операции
2	_fix_env.py	Добавляет include_object в env.py
3	Фикс .mako	Английский шаблон (без крокозябр)
4	docker compose down -v	Сброс БД (данные не жалко)
5	docker compose up -d --build	Alembic накатит всё с нуля
6	Проверка	\dt, \d employee_settings, SELECT tablename FROM pg_tables WHERE tablename LIKE 'records_%'
________________________________________
Что я хочу от тебя прямо сейчас
Просто пришли вывод двух команд:
powershell
