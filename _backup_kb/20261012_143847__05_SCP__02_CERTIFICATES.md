# Сертификаты
Статус: черновик
Дата: 2026-10-02
Связанные файлы KB: 05_SCP\01_OVERVIEW.md, 06_DEPLOY\02_NGINX_TLS.md, 04_CLIENT\09_REGISTRATION.md

## Назначение
Описать работу SCP с TLS-сертификатами: просмотр текущего, перевыпуск (renew), экспорт `ca.pem`, бэкап и откат. Это карта для администратора сервера и для разработчика, который дорабатывает SCP.

## Содержание

### Где лежат сертификаты
| Файл | Путь | Назначение |
|---|---|---|
| `fullchain.pem` | `D:\tracker\certs\fullchain.pem` | Публичный сертификат (для nginx и клиентов) |
| `privkey.pem` | `D:\tracker\certs\privkey.pem` | Приватный ключ (только сервер, не раздавать) |
| `ca.pem` | `D:\tracker\client\ca.pem` | Копия сертификата для клиента (вшивается в установщик) |

**Монтирование в nginx:**
- `./certs:/etc/nginx/certs:ro` в `docker-compose.yml`.
- nginx использует `/etc/nginx/certs/fullchain.pem` и `/etc/nginx/certs/privkey.pem`.

### Чтение сертификата (`read_certificate_info`)

