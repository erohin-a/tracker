<!-- Часть 1390 из 1409 -->
# --- 6. Roadmap P1: уточнить SCP ---
*Хлебные крошки:* --- 6. Roadmap P1: уточнить SCP ---

[◀ --- 5. Roadmap P0: убрать cookie 401 ---](1389_5_Roadmap_P0_ubrat_cookie_401.md) | [Оглавление](00_BCE_INDEX.md) | [--- 7. Roadmap P1: добавить UX-аудит --- ▶](1391_7_Roadmap_P1_dobavit_UX_audit.md)

---

# --- 6. Roadmap P1: уточнить SCP ---
old_p1 = "SCP BuildTab/AdminTab."
new_p1 = (
    "SCP AdminTab — локальное управление без веб-доступа (гибрид):\n"
    "  напрямую: сброс пароля веб-админа, смена ADMIN_API_KEY,\n"
    "  пересоздание admin-пользователя (psycopg + bcrypt + .env);\n"
    "  через API: выпуск bootstrap/re-registration токенов,\n"
    "  диагностика api/db/nginx/scheduler.\n"
    "SCP BuildTab — сборка клиента (PyInstaller + Inno Setup)."
)
rp(p, old_p1, new_p1, "roadmap: SCP AdminTab (гибрид)")

