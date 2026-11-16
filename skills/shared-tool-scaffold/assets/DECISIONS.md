# {{PROJECT_NAME}} — Decisions Log

A running log of architectural decisions (ADRs). Add a new entry whenever you make
a choice a future maintainer would otherwise have to reverse-engineer.

---

### ADR-001: Shared-folder tool base architecture
**Decision:** Python/Flask backend serving a single-file `index.html`, run locally
by each colleague from a shared SharePoint/OneDrive folder, with live multi-user
sync over a tiny JSON state API.

**Rationale — the four failure modes this prevents:**
1. **venv in a synced folder corrupts across machines** → the virtualenv is
   created **device-local** (`~/.cache/{{PROJECT_SLUG}}/venv` /
   `%LOCALAPPDATA%\{{PROJECT_SLUG}}\venv`) by the start scripts; only source + state
   live in the shared folder.
2. **Two people saving at once lose work** → the server owns a monotonic `rev`;
   clients send `baseRev` and get a `409` + conflict banner instead of a silent
   overwrite.
3. **A crash mid-save corrupts state** → writes go temp-file → `fsync` →
   `os.replace` (atomic); the prior state is snapshotted to a rotating,
   device-local backup dir first.
4. **Testing against live data is destructive** → `{{PREFIX}}_STATE_FILE`,
   `{{PREFIX}}_BACKUP_DIR`, `{{PREFIX}}_PORT` are env-overridable.

**Consequences:**
- The server re-reads `index.html` from disk per request, so **HTML/JS edits need
  no restart** — only `server.py` changes do.
- Idle clients adopt remote changes automatically (poll `/rev` every 3s); a client
  mid-edit is never overwritten (`hasLocalEdit()` guard).
- On-disk state carries a `schemaVersion`; `migrate_state()` upgrades old files
  additively so colleagues on mixed builds don't lose data.