**Функция:**
```python
def read_certificate_info(cert_path: Path) -> dict:
    # Возвращает: cn, san_list, fingerprint_sha256,
    # not_before, not_after, days_left, pem_path
Что делает:

Читает PEM-файл через Path.read_bytes().

Загружает через x509.load_pem_x509_certificate(pem_bytes, default_backend()).

Извлекает:

CN — cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME).

SAN — cert.extensions.get_extension_for_class(x509.SubjectAlternativeName). Извлекает DNSName и IPAddress.

Отпечаток SHA-256 — cert.fingerprint(hashes.SHA256()).hex().

Даты — not_valid_before_utc, not_valid_after_utc.

Осталось дней — (not_after - now).days.

При ошибке — возвращает {"error": str(e)}.

Что показывает вкладка «Сертификат»
Информация:

Поле	Описание
Путь	D:\tracker\certs\fullchain.pem
Common Name	CN сертификата
SAN	Список DNS/IP через запятую
Отпечаток SHA-256	64 hex-символа (визуально разбит по 8)
Действует с	DD.MM.YYYY HH:MM
Действует до	DD.MM.YYYY HH:MM
Осталось дней	Число + цвет (зелёный / жёлтый / красный)
Цвет «Осталось дней»:

> 30 — зелёный (#28a745) + «(OK)».

10..30 — жёлтый (#e0a800) + «⚠ скоро».

< 10 — красный (#dc3545) + «⚠ срочно».

Кнопки:

🔄 «Проверить сертификат» (refresh()).

📋 «Показать отпечаток» (копирует в буфер обмена).

💾 «Сохранить ca.pem в файл...» (обсуждалась, не реализована).

🔄 «Обновить сертификат» (красная, открывает RenewCertDialog).

Диалог «Обновить сертификат» (RenewCertDialog)
Заголовок: «🔄 Обновление TLS-сертификата сервера».

Предупреждение:

⚠ После обновления сертификата все текущие клиенты отключатся. Им понадобится обновлённый ca.pem. Раздайте его через новую сборку TrackerSetup.exe или через настройки клиента.

Поля формы:

Поле	Тип	Дефолт	Назначение
Common Name (CN)	QLineEdit	localhost	CN сертификата
SAN (через запятую)	QLineEdit	localhost,127.0.0.1	SAN-список
Срок действия	QSpinBox (1..3650)	365	Дней
Копировать fullchain.pem → client/ca.pem	QCheckBox	✅	Обновить копию для клиента
Перезапустить nginx	QCheckBox	✅	docker compose restart nginx
Кнопки:

«Сгенерировать» (красная).

«Отмена».

Статус-панель: QPlainTextEdit — логи генерации.

Логика генерации (_on_generate)
Шаги:

Валидация CN — не пустой.

Парсинг SAN:

Разделение по запятой.

Если начинается с DNS: или IP: — оставить как есть.

Иначе — эвристика: если похоже на IP (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) → IP:, иначе → DNS:.

Гарантировать, что CN входит в SAN.

Подтверждение через QMessageBox.question с полной информацией.

Бэкап — backup_certs(CERTS_DIR) → certs/backup_YYYYMMDD_HHMMSS/.

Генерация — generate_certificate(cn, san_list, days, FULLCHAIN, PRIVKEY).

При ошибке openssl — откат из бэкапа (копирование fullchain.pem и privkey.pem обратно).

Чтение нового сертификата через read_certificate_info — логирование CN, SAN, отпечатка, срока.

Копирование в client/ca.pem (если чекбокс включён) — shutil.copy2(FULLCHAIN, CLIENT_CA).

Перезапуск nginx (если чекбокс включён) — docker_compose_restart("nginx").

Итоговое сообщение через QMessageBox.information.

Команда OpenSSL
python
cmd = [
    openssl, "req", "-x509", "-newkey", "rsa:4096",
    "-keyout", str(out_privkey),    # certs/privkey.pem
    "-out", str(out_fullchain),     # certs/fullchain.pem
    "-days", str(days),
    "-nodes",                        # без пароля на ключ
    "-subj", f"/CN={cn}",
    "-addext", f"subjectAltName={san_str}",
    "-addext", "basicConstraints=critical,CA:TRUE",
]
san_str: "DNS:localhost,IP:127.0.0.1".

Параметры:

-x509 — самоподписанный.

-newkey rsa:4096 — новый ключ.

-nodes — без пароля (важно для автоматического перезапуска nginx).

-addext subjectAltName=... — SAN (обязателен для современных браузеров/клиентов).

-addext basicConstraints=critical,CA:TRUE — сертификат может подписывать других (для self-signed цепочки).

Таймаут: 120 секунд.

Обработка ошибок:

FileNotFoundError → «Не найден openssl.exe. Проверьте путь. Установите: winget install ShiningLight.OpenSSL.Light».

TimeoutExpired → «openssl timeout > 120 секунд».

Ненулевой код возврата → сообщение с stderr и stdout.

Бэкап и откат
backup_certs(certs_dir):

Создаёт certs/backup_YYYYMMDD_HHMMSS/.

Копирует fullchain.pem и privkey.pem.

Возвращает путь к папке бэкапа.

Откат:

При ошибке generate_certificate — копирует файлы из бэкапа обратно.

Логирует «↩ Откат из бэкапа...» и «✅ Откат выполнен».

Ротация бэкапов:

Не реализована. Старые бэкапы остаются в certs/backup_*/.

В планах — retention (хранить 5 последних).

Экспорт ca.pem
Кнопка «Сохранить ca.pem в файл...»:

Обсуждалась, не реализована.

Планируемая логика: QFileDialog.getSaveFileName → shutil.copy2(FULLCHAIN, path).

Дефолтное имя: tracker_ca.pem.

Назначение: раздать сотрудникам, чтобы обновили %APPDATA%\Tracker\ca.pem вручную.

Перезапуск nginx
docker_compose_restart("nginx"):

python
subprocess.run(
    ["docker", "compose", "restart", "nginx"],
    cwd=str(BASE_DIR),
    capture_output=True,
    text=True,
    timeout=60,
    check=False,
)
Критично: cwd=str(BASE_DIR) — иначе docker compose не найдёт docker-compose.yml.

Таймаут: 60 секунд.

Ошибки:

FileNotFoundError → «docker не найден в PATH».

TimeoutExpired → «docker restart timeout > 60 сек».

Ненулевой код → stderr или stdout.

Что происходит после смены сертификата
nginx перезапущен — новые соединения идут с новым сертификатом.

Уже подключённые клиенты — получат SSL: CERTIFICATE_VERIFY_FAILED при следующем запросе.

Клиенты отключатся — их ca.pem больше не подходит.

Что нужно сделать:

Собрать новый установщик TrackerSetup.exe с обновлённым ca.pem.

Раздать сотрудникам.

Или вручную заменить %APPDATA%\Tracker\ca.pem на каждом ПК.

Замена ca.pem через UI клиента — обсуждалась, не реализована (P1).

Известные проблемы
Проблема	Причина	Решение
unknown directive "CN=localhost"	Мусор в nginx.conf	Перезаписать конфиг
Hostname mismatch	Сертификат без SAN	Перевыпустить с -addext subjectAltName=...
SSL: CERTIFICATE_VERIFY_FAILED	Клиент не доверяет самоподписанному	Положить ca.pem в %APPDATA%\Tracker\
nginx не поднимается	Сертификат или порт	docker compose logs nginx --tail=50
openssl не найден	Не установлен	winget install ShiningLight.OpenSSL.Light
PermissionError на privkey.pem	Файл занят	Закрыть редакторы/антивирус
Срок действия истёк	Не обновили вовремя	Перевыпустить сертификат
Клиенты не подключаются после renew	Нет нового ca.pem	Раздать ca.pem через установщик
Проверка сертификата вручную
Просмотр CN и SAN:

powershell
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -subject -ext subjectAltName
Отпечаток SHA-256:

powershell
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -fingerprint -sha256
Даты действия:

powershell
openssl x509 -in D:\tracker\certs\fullchain.pem -noout -dates
Проверка соединения:

powershell
curl.exe -k https://localhost/api/v1/version
Проверка из Python:

python
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from pathlib import Path

cert = x509.load_pem_x509_certificate(
    Path(r"D:\tracker\certs\fullchain.pem").read_bytes(),
    default_backend(),
)
print("CN:", cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value)
print("Not after:", cert.not_valid_after_utc)
Когда перевыпускать сертификат
Ситуация	Действие
Истёк срок действия	Обязательно перевыпустить
Сменился hostname/IP сервера	Обязательно (SAN)
Утечка privkey.pem	Обязательно (компрометация)
Плановая ротация (раз в 1–2 года)	Рекомендуется
Добавили новый SAN (например, 192.168.1.10)	Перевыпустить
Переход с self-signed на Let's Encrypt	Заменить сертификат на новый
Смена алгоритма (RSA → ECDSA)	Перевыпустить
Работа с Let's Encrypt
Не реализована через SCP.

Для прода — заменить self-signed на Let's Encrypt или корпоративный.

Let's Encrypt требует домен и валидацию.

certbot можно использовать отдельно, положив файлы в certs/.

Связь с другими компонентами
С nginx (06_DEPLOY\02_NGINX_TLS.md):

nginx читает fullchain.pem и privkey.pem.

После перевыпуска — docker compose restart nginx.

С клиентом (04_CLIENT\09_REGISTRATION.md):

Клиент использует ca.pem для проверки сертификата.

При смене сертификата — клиент отключается.

Нужно обновить ca.pem на каждом ПК.

С установщиком (06_DEPLOY\06_INSTALLER.md):

Установщик вшивает client/ca.pem.

После перевыпуска сертификата — пересобрать установщик.

С Docker (06_DEPLOY\01_DOCKER.md):

certs/ монтируется в nginx как read-only.

При смене сертификата — перезапуск nginx.

Логи
text
2026-10-02 10:00:00 INFO tracker.scp Certs backed up to D:\tracker\certs\backup_20261002_100000
2026-10-02 10:00:01 INFO tracker.scp Generating certificate: CN=localhost, SAN=DNS:localhost,IP:127.0.0.1, days=365
2026-10-02 10:00:05 INFO tracker.scp Certificate generated successfully
2026-10-02 10:00:05 INFO tracker.scp Fingerprint: a1b2c3...
2026-10-02 10:00:06 INFO tracker.scp Copied fullchain.pem to client\ca.pem
2026-10-02 10:00:10 INFO tracker.scp docker compose restart nginx: OK
Ключевые решения
OpenSSL через subprocess, не Python-библиотеки. Надёжнее, привычнее.

RSA 4096, -nodes. Совместимость + автоматический перезапуск nginx.

SAN обязателен. Без него современные клиенты отказываются.

Бэкап перед генерацией. Обязательно, с автоматическим откатом.

basicConstraints=critical,CA:TRUE. Self-signed может быть CA.

Проверка days_left с цветом. Быстрая оценка состояния.

Копирование в client/ca.pem — опция. Можно отключить для ручного контроля.

Перезапуск nginx — опция. Можно сгенерировать и проверить перед перезапуском.

ca.pem для клиентов — вшивается в установщик. Не раздаётся вручную.

Не реализована замена ca.pem через UI. В планах (P1).

Ссылки на код
запросить: control/gui.py — CertificateTab, RenewCertDialog, read_certificate_info, generate_certificate, backup_certs, find_openssl, docker_compose_restart

запросить: certs/fullchain.pem, certs/privkey.pem — текущие сертификаты

запросить: client/ca.pem — копия для клиента

запросить: server/nginx.conf — где используются сертификаты

запросить: docker-compose.yml — монтирование ./certs

запросить: client/http_client.py — как клиент использует ca.pem

запросить: client/config.py — SSL_CA_BUNDLE, TRACKER_PIN

Открытые вопросы / чего не хватает
нет данных: реализована ли кнопка «Сохранить ca.pem в файл» — обсуждалась, не реализована.

нет данных: есть ли ротация бэкапов сертификатов — нет.

нет данных: работает ли откат при ошибке openssl — заявлен, не проверен на практике.

нет данных: тестировался ли renew с SAN, отличным от localhost,127.0.0.1.

нет данных: как ведут себя клиенты при смене сертификата — отключаются, но нужно ли логировать.

не решено: нужна ли интеграция с Let's Encrypt через SCP.

не решено: нужна ли поддержка ECDSA-сертификатов (быстрее RSA).

не решено: заменить ли self-signed на корпоративный CA в проде.

не решено: как быть с клиентами, которые не могут заменить ca.pem (например, на удалённых ПК).

не решено: нужна ли автоматическая проверка «сертификат скоро истекает» (за 30 дней) с алертом.

не решено: должен ли SCP уметь работать с удалённым сервером (SSH).

не решено: где хранить privkey.pem для прода (Vault, KMS).

не решено: как быть с wildcard-сертификатами (для нескольких доменов).

не решено: нужна ли ротация сертификата по расписанию.

не решено: логировать ли renew в audit_log (сейчас только stdout).

Готово. Один файл выше. Следующий по индексу — 05_SCP\03_BUILD.md.