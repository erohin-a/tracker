<!-- Часть 395 из 1409 -->
# 2) Добавить обработчики _on_connected и _on_server_down
*Хлебные крошки:* 2) Добавить обработчики _on_connected и _on_server_down

[◀ 1) Заменить подключение сигналов в _start_sync_worker](394_1_Zamenit_podklyuchenie_signalov_v_start_sync_worker.md) | [Оглавление](00_BCE_INDEX.md) | [3) Поправить _on_synced: не перезаписывать last_sync_ts при n=0 ▶](396_3_Popravit_on_synced_ne_perezapisyvat_last_sync_ts_pri_n_0.md)

---

# 2) Добавить обработчики _on_connected и _on_server_down
$marker = "    def _on_synced(self, n):"
$handlers = @'
    def _on_connected(self):
        self.lbl_server.setText("? онлайн")
        self.lbl_server.setStyleSheet("color:#28a745; font-size:13px;")

    def _on_server_down(self):
        self.lbl_server.setText("? офлайн")
        self.lbl_server.setStyleSheet("color:#dc3545; font-size:13px;")

    def _on_synced(self, n):
'@

if ($content.Contains("    def _on_synced(self, n):") -and -not $content.Contains("def _on_connected")) {
    $content = $content.Replace("    def _on_synced(self, n):", $handlers)
    Write-Host "  OK  обработчики добавлены" -ForegroundColor Green
}

