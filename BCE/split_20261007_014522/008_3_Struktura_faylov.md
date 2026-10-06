<!-- Часть 8 из 1409 -->
# 3. Структура файлов
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 3. Структура файлов

[◀ Поток данных](007_Potok_dannyh.md) | [Оглавление](00_BCE_INDEX.md) | [4. Полный список файлов с описанием ▶](009_4_Polnyy_spisok_faylov_s_opisaniem.md)

---

## 3. Структура файлов

```
D:\tracker\
?
??? .env                              ? секреты сервера (не в git!)
??? docker-compose.yml                ? оркестрация контейнеров
??? certs\                            ? TLS-сертификаты
?   ??? fullchain.pem
?   ??? privkey.pem
?
??? server\                           ? серверная часть
?   ??? __init__.py
?   ??? config.py
?   ??? database.py
?   ??? models.py
?   ??? schemas.py
?   ??? security.py
?   ??? main.py
?   ??? Dockerfile
?   ??? requirements.txt
?   ??? nginx.conf
?
??? client\                           ? клиентская часть
    ??? .env                          ? настройки клиента
    ??? .venv\                        ? виртуальное окружение Python
    ??? __init__.py
    ??? config.py
    ??? crypto.py
    ??? db.py
    ??? http_client.py
    ??? registration.py
    ??? collector.py
    ??? sync.py
    ??? updater.py
    ??? main.py
    ??? build.spec
    ??? version_info.txt
    ??? requirements.txt
    ??? icon.ico                      ? опционально
```

Дополнительные файлы, создаваемые **во время работы**:

```
%APPDATA%\Tracker\                    ? данные клиента на ПК сотрудника
??? data.db                           ? локальная SQLite
??? data.db-wal                       ? WAL-журнал SQLite
??? data.db-shm                       ? shared memory SQLite
??? client.log                        ? лог клиента
??? bootstrap.txt                     ? одноразовый токен регистрации (удаляется после успеха)
??? ca.pem                            ? копия сертификата сервера для проверки
??? credentials.enc                   ? fallback-хранилище секретов, если keyring не работает
```

---

