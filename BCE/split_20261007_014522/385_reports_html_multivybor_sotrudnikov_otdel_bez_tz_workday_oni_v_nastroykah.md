<!-- Часть 385 из 1409 -->
# reports.html — мультивыбор сотрудников + отдел, без tz/workday (они в настройках)
*Хлебные крошки:* reports.html — мультивыбор сотрудников + отдел, без tz/workday (они в настройках)

[◀ employees.html — с отделами и вкладками Активные/Уволенные](384_employees_html_s_otdelami_i_vkladkami_Aktivnye_Uvolennye.md) | [Оглавление](00_BCE_INDEX.md) | [Обновляем sync.py — сохраняем last_sync_ts после успешной синхронизации ▶](386_Obnovlyaem_sync_py_sohranyaem_last_sync_ts_posle_uspeshnoy_sinhronizatsii.md)

---

# reports.html — мультивыбор сотрудников + отдел, без tz/workday (они в настройках)
$reports_html = @'
{% extends "base.html" %}
{% block title %}Отчёты{% endblock %}
{% block content %}
<h3 class="mb-4">Отчёты</h3>

<div class="card">
  <div class="card-body">
    <form method="post" action="/admin/reports/generate" id="reportForm">

      <div class="mb-3">
        <label class="form-label fw-bold">Период</label>
        <div class="d-flex flex-wrap gap-2 mb-2">
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(0)">Сегодня</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(1)">Вчера</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(7)">7 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setPeriod(30)">30 дней</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setThisMonth()">Этот месяц</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="setLastMonth()">Прошлый месяц</button>
        </div>
        <div class="row g-2">
          <div class="col-md-3"><input class="form-control" type="date" name="date_from" id="date_from" required value="{{ today }}"></div>
          <div class="col-md-3"><input class="form-control" type="date" name="date_to" id="date_to" required value="{{ today }}"></div>
        </div>
      </div>

      <div class="row g-3">

        <div class="col-md-3">
          <label class="form-label">
            Сотрудники
            <span class="hint" data-bs-toggle="tooltip" title="Зажмите Ctrl (Cmd на Mac) чтобы выбрать нескольких. Если ничего не выбрано — все.">?</span>
          </label>
          <select name="employee_ids" class="form-select multi-select" multiple>
            {% for e in employees %}
              <option value="{{ e.id }}">{{ e.full_name }}{% if e.external_id %} ({{ e.external_id }}){% endif %}</option>
            {% endfor %}
          </select>
          <div class="form-text">Ctrl + клик для нескольких</div>
        </div>

        <div class="col-md-3">
          <label class="form-label">Отдел</label>
          <select name="department_id" class="form-select">
            <option value="">Все отделы</option>
            {% for d in departments %}<option value="{{ d.id }}">{{ d.name }}</option>{% endfor %}
          </select>
        </div>

        <div class="col-md-3">
          <label class="form-label">Компьютер</label>
          <select name="computer_id" class="form-select">
            <option value="">Все компьютеры</option>
            {% for c in computers %}<option value="{{ c.id }}">{{ c.hostname or c.computer_uid[:14] }}</option>{% endfor %}
          </select>
        </div>

        <div class="col-md-3">
          <label class="form-label">Группировка</label>
          <select name="group_by" class="form-select">
            <option value="days" selected>Рабочие дни ? Сотрудник (табель)</option>
            <option value="employees">По сотрудникам</option>
            <option value="computers">По компьютерам</option>
            <option value="sessions">Детально — каждая сессия</option>
          </select>
        </div>

        <div class="col-md-3">
          <label class="form-label">Формат</label>
          <select name="fmt" class="form-select">
            <option value="html">Просмотр</option>
            <option value="xlsx">Excel (XLSX)</option>
            <option value="csv">CSV</option>
          </select>
        </div>
      </div>

      <div class="mt-3">
        <label class="form-label fw-bold">Что показывать</label>
        <div class="d-flex flex-wrap gap-4">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_apps" id="show_apps" checked>
            <label class="form-check-label" for="show_apps">Топ-программы (с разбивкой по сотрудникам)</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="show_abnormal" id="show_abnormal" checked>
            <label class="form-check-label" for="show_abnormal">Пометки аварийных завершений</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="checkbox" name="expand_details" id="expand_details">
            <label class="form-check-label" for="expand_details">Разворачивать детали</label>
          </div>
        </div>
      </div>

      <div class="alert alert-secondary py-2 small mt-3 mb-0">
        Часовой пояс, начало рабочего дня и порог паузы настраиваются в
        <a href="/admin/settings">Настройках</a> и применяются ко всем отчётам.<br>
        Текущие: TZ = <strong>{{ cfg.report_timezone }}</strong>,
        начало дня = <strong>{{ '%02d' % cfg.workday_start_hour }}:00</strong>,
        порог паузы = <strong>{{ cfg.activity_gap_minutes }} мин</strong>.
      </div>

      <button class="btn btn-primary mt-3">Сформировать отчёт</button>
    </form>
  </div>
