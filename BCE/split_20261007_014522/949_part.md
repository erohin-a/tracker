<!-- Часть 949 из 1409 -->
# ============================================================
*Хлебные крошки:* ============================================================

[◀ Сам диалог](948_Sam_dialog.md) | [Оглавление](00_BCE_INDEX.md) | [Записываем финальный файл ▶](950_Zapisyvaem_finalnyy_fayl.md)

---

# ============================================================
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("settings.title"))
        self.setMinimumSize(660, 640)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        tabs = QTabWidget()
        tabs.addTab(ReminderTab(), t("settings.tab.reminder"))
        tabs.addTab(GeneralTab(), t("settings.tab.general"))
        tabs.addTab(RegistrationTab(), t("settings.tab.registration"))

        btn_close = QPushButton(t("btn.close"))
        btn_close.setMinimumHeight(36)
        btn_close.clicked.connect(self.accept)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_close)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addLayout(bottom)
        self.setLayout(layout)
'@

[System.IO.File]::WriteAllText("D:\tracker\client\_sd_part3.tmp", $part3, [System.Text.UTF8Encoding]::new($false))
Write-Host "OK: часть 3 записана ($($part3.Length) символов)" -ForegroundColor Green
________________________________________
Скрипт 4 — Склейка частей + проверка
powershell
$ErrorActionPreference = "Continue"
Set-Location D:\tracker

$p1 = [System.IO.File]::ReadAllText("D:\tracker\client\_sd_part1.tmp", [System.Text.UTF8Encoding]::new($false))
$p2 = [System.IO.File]::ReadAllText("D:\tracker\client\_sd_part2.tmp", [System.Text.UTF8Encoding]::new($false))
$p3 = [System.IO.File]::ReadAllText("D:\tracker\client\_sd_part3.tmp", [System.Text.UTF8Encoding]::new($false))

$full = $p1 + $p2 + $p3

