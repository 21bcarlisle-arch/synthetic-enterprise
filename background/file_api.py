"""
Authenticated file API for Claude read/write access.
Read scope:  docs/
Write scope: docs/staging/ only
Auth:        X-Api-Key header
"""
import html
import httpx
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

from fastapi import FastAPI, Form, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = (REPO_ROOT / "docs").resolve()
STAGING_DIR = (REPO_ROOT / "docs" / "staging").resolve()
RESPONSES_DIR = (STAGING_DIR / "responses").resolve()
GATE_TOKENS_DIR = (STAGING_DIR / ".gate_tokens").resolve()

# Load from .env.file-api if FILE_API_KEY not already in environment.
# 2026-07-11, Option 2 floor (director in-console authorization): resolves
# through background/secrets_location.py, new out-of-tree location first,
# old in-tree path as a fallback during the transition.
from background.secrets_location import resolve_secret_file  # noqa: E402
_ENV_FILE = resolve_secret_file(".env.file-api")
if not os.environ.get("FILE_API_KEY") and _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text().splitlines():
        if _line.startswith("FILE_API_KEY="):
            os.environ["FILE_API_KEY"] = _line.split("=", 1)[1].strip()
            break

_API_KEY = os.environ.get("FILE_API_KEY", "")


def _auth(x_api_key: str = Header(..., alias="X-Api-Key")) -> None:
    if not _API_KEY or x_api_key != _API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.get("/health")
def health():
    # Deliberately omits REPO_ROOT (a local filesystem path) — this endpoint
    # is unauthenticated and reachable via Tailscale Funnel.
    return {"status": "ok"}


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


def _js_string(value: str) -> str:
    """JSON-encode a string for safe embedding inside a <script> tag."""
    return json.dumps(value).replace("</", "<\\/")


@app.get("/stage-ui", response_class=HTMLResponse)
def stage_ui_form():
    """Entry form — POSTs filename/content/key as a form body, so there's no
    URL-encoding or URL-length limit on the staged content."""
    return """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Stage a file</title></head>
<body>
  <h1>Stage a file for review</h1>
  <form method="post" action="/stage-ui">
    <p><label>API Key<br><input type="password" name="key" required style="width:100%"></label></p>
    <p><label>Filename<br><input type="text" name="filename" required style="width:100%"></label></p>
    <p><label>Content<br><textarea name="content" rows="20" required style="width:100%"></textarea></label></p>
    <button type="submit">Preview</button>
  </form>
</body>
</html>"""


@app.post("/stage-ui", response_class=HTMLResponse)
def stage_ui_preview(
    filename: str = Form(...),
    content: str = Form(...),
    key: str = Form(...),
):
    """Preview the submitted file before writing it to docs/staging/ — the
    actual write happens client-side via POST /write when "Submit" is
    clicked, same as before, just no longer round-tripped through the URL."""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Staging Review</title></head>
<body>
  <h1>Review staged file</h1>
  <p><strong>Filename:</strong> {html.escape(filename)}</p>
  <pre>{html.escape(content)}</pre>
  <button id="submit">Submit</button>
  <p id="result"></p>
  <script>
    document.getElementById("submit").addEventListener("click", async () => {{
      const res = await fetch("/write", {{
        method: "POST",
        headers: {{
          "Content-Type": "application/json",
          "X-Api-Key": {_js_string(key)}
        }},
        body: JSON.stringify({{path: {_js_string(filename)}, content: {_js_string(content)}}})
      }});
      document.getElementById("result").textContent = res.ok
        ? "Submitted: " + JSON.stringify(await res.json())
        : "Error: " + res.status;
    }});
  </script>
</body>
</html>"""


_MOBILE_STYLE = """
  <style>
    body { font-family: system-ui, sans-serif; max-width: 700px; margin: 0 auto; padding: 1em; }
    input, textarea, button { width: 100%; font-size: 16px; padding: 0.5em; margin: 0.3em 0; box-sizing: border-box; }
    pre { white-space: pre-wrap; word-break: break-word; background: #f4f4f4; padding: 1em; border-radius: 4px; }
  </style>"""


@app.get("/ui/stage", response_class=HTMLResponse)
def ui_stage():
    """Mobile-friendly form that writes a file straight to docs/staging/ via
    POST /write. The API key is cached in localStorage so it only needs to
    be entered once per device."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Stage a file</title>
  {_MOBILE_STYLE}
</head>
<body>
  <h1>Stage a file</h1>
  <label>API Key<br><input type="password" id="key"></label>
  <label>Filename<br><input type="text" id="filename" placeholder="TASK_FOO.md" required></label>
  <label>Content<br><textarea id="content" rows="14" required></textarea></label>
  <button id="submit">Submit</button>
  <p id="result"></p>
  <script>
    const keyEl = document.getElementById("key");
    keyEl.value = localStorage.getItem("fileApiKey") || "";
    document.getElementById("submit").addEventListener("click", async () => {{
      const key = keyEl.value;
      localStorage.setItem("fileApiKey", key);
      const filename = document.getElementById("filename").value.trim();
      const content = document.getElementById("content").value;
      if (!filename) {{
        document.getElementById("result").textContent = "Error: filename is required";
        return;
      }}
      const res = await fetch("/write", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json", "X-Api-Key": key }},
        body: JSON.stringify({{ path: filename, content: content }})
      }});
      document.getElementById("result").textContent = res.ok
        ? "Staged: " + JSON.stringify(await res.json())
        : "Error: " + res.status;
    }});
  </script>
