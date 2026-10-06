<!-- Часть 30 из 1409 -->
# 7. Проблемы, которые мы преодолели
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 7. Проблемы, которые мы преодолели

[◀ Просмотр данных (SQL)](029_Prosmotr_dannyh_SQL.md) | [Оглавление](00_BCE_INDEX.md) | [8. Что не реализовано ▶](031_8_Chto_ne_realizovano.md)

---

## 7. Проблемы, которые мы преодолели

| # | Симптом | Причина | Решение |
|---|---|---|---|
| 1 | `curl -k` в PowerShell не работает | `curl` — алиас `Invoke-WebRequest` | Использовать `curl.exe` |
| 2 | `ModuleNotFoundError: No module named 'server'` | `build: ./server` дал неверный build context | `build: { context: ., dockerfile: server/Dockerfile }` |
| 3 | Порт 80 занят Windows (`HTTP.sys`, PID 4) | IIS / WinRM / BranchCache | Убрать блок `listen 80`, оставить только 443 |
| 4 | `unknown directive "CN=localhost"` | Мусор от openssl-команды в `nginx.conf` | Перезаписать `nginx.conf` через here-string |
| 5 | `ModuleNotFoundError: PyQt6` | venv не активирован | `.venv\Scripts\Activate.ps1` |
| 6 | `ModuleNotFoundError: client` | Запуск из `client/`, а не из `tracker/` | `cd D:\tracker; python -m client.main` |
| 7 | `SyntaxError: def _validate(obj Any)` | Пропали `:` и `->` при копипасте | Перезаписать `crypto.py` через here-string |
| 8 | `NameError: name 'Path' is not defined` | Пропала строка `from pathlib import Path` | Перезаписать `config.py` через here-string |
| 9 | `.env` не читается | `python-dotenv` не установлен или `Path` не определён | `pip install python-dotenv` + починить `config.py` |
| 10 | `SSL: CERTIFICATE_VERIFY_FAILED: self-signed` | Python не доверяет самоподписанному сертификату | Добавить CA в `%APPDATA%\Tracker\ca.pem` + `TRACKER_CA_BUNDLE` |
| 11 | `Hostname mismatch: certificate is not valid for 'localhost'` | Сертификат без SAN | Перевыпустить с `-addext "subjectAltName=DNS:localhost,IP:127.0.0.1"` |
| 12 | `401 Unauthorized` на `/register` | Bootstrap-токен сгорел / не выпущен / неверный | Выпустить новый через `/admin/bootstrap-tokens`, сохранить **только значение** `token` |
| 13 | `Invalid or expired bootstrap token` | Токен использован | Проверить в БД, выпустить новый |
| 14 | JSON decode error при curl | PowerShell съел кавычки | Использовать `ConvertTo-Json` + `--data-binary @файл` |
| 15 | `.env` в UTF-16 с BOM | PowerShell `Out-File` | Использовать `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` |

---

