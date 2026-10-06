<!-- Часть 980 из 1409 -->
# Дополняем DARK_QSS перед закрывающими тройными кавычками
*Хлебные крошки:* Дополняем DARK_QSS перед закрывающими тройными кавычками

[◀ ---------- 3.2. Убираем inline-стили с кнопок старт/стоп (заменим на objectName) ----------](979_3_2_Ubiraem_inline_stili_s_knopok_start_stop_zamenim_na_objectName.md) | [Оглавление](00_BCE_INDEX.md) | [Найдём конец DARK_QSS ▶](981_Naydem_konets_DARK_QSS.md)

---

# Дополняем DARK_QSS перед закрывающими тройными кавычками
addition = '''
/* ---------- Главное окно ---------- */
QMainWindow { background-color: #2b2b2b; }
QMainWindow > QWidget { background-color: #2b2b2b; }

/* ---------- Панель информации в главном окне ---------- */
QFrame#infoPanel {
    background-color: #3a3a3a;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { color: #e0e0e0; background: transparent; }
QFrame#infoPanel QLabel[role="title"] { color: #a0a0a0; }

/* ---------- Кнопки старт/стоп ---------- */
QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:pressed { background-color: #218838; }
QPushButton#btnStart:disabled { background-color: #404040; color: #888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:pressed { background-color: #c82333; }
QPushButton#btnStop:disabled { background-color: #404040; color: #888; }

/* ---------- Светлый QSS-вариант тоже нужен ---------- */
'''

LIGHT_QSS = """
QFrame#infoPanel {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 8px;
}
QFrame#infoPanel QLabel { background: transparent; }

QPushButton#btnStart {
    background-color: #28a745; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStart:hover { background-color: #34ce57; }
QPushButton#btnStart:disabled { background-color: #c0c0c0; color: #888; }

QPushButton#btnStop {
    background-color: #dc3545; color: white; font-weight: bold;
    padding: 14px; font-size: 15px; border: none; border-radius: 6px;
}
QPushButton#btnStop:hover { background-color: #e04a5a; }
QPushButton#btnStop:disabled { background-color: #c0c0c0; color: #888; }
"""

"""

