# --- 8. Приоритеты: обновить P0 ---

*Часть 100 из 100. Источник: `BCE.md`.*

[◀ D:\tracker\tools\grep_pivot.py](099_D_tracker_tools_grep_pivot_py.md) | [Оглавление](00_BCE_INDEX.md) | — ▶

---

# --- 8. Приоритеты: обновить P0 ---
old_prio = "Закрыть P0: cookie 401, установщик, публикация версий."
new_prio = (
    "Закрыть P0: установщик клиента, публикация версий.\n"
    "Параллельно P1: SCP AdminTab (аварийный доступ), SCP BuildTab,\n"
    "UX-аудит админки и клиента (тултипы, интуитивность), ca.pem через UI."
)
rp(p, old_prio, new_prio, "приоритеты: P0/P1")

# --- 9. Добавить раздел про следующий чат ---
old_end = "Готово. Один файл выше. Следующий — обновить 00_INDEX.md."
new_end = (
    "---\n\n"
    "## 11. Что делать в следующем чате (после handoff)\n\n"
    "1. Глубокий UX-аудит админки и клиента:\n"
    "   - интуитивность навигации, названий, кнопок;\n"
    "   - что упущено, где пользователь может запутаться;\n"
    "   - список мест под всплывающие подсказки (title=, Bootstrap tooltip);\n"
    "   - единый стиль сообщений об ошибках и успехе.\n"
    "2. Затем — SCP AdminTab (вариант «гибрид»).\n"
    "3. Затем — установщик клиента (Inno Setup) и публикация версий.\n"
)
rp(p, old_end, new_end, "раздел 11: план следующего чата")

print(f"\nБэкап: {BACKUP}")
print("OK")
Патчер 2 — D:\tracker\tools\kb_patch_5_scp_admin.py
python
# D:\tracker\tools\kb_patch_5_scp_admin.py
# Обновляет документацию SCP: 05_SCP\01_OVERVIEW.md и 05_SCP\04_ADMIN.md.
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"D:\tracker")
KB = ROOT / "docs"
BACKUP = ROOT / "_backup_kb_patch" / datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP.mkdir(parents=True, exist_ok=True)

def bak(p: Path):
    rel = p.relative_to(ROOT)
    dst = BACKUP / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)

# ============================================================
# 1. 05_SCP\04_ADMIN.md — переписать
# ============================================================
p = KB / "05_SCP" / "04_ADMIN.md"
if p.exists():
    bak(p)
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(
    """# 04_ADMIN.md — SCP AdminTab (локальное управление без веб-доступа)

**Статус:** план (вариант «гибрид»).
**Назначение:** SCP — «аварийный люк». Если админ забыл пароль, потерял доступ к веб-админке или сломал сессию, он всегда может запустить SCP локально и восстановить доступ.

## Принцип «гибрид»

- **Критичные операции — напрямую** (файл `.env` + БД через `psycopg`). Работают, даже если api/db/nginx лежат.
- **Удобные операции — через API** (когда api жив). Не дублируем логику, используем существующие эндпоинты `/api/v1/admin/*`.

Проверка «жив ли API» — `GET /api/v1/version` раз в 30 секунд. В UI рядом с «api-кнопками» бейдж **онлайн / офлайн**.

## Группа 1. Напрямую (аварийный режим)

| Действие | Что делает SCP |
|---|---|
| Сброс пароля веб-админа | `psycopg` → `UPDATE admin_users SET password_hash=..., password_changed_at=now()`. Хеш через `bcrypt` (та же либа, что в сервере). Запись в `audit_log`: `actor="scp:local"`, `action="password_reset"` |
| Смена `ADMIN_API_KEY` | Генерирует `secrets.token_urlsafe(48)`. Бэкап `.env` в `_backup_env\\<ts>.env`. Правка строки `ADMIN_API_KEY=`. Предлагает «Перезапустить api сейчас?» (docker compose restart api) |
| Пересоздание пользователя `admin` | Если админ удалил себя из БД — создаёт заново с ролью `admin` и заданным паролем |

## Группа 2. Через API (нормальный режим)

| Действие | Эндпоинт |
|---|---|
| Выпуск bootstrap-токена | `POST /api/v1/admin/bootstrap-tokens` (заголовок `x-admin-token`) |
| Выпуск re-registration-токена | `POST /api/v1/admin/computers/{uid}/re-registration-token` |
| Список ПК для выбора | чтение БД напрямую либо через admin API |
| Диагностика api | `GET /api/v1/version` |
| Диагностика БД | `SELECT count(*) FROM task_runs WHERE status='failed' AND started_at > now() - interval '24 hours'` |
| Диагностика контейнеров | `docker compose ps` → парсинг, статус в UI |

## Группа 3. Опционально (если решим расширять)

- Бэкап БД: `docker compose exec db pg_dump` → `D:\\tracker\\backups\\<ts>.sql.gz`.
- Просмотр `.env` (маскировать секреты, раскрыть по клику).
- Открыть `docker compose logs api --tail=200` в окно SCP.

## Безопасность

- Все изменения — в `audit_log`.
- Пароли — только в виде хеша, никогда не логируются.
- Бэкап `.env` перед записью — обязательно.
- SCP работает локально, под админ-аккаунтом Windows.

## Что нужно технически

- Библиотеки: `psycopg[binary]`, `bcrypt` (проверить версию — как в сервере).
- Прямые SQL — без импорта `server.models` (SCP не должен тянуть серверный код).
- Парсер `.env` — простой, сохраняет комментарии и структуру.

## Связанные файлы

- `05_SCP\\01_OVERVIEW.md` — общее описание SCP.
- `05_SCP\\02_CERTIFICATES.md` — вкладка «Сертификат».
- `05_SCP\\03_BUILD.md` — вкладка «Сборка».
- `03_SERVER\\04_AUTH.md` — логика аутентификации на сервере.
""",
    encoding="utf-8",
)
print("[OK] 04_ADMIN.md переписан")

