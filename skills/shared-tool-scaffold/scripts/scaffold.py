#!/usr/bin/env python3
"""Scaffold a shared-folder team tool from the bundled templates.

Copies assets/ into the destination folder, substitutes placeholders, renames
gitignore -> .gitignore, and makes the start scripts executable.

Example:
    python3 scaffold.py --name "Team Planning Board" --slug team_planning \
        --port 8080 --theme "#2563eb" --subtitle "Shared weekly plan" \
        --dest "/path/to/shared/Team Planning Board"
"""
import argparse
import re
import shutil
import stat
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / 'assets'

# Files copied verbatim (with placeholder substitution). gitignore is renamed.
TEXT_FILES = [
    'server.py', 'index.html', 'requirements.txt',
    'start.command', 'start.sh', 'start.bat',
    'README.md', 'DECISIONS.md', 'favicon.svg',
]
EXECUTABLE = {'start.command', 'start.sh'}


def slugify(name: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return s or 'tool'


def prefix_from_slug(slug: str) -> str:
    # Env-var prefix: the uppercased slug, e.g. team_planning -> TEAM_PLANNING.
    return re.sub(r'[^A-Z0-9]+', '_', slug.upper()).strip('_') or 'APP'


def substitute(text: str, repl: dict) -> str:
    for key, val in repl.items():
        text = text.replace('{{' + key + '}}', val)
    return text


def main() -> int:
    p = argparse.ArgumentParser(description='Scaffold a shared-folder team tool.')
    p.add_argument('--name', required=True, help='Display name / title')
    p.add_argument('--slug', help='Lowercase slug for venv/cache dir (default: from name)')
    p.add_argument('--port', type=int, default=8080)
    p.add_argument('--theme', default='#2563eb', help='Primary color (hex)')
    p.add_argument('--subtitle', default='')
    p.add_argument('--dest', required=True, help='Destination folder')
    p.add_argument('--force', action='store_true', help='Allow writing into a non-empty folder')
    args = p.parse_args()

    slug = args.slug or slugify(args.name)
    prefix = prefix_from_slug(slug)
    dest = Path(args.dest).expanduser()

    if dest.exists() and any(dest.iterdir()) and not args.force:
        print(f'ERROR: destination "{dest}" is not empty. Re-run with --force to proceed.')
        return 1
    dest.mkdir(parents=True, exist_ok=True)

    repl = {
        'PROJECT_NAME': args.name,
        'PROJECT_SLUG': slug,
        'PREFIX': prefix,
        'PORT': str(args.port),
        'THEME_COLOR': args.theme,
        'SUBTITLE': args.subtitle,
        'FAVICON_LETTER': (args.name.strip()[:1] or '•').upper(),
    }

    for fname in TEXT_FILES:
        src = ASSETS / fname
        text = substitute(src.read_text(encoding='utf-8'), repl)
        out = dest / fname
        out.write_text(text, encoding='utf-8')
        if fname in EXECUTABLE:
            out.chmod(out.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # gitignore -> .gitignore (substitution not needed but harmless)
    (dest / '.gitignore').write_text(
        substitute((ASSETS / 'gitignore').read_text(encoding='utf-8'), repl),
        encoding='utf-8')

    print(f'✓ Scaffolded "{args.name}" into: {dest}')
    print(f'  slug={slug}  port={args.port}  env-prefix={prefix}_*')
    print()
    print('Next steps:')
    print(f'  1. Smoke test:  {prefix}_PORT={args.port + 10} '
          f'{prefix}_STATE_FILE=/tmp/{slug}_smoke.yaml python3 "{dest}/server.py"')
    print(f'     Then open http://localhost:{args.port + 10}/health')
    print('  2. Move the folder into your shared SharePoint/OneDrive location.')
    print('  3. Colleagues double-click start.command (Mac) or start.bat (Windows).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
