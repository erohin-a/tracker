<!-- Часть 288 из 1409 -->
# in loop:
*Хлебные крошки:* in loop:

[◀ ---------- Client config ----------](287_Client_config.md) | [Оглавление](00_BCE_INDEX.md) | [after loop: ▶](289_after_loop.md)

---

# in loop:
if g["first_start"] is None or r["start_local"] < g["first_start"]:
    g["first_start"] = r["start_local"]
if g["last_end"] is None or r["end_local"] > g["last_end"]:
    g["last_end"] = r["end_local"]

