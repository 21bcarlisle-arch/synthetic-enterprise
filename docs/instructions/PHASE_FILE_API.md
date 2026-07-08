# Instruction: Deploy Secure File API with Tailscale Funnel

## Objective
Deploy a lightweight authenticated file API on Skynet that Claude can use to read
phase summaries and write instruction files directly, without manual relay.

Claude can then:
- **Read**: any file under `docs/`
- **Write**: instruction files to `docs/instructions/` only

---

## Steps

### 1. Locate the repo root
```bash
cd ~/synthetic-enterprise  # adjust if different
REPO_ROOT=$(pwd)
```

### 2. Generate an API key and store it
```bash
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
mkdir -p background
cat > background/.env.file-api << EOF
FILE_API_KEY=${API_KEY}
EOF
chmod 600 background/.env.file-api
```

Ensure `.env.file-api` is gitignored:
```bash
grep -q '.env.file-api' .gitignore || echo 'background/.env.file-api' >> .gitignore
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn --break-system-packages
```

### 4. Write the file API
Create `background/file_api.py`:

```python
"""
Authenticated file API for Claude read/write access.
Read scope:  docs/
Write scope: docs/instructions/ only
Auth:        X-Api-Key header
"""
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = (REPO_ROOT / "docs").resolve()
INSTRUCTIONS_DIR = (REPO_ROOT / "docs" / "instructions").resolve()
_API_KEY = os.environ.get("FILE_API_KEY", "")


def _auth(x_api_key: str = Header(..., alias="X-Api-Key")) -> None:
    if not _API_KEY or x_api_key != _API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.get("/health")
def health():
    return {"status": "ok", "repo": str(REPO_ROOT)}


@app.get("/read")
def read_file(
    path: str = Query(..., description="Path relative to docs/"),
    x_api_key: str = Header(..., alias="X-Api-Key"),
):
    _auth(x_api_key)
    target = (DOCS_DIR / path).resolve()
    if not str(target).startswith(str(DOCS_DIR)):
        raise HTTPException(status_code=400, detail="Path outside docs/")
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if not target.is_file():
        raise HTTPException(status_code=400, detail="Not a file")
    return {"path": path, "content": target.read_text(encoding="utf-8")}


@app.get("/list")
def list_files(
    path: str = Query(default="", description="Subdirectory relative to docs/"),
    x_api_key: str = Header(..., alias="X-Api-Key"),
):
    _auth(x_api_key)
    target = (DOCS_DIR / path).resolve() if path else DOCS_DIR
    if not str(target).startswith(str(DOCS_DIR)):
        raise HTTPException(status_code=400, detail="Path outside docs/")
    if not target.exists():
        raise HTTPException(status_code=404, detail="Directory not found")
    files = [str(f.relative_to(DOCS_DIR)) for f in target.rglob("*") if f.is_file()]
    return {"files": sorted(files)}


class WriteRequest(BaseModel):
    path: str
    content: str


@app.post("/write")
def write_file(
    req: WriteRequest,
    x_api_key: str = Header(..., alias="X-Api-Key"),
):
    _auth(x_api_key)
    target = (INSTRUCTIONS_DIR / req.path).resolve()
    if not str(target).startswith(str(INSTRUCTIONS_DIR)):
        raise HTTPException(status_code=400, detail="Path outside docs/instructions/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(req.content, encoding="utf-8")
    return {"written": str(target.relative_to(REPO_ROOT))}
```

### 5. Write tests
Create `tests/background/test_file_api.py`:

