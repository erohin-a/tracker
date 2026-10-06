<!-- Часть 752 из 1409 -->
# ---------- Патч B: импорт функции t() для использования в замыкании ----------
*Хлебные крошки:* ---------- Патч B: импорт функции t() для использования в замыкании ----------

[◀ ------------------------------------------------------------](751_part.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](753_part.md)

---

# ---------- Патч B: импорт функции t() для использования в замыкании ----------
if ($content -match "from \.i18n import .*\bt\b") {
    Write-Host "Патч B: t уже импортирован" -ForegroundColor Yellow
    "stepB: t already imported" | Out-File $log -Append -Encoding utf8
} else {
    $oldImport = "from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang"
    $newImport = "from .i18n import SUPPORTED_LANGS, DEFAULT_LANG, is_valid_lang, t"
    if ($content.Contains($oldImport)) {
        $content = $content.Replace($oldImport, $newImport)
        Write-Host "Патч B: OK — t добавлен в импорт" -ForegroundColor Green
        "stepB: t imported" | Out-File $log -Append -Encoding utf8
        $changed = $true
    } else {
        Write-Host "Патч B: НЕ НАЙДЕН импорт из .i18n" -ForegroundColor Red
        "stepB: FAILED - no import line" | Out-File $log -Append -Encoding utf8
    }
}

