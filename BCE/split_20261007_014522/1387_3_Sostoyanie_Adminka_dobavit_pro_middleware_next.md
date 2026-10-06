<!-- Часть 1387 из 1409 -->
# --- 3. Состояние → Админка: добавить про middleware/next ---
*Хлебные крошки:* --- 3. Состояние → Админка: добавить про middleware/next ---

[◀ Ищем "Скриншоты не собираются	Приватность + 152-ФЗ" — последняя строка таблицы.](1386_Ischem_Skrinshoty_ne_sobirayutsya_Privatnost_152_FZ_poslednyaya_stroka_tablitsy.md) | [Оглавление](00_BCE_INDEX.md) | [--- 4. Состояние → SCP: расписать AdminTab --- ▶](1388_4_Sostoyanie_SCP_raspisat_AdminTab.md)

---

# --- 3. Состояние → Админка: добавить про middleware/next ---
old_admin = "✅ Планировщик, аудит, корзина."
new_admin = (
    "✅ Планировщик, аудит, корзина.\n"
    "✅ Cookie 401 → редирект на /admin/login?next=... (middleware в main.py).\n"
    "✅ После логина возврат на исходную страницу (next, безопасно проверяется)."
)
rp(p, old_admin, new_admin, "состояние: админка")

