<!-- Часть 1388 из 1409 -->
# --- 4. Состояние → SCP: расписать AdminTab ---
*Хлебные крошки:* --- 4. Состояние → SCP: расписать AdminTab ---

[◀ --- 3. Состояние → Админка: добавить про middleware/next ---](1387_3_Sostoyanie_Adminka_dobavit_pro_middleware_next.md) | [Оглавление](00_BCE_INDEX.md) | [--- 5. Roadmap P0: убрать cookie 401 --- ▶](1389_5_Roadmap_P0_ubrat_cookie_401.md)

---

# --- 4. Состояние → SCP: расписать AdminTab ---
old_scp = "⚠️ BuildTab, AdminTab — заглушки."
new_scp = (
    "⚠️ BuildTab — заглушка.\n"
    "⚠️ AdminTab — заглушка. План (вариант «гибрид»):\n"
    "   * напрямую (работает, даже если api лежит):\n"
    "     - сброс пароля веб-админа (psycopg + bcrypt → UPDATE admin_users)\n"
    "     - смена ADMIN_API_KEY (.env + бэкап + предложение restart api)\n"
    "     - создание пользователя admin заново, если удалён\n"
    "   * через API (когда api жив):\n"
    "     - выпуск bootstrap-токенов\n"
    "     - выпуск re-registration-токенов\n"
    "     - диагностика: api/db/nginx/scheduler — «зелёный/жёлтый/красный»"
)
rp(p, old_scp, new_scp, "состояние: SCP")

