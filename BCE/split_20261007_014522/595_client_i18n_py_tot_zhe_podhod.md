<!-- Часть 595 из 1409 -->
# client/i18n.py — тот же подход
*Хлебные крошки:* client/i18n.py — тот же подход

[◀ server/i18n.py](594_server_i18n_py.md) | [Оглавление](00_BCE_INDEX.md) | [Читаем текущее содержимое ▶](596_Chitaem_tekuschee_soderzhimoe.md)

---

# client/i18n.py — тот же подход
def t(key: str) -> str:
    return TRANSLATIONS.get(key, {}).get(CURRENT_LANG) or key
В PyQt6:
python
QLabel(t("client.status.ready"))
Переключение: кладём язык в сессию (или cookie) для админки, в .env — для клиента. При запросе страницы — язык берётся из сессии, передаётся в шаблон.
________________________________________
Итого — мой ответ
Да, делаем. Не сложно, но объёмно. Начинаем с инфраструктуры, а строки переводим постепенно, чтобы не сойти с ума от переписывания 700 штук за один раз.
Порядок такой:
D1 — обновляем requirements.txt (только alembic).
E1–E5 — инфраструктура i18n (модули + хуки).
D2–D9 — Alembic (как в плане).
Дальше — Спринт 1.2 с новыми таблицами, уже с i18n.
________________________________________
Скрипт D1 — обновляем requirements.txt
Он не меняется (i18n не требует новых пакетов). Просто добавляем alembic.
powershell
powershell
$ErrorActionPreference = "Stop"
$reqPath = "D:\tracker\server\requirements.txt"

