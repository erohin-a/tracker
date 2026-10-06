<!-- Часть 879 из 1409 -->
# PowerShell script that uses Python itself to write the file
*Хлебные крошки:* PowerShell script that uses Python itself to write the file

[◀ После всех настроек:](878_Posle_vseh_nastroek.md) | [Оглавление](00_BCE_INDEX.md) | [General ▶](880_General.md)

---

# PowerShell script that uses Python itself to write the file
$writer_script = @'
import json
import sys

lines = json.loads(sys.stdin.read())
with open(r"D:\tracker\client\settings_dialog.py", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
'@
No, this is getting too complicated.
Simplest reliable approach: use the here-string @'...'@ approach for each file. If content > 30-50 lines, split.
Let me just do it and see. I'll write settings_dialog.py in one here-string, ~400 lines. If it works for the user, great.
Actually, let me be pragmatic. Let me first do the small files (i18n.py, themes.py, config.py patch), test with the user, then do settings_dialog.py.
Response plan:
Short intro - what we're doing
Script 1: client/i18n.py (new file, ~100 lines)
Script 2: client/themes.py (new file, ~50 lines)
Script 3: patch config.py - add config loaders
Test run
Then next message: settings_dialog.py rewrite + main.py patch.
That way if here-string issue occurs, we catch it early on small files.
Let me write.
Wait, I need to think about what i18n keys we need for the settings dialog.
Let me list them:
text
