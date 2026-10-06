<!-- Часть 396 из 1409 -->
# 3) Поправить _on_synced: не перезаписывать last_sync_ts при n=0
*Хлебные крошки:* 3) Поправить _on_synced: не перезаписывать last_sync_ts при n=0

[◀ 2) Добавить обработчики _on_connected и _on_server_down](395_2_Dobavit_obrabotchiki_on_connected_i_on_server_down.md) | [Оглавление](00_BCE_INDEX.md) | [Чистим лог, чтобы видеть только свежие сообщения ▶](397_Chistim_log_chtoby_videt_tolko_svezhie_soobscheniya.md)

---

# 3) Поправить _on_synced: не перезаписывать last_sync_ts при n=0
$oldSynced = @'
    def _on_synced(self, n):
        self.lbl_server.setText("? онлайн")
        try:
            db.set_meta("last_sync_ts", datetime.now(timezone.utc).isoformat())
        except Exception:
            pass
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")
'@

$newSynced = @'
    def _on_synced(self, n):
        if n > 0:
            self.status.setText(f"Синхронизировано {n}")
'@

if ($content.Contains($oldSynced)) {
    $content = $content.Replace($oldSynced, $newSynced)
    Write-Host "  OK  _on_synced очищен" -ForegroundColor Green
}

[System.IO.File]::WriteAllText($mainPath, $content, [System.Text.UTF8Encoding]::new($false))
python -c "import ast; ast.parse(open(r'$mainPath', encoding='utf-8').read()); print('  main.py SYNTAX OK')"
________________________________________
Шаг 4. Запуск и наблюдение
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

