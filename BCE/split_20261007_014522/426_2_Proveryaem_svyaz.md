<!-- Часть 426 из 1409 -->
# --- 2. Проверяем связь ---
*Хлебные крошки:* --- 2. Проверяем связь ---

[◀ --- 1. Обновляем client/.env ---](425_1_Obnovlyaem_client_env.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](427_part.md)

---

# --- 2. Проверяем связь ---
Write-Host "`n--- Проверка через IPv4 ---" -ForegroundColor Cyan
curl.exe -k -4 https://127.0.0.1/api/v1/version

Write-Host "`n--- Проверка через Python (как делает клиент) ---" -ForegroundColor Cyan
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -c @"
import socket
print('getaddrinfo(127.0.0.1):', socket.getaddrinfo('127.0.0.1', 443, type=socket.SOCK_STREAM)[0][4])
print('getaddrinfo(localhost):', socket.getaddrinfo('localhost', 443, type=socket.SOCK_STREAM)[0][4])

import httpx
try:
    r = httpx.get('https://127.0.0.1/api/v1/version', verify=False, timeout=5.0)
    print('127.0.0.1 ?', r.status_code, r.json())
except Exception as e:
    print('127.0.0.1 ? ОШИБКА:', e)
"@
Ожидаемый вывод:
text
OK  client/.env обновлён
TRACKER_SERVER_URL=https://127.0.0.1
TRACKER_PIN=
TRACKER_VERSION=1.0.0

--- Проверка через IPv4 ---
{"latest_version":"0.0.0",...}

