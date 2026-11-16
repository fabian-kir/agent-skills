# Architecture reference

Read this when modifying the sync or persistence logic, or when a user asks *why*
the scaffold is built the way it is. Each guarantee below exists to prevent a
specific failure that shared-folder tools hit in practice; changing the mechanism
without understanding the invariant reintroduces the bug.

## 1. Device-local virtualenv

**Invariant:** nothing under the shared folder is machine-specific.

A virtualenv contains absolute paths and compiled binaries. If it sits in the
OneDrive/SharePoint folder, it syncs to every colleague and corrupts — different
OS, different Python, path clashes, sync conflicts on thousands of tiny files. So
the start scripts create the venv at `~/.cache/<slug>/venv` (Mac/Linux) or
`%LOCALAPPDATA%\<slug>\venv` (Windows). The shared folder holds only source and the
state file.

## 2. Atomic writes

**Invariant:** the state file is never observed half-written.

`save_state()` writes to a temp file **in the same directory**, flushes, `fsync`s,
then `os.replace()`s it over the target. `os.replace` is atomic on the same
filesystem, so a reader (or a crash) sees either the complete old file or the
complete new one — never a truncated mix. The temp file must be in the same dir so
the replace stays on one filesystem.

## 3. Rotating device-local backups

**Invariant:** any save can be rolled back, and backups never pollute sync.

Before each write, the current state is copied to `<backup_dir>/state_<ts>.yaml`.
The backup dir defaults **off** the shared folder (device-local) so snapshots don't
sync-storm across the team. The newest `MAX_BACKUPS` (30) are kept. A backup
failure is swallowed — it must never block the actual save.

## 4. Optimistic concurrency (rev + 409)

**Invariant:** a save never silently overwrites work saved by someone else.

The server stores a monotonic integer `rev`. On save, the client sends the
`baseRev` it started editing from. Under a lock, the server compares `baseRev` to
the current `rev`:
- equal → accept, increment `rev`, persist.
- different → someone saved in between → return `409` with the current server
  state. The client shows a banner: **Load theirs** (discard local, adopt server)
  or **Keep mine** (adopt the server's `rev`, then re-save, which now succeeds).

The `STATE_LOCK` serialises concurrent POSTs so the read-compare-write is not
racy.

## 5. Idle-adopt polling

**Invariant:** a colleague mid-edit is never yanked out from under.

Every client polls `/rev` (cheap) every 3s. If the server `rev` moved past the
client's:
- if `hasLocalEdit()` (a debounced save is queued, an editor/popover is open, or an
  input is focused) → just flag "new changes available" and wait.
- else → fetch `/state` and adopt it, re-rendering.

`/rev` is separate from `/state` precisely so the common "nothing changed" poll is
tiny.

## 6. Single-file frontend, served fresh

**Invariant:** front-end iteration needs no restart.

The `/` route `send_from_directory`s `index.html` on every request, so editing the
HTML/JS and refreshing the browser is enough. Only `server.py` changes need a
restart. This is why the whole app is one file with no build step — it keeps the
edit loop instant and removes Node/toolchain requirements on colleagues' machines.

## 7. Schema versioning

**Invariant:** colleagues on mixed builds don't lose data.

On-disk state carries `schemaVersion`. `load_state()` runs `migrate_state()`, which
upgrades older shapes **additively** (add missing fields with defaults; never drop
data). Bump `SCHEMA_VERSION` and add a branch whenever `serialize()`'s shape
changes. Because migrations are additive, an older client opening a newer file
still works.

## The three developer anchors

The sync client is wired to exactly three functions in `index.html`, so app
developers almost never touch networking:

- `serialize()` → the object persisted & synced (real data only; keep view-only
  prefs out so they don't sync between machines).
- `hydrate(state)` → apply a loaded/remote state onto the app.
- `renderApp()` → build the UI from state.

`autoSave()` (debounced) is called after any mutating change; `apiSave()`,
`pollRev()`, `applyRemote()`, and the conflict banner all operate through those
three anchors.
