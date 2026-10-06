<!-- Часть 505 из 1409 -->
# Копируем Arial и Arial Bold
*Хлебные крошки:* Копируем Arial и Arial Bold

[◀ Создаём папку](504_Sozdaem_papku.md) | [Оглавление](00_BCE_INDEX.md) | [Находим начало блока _pdf_table_data ▶](506_Nahodim_nachalo_bloka_pdf_table_data.md)

---

# Копируем Arial и Arial Bold
Copy-Item "$env:WINDIR\Fonts\arial.ttf"  "D:\tracker\server\fonts\DejaVuSans.ttf"      -Force
Copy-Item "$env:WINDIR\Fonts\arialbd.ttf" "D:\tracker\server\fonts\DejaVuSans-Bold.ttf" -Force

Get-ChildItem "D:\tracker\server\fonts" | Format-Table Name, Length
Arial в Windows есть всегда, поддержка кириллицы полная. PDF-рендерер скажет DejaVuSans.ttf — но это просто имя, на деле внутри Arial. Работает отлично.
________________________________________
Вероятный фикс №2 — .dockerignore режет fonts
Проверьте содержимое D:\tracker\.dockerignore и D:\tracker\server\.dockerignore (см. шаг 4 диагностики). Если там есть строки вроде fonts, *.ttf — удалите их.
Частая причина: .dockerignore создают с шаблоном для Python-проектов, а в нём есть правила типа *.ttf, *.woff.
________________________________________
Вероятный фикс №3 — образ не пересобрался с --build
Если reportlab не установлен (шаг 3 выдаёт ModuleNotFoundError):
powershell
cd D:\tracker
docker compose down
docker compose up -d --build
Ключевое — --build. Просто up -d возьмёт старый образ.
________________________________________
Вероятный фикс №4 — проблема в коде PDF-рендера
Если и шрифт, и reportlab на месте, а ошибка остаётся — пришлите полный traceback из docker compose logs api --tail=60. Я там вижу конкретную строку и правлю.
Возможные причины в коде:
from reportlab.lib.enums import TA_LEFT, TA_CENTER — но TA_LEFT = 0, а TA_CENTER = 1, в новых версиях reportlab может быть TA_JUSTIFY устарел
ROWBACKGROUNDS может дать конфликт с явным BACKGROUND для weekend/holiday — надо смотреть порядок команд стиля
Если скажете, что именно в трейсбеке — поправлю точечно.
________________________________________
Что мне прислать
Одним сообщением — вывод скрипта диагностики (все 5 блоков). Особенно важны блоки 1–3 и последние 40 строк логов с Traceback.
По ним сразу скажу:
«Скачай Arial, потому что шрифт не долетел» — или
«Поправь .dockerignore, потому что fonts исключён» — или
«Вот строка N в _render_pdf, замени на такую-то»
И PDF заработает.
(.venv) PS D:\tracker> # 1. Скачался ли шрифт? >> dir D:\tracker\server\fonts >> >> # 2. Виден ли он в контейнере? >> docker compose exec -T api ls -la /app/server/fonts/ >> >> # 3. Установлен ли reportlab? >> docker compose exec -T api python -c "import reportlab; print(reportlab.Version)" Каталог: D:\tracker\server\fonts Mode LastWriteTime Length Name ---- ------------- ------ ---- -a---- 07.12.2019 12:08 1036584 DejaVuSans.ttf total 1024 drwxr-xr-x 2 root root 4096 Sep 17 20:02 . drwxr-xr-x 1 root root 4096 Sep 17 20:19 .. -rwxr-xr-x 1 root root 1036584 Dec 7 2019 DejaVuSans.ttf 4.2.2
Всё на месте — шрифт и reportlab. Значит, 500 в самом коде _render_pdf. Нужен traceback.
Давайте попрошу логи. Но лучше сразу дам вероятную причину и исправление.
Смотрю на код _render_pdf... Возможные проблемы:
reportlab.Version возвращает 4.2.2 — ок.
Импорт from reportlab.lib.enums import TA_LEFT, TA_CENTER — есть.
_pdf_table_data(report, styles) — внутри цикл. Может падать на каком-то поле. Например r['date'] в sessions может быть None (если группировка не days). Нет, я проверил — там своя ветка.
Хм, давайте посмотрим внимательнее на дату в группировке days:
python
d = r["date"]
d_str = d.strftime("%d.%m.%Y")
Если d — это date, то ок. Но в группировке _split_by_day мы кладём date — это datetime.date. OK.
Проблема может быть в _c.HexColor("#fff3cd") — если colors импортирован как from reportlab.lib import colors as _c, то .HexColor есть.
Ещё возможные проблемы:
paragraphStyle с кириллицей до регистрации шрифта — нет, регистрируем до
SimpleDocTemplate падает если buf не поддерживает seek — BytesIO поддерживает
Возможно проблема в TA_LEFT/TA_CENTER импорте. Попробую иначе.
Хм, ещё одна идея: _hms_to_excel — не для PDF, но _fmt_dur для PDF возвращает строку "HH:MM:SS". OK.
Погоди, а вдруг проблема в сигнатуре _pdf_table_data? Она определена с параметром report без type hints, внутри используется report["group_by"]. Если report — dict, ок.
Может быть падает на styles["cell"] — я использую styles["cell"] и styles["cell_center"], они определены. OK.
Другой вариант: Paragraph(str(...)) не может сериализовать не-ASCII до регистрации шрифта. Но шрифт зарегистрирован.
Самый вероятный — paragraph со str() от None или от чего-то не-строкового. У меня cell(text) уже преобразует через str(). OK.
Стоп! Вижу потенциальную проблему. В _render_pdf я использую from reportlab.lib.enums import TA_LEFT, TA_CENTER. В reportlab 4.x эти константы существуют, но могут быть другой формы. Проверить не могу.
Ещё вариант: _fmt_dur определён вне класса — ок.
Возможная проблема: строка:
python
("FONTSIZE", (0, 0), (-1, -1), 9),
норм.
Или:
python
("ROWBACKGROUNDS", (0, 1), (-1, -1), [_c.white, _c.HexColor("#f8f9fa")]),
Может конфликтовать с BACKGROUND для weekend/holiday в style_cmds — reportlab применит последний. Порядок: ROWBACKGROUNDS добавлен раньше, потом weekend/holiday идут следом. OK.
Хм. Давайте просто попрошу traceback.
Но! Я могу подстраховаться — переписать _render_pdf более надёжно и защищённо. Давайте:
Уберу ROWBACKGROUNDS — заменю на чередование вручную
Оберну всё в try/except с понятным логом
Или — ещё вариант — самый вероятный: проблема в SimpleDocTemplate с title=f"Отчёт {date_from} — {date_to}", где — это em-dash. Возможно, это вызывает ошибку кодирования в PDF metadata. Reportlab должен обрабатывать, но...
Ещё возможная проблема — Paragraph(..., styles["subtitle"]) с текстом, содержащим | и ' — не должно ломать.
Стоп, ещё одно: from reportlab.lib.enums import TA_LEFT, TA_CENTER — возможно, в 4.2.2 в enums нет TA_LEFT? На самом деле, в reportlab есть TA_LEFT = 0 и TA_CENTER = 1. Должны быть.
Давайте всё-таки попрошу traceback. Без него я только гадаю.
Дам короткий скрипт для получения traceback и одновременно дам более надёжный PDF-рендер с логированием ошибки, чтобы при следующем 500 в логах было понятно, что не так.
Всё на месте: шрифт, reportlab 4.2.2. Значит, падает сам код
Нужен точный traceback — без него гадаю. Сделаю сразу два шага: попрошу лог и добавлю в PDF-рендер обработку ошибок, чтобы на будущее в логе было понятное сообщение.
________________________________________
Шаг 1 — получим traceback
Откройте /admin/reports, выберите PDF, сформируйте. Через 3 секунды:
powershell
cd D:\tracker
docker compose logs api --tail=60
Ищите блок Traceback (most recent call last):. Пришлите его мне — там будет конкретная строка в web_admin.py.
________________________________________
Шаг 2 — заменяем _render_pdf на защищённую версию
Пока смотрим лог, обновим рендер — я уберу сомнительные места (ROWBACKGROUNDS, TA_LEFT/TA_CENTER, title с em-dash) и добавлю логирование ошибок. Если и упадёт — в логе будет видно, что именно.
powershell
$ErrorActionPreference = "Stop"
$mainPath = "D:\tracker\server\web_admin.py"
$content = [System.IO.File]::ReadAllText($mainPath, [System.Text.UTF8Encoding]::new($false))

