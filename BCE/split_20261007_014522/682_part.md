<!-- Часть 682 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ 3. Патчим base.html — переключатель + меню через _()](681_3_Patchim_base_html_pereklyuchatel_menyu_cherez.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](683_part.md)

---

# ============================================================
$basePath = "$serverDir\templates\base.html"
$baseContent = [System.IO.File]::ReadAllText($basePath, [System.Text.UTF8Encoding]::new($false))

if ($baseContent.Contains('set-lang')) {
    Write-Host "base.html уже содержит переключатель языка" -ForegroundColor Yellow
} else {
    # 3.1. Меняем navbar: меню через _() + переключатель RU/EN
    $oldNav = @'
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid px-4">
        <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
        <div class="navbar-nav ms-auto">
            {% if admin %}
            <a class="nav-link {% if request.url.path == '/admin/employees' %}active{% endif %}" href="/admin/employees">Сотрудники</a>
            <a class="nav-link {% if '/departments' in request.url.path %}active{% endif %}" href="/admin/departments">Отделы</a>
            <a class="nav-link {% if '/computers' in request.url.path %}active{% endif %}" href="/admin/computers">Компьютеры</a>
            <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}" href="/admin/tokens">Токены</a>
            <a class="nav-link {% if '/reports' in request.url.path %}active{% endif %}" href="/admin/reports">Отчёты</a>
            <a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">Настройки</a>
            <a class="nav-link {% if '/calendar' in request.url.path %}active{% endif %}" href="/admin/calendar">Календарь</a>
            <a class="nav-link {% if '/audit' in request.url.path %}active{% endif %}" href="/admin/audit">Аудит</a>
            <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
            <a class="nav-link" href="/admin/logout">Выход</a>
            {% endif %}
        </div>
    </div>
</nav>
'@

    $newNav = @'
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid px-4">
        <a class="navbar-brand" href="/admin">?? Tracker Admin</a>
        <div class="navbar-nav ms-auto align-items-center">
            {% if admin %}
            <a class="nav-link {% if request.url.path == '/admin/employees' %}active{% endif %}" href="/admin/employees">{{ _("menu.employees") }}</a>
            <a class="nav-link {% if '/departments' in request.url.path %}active{% endif %}" href="/admin/departments">{{ _("menu.departments") }}</a>
            <a class="nav-link {% if '/computers' in request.url.path %}active{% endif %}" href="/admin/computers">{{ _("menu.computers") }}</a>
            <a class="nav-link {% if '/tokens' in request.url.path %}active{% endif %}" href="/admin/tokens">{{ _("menu.tokens") }}</a>
            <a class="nav-link {% if '/reports' in request.url.path %}active{% endif %}" href="/admin/reports">{{ _("menu.reports") }}</a>
            <a class="nav-link {% if '/settings' in request.url.path %}active{% endif %}" href="/admin/settings">{{ _("menu.settings") }}</a>
            <a class="nav-link {% if '/calendar' in request.url.path %}active{% endif %}" href="/admin/calendar">{{ _("menu.calendar") }}</a>
            <a class="nav-link {% if '/audit' in request.url.path %}active{% endif %}" href="/admin/audit">{{ _("menu.audit") }}</a>

            {# ---------- Переключатель языка ---------- #}
            <div class="d-flex align-items-center ms-3" role="group" aria-label="Language">
                {% for l in supported_langs %}
                <a class="btn btn-sm {% if l.code == current_lang %}btn-warning text-dark fw-bold{% else %}btn-outline-light{% endif %} me-1"
                   href="/admin/set-lang/{{ l.code }}?next={{ request.url.path }}"
                   title="{{ l.label }}">{{ l.short }}</a>
                {% endfor %}
            </div>

            <span class="navbar-text ms-3 text-warning">{{ admin }}</span>
            <a class="nav-link" href="/admin/logout">{{ _("menu.logout") }}</a>
            {% endif %}
        </div>
    </div>
</nav>
'@

    if ($baseContent.Contains($oldNav)) {
        $baseContent = $baseContent.Replace($oldNav, $newNav)
        Write-Host "OK: navbar обновлён — меню через _(), добавлен переключатель" -ForegroundColor Green
    } else {
        Write-Host "Не найден блок navbar — правьте вручную" -ForegroundColor Yellow
        Write-Host "Откройте server/templates/base.html и найдите <nav ...>" -ForegroundColor Yellow
        exit 1
    }

    [System.IO.File]::WriteAllText($basePath, $baseContent, [System.Text.UTF8Encoding]::new($false))
}