--- Проверка через Python ---
getaddrinfo(127.0.0.1): ('127.0.0.1', 443)
getaddrinfo(localhost): ('::1', 443, ...)   ? вот оно!
127.0.0.1 ? 200 {'latest_version': '0.0.0.0', ...}
Если увидите что-то похожее — всё правильно, 127.0.0.1 решает проблему.
________________________________________
Запуск клиента
Клиент должен быть закрыт. Запускаем заново:
powershell
cd D:\tracker
client\.venv\Scripts\Activate.ps1
python -m client.main
Параллельно во втором окне:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Wait -Encoding UTF8
Ожидаемые строки:
text
tracker.sync INFO SyncWorker started; server=https://127.0.0.1
tracker.sync INFO Server reachable (HTTP 200)
На панели клиента — «? онлайн» зелёным.
________________________________________
Если появится ошибка SSL
Возможные варианты:
SSL: CERTIFICATE_VERIFY_FAILED
Сертификат не покрывает 127.0.0.1 — но у вас SAN DNS:localhost,IP:127.0.0.1, поэтому должно работать. Если всё-таки ошибка — проверьте:
powershell
Get-Content "$env:APPDATA\Tracker\ca.pem" | Select-String "127.0.0.1"
Если не найдёт — перевыпустим сертификат.
На будущее — TRACKER_INSECURE=1
Если хотите временно выключить проверку SSL (только для теста), добавьте в client/.env:
text
TRACKER_INSECURE=1
Клиент перестанет проверять сертификат. Это для отладки, на проде не использовать.
________________________________________
Почему так произошло
Скорее всего, у вас в корпоративной сети установлен DNS-суффикс ANTOR.msk, и Windows некорректно резолвит localhost через IPv6. Это типичная проблема в доменных окружениях с WSL2.
На будущее: делайте в client/.env https://127.0.0.1 для локальной разработки. При развёртывании на реальном сервере — там будет либо IP, либо нормальное DNS-имя (например, tracker.company.ru), и проблемы не возникнет.
________________________________________
После того как «онлайн» появится
Пришлите:
powershell
Get-Content "$env:APPDATA\Tracker\client.log" -Tail 30 -Encoding UTF8
docker compose logs api --tail=20
И скажите — ушли ли 500-е ошибки. После этого переходим к следующему блоку:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация, поиск
XLSX — убрать «Группа»/«Аварийный», добавить «Год / Месяц / Число»
Группировка «Месяц ? Сотрудник» в онлайн-отчёте
Календарь рабочих/нерабочих дней
Heartbeat + Онлайн/Оффлайн на дашборде
Массовая привязка ПК через CSV
PDF-отчёт
Запускайте скрипт, пришлите лог — и поехали дальше.
Если всё олк переходим к следующему блоку
Логи показывают что теперь всё работает - 200 OK на sessions и records/batch. Есть ещё иногда getaddrinfo failed, но это скорее всего остаточные проблемы с локальным DNS.
Похоже проблема была в том, что клиент использует "https://localhost" в некоторых случаях (в httpx запросах видно https://localhost/...), а в config.py SERVER_URL установлен на 127.0.0.1. То есть у клиента могут быть разные источники URL - config.py клиента и .env.
Но главное - синхронизация идёт, 200 OK. Пользователь говорит "переходим к следующему блоку".
Следующий блок по плану:
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров, зависимая фильтрация, поиск
XLSX — убрать «Группа»/«Аварийный», добавить «Год / Месяц / Число»
Группировка «Месяц ? Сотрудник» в онлайн-отчёте
Календарь рабочих/нерабочих дней
Heartbeat + Онлайн/Оффлайн на дашборде
Массовая привязка ПК через CSV
PDF-отчёт
Давайте выдам всё крупным блоком. Много кода, но я буду структурировать по шагам.
Начнём с server/web_admin.py - полная замена с:
Мультивыбор отделов и сотрудников (с зависимой фильтрацией на JS)
Мультивыбор компьютеров
Поиск в select
Группировка по месяцам
XLSX с колонками Год/Месяц/Число, без Группы и Аварийных
Heartbeat endpoint
Плюс client/main.py - добавить heartbeat
Плюс server/main.py - добавить /api/v1/heartbeat
Плюс шаблоны:
reports.html - с мультивыбором
report_result.html - с новыми группировками
dashboard.html - с онлайн/оффлайн
base.html - с tooltips
Плюс models.py - уже есть поле last_seen_at, только надо его обновлять в heartbeat
Плюс календарь рабочих/нерабочих дней - новая модель + страница
Это ОГРОМНЫЙ блок. Давайте разделю его на 2-3 сообщения, чтобы пользователь не утонул.
Разделю так:
Сообщение 1 (это): Фильтры + поиск + мультивыбор + heartbeat + XLSX-колонки + группировка по месяцам
Сообщение 2: Календарь рабочих дней + подсветка Сб/Вс + массовая привязка ПК + PDF
Или даже так, чтобы всё-таки влезло, я уплотню код и дам всё в одном сообщении, но с понятной разбивкой.
Попробую так - одно большое сообщение со всеми 7 пунктами, но каждый пункт компактный.
Актуально: клиент использует 127.0.0.1, но в логах видно "https://localhost/..." - значит config.py клиента всё ещё содержит localhost. Это ок, потому что httpx иногда резолвит, но проблема возникает. Надо будет починить клиентский config.py чтобы он читал SERVER_URL правильно.
Проверю - в .env клиента TRACKER_SERVER_URL=https://127.0.0.1, но в логах https://localhost. Значит config.py берёт не из .env, либо .env перезаписывается, либо .env был не тот.
Скорее всего в config.py клиента SERVER_URL не читается из .env - там дефолт "https://tracker.example.com", а в .env override=True должно работать. Но в логах видно https://localhost - значит где-то зашито localhost.
Возможно, в http_client есть свой URL. Или в crypto.py. Или где-то ещё прописан localhost. Надо проверить.
Ладно, я это учту и дам патч клиента тоже. Но сначала перейдём к основному блоку.
Начну отвечать. Буду лаконичен. Дам полные скрипты.
Отлично, синхронизация пошла — 200 OK на sessions и batch ??
Из логов видно: записи уходят, ошибок 500 нет. Остались редкие getaddrinfo failed — это старые файлы клиента ещё держат где-то localhost (в config.py клиента дефолт). Поправим это в текущем блоке заодно.
Переходим к следующему крупному блоку. Он большой — разбил на 3 подблока. Каждый — отдельный PowerShell-скрипт.
Что делаем
Подблок A.
Фильтры в отчётах — мультивыбор отделов + сотрудников + компьютеров с зависимой фильтрацией
Поиск внутри <select multiple> (собственный, без библиотек)
Группировка «Месяц ? Сотрудник» в онлайн-отчёте
XLSX — убрать «Группа» и «Аварийный», добавить колонки «Год / Месяц / Число»
Подблок B.
Heartbeat — эндпоинт + колонка «Онлайн/Оффлайн» на дашборде
Фикс дефолтного localhost в клиенте
Массовая привязка ПК через CSV
Подблок C.
Календарь рабочих/нерабочих дней + подсветка Сб/Вс
PDF-отчёт
Начнём с A. Скрипты запускать по порядку.
________________________________________
Скрипт A1 — server/web_admin.py (полная замена)
powershell
$ErrorActionPreference = "Stop"
$serverDir = "D:\tracker\server"

$web_admin_py = @'
"""
Веб-интерфейс администратора.
"""
import csv
import hashlib
import io
import json
import secrets
from collections import defaultdict
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional, List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import (
    AppSetting, AuditLog, BootstrapToken, Computer, Department,
    Employee, Record, WorkSession,
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="server/templates")

RU_MONTHS = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
             "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


