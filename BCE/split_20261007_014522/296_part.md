<!-- Часть 296 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ web_admin.py](295_web_admin_py.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](297_part.md)

---

# ============================================================
$web_admin_py = @'
"""
Веб-интерфейс администратора для проекта «Трекер».
"""
import csv
import hashlib
import io
import json
import secrets
from collections import defaultdict
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import (
    AppSetting, AuditLog, BootstrapToken, Computer, Employee, Record, WorkSession,
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="server/templates")


