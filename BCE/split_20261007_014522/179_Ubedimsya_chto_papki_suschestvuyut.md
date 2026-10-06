<!-- Часть 179 из 1409 -->
# Убедимся, что папки существуют
*Хлебные крошки:* Убедимся, что папки существуют

[◀ ============================================================](178_part.md) | [Оглавление](00_BCE_INDEX.md) | [---------------- requirements.txt ---------------- ▶](180_requirements_txt.md)

---

# Убедимся, что папки существуют
$serverDir = "D:\tracker\server"
$templatesDir = "D:\tracker\server\templates"
New-Item -ItemType Directory -Force -Path $serverDir | Out-Null
New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null

