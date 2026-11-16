# {{PROJECT_NAME}}

{{SUBTITLE}}

A small browser-based team tool. It runs locally on each colleague's machine but
lives in a shared SharePoint/OneDrive folder, so everyone edits the same data and
sees each other's changes within a few seconds.

## Run it (colleagues)

1. Make sure the folder is fully downloaded (not "online-only" in OneDrive).
2. Double-click:
   - **Mac:** `start.command` — first time, right-click → **Open** to clear the
     macOS security prompt.
   - **Windows:** `start.bat`
3. The launcher finds Python 3, sets up a local environment the first time, and
   opens your browser at <http://localhost:{{PORT}}> automatically.

If Python 3 isn't installed, the launcher shows the download link and stops.
Install from <https://www.python.org/downloads/> (on Windows tick **Add Python to
PATH**), then run it again.

## How saving & sync work

- Changes save automatically a moment after you make them; there's also a **Save**
  button.
- If a colleague saved while you were editing, you'll see a banner letting you
  keep your version or load theirs — no silent overwrites.
- Every save snapshots the previous state to a local backup folder on your own
  machine (`~/.cache/{{PROJECT_SLUG}}/backups` on Mac/Linux,
  `%USERPROFILE%\.cache\{{PROJECT_SLUG}}\backups` on Windows), keeping the last 30.

## For developers

- **Frontend:** everything is in `index.html` (single file, no build step). Edit
  `serialize()`, `hydrate()` and `renderApp()`. HTML/JS edits take effect on a
  simple browser refresh — no server restart.
- **Backend:** `server.py`. Restart only after changing this file. Add
  project-specific routes in the marked section.
- **Safe testing:** never test against the live state file. Override paths/port:
  ```bash
  {{PREFIX}}_PORT=8090 {{PREFIX}}_STATE_FILE=/tmp/test_state.yaml python server.py
  ```
- Architecture decisions are logged in `DECISIONS.md`.