</div>

<script>
function fmt(d) {
  var y = d.getFullYear(), m = String(d.getMonth()+1).padStart(2,'0'), dd = String(d.getDate()).padStart(2,'0');
  return y + '-' + m + '-' + dd;
}
function setPeriod(daysAgo) {
  var to = new Date(), from = new Date();
  from.setDate(from.getDate() - daysAgo);
  document.getElementById('date_from').value = fmt(from);
  document.getElementById('date_to').value = fmt(to);
}
function setThisMonth() {
  var now = new Date();
  document.getElementById('date_from').value = fmt(new Date(now.getFullYear(), now.getMonth(), 1));
  document.getElementById('date_to').value = fmt(new Date(now.getFullYear(), now.getMonth()+1, 0));
}
function setLastMonth() {
  var now = new Date();
  document.getElementById('date_from').value = fmt(new Date(now.getFullYear(), now.getMonth()-1, 1));
  document.getElementById('date_to').value = fmt(new Date(now.getFullYear(), now.getMonth(), 0));
}
</script>
{% endblock %}
'@
[System.IO.File]::WriteAllText("$templatesDir\reports.html", $reports_html, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  reports.html" -ForegroundColor Green

Write-Host "`n=== Шаблоны обновлены ===" -ForegroundColor Cyan
________________________________________
Скрипт 5 — миграция БД + пересборка
powershell
$ErrorActionPreference = "Stop"
Set-Location D:\tracker

Write-Host "--- Миграция БД ---" -ForegroundColor Cyan

docker compose up -d db
Start-Sleep -Seconds 8

docker compose exec -T db psql -U tracker -d tracker -c @"
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS department_id INTEGER REFERENCES departments(id);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS fired_at TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"@

Write-Host "`n--- Пересборка ---" -ForegroundColor Cyan
docker compose down
docker compose up -d --build
Start-Sleep -Seconds 25

docker compose ps
Write-Host "`n--- Логи API ---" -ForegroundColor Cyan
docker compose logs api --tail=30

Write-Host "`nОткройте: https://localhost/admin/settings" -ForegroundColor Green
________________________________________
Скрипт 6 — клиент: время + панель
powershell
$ErrorActionPreference = "Stop"
$clientDir = "D:\tracker\client"

$main_py = @'
import json
import logging
import os
import signal
import socket
import sys
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QSocketNotifier, QThread, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMenu, QMessageBox, QPushButton, QSystemTrayIcon,
    QVBoxLayout, QWidget,
)

from . import db, http_client
from .autostart import set_autostart
from .collector import CollectorWorker
from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH, IDLE_CLOSE_MINUTES
from .registration import ensure_registered
from .sync import SyncWorker
from .updater import UpdateChecker, apply_update

handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024,
                              backupCount=3, encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[handler],
)
log = logging.getLogger("tracker.main")


def _icon_path() -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "icon.ico")


