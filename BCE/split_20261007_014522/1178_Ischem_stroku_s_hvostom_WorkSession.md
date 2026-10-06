<!-- Часть 1178 из 1409 -->
# Ищем строку с хвостом ), WorkSession
*Хлебные крошки:* Ищем строку с хвостом ), WorkSession

[◀ 2. Пробуем распарсить](1177_2_Probuem_rasparsit.md) | [Оглавление](00_BCE_INDEX.md) | [Найдём все функции экспорта отчёта ▶](1179_Naydem_vse_funktsii_eksporta_otcheta.md)

---

# Ищем строку с хвостом ), WorkSession
bad = "    ), WorkSession"
good = "    )"

found = False
for i, line in enumerate(lines):
    if line.rstrip() == bad:
        lines[i] = good
        found = True
        print(f"OK: строка {i+1} исправлена: '{bad}' -> '{good}'")
        break

if not found:
    print("WARN: строка '    ), WorkSession' не найдена")
    # Ищем любые строки, содержащие '), WorkSession'
    for i, line in enumerate(lines, 1):
        if "WorkSession" in line and ")" in line and "from" not in line and "import" not in line:
            print(f"  строка {i}: {line}")

if found:
    PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    content = "\n".join(lines)
    try:
        ast.parse(content)
        print("SYNTAX OK")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: line={e.lineno}, msg={e.msg}")
        print(f"Текст: {e.text}")
'@

