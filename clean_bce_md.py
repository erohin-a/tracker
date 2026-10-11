"""
Снимает pandoc-экранирование в .md файлах BCE.
Pandoc превращает '# Заголовок' в '\# Заголовок', '**bold**' в '\*\*bold\*\*' и т.д.
Этот скрипт возвращает исходный Markdown.
"""
import re
import sys
from pathlib import Path

# Символы, которые pandoc экранирует обратным слэшем
ESCAPES = r'\`*_{}[]()#+-.!|~<>'

# Паттерн: обратный слэш + один из спецсимволов
PATTERN = re.compile(r'\\([' + re.escape(ESCAPES) + r'])')


def clean(text: str) -> str:
    """Убирает '\' перед markdown-спецсимволами."""
    return PATTERN.sub(r'\1', text)


def fix_first_heading(text: str, n: int) -> str:
    """Заменяет '# @@ N часть разработки' на '# Часть N — ...'."""
    titles = {
        1: "Часть 1 — начало проекта",
        2: "Часть 2 — сервер и модели",
        3: "Часть 3 — админка и отчёты",
        4: "Часть 4 — клиент и синхронизация",
        5: "Часть 5 — i18n, темы, напоминания",
        6: "Часть 6 — SCP и сертификаты",
        7: "Часть 7 — установщик и развёртывание",
        8: "Часть 8 — финальная сборка",
    }
    # Первая строка файла
    lines = text.split('\n', 1)
    if lines and lines[0].lstrip().startswith('#'):
        lines[0] = '# ' + titles.get(n, f'Часть {n}')
        return '\n'.join(lines)
    return text


def process(path: Path, n: int):
    raw = path.read_text(encoding='utf-8')
    cleaned = clean(raw)
    cleaned = fix_first_heading(cleaned, n)
    path.write_text(cleaned, encoding='utf-8')
    print(f"[OK] {path.name}: {len(raw)} -> {len(cleaned)} символов")


if __name__ == '__main__':
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'D:\tracker\docs\BCE')

    for i in range(1, 9):
        f = target / f'part_{i:02d}.md'
        if not f.exists():
            print(f"[!] Нет файла: {f}")
            continue
        process(f, i)