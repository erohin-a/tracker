<!-- Часть 185 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ requirements.txt](184_requirements_txt.md) | [Оглавление](00_BCE_INDEX.md) | [============================================================ ▶](186_part.md)

---

# ============================================================
$req_txt = @'
fastapi==0.111.0
uvicorn[standard]==0.30.1
gunicorn==22.0.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
pydantic==2.7.4
pydantic-settings==2.3.0
cryptography==42.0.8
python-multipart==0.0.9
jinja2==3.1.4
itsdangerous==2.2.0
openpyxl==3.1.5
tzdata==2024.1
'@
[System.IO.File]::WriteAllText("$serverDir\requirements.txt", $req_txt, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK  requirements.txt" -ForegroundColor Green