[System.IO.File]::WriteAllText("D:\tracker\_fix_line265.py", $patcher, [System.Text.UTF8Encoding]::new($false))
Write-Host "=== Фикс строки 265 ===" -ForegroundColor Cyan
& client\.venv\Scripts\python.exe _fix_line265.py
Что ожидаем
text
OK: строка 265 исправлена: '    ), WorkSession' -> '    )'
SYNTAX OK
После фикса
Проверь ещё раз диагностикой:
powershell
& client\.venv\Scripts\python.exe _diag_tasks.py
Должно быть SYNTAX OK и никаких следов ), WorkSession.
Пересобери и перезапусти:
powershell
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose logs api --tail=20
Через 30 минут проверь /admin/scheduler. Должна появиться зелёная строка close_stale_sessions | успех.
Запускай, пришли вывод.
>> & client\.venv\Scripts\python.exe _fix_line265.py === Фикс строки 265 === OK: строка 265 исправлена: ' ), WorkSession' -> ' )' SYNTAX OK (.venv) PS D:\tracker> & client\.venv\Scripts\python.exe _diag_tasks.py === Строки 250-285 === 250 | def close_stale_sessions(db: Session) -> str: 251 | """ 252 | Закрывает сессии, которые клиент так и не закрыл. 253 | 254 | Сценарий: сотрудник ушёл домой, забыл нажать «Конец работы», 255 | ПК выключили или клиент упал. Сессия висит в БД с session_end = NULL. 256 | Такая сессия портит отчёты (был случай: 17 часов за один день). 257 | 258 | Запускается каждые 30 минут (cron */30 * * * *). 259 | """ 260 | from .models import ( 261 | AppSetting as _AppSetting, 262 | Record as _Record, 263 | WorkSession, 264 | AuditLog, 265 | ) 266 | 267 | row = db.query(_AppSetting).filter( 268 | _AppSetting.key == "stale_session_hours" 269 | ).first() 270 | try: 271 | stale_hours = max(1, min(24, int(row.value))) if row else 2 272 | except (ValueError, TypeError): 273 | stale_hours = 2 274 | 275 | cutoff = _now() - timedelta(hours=stale_hours) 276 | 277 | stale = ( 278 | db.query(WorkSession) 279 | .filter( 280 | WorkSession.session_end.is_(None), 281 | WorkSession.session_start < cutoff, 282 | ) 283 | .all() 284 | ) 285 | === Все строки с 'from .models import' === 217 | from .models import AppSetting as _AppSetting 218 | 219 | def _get(key: str, default: str) -> str: 220 | row = db.query(_AppSetting).filter(_AppSetting.key == key).first() 221 | return row.value if row else default 222 | 223 | tz_name = _get("report_timezone", "Europe/Moscow") --- 260 | from .models import ( 261 | AppSetting as _AppSetting, 262 | Record as _Record, 263 | WorkSession, 264 | AuditLog, 265 | ) 266 | --- SYNTAX OK нажал принудительный запуск скриншот во вложении
Скриншот показывает, что задача всё ещё падает с NameError: name 'AuditLog' is not defined. Хотя синтаксис OK и импорт вроде бы на месте.
Причина — Python видит импорт внутри функции, но ошибка всё равно возникает. Это происходит, потому что в файле есть проблема с областью видимости: AuditLog используется в другой функции, где он не импортирован, ИЛИ старая версия файла в контейнере (не пересобралась).
Смотрим внимательно:
Строки 260-265 — импорт внутри close_stale_sessions.
Но что если AuditLog используется не внутри close_stale_sessions, а в aggregate_daily_stats или другой функции?
Или: контейнер не пересобрался, и в нём старая версия файла.
Скриншот показывает: последний запуск 25.09.2026 21:20 — ошибка NameError: name 'AuditLog' is not defined. До этого 20:54 — та же ошибка.
Значит, docker compose up -d --build не пересобрал образ, или пользователь ещё не пересобирал после фикса строки 265.
Стоп — судя по выводу, скрипт _fix_line265.py прошёл, потом _diag_tasks.py показал SYNTAX OK. Но пользователь пишет "нажал принудительный запуск скриншот во вложении" — и на скриншоте всё ещё ошибка AuditLog.
Это значит: контейнер всё ещё работает со старой версией tasks.py, потому что не было docker compose up -d --build после фикса.
Нужно:
Пересобрать образ.
Или, если контейнер запущен и файл tasks.py не примонтирован — пересборка обязательна.
Также обратим внимание: в close_stale_sessions импорт теперь правильный. Но NameError: name 'AuditLog' is not defined на строке 21:20 — это уже после фикса строки 265? Смотрю: пользователь запустил фикс, потом diag, потом "нажал принудительный запуск". Если он не пересобрал контейнер, то запуск идёт по старой версии в контейнере.
Даю команду на пересборку.
Также — обратим внимание, что в PowerShell после _fix_line265.py и _diag_tasks.py пользователь не выполнил docker compose down && up -d --build. Обязательно надо это сделать.
Кроме того — возможно, надо проверить, что в контейнере действительно новая версия файла. Дам команду проверки и пересборки.
Синтаксис починен, но задача всё ещё падает с NameError: AuditLog. Причина одна: контейнер не пересобран — он всё ещё работает со старой версией tasks.py, которая загружена в образ при последней сборке. Правки на хосте без --build не доходят.
Проверим и пересоберём.
Шаг 1 — проверить, что в контейнере старая версия
powershell
Set-Location D:\tracker
Write-Host "=== Что в контейнере сейчас ===" -ForegroundColor Cyan
docker compose exec -T api grep -n "WorkSession" /app/server/tasks.py | Select-Object -First 5
Write-Host ""
docker compose exec -T api grep -n "AuditLog" /app/server/tasks.py | Select-Object -First 5
Если увидишь старую строку from .models import AppSetting as _AppSetting, Record as _Record — это точно старая версия.
Шаг 2 — пересобрать образ с новым кодом
powershell
Set-Location D:\tracker
Write-Host "=== Пересборка ===" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25
docker compose ps
Write-Host ""
Write-Host "=== Проверка, что новая версия в контейнере ===" -ForegroundColor Cyan
docker compose exec -T api grep -n "WorkSession," /app/server/tasks.py
docker compose exec -T api grep -n "AuditLog," /app/server/tasks.py
Ожидаем:
Все три контейнера Up.
В grep увидим строки WorkSession, и AuditLog, — значит, новая версия внутри.
Шаг 3 — принудительно запустить задачу
Через веб-интерфейс /admin/scheduler нажми «Запуск» у задачи close_stale_sessions. Или через консоль:
powershell
docker compose exec -T api python -c @"
from server.database import SessionLocal
from server import tasks
db = SessionLocal()
try:
    result = tasks.close_stale_sessions(db)
    print('OK:', result)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
