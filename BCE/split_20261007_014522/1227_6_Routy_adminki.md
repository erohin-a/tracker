<!-- Часть 1227 из 1409 -->
# 6. Роуты админки
*Хлебные крошки:* Трекер — учёт рабочего времени. Handoff-документ / 6. Роуты админки

[◀ 5. Метрики отчётов — как считаем](1226_5_Metriki_otchetov_kak_schitaem.md) | [Оглавление](00_BCE_INDEX.md) | [7. Роли пользователей ▶](1228_7_Roli_polzovateley.md)

---

## 6. Роуты админки

**Аутентификация:**
- `GET /admin/login`, `POST /admin/login`, `GET /admin/logout`
- `GET /admin/setup` — первый запуск (если admin_users пуста)
- `GET /admin/set-lang/{code}` — переключение RU/EN

**Основные страницы:**
- `/admin` — дашборд
- `/admin/employees` (+ create/edit/fire/restore/delete-forever)
- `/admin/departments` (+ create/rename/delete)
- `/admin/computers` (+ assign/revoke/activate/bulk-assign/soft-delete/restore/re-reg-token)
- `/admin/tokens` — bootstrap-токены
- `/admin/reports` — форма и результат
- `/admin/reports/pivot` — **интерактивная сводная (PivotTable.js)**
- `/admin/sessions` — список сессий
- `/admin/calendar` — календарь рабочих дней
- `/admin/settings` — настройки приложения
- `/admin/scheduler` — планировщик задач
- `/admin/schedules` — графики работы
- `/admin/users` — пользователи админки
- `/admin/logins` — история входов
- `/admin/audit` — журнал аудита
- `/admin/trash` — корзина

**API:**
- `POST /api/v1/computers/register`
- `POST /api/v1/sessions`
- `POST /api/v1/records/batch`
- `POST /api/v1/heartbeat`
- `GET /api/v1/client-config` — эффективные настройки для ПК
- `PUT /api/v1/client-settings` — приём изменений от клиента
- `DELETE /api/v1/client-settings` — сброс к глобальным
- `GET /api/v1/version`
- `POST /api/v1/admin/bootstrap-tokens` — выпуск токена
- `POST /api/v1/admin/computers/{uid}/revoke`
- `POST /api/v1/admin/computers/{uid}/re-registration-token`
- `POST /admin/api/pivot-data` — плоские строки для pivot-таблицы

---