if ($changed) {
    try {
        [System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "`nOK: web_admin.py сохранён" -ForegroundColor Green
        "saved" | Out-File $log -Append -Encoding utf8
    } catch {
        Write-Host "ОШИБКА сохранения: $_" -ForegroundColor Red
        "ERROR: $_" | Out-File $log -Append -Encoding utf8
    }
} else {
    Write-Host "`nФайл не изменён" -ForegroundColor Yellow
}

python -c "import ast; ast.parse(open(r'D:\tracker\server\web_admin.py', encoding='utf-8').read()); print('SYNTAX OK')"

"=== E2-fix DONE $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Host "`n=== E2-fix завершён. Лог: $log ===" -ForegroundColor Cyan
________________________________________
Скрипт E2d2 — пересборка + получение логов
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

Write-Host "=== Пересборка API ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 20

Write-Host "`n=== Статус ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Чистим логи API перед тестом ===" -ForegroundColor Cyan
Write-Host "Логи API будут показывать только то, что произойдёт после этого момента." -ForegroundColor Gray

Write-Host "`n=== Что делать сейчас ===" -ForegroundColor Green
Write-Host "1. Откройте https://localhost/admin — увидите RU/EN в шапке" -ForegroundColor Green
Write-Host "2. НЕ нажимайте пока. Сначала запустите в ВТОРОМ окне PowerShell:" -ForegroundColor Yellow
Write-Host "   docker compose logs api -f --tail=5" -ForegroundColor Yellow
Write-Host "3. Теперь нажмите EN в браузере" -ForegroundColor Green
Write-Host "4. Если 500 — скопируйте из второго окна ВСЁ, начиная с Traceback" -ForegroundColor Green
________________________________________
Что мне прислать, если фикс не помог
Одним сообщением:
Вывод скрипта E2b-fix (видно, применился ли Патч A и B).
Вывод docker compose logs api --tail=60 — после того, как нажали EN и получили 500.
Содержимое лога: Get-Content D:\tracker\_e2fix.log.
По трейсбеку я скажу конкретную строку в web_admin.py, где упало.
________________________________________
Что мы сделали и почему это правильно
Было: _ регистрировалась как глобал Jinja, читала язык из contextvars.
Проблема: contextvars ненадёжны в sync-обработчиках FastAPI + отложенном рендере Starlette.
Стало: каждый запрос создаёт свою _, замкнутую на конкретный язык.
Плюс: работает без вариантов, даже если Starlette поменяет внутренности.
Побочный бонус — в будущем, когда у каждого пользователя будет свой язык (admin_users.language), мы просто изменим источник языка в context processor — от cookie к полю пользователя. А шаблоны трогать не надо.
________________________________________
Запусти E2b-fix, потом E2d2. Если после пересборки EN работает — прекрасно, идём дальше (E4 — клиентский i18n). Если снова 500 — пришли трейсбек, докопаемся до сути.
Патч A: НЕ НАЙДЕН старый блок context processor Выполните: docker compose exec api grep -n '_i18n_context_processor' /app/server/web_admin.py Патч B: НЕ НАЙДЕН импорт из .i18n Файл не изменён SYNTAX OK === E2-fix завершён. Лог: D:\tracker\_e2fix.log ===
Пользователь прав. Мы обсудили в самом начале Спринта 5, что настройки напоминания должны быть у каждого сотрудника свои, и их можно менять с обеих сторон (сервер ? клиент), с приоритетом сервера.
Сейчас я сделал настройки глобальными (в AppSetting) — они одинаковые для всех. Это неправильно по плану.
Что нужно переделать:
План правильной реализации
На сервере:
Глобальные настройки в AppSetting — это дефолты для всех.
Индивидуальные настройки — в новой таблице employee_settings (или в employees дополнительные колонки). Поля:
employee_id (FK)
reminder_enabled (nullable — если NULL, берётся глобальное)
reminder_threshold_minutes
reminder_repeat_minutes
reminder_max_per_day
end_of_day_hour
end_of_day_minute
updated_at, updated_by
Endpoint /api/v1/client-config должен возвращать эффективные настройки для конкретного ПК. ПК знает X-Computer-Uid ? находим employee_id ? берём персональные настройки, если есть, иначе глобальные.
UI: на странице сотрудника — вкладка/секция «Настройки напоминания» с полями, где пустое значение = «как у всех», заполненное = «своё». Кнопка «Сбросить к общим».
На клиенте:
Пользователь может поменять свои настройки локально — они сохраняются в SQLite, синхронизируются с сервером.
При конфликте приоритет у сервера. То есть: клиент при синхронизации отправляет свои изменения на сервер (PUT /api/v1/client-settings), сервер решает — принять или отклонить. Если сервер недавно менял — приоритет сервера, клиент получает ответ и обновляет локально.
Это как раз то, что мы обсуждали: «Если по времени это произошло одновременно — приоритет на сервер».
Что делать сейчас
Сейчас нужно:
Создать модель EmployeeSettings (или добавить поля в employees).
Alembic-миграция.
Обновить /api/v1/client-config — брать настройки по X-Computer-Uid.
UI: страница /admin/employees/{id}/settings.
Endpoint PUT /api/v1/client-settings — приём изменений от клиента.
Клиентская часть — учтёт это в A2.
Это существенно больше, чем я анонсировал. Давай сделаем правильно, поэтапно.
Ответ пользователю
Сначала объясню, что я сделал не так, и предложу правильную архитектуру. Потом дам скрипты.
Мой план:
Этап 1 (сейчас)
Создать модель EmployeeSettings с полями напоминания (все nullable).
Alembic-миграция.
Переделать /api/v1/client-config — читать X-Computer-Uid из заголовка, находить employee_id, брать персональные, иначе глобальные.
UI: страница /admin/employees/{id}/settings с формой.
Этап 2 (после)
Endpoint PUT /api/v1/client-settings — клиент отправляет свои изменения.
Логика приоритета (server wins) + запись в аудит.
Этап 3
Клиентская часть (в A2, которую делаем позже) — локальный UI + синхронизация.
Начну с объяснения и первого этапа. Скрипты:
Модель EmployeeSettings в models.py.
Alembic-миграция через alembic revision --autogenerate (или ручная).
Патч /api/v1/client-config — эффективные настройки.
Роуты + шаблон страницы /admin/employees/{id}/settings.
i18n.
Учитывая размер, разобью на 2-3 сообщения.
Начнём. Сначала объясню подход, потом сделаем модель + миграцию.
Стоп, важный момент: пользователь использует Alembic. Мне нужно:
Добавить модель EmployeeSettings.
Запустить alembic revision --autogenerate через docker.
Применить.
Или можно через SQL ALTER TABLE. Но у нас же Alembic! Давай правильно — через Alembic.
Порядок:
Добавить модель в models.py.
Запустить docker compose exec api alembic revision --autogenerate -m "add employee_settings".
Проверить миграцию.
Применить — docker compose exec api alembic upgrade head (или через entrypoint).
Хорошо, начнём.
На самом деле, поскольку мы уже глубоко ушли в Спринт 5 часть A и сделали глобальные настройки, правильнее:
Вариант 1: Сначала закончить A (глобальные настройки + клиент), а потом добавить индивидуальные поверх. Тогда базовый функционал заработает быстрее, а «поверх» — это апгрейд.
Вариант 2: Сразу сделать правильно — с индивидуальными.
Пользователь хочет правильно. Давай вариант 2, но без выбрасывания уже сделанного:
Глобальные настройки остаются — это дефолт для всех.
Добавляем индивидуальные — те же поля в новой таблице employee_settings, все nullable.
В /api/v1/client-config: берём X-Computer-Uid ? находим employee_id ? если есть запись в employee_settings, мержим её поля поверх глобальных.
На UI сотрудника — форма с полями, где пусто = дефолт, заполнено = override.
Это элегантно и не выбрасывает работу.
Хорошо, пишу ответ.
По объёму — начну с объяснения и первого скрипта (модель + миграция). Потом следующим сообщением — патч endpoint и UI.
Или можно сразу дать всё в одном сообщении — но это будет много. Давай сначала модель+миграцию+endpoint, потом UI.
Хм, а можно ли ещё и endpoint сразу? Давай сделаю:
Модель EmployeeSettings (одна таблица с полями).
Alembic миграция.
Патч /api/v1/client-config — эффективные настройки.
Проверка.
Потом UI отдельно.
Погнали.
Ты прав, это моя ошибка. Давай переделаем правильно
Извиняюсь — я сделал глобальные настройки напоминания (одни для всех), а мы договаривались, что у каждого сотрудника они свои, и можно менять с обеих сторон (клиент ? сервер).
Правильная архитектура
Три уровня настроек:
Глобальные дефолты (AppSetting) — то, что мы уже сделали. Это значения по умолчанию для всех сотрудников. Если у сотрудника нет персональных — берётся отсюда.
Индивидуальные настройки (employee_settings — новая таблица). Каждое поле nullable. NULL = «как у всех», заполнено = override.
Локальные настройки клиента — те же поля в SQLite на ПК. Синхронизируются с сервером:
Клиент пушит свои изменения на сервер.
Сервер решает, что принять (при конфликте — приоритет сервера, как мы обсуждали).
Клиент получает ответ и обновляет локальные.
Endpoint /api/v1/client-config:
Читает X-Computer-Uid из заголовка.
Находит employee_id этого ПК.
Мержит: глобальные дефолты ? персональные override сотрудника.
Возвращает эффективные значения.
Что делаем сейчас (часть 1):
Создать модель EmployeeSettings.
Alembic-миграция.
Переделать /api/v1/client-config — эффективные настройки для конкретного ПК.
Проверить.
Следующее сообщение (часть 2):
UI: страница /admin/employees/{id}/settings с полями, где «пусто = как у всех».
Endpoint PUT /api/v1/client-settings для приёма изменений от клиента.
Начинаем с части 1.
________________________________________
Скрипт P1 — модель EmployeeSettings
powershell
$ErrorActionPreference = "Continue"
$path = "D:\tracker\server\models.py"
$content = [System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false))

if ($content.Contains("class EmployeeSettings")) {
    Write-Host "Модель уже есть" -ForegroundColor Yellow
} else {
    $addition = @'