"@
Если увидишь OK: Зависших сессий нет или OK: Закрыто зависших сессий: N — победа.
Если снова NameError — значит, в контейнере всё ещё старая версия, и надо смотреть, почему docker compose up -d --build не подхватывает изменения.
Шаг 4 — если и после пересборки ошибка
Тогда проверим содержимое контейнера целиком:
powershell
docker compose exec -T api cat /app/server/tasks.py | Select-String -Pattern "from .models import" -Context 0,8
Это покажет реальный импорт в контейнере. Если он не совпадает с тем, что на хосте — значит, Docker не пересобирает образ (например, из-за кэша слоёв или потому что файл tasks.py в .dockerignore).
Начни с шага 1 и 2. Пришли вывод grep из шага 1 (что в контейнере до пересборки) и вывод команды из шага 3 (запуск задачи).
переходим к следующим шогам
Пользователь показал скриншот — задача close_stale_sessions теперь работает успешно:
#66 (25.09.2026 21:40) — успех, "Зависших сессий нет (порог 2ч)"
#65 (25.09.2026 21:30) — успех, "Зависших сессий нет (порог 2ч)"
Значит пересборка прошла, задача работает. Отлично.
Теперь переходим к следующим шагам. По моему плану приоритетов:
Приоритет 1 — закончить отчёты:
? close_stale_sessions — сделано
XLSX/CSV/PDF — новые колонки (Интенсивная, переопределённая Пауза)
Кнопка «Вчера» — ставит только date_from
Cookie админки: 401 ? редирект на /login
Начну с пункта 2 (XLSX/CSV/PDF) — это самое важное для отчётов, потому что при выгрузке данные сейчас неполные.
Смотрю на скриншот отчёта из предыдущего сообщения — там видно:
В таблице есть колонки: Рабочий день | Сотрудник | 1C ID | Отдел | Сессий | Отработано | С трекером | Интенсивная | Эффективно | Пауза
Раскрытие сессии показывает: Начало | Конец | Отработано | Интенсивная | Эффективно | Пауза | Авар.
Раскрытие программ показывает: Программа | Время | Клавиатура | Мышь
Всё это уже есть в HTML. Но при экспорте в XLSX/CSV/PDF — там ещё старые колонки (Отработано / С трекером / Эффективно, без Интенсивной и переопределённой Паузы).
Мне нужно посмотреть текущий _report_to_table в web_admin.py, чтобы понять, что там сейчас. И _render_csv, _render_xlsx, _render_pdf.
Давай сначала диагностику — покажу текущее содержимое этих функций.
Актуальный план:
Диагностика: посмотреть _report_to_table, _render_csv, _render_xlsx, _render_pdf в web_admin.py
Дать патч с новыми колонками
Проверить на живом отчёте
Также надо не забыть про:
Кнопка «Вчера» в reports.html
Cookie 401 ? редирект
Начну с диагностики — покажу функции.
Формат ответа:
Подтверждение что фикс сработал
Диагностический скрипт
Просьба прислать вывод
Пусть будет компактно.
Отлично, задача close_stale_sessions теперь работает — в истории видно два успешных запуска подряд (#65 и #66). Баг закрыт.
Переходим к следующим шагам. По приоритету — доделать экспорт отчётов (XLSX/CSV/PDF), потом кнопка «Вчера» и редирект на логин.
Что делаем
Экспорт в XLSX/CSV/PDF сейчас использует старые колонки — без «Интенсивной» и с прежней формулой «Паузы». Надо привести к тому, что видно в HTML-версии отчёта:
Рабочий день / Месяц / Сотрудник / 1C ID / Отдел / Компьютер
Сессий
Отработано (span)
С трекером (union)
Интенсивная ? новое
Эффективно
Пауза ? переопределена как pause_seconds + (Отработано ? С трекером)
Чтобы не гадать с текущим кодом, сначала посмотрим, что сейчас в _report_to_table и функциях экспорта.
Диагностика — что сейчас в web_admin.py
Скопируй блок целиком в PowerShell и запусти:
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$diag = @'
import re
from pathlib import Path

PATH = Path(r"D:\tracker\server\web_admin.py")
content = PATH.read_text(encoding="utf-8")

