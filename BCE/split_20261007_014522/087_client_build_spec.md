<!-- Часть 87 из 1409 -->
# `client/build.spec`
*Хлебные крошки:* Полный код всех файлов проекта «Трекер» / ?? Папка `client/` / `client/build.spec`

[◀ `client/main.py`](086_client_main_py.md) | [Оглавление](00_BCE_INDEX.md) | [`client/version_info.txt` ▶](088_client_version_info_txt.md)

---

### `client/build.spec`

```python
import os

_hidden = [
    'pynput.keyboard._win32', 'pynput.mouse._win32',
    'pynput.keyboard._xorg', 'pynput.mouse._xorg',
    'keyring.backends.Windows', 'keyring.backends.SecretService',
    'keyring.backends.kwallet', 'keyring.backends.libsecret',
    'cryptography', 'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.backends.openssl.backend',
]

_datas = [(f, '.') for f in ('icon.ico',) if os.path.exists(f)]
_ver = {'version': 'version_info.txt'} if os.path.exists('version_info.txt') else {}
_icon = 'icon.ico' if os.path.exists('icon.ico') else None

a = Analysis(['main.py'], pathex=['.'], binaries=[], datas=_datas,
             hiddenimports=_hidden, hookspath=[], runtime_hooks=[],
             excludes=[], noarchive=False)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='Tracker',
          debug=False, strip=False, upx=False, console=False,
          icon=_icon, **_ver)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
               strip=False, upx=False, name='Tracker')
```

