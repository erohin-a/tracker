<!-- Часть 282 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Патч main.py — таймер авто-закрытия + периодическая отправка](281_Patch_main_py_taymer_avto_zakrytiya_periodicheskaya_otpravka.md) | [Оглавление](00_BCE_INDEX.md) | [Проверка синтаксиса ▶](283_Proverka_sintaksisa.md)

---

# ============================================================
Write-Host "`n--- Патч main.py ---" -ForegroundColor Cyan

$mainPath = "$clientDir\main.py"
$mainContent = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

if ($mainContent.Contains("_idle_timer")) {
    Write-Host "  Уже пропатчен — пропускаем" -ForegroundColor Yellow
} else {
    # 1) Импорт QTimer
    $mainContent = $mainContent.Replace(
        "from PyQt6.QtCore import QSocketNotifier, QThread",
        "from PyQt6.QtCore import QSocketNotifier, QThread, QTimer"
    )

    # 2) Импорт IDLE_CLOSE_MINUTES из config
    $mainContent = $mainContent.Replace(
        "from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH",
        "from .config import BASE_DIR, CLIENT_VERSION, LOG_PATH`nfrom .config import IDLE_CLOSE_MINUTES"
    )

    # 3) Запускаем таймер в _start после запуска sync-воркера
    $oldBlock = @'
        # Sync-воркер работает всегда — чтобы отправлять старые сессии и записи
        self._start_sync_worker()

        # Проверка обновлений
        self._check_updates()
'@

    $newBlock = @'
        # Sync-воркер работает всегда — чтобы отправлять старые сессии и записи
        self._start_sync_worker()

        # Таймер авто-закрытия «висящих» сессий (раз в минуту)
        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(60 * 1000)  # 1 минута
        self._idle_timer.timeout.connect(self._check_idle_session)
        self._idle_timer.start()

        # Проверка обновлений
        self._check_updates()
'@

    $mainContent = $mainContent.Replace($oldBlock, $newBlock)

    # 4) Добавляем метод _check_idle_session в класс MainWindow
    $methodToInsert = @'
    def _check_idle_session(self):
        """
        Раз в минуту проверяем: если активная сессия давно без активности,
        закрываем её автоматически временем последней активности.
        """
        try:
            closed_uid = db.auto_close_idle_session(IDLE_CLOSE_MINUTES)
            if closed_uid:
                log.info("Auto-closed idle session %s", closed_uid)
                self.session_uid = None
                self.session_label.setText("Сессия: авто-закрыта по бездействию")
                self.btn_start.setEnabled(True)
                self.btn_stop.setEnabled(False)
                self.status.setText("Сессия закрыта автоматически, отправляем на сервер…")
                if self.sync:
                    self.sync.trigger()
                # Останавливаем сборщик, если ещё работает
                self._stop_collector()
        except Exception:
            log.exception("_check_idle_session failed")

    # --- autostart ---
'@

    # Вставляем метод перед комментарием "# --- autostart ---"
    $mainContent = $mainContent.Replace("    # --- autostart ---", $methodToInsert)

    [System.IO.File]::WriteAllText($mainPath, $mainContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  main.py пропатчен" -ForegroundColor Green
}

