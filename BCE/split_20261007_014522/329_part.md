<!-- Часть 329 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ settings.html (новый)](328_settings_html_novyy.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](330_part.md)

---

# ============================================================
$settings_html = @'
{% extends "base.html" %}
{% block title %}Настройки{% endblock %}
{% block content %}
<h3 class="mb-4">Настройки системы</h3>

{% if saved %}
<div class="alert alert-success py-2">? Настройки сохранены. Клиенты подхватят изменения в течение 5 минут.</div>
{% endif %}

<div class="card" style="max-width:720px">
  <div class="card-body">
    <form method="post" action="/admin/settings/save">
      <div class="mb-3">
        <label class="form-label">
          Закрывать «висящие» сессии через
          <span class="hint" data-bs-toggle="tooltip" title="Если с последней активности прошло больше указанного времени, клиент автоматически закроет сессию временем последней активности. Клиенты получают новое значение при следующей синхронизации (максимум через 5 минут).">?</span>
        </label>
        <div class="input-group" style="max-width:260px">
          <input type="number" name="idle_close_minutes" class="form-control"
                 value="{{ idle_close_minutes }}" min="5" max="480" required>
          <span class="input-group-text">минут без активности</span>
        </div>
        <div class="form-text">
          Рекомендуется 30 минут. Минимум 5, максимум 480 (8 часов).
        </div>
      </div>

      <div class="alert alert-info py-2 small mb-3">
        <strong>Как это работает:</strong> клиент на каждом ПК раз в 5 минут получает
        актуальное значение с сервера. Если с последней активности прошло больше
        указанного времени — сессия закрывается автоматически, причём временем
        <em>последней активности</em>, а не моментом срабатывания таймера.
        Сессия помечается как «аварийная».
      </div>

      <button class="btn btn-primary">Сохранить</button>
    </form>
  </div>
</div>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\settings.html", $settings_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  settings.html" -ForegroundColor Green