</body>
</html>"""


@app.get("/ui/status", response_class=HTMLResponse)
def ui_status():
    """Mobile-friendly read page — fetches and displays docs/status/LATEST.md
    via GET /read. The API key is cached in localStorage so it only needs to
    be entered once per device."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Latest Status</title>
  {_MOBILE_STYLE}
</head>
<body>
  <h1>Latest Status</h1>
  <label>API Key<br><input type="password" id="key"></label>
  <button id="load">Load</button>
  <pre id="content">(not loaded)</pre>
  <script>
    const keyEl = document.getElementById("key");
    keyEl.value = localStorage.getItem("fileApiKey") || "";
    async function load() {{
      const key = keyEl.value;
      localStorage.setItem("fileApiKey", key);
      const res = await fetch("/read?path=status/LATEST.md", {{
        headers: {{ "X-Api-Key": key }}
      }});
      document.getElementById("content").textContent = res.ok
        ? (await res.json()).content
        : "Error: " + res.status;
    }}
    document.getElementById("load").addEventListener("click", load);
    if (keyEl.value) load();
  </script>
</body>
</html>"""


class WriteRequest(BaseModel):
    path: str
    content: str


@app.post("/write")
def write_file(
    req: WriteRequest,
    x_api_key: str = Header(..., alias="X-Api-Key"),
):
    _auth(x_api_key)
    if not req.path.strip():
        raise HTTPException(status_code=400, detail="Path must not be empty")
    target = (STAGING_DIR / req.path).resolve()
    if not str(target).startswith(str(STAGING_DIR)) or target == STAGING_DIR:
        raise HTTPException(status_code=400, detail="Path outside docs/staging/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(req.content, encoding="utf-8")
    return {"written": str(target.relative_to(REPO_ROOT))}


def generate_gate_token(gate: str) -> str:
    """Create and store a single-use response token for `gate`.

    Called by session_watchdog when it sends a REVIEW_GATE notification, so
    the notification's reply action can authenticate to POST /respond
    without embedding FILE_API_KEY (which would transit ntfy.sh's servers).
    """
    token = secrets.token_urlsafe(16)
    GATE_TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    (GATE_TOKENS_DIR / f"{gate}.token").write_text(token, encoding="utf-8")
    return token


class RespondRequest(BaseModel):
    gate: str
    decision: str
    token: str | None = None


@app.post("/respond")
def respond(
    req: RespondRequest,
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
):
    """Record Rich's decision on a gate, for the watchdog autoloop to pick
    up on its next polling cycle. Authenticates via either a single-use
    gate token (from generate_gate_token, consumed on use) or the full
    FILE_API_KEY."""
    if not req.gate.strip() or "/" in req.gate or "\\" in req.gate or ".." in req.gate:
        raise HTTPException(status_code=400, detail="Invalid gate id")

    token_path = GATE_TOKENS_DIR / f"{req.gate}.token"
    authorized = bool(_API_KEY) and x_api_key == _API_KEY
    if not authorized and req.token and token_path.is_file():
        authorized = token_path.read_text(encoding="utf-8") == req.token

    if not authorized:
        raise HTTPException(status_code=403, detail="Forbidden")

    if token_path.is_file():
        token_path.unlink()

    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    response_path = RESPONSES_DIR / f"{req.gate}.json"
    response_path.write_text(
        json.dumps({
            "gate": req.gate,
            "decision": req.decision,
            "received_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }),
        encoding="utf-8",
    )
    return {"recorded": str(response_path.relative_to(REPO_ROOT))}


def _funnel_active() -> bool | None:
    """True/False if `tailscale funnel status` could be checked, None if the
    tailscale CLI isn't available or the check failed."""
    try:
        result = subprocess.run(
            ["tailscale", "funnel", "status"],
            capture_output=True, text=True, timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return "no serve config" not in result.stdout.lower()


def _staging_writable() -> bool:
    probe = STAGING_DIR / ".healthz_probe"
    try:
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        probe.write_text(str(time.time()))
        probe.unlink()
        return True
    except OSError:
        return False


def _last_file_received() -> str | None:
    """ISO timestamp of the most recently modified file in docs/staging/,
    or None if the directory is empty."""
    if not STAGING_DIR.is_dir():
        return None
    mtimes = [f.stat().st_mtime for f in STAGING_DIR.iterdir() if f.is_file()]
    if not mtimes:
        return None
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(max(mtimes)))


@app.get("/healthz")
def healthz():
    return {
        "uvicorn": "alive",
        "funnel_active": _funnel_active(),
        "staging_writable": _staging_writable(),
        "last_file_received": _last_file_received(),
    }


class QueryRequest(BaseModel):
    question: str
    queryContext: str = ""


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3:14b"
QUERY_SYSTEM = (
    "You are a data analyst for a UK energy supply business simulation (2016-2025). "
    "Answer questions concisely and factually based only on the data provided. "
    "If the data does not contain the information needed, say so. "
    "Keep answers under 200 words. Do not use markdown headers."
)


@app.post("/query")
def query_sim(req: QueryRequest):
    """Local NL query via Ollama/Qwen3. No auth — only reachable on Tailscale."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Missing question")

    system = QUERY_SYSTEM
    if req.queryContext:
        system += "\n\nSimulation data:\n" + req.queryContext

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": "/no_think " + req.question.strip()},
        ],
        "stream": False,
    }

    try:
        r = httpx.post(OLLAMA_URL, json=payload, timeout=90)
        r.raise_for_status()
        answer = r.json().get("message", {}).get("content", "").strip()
        if not answer:
            raise ValueError("Empty response from Ollama")
        return {"answer": answer}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama not reachable — is it running?")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

