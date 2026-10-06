<!-- Часть 1006 из 1409 -->
# Добавляем QObject-обёртку с сигналом после SUPPORTED_THEMES
*Хлебные крошки:* Добавляем QObject-обёртку с сигналом после SUPPORTED_THEMES

[◀ Диагностика: сколько раз datetime используется](1005_Diagnostika_skolko_raz_datetime_ispolzuetsya.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](1007_part.md)

---

# Добавляем QObject-обёртку с сигналом после SUPPORTED_THEMES
old_marker = '''SUPPORTED_THEMES = [
    {"code": "light"},
    {"code": "dark"},
    {"code": "system"},
]
'''

new_block = '''SUPPORTED_THEMES = [
    {"code": "light"},
    {"code": "dark"},
    {"code": "system"},
]


