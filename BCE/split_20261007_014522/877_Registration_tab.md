<!-- Часть 877 из 1409 -->
# Registration tab
*Хлебные крошки:* Registration tab

[◀ General tab](876_General_tab.md) | [Оглавление](00_BCE_INDEX.md) | [После всех настроек: ▶](878_Posle_vseh_nastroek.md)

---

# Registration tab
reg.group.info
reg.uid
reg.hostname
reg.server
reg.group.server
reg.server_url
reg.cert_fingerprint
reg.check_connection
reg.bootstrap_token
reg.reregister
OK let me write it. I'll include RU/EN versions.
For themes, standard QSS:
Light - default
Dark - dark background, light text
Let me draft a minimal but working QSS.
For the main window currently it has hardcoded styles (buttons with green/red). With dark theme, these need to be adjusted. That's complex. Let me keep the buttons as-is but change the overall widget background/foreground.
Actually the buttons have explicit background colors, so they'll stay green/red - that's fine.
Let me write.
Let me plan config.py additions:
python
CONFIG_FILE = BASE_DIR / "config.json"

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_config(data: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_setting(key: str, default=None):
    return load_config().get(key, default)

def set_setting(key: str, value) -> None:
    data = load_config()
    data[key] = value
    save_config(data)

