<!-- Часть 279 из 1409 -->
# Проверка синтаксиса
*Хлебные крошки:* Проверка синтаксиса

[◀ --- Авто-закрытие «висящих» сессий ---](278_Avto_zakrytie_visyaschih_sessiy.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](280_part.md)

---

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'$dbPath', encoding='utf-8').read()); print('  db.py SYNTAX OK')"