```python
import pytest
from fastapi.testclient import TestClient

import os
os.environ["FILE_API_KEY"] = "test-key-abc123"

from background.file_api import app, DOCS_DIR, INSTRUCTIONS_DIR

client = TestClient(app)
HEADERS = {"X-Api-Key": "test-key-abc123"}
BAD_HEADERS = {"X-Api-Key": "wrong"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_read_rejects_bad_key():
    r = client.get("/read?path=calibration/weather-engine.md", headers=BAD_HEADERS)
    assert r.status_code == 403


def test_write_rejects_bad_key():
    r = client.post("/write", json={"path": "test.md", "content": "x"}, headers=BAD_HEADERS)
    assert r.status_code == 403


def test_write_path_traversal_blocked():
    r = client.post(
        "/write",
        json={"path": "../../CLAUDE.md", "content": "pwned"},
        headers=HEADERS,
    )
    assert r.status_code == 400


def test_read_path_traversal_blocked():
    r = client.get("/read?path=../CLAUDE.md", headers=HEADERS)
    assert r.status_code == 400


def test_read_missing_file_returns_404():
    r = client.get("/read?path=does-not-exist.md", headers=HEADERS)
    assert r.status_code == 404


def test_list_returns_files():
    r = client.get("/list", headers=HEADERS)
    assert r.status_code == 200
    assert "files" in r.json()


def test_write_and_read_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("background.file_api.INSTRUCTIONS_DIR", tmp_path)
    monkeypatch.setattr("background.file_api.DOCS_DIR", tmp_path.parent)
    content = "# Test instruction\nDo something."
    r = client.post(
        "/write",
        json={"path": "TEST_PHASE.md", "content": content},
        headers=HEADERS,
    )
    assert r.status_code == 200
```

### 6. Run the harness
```bash
make check
```
Fix any failures before proceeding.

### 7. Launch the API in a tmux session
```bash
tmux new-session -d -s file-api \
  "cd ${REPO_ROOT} && \
   source background/.env.file-api && \
   export FILE_API_KEY && \
   uvicorn background.file_api:app --host 127.0.0.1 --port 8765"
```

Verify it's up:
```bash
curl -s http://127.0.0.1:8765/health
```

### 8. Enable Tailscale Funnel
```bash
tailscale funnel 8765
```

If this fails with a permissions error, try:
```bash
sudo tailscale funnel 8765
```

If Funnel is not enabled on the account, it will print a URL to enable it in the
Tailscale admin console. Pause here, enable it, then retry. Send an NTFY message:
`FILE_API: Funnel needs enabling at https://login.tailscale.com/admin/dns — awaiting action`

Once Funnel is running, capture the public URL:
```bash
FUNNEL_URL=$(tailscale funnel status 2>/dev/null | grep -oP 'https://[^\s]+' | head -1)
echo "Funnel URL: ${FUNNEL_URL}"
```

Verify public access:
```bash
curl -s "${FUNNEL_URL}/health"
```

### 9. Add file-api to start_worker.sh
Append to `background/start_worker.sh` so it launches on worker start:
```bash
# Start file API
if ! tmux has-session -t file-api 2>/dev/null; then
  tmux new-session -d -s file-api \
    "cd ${REPO_ROOT} && source background/.env.file-api && export FILE_API_KEY && \
     uvicorn background.file_api:app --host 127.0.0.1 --port 8765"
  echo "file-api session started"
fi
```

### 10. Update CLAUDE.md
Add a section:

```markdown
## Claude File API

A lightweight file API runs on Skynet, exposed via Tailscale Funnel.

- **Base URL**: <FUNNEL_URL>
- **Read**: GET /read?path=<relative-to-docs/>
- **Write**: POST /write {"path": "<relative-to-docs/instructions/>", "content": "..."}
- **List**: GET /list?path=<optional-subdirectory>
- **Auth**: X-Api-Key header
- **API key**: stored in background/.env.file-api (gitignored); sent to Rich via NTFY on deploy

Claude uses this to read phase summaries and write new instruction files
without manual relay.
```

Replace `<FUNNEL_URL>` with the actual URL captured above.

### 10a. Reliability improvements (2026-06-12)

The original deployment above is still accurate for `/read`, `/list`, `/write`,
and the auth model. Three additions were made on top of it:

