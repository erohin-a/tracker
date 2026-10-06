<!-- Часть 290 из 1409 -->
# in _check_idle_session:
*Хлебные крошки:* in _check_idle_session:

[◀ after loop:](289_after_loop.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](291_part.md)

---

# in _check_idle_session:
idle = db.get_idle_close_minutes(IDLE_DEFAULT)
closed_uid = db.auto_close_idle_session(idle)
OK. Now let me really write.
Actually for client main.py the import statement I added before was:
python
from .config import IDLE_CLOSE_MINUTES
I'll use a PowerShell replace to change it.
Hmm, actually easier to just add a new import without removing the old. Let me add:
python
from .config import IDLE_CLOSE_MINUTES as IDLE_CLOSE_MINUTES_DEFAULT
But then in code IDLE_CLOSE_MINUTES unused. Messy.
Let me just leave IDLE_CLOSE_MINUTES in config as default and modify main.py:
python
idle = db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)
closed_uid = db.auto_close_idle_session(idle)
Change db.auto_close_idle_session(IDLE_CLOSE_MINUTES) ? db.auto_close_idle_session(db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)).
Simple replace.
OK, writing.
Let me finalize size. This will be a big response, but let's go.
For base.html — add nav link:
html
<a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>
For settings.html — simple form:
html
{% extends "base.html" %}
{% block title %}Настройки{% endblock %}
{% block content %}
<h3 class="mb-4">Настройки системы</h3>

{% if saved %}
<div class="alert alert-success py-2">Настройки сохранены</div>
{% endif %}

<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/settings/save">
      <div class="mb-3">
        <label class="form-label">
          Закрывать «висящие» сессии через (минут без активности)
          <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени, клиент автоматически закроет сессию временем последней активности. Клиенты получают новое значение при следующей синхронизации (макс. 5 минут).">?</span>
        </label>
        <input type="number" name="idle_close_minutes" class="form-control" value="{{ idle_close_minutes }}" min="5" max="480" style="max-width:200px">
        <div class="form-text">Рекомендуемое значение: 30 мин. Минимум 5, максимум 480.</div>
      </div>
      <button class="btn btn-primary">Сохранить</button>
    </form>
  </div>
</div>
{% endblock %}
OK. Now writing the full response. Let me be efficient.
Actually — user might appreciate a note about how client picks up the setting. Let me mention: "клиент подтянет через ?5 минут".
Alright, going to write now.
Let me also make sure the report_result.html handles the new columns and top_programs expansion well.
Column structure for top programs table:
| Программа | Время | Клавиатура | Мышь | (bar) |
Each program row followed by an optional hidden expansion row.
html
<table class="table table-sm mb-0">
  <thead><tr>
    <th style="width:35%">Программа</th>
    <th>Время</th>
    <th>Клавиатура</th>
    <th>Мышь</th>
    <th style="width:30%"></th>
  </tr></thead>
  <tbody>
  {% for a in report.totals.top_apps %}
    <tr>
      <td>{{ a.app }}</td>
      <td style="white-space:nowrap">{{ a.seconds | dur }}</td>
      <td>{{ a.keyboard | dur }}</td>
      <td>{{ a.mouse | dur }}</td>
      <td>
        <span class="app-bar" style="width: {{ (a.seconds / max_app_seconds * 100) if max_app_seconds else 0 }}%"></span>
      </td>
    </tr>
    {% if a.by_employee and a.by_employee|length > 1 %}
      <tr>
        <td colspan="5" class="p-0 bg-light">
          <details>
            <summary style="padding:6px 12px;cursor:pointer;color:#555;font-size:0.9em">
              ? Развернуть по сотрудникам ({{ a.by_employee|length }})
            </summary>
            <div style="padding:8px 12px">
              <table class="table table-sm mb-0">
                <thead><tr><th>Сотрудник</th><th>1C ID</th><th>Время</th><th>Клавиатура</th><th>Мышь</th></tr></thead>
                <tbody>
                {% for e in a.by_employee %}
                  <tr>
                    <td>{{ e.employee_name }}</td>
                    <td><code>{{ e.external_id or '—' }}</code></td>
                    <td>{{ e.seconds | dur }}</td>
                    <td>{{ e.keyboard | dur }}</td>
                    <td>{{ e.mouse | dur }}</td>
                  </tr>
                {% endfor %}
                </tbody>
              </table>
            </div>
          </details>
        </td>
      </tr>
    {% endif %}
  {% endfor %}
  </tbody>
</table>
Good.
Now writing all scripts.
One more thing — the server /api/v1/client-config should ideally require X-Computer-Uid. But it's just idle minutes, low sensitivity. Let me make it public for simplicity. Actually, let me require nothing and return default if no header.
OK writing.
Let me combine server main.py patch into script 3 along with anything else server-side. Since main.py is stable, I'll do a PowerShell insert.
Alright, final structure:
Script 1: server/models.py (add AppSetting) + server/web_admin.py (full replacement)
Script 2: server/templates: base.html, settings.html (new), reports.html, report_result.html
Script 3: server/main.py patch (add endpoint)
Script 4: client patches (db.py add helper, sync.py add config fetch, main.py use db value)
Script 5: rebuild + test instructions
Let me write it all.
Hmm — models.py only has one new class. Instead of replacing whole file I'll use a PowerShell replace to insert AppSetting before class AuditLog. That way I don't have to retype it all. But user asked "if you change the code, give me the whole file". Hmm. Let me give full models.py anyway — it's short.
OK writing now. Let me focus.
Настраиваемый idle-порог + новая логика отчёта
Что изменится
Настройки в админке — страница /admin/settings, поле «Закрывать висящие сессии через N минут».
Клиент подтягивает это значение с сервера раз в 5 минут.
«Отработано» = от старта первой сессии до конца последней сессии за день.
«Эффективное время» = сумма эффективных времён (то, что раньше было «Отработано»).
Топ программ — кликабельные, показывают разбивку по сотрудникам.
________________________________________
Скрипт 1 — серверные Python-файлы
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

