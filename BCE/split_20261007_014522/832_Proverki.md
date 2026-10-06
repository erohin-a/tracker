<!-- Часть 832 из 1409 -->
# Проверки
*Хлебные крошки:* Проверки

[◀ ============================================================](831_part.md) | [Оглавление](00_BCE_INDEX.md) | [1. menu.profile ▶](833_1_menu_profile.md)

---

# Проверки
checks = [
    "/api/v1/client-settings",
    "server_recently",
    "ClientSettingsIn",
    "client_update",
]
for c in checks:
    found = c in new_content
    print(f"  {'OK' if found else 'MISS'}: {c}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_patch_client_settings_endpoint.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: _patch_client_settings_endpoint.py создан" -ForegroundColor Green
Write-Host ""
Write-Host "=== Запуск ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _patch_client_settings_endpoint.py
Что ожидаем:
text
OK: /api/v1/client-settings добавлен
SYNTAX OK
  OK: /api/v1/client-settings
  OK: server_recently
  OK: ClientSettingsIn
  OK: client_update
Важно: я использую ClientSettingsIn и ClientSettingsOut из schemas.py, но не импортировал их в main.py. Проверим импорты — если их нет, надо добавить. Посмотрим после запуска.
________________________________________
Порядок запусков
Скрипт 1 — проверка admin/login (30 сек)
Скрипт 2 — Pydantic схема (30 сек)
Скрипт 3 — патч client-config (2 мин)
Скрипт 4 — новый endpoint PUT /client-settings (2 мин)
Запускай по порядку и пришли мне вывод каждого. После Скрипта 3 и 4 — не пересобирай сразу, я должен проверить, что импорты ClientSettingsIn в main.py корректны, иначе будет NameError при старте.
Если в Скрипте 4 увидим MISS: ClientSettingsIn — значит нужно добавить импорт в main.py, дам отдельный мини-скрипт.
________________________________________
Что дальше (следующее сообщение)
После того как оба endpoint'а заработают и пересоберём:
UI: страница /admin/employees/{id}/settings — форма с полями + кнопка "Сбросить к общим".
Кнопка "Настройки напоминания" в карточке сотрудника.
Клиентская часть (этап 3): client/reminder.py, патчи main.py клиента.
Погнали. Запускай 1?2?3?4 по очереди, присылай выводы.
Скрипт 1 PS D:\tracker> $ErrorActionPreference = "Continue" >> Set-Location D:\tracker >> >> Write-Host "=== /admin/login ===" -ForegroundColor Cyan >> curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin/login" >> >> Write-Host "`n=== /admin (должен быть 303 на логин) ===" -ForegroundColor Cyan >> curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin" >> >> Write-Host "`n=== /admin/settings ===" -ForegroundColor Cyan >> curl.exe -k -s -o NUL -w "HTTP %{http_code}`n" "https://localhost/admin/settings" === /admin/login === HTTP 303 === /admin (должен быть 303 на логин) === HTTP 301 === /admin/settings === HTTP 401 PS D:\tracker>
Отлично. Из диагностики:
i18n — почти всё на месте, отсутствует только menu.profile
logins.html — структура понятна, в нём тоже есть крокозябры [Р»РѕРіРё] (это "Логи") и в†ђ (стрелка)
users.html — тоже есть крокозябры, но это отдельная тема
Теперь моя задача:
Добавить menu.profile + i18n ключи для profile страницы
Патчить base.html — разграничить sidebar по ролям + добавить ссылку на profile
Создать /admin/profile — страницу профиля
Проверить/починить крокозябры в users.html и logins.html (убрать [СЂРµРґ] и т.д.)
Но сначала — я должен показать контекст base.html (строки 140-260). Пользователь не запустил вторую команду. Мне нужно попросить показать base.html.
Хотя... по выводу я уже вижу большинство строк. Мне нужно увидеть полный контекст, чтобы патчить точно. Давай запрошу.
Но чтобы не терять время, я могу:
Добавить i18n ключи
Показать base.html и запросить патч
Параллельно — начать с чистки крокозябр в users.html и logins.html
Давай сделаю всё сразу.
Стоп, нужно подумать. base.html у меня нет целиком. Я знаю только некоторые строки (140-198). Но мне нужно:
Строки 140 — начало sidebar
Строки 200-260 — конец sidebar и main content
Где именно вставлять условия по ролям
Давай попрошу показать base.html строки 130-260, а параллельно дам скрипт для i18n ключей.
Также надо решить, что с крокозябрами в users.html. Судя по всему, там [СЂРµРґ] — это [ред] (редактировать) — испортилось при копировании. Или это emoji ??. Надо заменить на чистые emoji или на текст без emoji.
Аналогично в logins.html — [Р»РѕРіРё] это [логи], в†ђ это ?.
Давай сначала i18n ключи, потом base.html диагностика, потом патчи.
Пусть ответ будет:
Добавляем i18n ключи (menu.profile + profile.*)
Запрос base.html для точного патча
Пока параллельно — починим крокозябры в users.html и logins.html
Или проще — давай сразу патчим base.html по тому что вижу (я знаю структуру). Патч такой:
Обернуть группы в условия по ролям
Заменить ссылку на logout / добавить перед ней ссылку на profile
Давай напишу патч по кусочкам. Мне нужно:
Строка 141-143 — группа Main (Дашборд) — доступна всем
Строка 149-161 — группа Directories (Сотрудники, Отделы, Графики, Компьютеры) — доступна admin, operator, hr, manager (без viewer)
Строка 165-179 — группа Data (Отчёты, Сессии, Календарь, Аудит) — доступна всем кроме viewer
Строка 185-199 — группа Admin (Токены, Планировщик, Пользователи, Входы, Корзина, Настройки) — только admin и оператор (частично)
Конкретная матрица:
Пункт	admin	operator	hr	manager	viewer
Дашборд	?	?	?	?	?
Сотрудники	?	?	?	?	?
Отделы	?	?	?	?	?
Графики	?	?	?	?	?
Компьютеры	?	?	?	?	?
Отчёты	?	?	?	? (свой отдел)	?
Сессии	?	?	?	?	?
Календарь	?	?	?	?	?
Аудит	?	?	?	?	?
Токены	?	?	?	?	?
Планировщик	?	?	?	?	?
Пользователи	?	?	?	?	?
Входы	?	?	?	?	?
Корзина	?	?	?	?	?
Настройки	?	?	?	?	?
Слишком сложно. Давай упростим:
admin — всё
operator — все группы, кроме «Пользователи», «Входы», «Корзина», «Настройки», «Планировщик», «Аудит»
hr — только «Справочники» (Сотрудники, Отделы, Графики, Календарь) + Дашборд + Отчёты
manager — Дашборд + Отчёты + Сотрудники
viewer — Дашборд + Отчёты
Это можно реализовать через {% if current_role in (...)%}.
Хорошо. Давай сделаю патч:
Сначала i18n — menu.profile + profile.* + поменять/добавить нужные ключи
Запросить base.html строки 130-270 для точного anchor
Параллельно — фикс крокозябр в users.html и logins.html
Начну.
Отлично — не хватает только menu.profile. Действуем по шагам
Скрипт 1 — i18n-ключи (profile + меню)
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$patcher = @'
import ast

I18N = r"D:\tracker\server\i18n.py"

with open(I18N, "r", encoding="utf-8") as f:
    content = f.read()

changed = []

