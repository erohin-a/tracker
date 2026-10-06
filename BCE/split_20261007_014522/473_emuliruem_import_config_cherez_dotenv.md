<!-- Часть 473 из 1409 -->
# эмулируем импорт config через dotenv
*Хлебные крошки:* эмулируем импорт config через dotenv

[◀ (не критично, но улучшает совместимость)](472_ne_kritichno_no_uluchshaet_sovmestimost.md) | [Оглавление](00_BCE_INDEX.md) | [Чистим лог ▶](474_Chistim_log.md)

---

# эмулируем импорт config через dotenv
import os
from pathlib import Path
from dotenv import load_dotenv
p = Path(r'D:\tracker\client\.env')
load_dotenv(p, override=True)
print('  из .env:', os.environ.get('TRACKER_SERVER_URL'))
print('  дефолт в config.py: см. строку с SERVER_URL')
"@

Write-Host "`nГотово. Перезапустите клиент." -ForegroundColor Green
________________________________________
Скрипт 3 — запуск клиента и наблюдение
Сначала закройте старый клиент: правый клик по иконке в трее ? Выход.
Затем:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1

