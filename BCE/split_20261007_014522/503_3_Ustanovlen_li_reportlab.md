<!-- Часть 503 из 1409 -->
# 3. Установлен ли reportlab?
*Хлебные крошки:* 3. Установлен ли reportlab?

[◀ 2. Виден ли он в контейнере?](502_2_Viden_li_on_v_konteynere.md) | [Оглавление](00_BCE_INDEX.md) | [Создаём папку ▶](504_Sozdaem_papku.md)

---

# 3. Установлен ли reportlab?
docker compose exec -T api python -c "import reportlab; print(reportlab.Version)"
Что должно быть:
dir — файл DejaVuSans.ttf (или arial.ttf), размер ~700 КБ
ls в контейнере — тот же файл виден по пути /app/server/fonts/
reportlab — версия вида 4.2.2
Если что-то из этого пусто — вот фикс.
________________________________________
Вероятный фикс №1 — шрифт не скачался
Если dir D:\tracker\server\fonts пусто или выдаёт ошибку — просто скопируем Arial из Windows:
powershell
$ErrorActionPreference = "Stop"

