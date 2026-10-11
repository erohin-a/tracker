"""
Добавляет новую часть BCE (part_NN.md) в оба _sidebar.md.
Идемпотентно: повторный запуск не создаёт дубликатов.

Запуск:
    python add_bce_part.py 9
"""
import sys
from pathlib import Path

DOCS = Path(r'D:\tracker\docs')
BCE  = DOCS / 'BCE'


def get_title(md_path: Path) -> str:
    """Читает первый заголовок '# ...' из файла part_NN.md."""
    with md_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
    return md_path.stem


def insert_after(path: Path, anchor: str, new_line: str) -> str:
    """
    Вставляет new_line после первой строки, содержащей anchor.
    Возвращает: 'added' | 'exists' | 'anchor_not_found'.
    """
    text = path.read_text(encoding='utf-8')

    if new_line.strip() in text:
        return 'exists'

    lines = text.split('\n')
    for i, line in enumerate(lines):
        if anchor in line:
            indent = line[:len(line) - len(line.lstrip())]
            lines.insert(i + 1, indent + new_line.strip())
            path.write_text('\n'.join(lines), encoding='utf-8')
            return 'added'

    return 'anchor_not_found'


def main() -> None:
    if len(sys.argv) < 2:
        print('Использование: python add_bce_part.py <номер>')
        print('Пример:        python add_bce_part.py 9')
        sys.exit(1)

    n = int(sys.argv[1])
    part_file = BCE / f'part_{n:02d}.md'

    if not part_file.exists():
        print(f'[!] Файл не найден: {part_file}')
        sys.exit(1)

    title  = get_title(part_file)
    prev_n = n - 1
    part_short = f'Часть {n}'

    print(f'Файл:      {part_file.name}')
    print(f'Заголовок: {title}')
    print()

    # 1) Корневой _sidebar.md  — короткая подпись "Часть N"
    root_sidebar = DOCS / '_sidebar.md'
    anchor_root  = f'[Часть {prev_n}]'
    line_root    = f'- [{part_short}](BCE/part_{n:02d}.md)'
    res = insert_after(root_sidebar, anchor_root, line_root)
    print(f'[корневой _sidebar.md]  {res}')

    # 2) BCE/_sidebar.md — полный заголовок из файла
    bce_sidebar = BCE / '_sidebar.md'
    anchor_bce  = f'[Часть {prev_n}'
    line_bce    = f'- [{title}](BCE/part_{n:02d}.md)'
    res = insert_after(bce_sidebar, anchor_bce, line_bce)
    print(f'[BCE/_sidebar.md]       {res}')

    print()
    print('Проверь:')
    print(f'  Get-Content {root_sidebar} -Tail 14 -Encoding UTF8')
    print(f'  Get-Content {bce_sidebar} -Encoding UTF8')
    print()
    print('Дальше:')
    print('  cd D:\\tracker\\docs')
    print(f'  git add .')
    print(f'  git commit -m "BCE: добавлена часть {n}"')
    print('  git push')


if __name__ == '__main__':
    main()