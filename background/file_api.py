"""
Authenticated file API for Claude read/write access.
Read scope:  docs/
Write scope: docs/staging/ only
Auth:        X-Api-Key header
"""
import html
import json
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
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


def _js_string(value: str) -> str:
    """JSON-encode a string for safe embedding inside a <script> tag."""
    return json.dumps(value).replace("</", "<\\/")


@app.get("/stage-ui", response_class=HTMLResponse)
def stage_ui(
    filename: str = Query(...),
    content: str = Query(...),
    key: str = Query(...),
):
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


class WriteRequest(BaseModel):
    path: str
    content: str


@app.post("/write")
def write_file(
    req: WriteRequest,
    x_api_key: str = Header(..., alias="X-Api-Key"),
):
    _auth(x_api_key)
    target = (STAGING_DIR / req.path).resolve()
    if not str(target).startswith(str(STAGING_DIR)):
        raise HTTPException(status_code=400, detail="Path outside docs/staging/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(req.content, encoding="utf-8")
    return {"written": str(target.relative_to(REPO_ROOT))}
