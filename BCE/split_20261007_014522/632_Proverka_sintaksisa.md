<!-- Часть 632 из 1409 -->
# Проверка синтаксиса
*Хлебные крошки:* Проверка синтаксиса

[◀ ============================================================](631_part.md) | [Оглавление](00_BCE_INDEX.md) | [Небольшой smoke-тест: проверим, что t() работает ▶](633_Nebolshoy_smoke_test_proverim_chto_t_rabotaet.md)

---

# Проверка синтаксиса
python -c "import ast; ast.parse(open(r'$i18nPath', encoding='utf-8').read()); print('SYNTAX OK')"