def _local_time_str(iso_str: str) -> str:
    """UTC ISO-строка ? локальное время HH:MM:SS."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%H:%M:%S")
    except Exception:
        return "—"


def _fmt_duration(seconds: int) -> str:
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Tracker {CLIENT_VERSION}")
        self.resize(560, 460)

        # --- главный статус ---
        self.status = QLabel("Инициализация...")
        self.status.setStyleSheet("font-size: 14px; padding: 4px; color:#555;")

        # --- кнопки ---
        self.btn_start = QPushButton("?  Начать работу")
        self.btn_start.setStyleSheet(
            "background-color:#28a745; color:white; font-weight:bold;"
            "padding:14px; font-size:15px; border:none; border-radius:6px;"
        )
        self.btn_start.clicked.connect(self._on_start_work)

        self.btn_stop = QPushButton("?  Конец работы")
        self.btn_stop.setStyleSheet(
            "background-color:#dc3545; color:white; font-weight:bold;"
            "padding:14px; font-size:15px; border:none; border-radius:6px;"
        )
        self.btn_stop.clicked.connect(self._on_stop_work)
        self.btn_stop.setEnabled(False)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_stop)

        # --- панель информации ---
        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background: #f8f9fa; border: 1px solid #dee2e6;"
            " border-radius: 6px; padding: 8px; }"
        )
        grid = QGridLayout(panel)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)

        def mk_label(text=""):
            l = QLabel(text)
            l.setStyleSheet("font-size: 13px;")
            return l

        def mk_title(text):
            l = QLabel(text)
            l.setStyleSheet("color:#6c757d; font-size:12px;")
            return l

        # Строка 1: сессия
        grid.addWidget(mk_title("Сессия"), 0, 0)
        self.lbl_session_start = mk_label("не запущена")
        grid.addWidget(self.lbl_session_start, 0, 1)

        grid.addWidget(mk_title("Сейчас работаем"), 0, 2)
        self.lbl_session_clock = mk_label("—")
        self.lbl_session_clock.setStyleSheet("font-size:13px; font-weight:bold; color:#28a745;")
        grid.addWidget(self.lbl_session_clock, 0, 3)

        # Строка 2: сервер
        grid.addWidget(mk_title("Сервер"), 1, 0)
        self.lbl_server = mk_label("—")
        grid.addWidget(self.lbl_server, 1, 1)

        grid.addWidget(mk_title("Последняя синхронизация"), 1, 2)
        self.lbl_last_sync = mk_label("никогда")
        grid.addWidget(self.lbl_last_sync, 1, 3)

        # Строка 3: очередь
        grid.addWidget(mk_title("В очереди"), 2, 0)
        self.lbl_pending = mk_label("0")
        grid.addWidget(self.lbl_pending, 2, 1)

        grid.addWidget(mk_title("Активное окно"), 2, 2)
        self.lbl_active_window = mk_label("—")
        grid.addWidget(self.lbl_active_window, 2, 3)

        # Автозапуск
        self.autostart_cb = QCheckBox("Автозапуск при входе в систему")
        self.autostart_cb.setChecked(self._load_autostart_setting())
        self.autostart_cb.stateChanged.connect(self._on_autostart_changed)

        # Собираем
        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addLayout(btns)
        layout.addWidget(panel)
        layout.addWidget(self.autostart_cb)
        layout.addStretch()

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        # --- state ---
        self.session_uid = None
        self.collector = None
        self.collector_thread = None
        self.sync = None
        self.sync_thread = None
        self._signal_notifier = None
        self._signal_socks = None

        self._build_tray()
        self._start()

        # Обновление панели каждую секунду
        self._ui_timer = QTimer(self)
        self._ui_timer.setInterval(1000)
        self._ui_timer.timeout.connect(self._update_panel)
        self._ui_timer.start()

    def _update_panel(self):
        try:
            # Сессия
            if self.session_uid:
                start_iso = db.get_session_start(self.session_uid) or ""
                self.lbl_session_start.setText(_local_time_str(start_iso))
                # длительность
                try:
                    start_dt = datetime.fromisoformat(start_iso)
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=timezone.utc)
                    elapsed = int((datetime.now(timezone.utc) - start_dt).total_seconds())
                    self.lbl_session_clock.setText(_fmt_duration(elapsed))
                except Exception:
                    self.lbl_session_clock.setText("—")
            else:
                self.lbl_session_start.setText("не запущена")
                self.lbl_session_clock.setText("—")

            # Очередь записей
            try:
                rows = db.get_conn().execute(
                    "SELECT COUNT(*) AS n FROM records WHERE synced=0 AND poisoned=0"
                ).fetchone()
                self.lbl_pending.setText(str(rows["n"]) if rows else "0")
            except Exception:
                self.lbl_pending.setText("?")

            # Последняя синхронизация
            last_sync = db.get_meta("last_sync_ts")
            if last_sync:
                try:
                    dt = datetime.fromisoformat(last_sync)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    local = dt.astimezone()
                    self.lbl_last_sync.setText(local.strftime("%d.%m %H:%M:%S"))
                except Exception:
                    self.lbl_last_sync.setText("—")
        except Exception:
            log.exception("_update_panel failed")

    # --- tray ---
    def _build_tray(self):
        self.tray = QSystemTrayIcon(self)
        ip = _icon_path()
        if os.path.exists(ip):
            self.tray.setIcon(QIcon(ip))
        else:
            self.tray.setIcon(self.style().standardIcon(
                self.style().StandardPixmap.SP_ComputerIcon))

        menu = QMenu()
        a_show = QAction("Показать", self)
        a_show.triggered.connect(self._show)
        a_start = QAction("Начать работу", self)
        a_start.triggered.connect(self._on_start_work)
        a_stop = QAction("Конец работы", self)
        a_stop.triggered.connect(self._on_stop_work)
        a_quit = QAction("Выход", self)
        a_quit.triggered.connect(self._quit)

        menu.addAction(a_show)
        menu.addSeparator()
        menu.addAction(a_start)
        menu.addAction(a_stop)
        menu.addSeparator()
        menu.addAction(a_quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def _show(self):
        self.showNormal()
        self.activateWindow()

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.tray.showMessage(
            "Tracker", "Свёрнуто в трей",
            QSystemTrayIcon.MessageIcon.Information, 2000,
        )

    # --- lifecycle ---
    def _start(self):
        try:
            ensure_registered()
        except Exception as e:
            log.exception("Registration failed")
            QMessageBox.critical(self, "Ошибка", f"Регистрация: {e}")
            self._quit()
            return

        try:
            db.init_db()
        except Exception as e:
            log.exception("DB init failed")
            QMessageBox.critical(self, "Ошибка БД", str(e))
            self._quit()
            return

        active = db.get_active_session_uid()
        if active:
            log.warning("Найдена незакрытая сессия %s — закрываем как аварийную", active)
            try:
                db.close_session(active, abnormal=True)
            except Exception:
                log.exception("close_session on start failed")

        self.status.setText("Готов к работе")

        self._start_sync_worker()

        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(60 * 1000)
        self._idle_timer.timeout.connect(self._check_idle_session)
        self._idle_timer.start()

        self._check_updates()

    def _start_sync_worker(self):
        self.sync_thread = QThread()
        self.sync = SyncWorker()
        self.sync.moveToThread(self.sync_thread)
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.server_down.connect(
            lambda: self.lbl_server.setText("? Offline"))
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()

    def _on_synced(self, n):
        # Обновляем индикатор сервера и последнюю синхронизацию
        self.lbl_server.setText("? онлайн")
        try:
            db.set_meta("last_sync_ts", datetime.now(timezone.utc).isoformat())
        except Exception:
            pass
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")

    def _on_auth_failed(self):
        QMessageBox.warning(self, "Авторизация",
                            "Сервер отклонил клиента. Требуется перерегистрация.")
        self.status.setText("Ошибка авторизации")

    # --- work session ---
    def _on_start_work(self):
        if self.session_uid is not None:
            return
        try:
            self.session_uid = str(uuid.uuid4())
            db.start_session(self.session_uid)
        except Exception as e:
            log.exception("start_session failed")
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать сессию: {e}")
            self.session_uid = None
            return

        self.collector_thread = QThread()
        self.collector = CollectorWorker(self.session_uid)
        self.collector.moveToThread(self.collector_thread)
        self.collector_thread.started.connect(self.collector.run)
        self.collector.error.connect(lambda m: self.status.setText(f"Сбор: {m}"))
        self.collector_thread.start()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status.setText("Работа начата")

        if self.sync:
            self.sync.trigger()

        log.info("Work session started uid=%s", self.session_uid)

    def _on_stop_work(self):
        if self.session_uid is None:
            return
        r = QMessageBox.question(
            self, "Конец работы",
            "Завершить рабочий день? Данные будут отправлены на сервер.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return

        uid = self.session_uid
        self._stop_collector()
        try:
            db.close_session(uid, abnormal=False)
        except Exception:
            log.exception("close_session failed")

        self.session_uid = None
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status.setText("Работа завершена, синхронизация…")

        if self.sync:
            self.sync.trigger()
        log.info("Work session stopped uid=%s", uid)

    def _stop_collector(self):
        if self.collector:
            try:
                self.collector.stop()
            except Exception:
                log.exception("collector.stop")
        if self.collector_thread:
            self.collector_thread.quit()
            if not self.collector_thread.wait(5000):
                log.warning("collector thread didn't stop")
        self.collector = None
        self.collector_thread = None

    def _check_idle_session(self):
        try:
            idle = db.get_idle_close_minutes(IDLE_CLOSE_MINUTES)
            closed_uid = db.auto_close_idle_session(idle)
            if closed_uid:
                log.info("Auto-closed idle session %s", closed_uid)
                self.session_uid = None
                self.btn_start.setEnabled(True)
                self.btn_stop.setEnabled(False)
                self.status.setText("Сессия закрыта автоматически, отправляем на сервер…")
                if self.sync:
                    self.sync.trigger()
                self._stop_collector()
        except Exception:
            log.exception("_check_idle_session failed")

    # --- autostart ---
    def _load_autostart_setting(self) -> bool:
        cfg = BASE_DIR / "config.json"
        if cfg.exists():
            try:
                return json.loads(cfg.read_text(encoding="utf-8")).get("autostart_enabled", False)
            except Exception:
                pass
        return False

    def _on_autostart_changed(self, state):
        enabled = (state == 2)
        ok = set_autostart(enabled)
        if not ok:
            QMessageBox.warning(self, "Автозапуск",
                                "Не удалось изменить автозапуск. Проверьте права.")
            return
        cfg = BASE_DIR / "config.json"
        data = {}
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
            except Exception:
                pass
        data["autostart_enabled"] = enabled
        cfg.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- updates ---
    def _check_updates(self):
        self._upd_thread = QThread()
        self._upd = UpdateChecker(auto_download=False)
        self._upd.moveToThread(self._upd_thread)
        self._upd_thread.started.connect(self._upd.run)
        self._upd.no_update.connect(self._upd_thread.quit)
        self._upd.update_available.connect(self._on_update_available)
        self._upd.update_ready.connect(self._on_update_ready)
        self._upd.error.connect(lambda e: log.warning("upd: %s", e))
        self._upd_thread.start()

    def _on_update_available(self, info):
        if info.get("mandatory"):
            self._download_and_apply(info)
        else:
            r = QMessageBox.question(self, "Обновление",
                                     f"Обновиться до {info['latest_version']}?")
            if r == QMessageBox.StandardButton.Yes:
                self._download_and_apply(info)

    def _on_update_ready(self, info, path):
        try:
            self._stop_collector()
            self._shutdown_sync()
            http_client.close_client()
            db.close_conn()
            from pathlib import Path
            apply_update(Path(path))
        except Exception:
            log.exception("apply update failed")

    def _download_and_apply(self, info):
        self._dl_thread = QThread()
        self._dl = UpdateChecker(auto_download=True)
        self._dl.moveToThread(self._dl_thread)
        self._dl_thread.started.connect(self._dl.run)
        self._dl.update_ready.connect(self._on_update_ready)
        self._dl.error.connect(lambda e: QMessageBox.warning(self, "Ошибка", e))
        self._dl_thread.start()

    def install_signal_handlers(self):
        r, w = socket.socketpair()
        r.setblocking(False)
        w.setblocking(False)

        def _noop(*_a):
            pass

        signal.signal(signal.SIGTERM, _noop)
        signal.signal(signal.SIGINT, _noop)
        signal.set_wakeup_fd(w.fileno())

        n = QSocketNotifier(r.fileno(), QSocketNotifier.Type.Read, self)

        def _on():
            try:
                r.recv(1024)
            except BlockingIOError:
                pass
            self._quit()

        n.activated.connect(_on)
        self._signal_notifier = n
        self._signal_socks = (r, w)

    def _shutdown_sync(self):
        if self.sync:
            try:
                self.sync.stop()
            except Exception:
                log.exception("sync.stop")
        if self.sync_thread:
            self.sync_thread.quit()
            if not self.sync_thread.wait(5000):
                log.warning("sync thread didn't stop")
        self.sync = None
        self.sync_thread = None

    def _quit(self):
        log.info("Shutting down")
        self._stop_collector()
        if self.session_uid:
            try:
                db.close_session(self.session_uid, abnormal=True)
                log.info("Closed session %s on quit (abnormal=True)", self.session_uid)
            except Exception:
                log.exception("close_session on quit")
            self.session_uid = None
        self._shutdown_sync()
        http_client.close_client()
        db.close_conn()
        try:
            if self._signal_notifier:
                self._signal_notifier.setEnabled(False)
                self._signal_notifier = None
            if self._signal_socks:
                r, w = self._signal_socks
                signal.set_wakeup_fd(-1)
                r.close()
                w.close()
                self._signal_socks = None
        except Exception:
            log.exception("signal cleanup")
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    win = MainWindow()
    win.install_signal_handlers()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'@
[System.IO.File]::WriteAllText("$clientDir\main.py", $main_py, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  client/main.py" -ForegroundColor Green
python -c "import ast; ast.parse(open(r'$clientDir\main.py', encoding='utf-8').read()); print('  SYNTAX OK')"