# ============================================================
# 2. 05_SCP\01_OVERVIEW.md — добавить упоминание AdminTab
# ============================================================
p = KB / "05_SCP" / "01_OVERVIEW.md"
if p.exists():
    bak(p)
    c = p.read_text(encoding="utf-8")
    marker = "## "
    # просто добавим блок в конец файла, если его там нет
    if "AdminTab" not in c:
        c = c.rstrip() + """

---

## AdminTab (план, вариант «гибрид»)

Подробности — в `05_SCP\\04_ADMIN.md`.

Кратко:
- Напрямую (аварийно): сброс пароля веб-админа, смена `ADMIN_API_KEY`, пересоздание `admin`.
- Через API: выпуск bootstrap/re-registration токенов, диагностика сервисов.
- Принцип: SCP должен работать всегда, даже если api лежит.
"""
        p.write_text(c, encoding="utf-8")
        print("[OK] 01_OVERVIEW.md дополнен")
    else:
        print("[skip] AdminTab уже упомянут")
else:
    print("[skip] 01_OVERVIEW.md отсутствует")

print("OK")
Запускай
powershell
cd D:\tracker
python tools\kb_patch_4_handoff.py
python tools\kb_patch_5_scp_admin.py
Ожидаемо: у патчера 1 — все [OK] без [skip]; у патчера 2 — 2 [OK].

Проверка:

powershell
cd D:\tracker\docs
Select-String -Path HANDOFF.md -Pattern "Админка|SCP|UX-аудит|93%|2026-10-07"
Публикуй KB
powershell
cd D:\tracker
.\update_site.bat
Введи осмысленное сообщение коммита, например:

text
HANDOFF: cookie 401 закрыт, SCP AdminTab (гибрид), UX-аудит в план
Содержимое last_chat.txt для нового чата
Скопируй это в файл last_chat.txt (или прямо в первое сообщение нового чата):

text
=== last_chat.txt ===
Проект «Трекер». Рабочая папка D:\tracker. KB: D:\tracker\docs\ (58 файлов).
Ссылка на KB: https://erohin-a.github.io/tracker/

[Последнее состояние на 2026-10-07]
- Готовность ~93%.
- Веб-pivot (PivotTable.js) — удалён, сводные строим в Excel из XLSX.
- PDF-экспорт — удалён, печать через браузер (Ctrl+P → Сохранить как PDF).
- Cookie 401 → редирект на /admin/login?next=... — реализовано (middleware в main.py).
- После логина возврат на исходную страницу через next — реализовано.
- HANDOFF.md обновлён: PDF и 401 из roadmap убраны, SCP AdminTab расписан (вариант «гибрид»), добавлен раздел «UX-аудит».

[План следующего чата]
1. Глубокий UX-аудит админки и клиента:
   - интуитивность навигации, названий, кнопок;
   - что упущено, где пользователь может запутаться;
   - всплывающие подсказки у ключевых кнопок;
   - единый стиль сообщений об ошибках и успехе.
2. Затем — SCP AdminTab (вариант «гибрид»).
3. Затем — установщик клиента (Inno Setup) и публикация версий.

[Правила работы]
- Русский, «ты», комментарии в коде на русском.
- Пользователь — не программист: подробно, готовые скрипты.
- Python-патчеры для правок >30 строк (here-string ломается).
- После правок Python: docker compose down && docker compose up -d --build.
- После правок HTML: docker compose restart api.
- Проверка: docker compose logs api --tail=30.
- После значимых шагов — обновлять файлы KB и запускать update_site.bat.
- Следить за длиной чата; при ~85% — предложить handoff.

=== Конец last_chat.txt ===
Что прислать
Вывод обоих патчеров.

Вывод проверки Select-String.

Вывод update_site.bat (коммит запушен).

После этого открывай новый чат, прикладывай:

HANDOFF.md

00_INDEX.md

last_chat.txt

И первой задачей ставим UX-аудит: я сделаю разбор текущего UI админки и клиента, покажу места под тултипы, найду неочевидные кнопки и предложу план улучшений. Потом SCP AdminTab.

Этот чат закрываем — он уже на ~72%. Увидимся в новом.