**POST-based `/stage-ui`** — the old `/stage-ui` took `filename`/`content` as
query parameters, which hit URL-length limits and required URL-encoding for
large staged instructions. It's now two routes:
- `GET /stage-ui` — returns an HTML form (filename, content, API key fields)
  that POSTs to `/stage-ui`.
- `POST /stage-ui` (`filename`, `content`, `key` as form fields) — renders an
  HTML-escaped preview with a Submit button that calls `POST /write` via JS.

This requires the `python-multipart` package for FastAPI's `Form(...)`:
```bash
pip install --user --break-system-packages python-multipart
```

**`/healthz`** — unauthenticated endpoint for monitoring, returns:
```json
{"uvicorn": "alive", "funnel_active": true|false|null,
 "staging_writable": true|false, "last_file_received": "<ISO timestamp>|null"}
```
`funnel_active` is `null` if the `tailscale` CLI isn't available.

**systemd service instead of tmux** — `background/file-api.service` is a
systemd unit that runs the same uvicorn command as the old tmux session, but
with `Restart=on-failure` so it survives crashes and reboots. The file-api
tmux block was removed from `background/start_worker.sh`.

**Installed (2026-06-12) as a user-level systemd unit** — no root needed after
all: `/run/user/1000/bus` exists even without `XDG_RUNTIME_DIR`/
`DBUS_SESSION_BUS_ADDRESS` set in the shell, so `systemctl --user` works once
those are exported, and `loginctl enable-linger rich` (also doesn't need
sudo) makes the user systemd instance start at boot/persist without an active
login session. Installed via:
```bash
mkdir -p ~/.config/systemd/user
cp ~/synthetic-enterprise/background/file-api.service ~/.config/systemd/user/
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
systemctl --user daemon-reload
systemctl --user enable --now file-api
loginctl enable-linger rich
```
The unit's `[Install]` target is `default.target` (user manager), not
`multi-user.target` (system manager), and it has no `User=` line.

Verify:
```bash
systemctl --user status file-api
curl -s http://127.0.0.1:8765/healthz
```

### 10b. Mobile UI pages (2026-06-12)

Two browser-friendly pages, served directly by the file API (no auth on the
GET — the API key is entered client-side and cached in `localStorage`):

- **`GET /ui/stage`** — write form. Filename + content + API key, POSTs
  straight to `POST /write` (lands in `docs/staging/`). Useful for staging
  instruction files from a phone.
- **`GET /ui/status`** — read page. Fetches `GET /read?path=status/LATEST.md`
  and renders it in a wrapped `<pre>` block. `docs/status/LATEST.md` is a
  short mobile-friendly status snapshot (kept separate from the full
  `STATUS.md` at the repo root).

Both pages set `<meta name="viewport" content="width=device-width,
initial-scale=1">` and use 16px inputs (avoids iOS auto-zoom on focus).

### 11. Commit and push
```bash
git add background/file_api.py tests/background/test_file_api.py \
        background/start_worker.sh CLAUDE.md .gitignore
git commit -m "feat: file API with Tailscale Funnel for Claude read/write access"
git push
```

### 12. Send NTFY
Send two messages to the shared NTFY topic (see `background/ntfy_utils.py`):

**Message 1 — URL:**
```
FILE_API live. URL: <FUNNEL_URL>
Read: GET /read?path=calibration/weather-engine.md
Write: POST /write to docs/instructions/
Health: <FUNNEL_URL>/health
```

**Message 2 — Key (send separately):**
```
FILE_API key: <API_KEY>
Store this securely. Not committed to repo.
```

---

## Acceptance criteria
- [ ] `make check` passes (all tests green including file_api tests)
- [ ] `/health` responds on localhost:8765
- [ ] `/health` responds on public Funnel URL
- [ ] Path traversal attempts return 400
- [ ] `file-api` tmux session running
- [ ] CLAUDE.md updated with Funnel URL
- [ ] Two NTFY messages sent (URL + key separately)
- [ ] Committed and pushed
