"""{{PROJECT_NAME}} — local Flask server.

Serves a single-file index.html plus a tiny JSON state API with live multi-user
sync. Designed to run from a shared SharePoint/OneDrive folder on colleagues'
machines. See DECISIONS.md (ADR-001) for the architecture rationale.
"""
import os
import shutil
import tempfile
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import yaml
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).parent

# On-disk state schema version. Bump when serialize() output shape changes and
# add a branch to migrate_state() so old files keep loading.
SCHEMA_VERSION = 1

# ── Config (env-overridable so tests never touch live data) ───────────────────
STATE_FILE = Path(os.environ.get(
    '{{PREFIX}}_STATE_FILE', BASE_DIR / 'state.yaml'))
# Backups live OFF the shared folder (device-local) to avoid sync noise.
BACKUP_DIR = Path(os.environ.get(
    '{{PREFIX}}_BACKUP_DIR', Path.home() / '.cache' / '{{PROJECT_SLUG}}' / 'backups'))
MAX_BACKUPS = 30
PORT = int(os.environ.get('{{PREFIX}}_PORT', {{PORT}}))

# Serialises writes so two simultaneous POSTs can't interleave.
STATE_LOCK = threading.Lock()

app = Flask(__name__)


# ── State I/O ─────────────────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return migrate_state(yaml.safe_load(f) or {})
    return {}


def migrate_state(data):
    """Upgrade an older on-disk state to the current SCHEMA_VERSION in place.

    Keep every branch additive and non-destructive: a colleague on an old build
    must still be able to open a newer state file without losing data.
    """
    if not isinstance(data, dict):
        return {}
    v = data.get('schemaVersion', 0)
    # Example migration scaffold — extend as the model evolves:
    # if v < 2:
    #     for item in data.get('items', []):
    #         item.setdefault('newField', None)
    #     v = 2
    data['schemaVersion'] = max(v, SCHEMA_VERSION)
    return data


def backup_current():
    """Snapshot the existing state before overwriting. Never let a backup
    failure block the real save."""
    if not STATE_FILE.exists():
        return
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        shutil.copy2(STATE_FILE, BACKUP_DIR / f'state_{ts}.yaml')
        for old in sorted(BACKUP_DIR.glob('state_*.yaml'))[:-MAX_BACKUPS]:
            old.unlink()
    except Exception:
        pass


def save_state(data):
    """Atomic write: temp file in the same dir -> fsync -> os.replace. A crash
    mid-write can only leave a discarded temp file; the real file is never seen
    half-written."""
    backup_current()
    fd, tmp = tempfile.mkstemp(dir=str(STATE_FILE.parent), prefix='.state_', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, STATE_FILE)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def state_rev(data):
    return data.get('rev', 0) if isinstance(data, dict) else 0


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(str(BASE_DIR), 'index.html')


@app.route('/favicon.svg')
def favicon():
    return send_from_directory(str(BASE_DIR), 'favicon.svg', mimetype='image/svg+xml')


@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(load_state())


@app.route('/rev')
def get_rev():
    """Cheap endpoint the clients poll to detect other users' saves."""
    return jsonify({'rev': state_rev(load_state())})


@app.route('/state', methods=['POST'])
def post_state():
    data = request.get_json(force=True)
    if data is None:
        return jsonify({'error': 'No JSON body'}), 400
    base = data.pop('baseRev', None)
    with STATE_LOCK:
        cur_rev = state_rev(load_state())
        # Optimistic concurrency: reject rather than overwrite a newer save.
        if base is not None and base != cur_rev:
            return jsonify({'conflict': True, 'state': load_state()}), 409
        data['rev'] = cur_rev + 1
        data['schemaVersion'] = SCHEMA_VERSION
        save_state(data)
        return jsonify({'ok': True, 'rev': data['rev']})


@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'schemaVersion': SCHEMA_VERSION,
        'stateFile': str(STATE_FILE),
        'stateExists': STATE_FILE.exists(),
        'port': PORT,
    })


# ── Add project-specific routes below (Excel export, import, PDF, ...) ─────────
# Keep them stateless where possible. Route all state mutation through the
# /state POST above so the concurrency/backup guarantees stay intact.


# ── Startup ───────────────────────────────────────────────────────────────────
def open_browser():
    import time
    time.sleep(1.2)
    webbrowser.open(f'http://localhost:{PORT}')


if __name__ == '__main__':
    print()
    print('  {{PROJECT_NAME}} — local server')
    print(f'  URL:        http://localhost:{PORT}')
    print(f'  State file: {STATE_FILE.name}')
    print('  Browser opens automatically. Ctrl+C to stop.')
    print()
    threading.Thread(target=open_browser, daemon=True).start()
    try:
        app.run(host='localhost', port=PORT, debug=False, use_reloader=False)
    except OSError as e:
        print(f'\n  ERROR: could not bind port {PORT} ({e}).')
        print(f'  Another instance may be running, or set {{PREFIX}}_PORT to a free port.\n')
