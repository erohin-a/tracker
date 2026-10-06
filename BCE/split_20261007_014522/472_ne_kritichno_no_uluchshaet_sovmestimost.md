<!-- Часть 472 из 1409 -->
# (не критично, но улучшает совместимость)
*Хлебные крошки:* (не критично, но улучшает совместимость)

[◀ --- 3. Патчим http_client.py: отключаем IPv6-предпочтение если нужно ---](471_3_Patchim_http_client_py_otklyuchaem_IPv6_predpochtenie_esli_nuzhno.md) | [Оглавление](00_BCE_INDEX.md) | [эмулируем импорт config через dotenv ▶](473_emuliruem_import_config_cherez_dotenv.md)

---

# (не критично, но улучшает совместимость)
Write-Host "`nТекущий SERVER_URL после правок:" -ForegroundColor Cyan
python -c @"
import sys
sys.path.insert(0, r'D:\tracker')
