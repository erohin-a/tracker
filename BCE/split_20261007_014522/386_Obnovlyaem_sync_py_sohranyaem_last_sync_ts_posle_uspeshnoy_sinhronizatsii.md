<!-- Часть 386 из 1409 -->
# Обновляем sync.py — сохраняем last_sync_ts после успешной синхронизации
*Хлебные крошки:* Обновляем sync.py — сохраняем last_sync_ts после успешной синхронизации

[◀ reports.html — мультивыбор сотрудников + отдел, без tz/workday (они в настройках)](385_reports_html_multivybor_sotrudnikov_otdel_bez_tz_workday_oni_v_nastroykah.md) | [Оглавление](00_BCE_INDEX.md) | [client/registration_dialog.py ▶](387_client_registration_dialog_py.md)

---

# Обновляем sync.py — сохраняем last_sync_ts после успешной синхронизации
$syncPath = "$clientDir\sync.py"
$syncContent = [System.IO.File]::ReadAllText($syncPath, [System.Text.UTF8Encoding]::new($false))

if (-not $syncContent.Contains("last_sync_ts")) {
    $syncContent = $syncContent.Replace(
        "        self.synced.emit(len(accepted))`n        return True",
        "        if accepted:`n            try:`n                from datetime import datetime, timezone as _tz`n                db.set_meta('last_sync_ts', datetime.now(_tz.utc).isoformat())`n            except Exception:`n                pass`n        self.synced.emit(len(accepted))`n        return True"
    )
    [System.IO.File]::WriteAllText($syncPath, $syncContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  OK  sync.py сохраняет last_sync_ts" -ForegroundColor Green
} else {
    Write-Host "  sync.py уже пропатчен" -ForegroundColor Yellow
}
python -c "import ast; ast.parse(open(r'$syncPath', encoding='utf-8').read()); print('  sync.py SYNTAX OK')"
________________________________________
Что делать после запуска
Запустить скрипты 1 ? 2 ? 3 ? 4 ? 5 ? 6 по порядку.
Открыть https://localhost/admin/settings — увидите 8 настроек (отчёты + клиенты).
Открыть https://localhost/admin/departments — создать пару отделов.
Открыть /admin/employees — вкладки «Активные» / «Уволенные» / «Все».
Открыть /admin/reports — сотрудники выбираются мультивыбором (Ctrl+клик), есть фильтр по отделу.
Сформировать XLSX — длительности должны быть в формате [ЧЧ]:ММ:СС, дата — ДД.ММ.ГГГГ.
Перезапустить клиент: cd D:\tracker; client\.venv\Scripts\Activate.ps1; python -m client.main — на панели появится время старта в локальном поясе, счётчик, статус сервера, очередь, последняя синхронизация.
________________________________________
Что осталось для следующей сессии
Из моих предложений — самое ценное:
Heartbeat-эндпоинт — колонка «Онлайн/Оффлайн» на дашборде. 20 минут работы.
Опоздания — сравнение старта сессии с workday_start_hour.
Плановые часы на месяц — сравнение «факт vs норма» в отчёте по сотрудникам.
PDF-отчёт — reportlab, шрифт с кириллицей.
Массовая привязка ПК — загрузка CSV «hostname ? ФИО».
Telegram-уведомления — если ПК офлайн > 30 мин.
Скажите, что делаем следующим — выдам такой же готовый код.
в админке в отчётах в фильтрах Отдел добавить возможность добавить возможность выбора нескольких отделов как и в сотрудниках. когда выбираем несколько отделов, в фильтре сотрудники сразу отфильтровываются и остаются только те которые входят в отдел. В фильтре компьютер тоже добавить возможность выбрать несколько. попробуй реализовать поиск в фильтрах. В XLSX отчётах убери столбец Группа и столбец и Аварийный. Добавь отдельно столбцы с форматом дата год (пример 2026) месяц (пример Сентябрь) число (пример 17) В отчётах онлайн нужно сделать возможность сворачивать до месяца. (когда будет 50 сотрудников и в сентябре 22 сотрудника будет очень много строчек и будет не читабельно) Также необходимо подсвечивать дни недели особенно субботы воскресенья возможность считать их или не считать. А может быть в настройках создать календарь рабочие не рабочие дни и ручками прям пройти на год в перед и проставить как считаешь? Как лучше поступить? Делаем твои предложения Heartbeat-эндпоинт — колонка «Онлайн/Оффлайн» на дашборде. 20 минут работы. Массовая привязка ПК — загрузка CSV «hostname ? ФИО». PDF-отчёт — reportlab, шрифт с кириллицей. В клиентской части не заработало Активное окно. давай его уберём. Давай начнём настраивать клиентский интерфейс что бы в нём проводить регистрацию. что бы в дальнейшем отправить Exe он его запустил зарегистрировал свой компьютер без всяких лишних манипуляций
The user is asking for a lot. Let me organize this carefully. The tasks are:
Admin reports filters:
Multiple departments selection (like employees)
When multiple departments selected, filter employees in the employee filter to only those in those departments
Multiple computers selection
Search in filters
XLSX reports:
Remove "Группа" column
Remove "Аварийный" column
Add date format columns: year (2026), month (Сентябрь), day (17)
Also make date in DMY format that Excel understands
Online reports (HTML):
Ability to collapse to month level (when 50 employees x 22 days = too many rows)
Weekend highlighting:
Highlight Saturday/Sunday
Ability to count or not count them
Better: calendar in settings where admin can mark working/non-working days for the year
Do the proposals:
Heartbeat endpoint + online/offline column on dashboard
Bulk PC assignment via CSV
PDF report with reportlab + Cyrillic
Client:
Remove "Active window" from client panel (didn't work)
Add registration wizard to client interface - so we can distribute EXE and user just runs it and registers
This is a lot. Let me think about the best approach. The user has been asking me to write full PowerShell scripts to replace files. That's been working well. But this is a huge amount of code. Let me break it into chunks.
Given the complexity, I should:
First address the client-side registration interface (task 6) - most important for distributing EXE
Remove Active window from client
Then admin filters (1, 2, 3, 4)
Then heartbeat, bulk PC, PDF
Finally weekend calendar
Actually, let me think about priority. The user says "Давай начнём настраивать клиентский интерфейс что бы в нём проводить регистрацию. что бы в дальнейшем отправить Exe он его запустил зарегистрировал свой компьютер без всяких лишних манипуляций"
This is important because currently client requires bootstrap.txt file to be pre-placed. For distributing as EXE, we need a wizard.
Let me structure my response:
Part 1 (this response): Client registration wizard + remove active window
Part 2 (next response): Admin reports filters
Part 3: XLSX changes + month collapsing + weekend highlighting + calendar
Part 4: Heartbeat + bulk assign + PDF
Actually, the user asked to do everything. Let me try to do it in one big response but organized. Or maybe split into 2 responses.
Given the sheer volume, I'll do a focused response for client registration wizard first, since that's the biggest value item, and outline what comes next. Then in the next message I'll do the admin part.
Wait, but the user said "Давай начнём настраивать клиентский интерфейс" - let's START setting up the client interface. So they want to do this now.
Let me focus on:
Client registration wizard (new RegistrationDialog in client)
Remove Active window from client panel
Server endpoint check for bootstrap-token validation (to give feedback in wizard)
Then briefly outline the rest.
Actually let me think about the registration flow:
User launches EXE
Client checks if registered (keyring/credentials.enc)
If not registered ? show dialog asking for bootstrap token
User enters token ? client sends to server ? gets client_secret
Saved to keyring, dialog closes, main window appears
But currently ensure_registered() reads from bootstrap.txt or env. We need to change this to show a dialog if not registered.
Also need a way to validate the token on server side without burning it (or just try to register and show error if fails).
Let me write:
client/registration_dialog.py - new file with QDialog
client/main.py - modified to show dialog if not registered
client/registration.py - modify ensure_registered to accept token as arg
client/main.py - remove "active window" from panel (actually it's just a label that shows "—" because no data)
Wait, the user said "не заработало Активное окно. давай его уберём" - the "Active window" field in the panel didn't work. Remove it.
Let me write these scripts.
For the registration dialog, I'll need:
Big title "Регистрация Трекера"
Text explaining what to do
Input field for bootstrap token
Button "Зарегистрировать"
Status/error label
On success - save and close
Also I should add a "tray" icon option maybe? Let me keep it simple.
Let me also make sure the dialog doesn't call ensure_registered() automatically - the main flow needs to change so that main window opens first, then it checks registration.
Actually let me think about the flow again:
main() creates QApplication
main() tries to check if registered
If not - show RegistrationDialog (modal)
If user cancels - quit
If registered successfully - proceed to MainWindow
MainWindow runs as normal
This is cleaner than opening MainWindow and then dialog. Let me do this.
Let me code it:
python
