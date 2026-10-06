<!-- Часть 16 из 1409 -->
# Шаг 2. Создать `.env` в корне
*Хлебные крошки:* Полное руководство по проекту «Трекер» / 5. Пошаговая установка с нуля / Шаг 2. Создать `.env` в корне

[◀ Шаг 1. Клонировать структуру](015_Shag_1_Klonirovat_strukturu.md) | [Оглавление](00_BCE_INDEX.md) | [Шаг 3. Создать сертификаты ▶](017_Shag_3_Sozdat_sertifikaty.md)

---

### Шаг 2. Создать `.env` в корне

```powershell
python -c "from cryptography.fernet import Fernet; print('SECRET_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(48))"
python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(48))"
```

Записать три строки в `D:\tracker\.env` через `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` — **без BOM**.

