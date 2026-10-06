<!-- Часть 394 из 1409 -->
# 1) Заменить подключение сигналов в _start_sync_worker
*Хлебные крошки:* 1) Заменить подключение сигналов в _start_sync_worker

[◀ ============================================================](393_part.md) | [Оглавление](00_BCE_INDEX.md) | [2) Добавить обработчики _on_connected и _on_server_down ▶](395_2_Dobavit_obrabotchiki_on_connected_i_on_server_down.md)

---

# 1) Заменить подключение сигналов в _start_sync_worker
$oldBlock = @'
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.server_down.connect(
            lambda: self.lbl_server.setText("? офлайн"))
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()
'@

$newBlock = @'
        self.sync_thread.started.connect(self.sync.run)
        self.sync.synced.connect(self._on_synced)
        self.sync.connected.connect(self._on_connected)
        self.sync.server_down.connect(self._on_server_down)
        self.sync.auth_failed.connect(self._on_auth_failed)
        self.sync_thread.start()
'@

if ($content.Contains($oldBlock)) {
    $content = $content.Replace($oldBlock, $newBlock)
    Write-Host "  OK  подписки на сигналы обновлены" -ForegroundColor Green
} elseif ($content.Contains("self.sync.connected.connect")) {
    Write-Host "  Уже пропатчен" -ForegroundColor Yellow
} else {
    Write-Host "  ВНИМАНИЕ: не найден блок _start_sync_worker — правьте вручную" -ForegroundColor Red
}

