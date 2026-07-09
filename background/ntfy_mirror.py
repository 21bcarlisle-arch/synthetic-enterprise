"""NTFY message mirror -- ADVISOR_VISIBILITY.md.

The advisor's only eyes on this project are the GitHub repo (Contents API)
-- it cannot see this terminal, any live NTFY traffic, or anything not
committed and pushed. This mirrors every outbound NTFY and inbound
from_rich message into a version-controlled log so the advisor can review
the day's traffic via the repo within ~10 minutes of send/receipt, without
Rich manually copy-pasting anything into the advisor chat by hand (his
explicit ask, and something he "hates").

Secret-scrubbed: this file is committed to a PUBLIC repo. The actual NTFY
topic value and anything that looks like an HMAC signature or content hash
(a long hex run) are stripped before writing, never the raw value.

Batched commits are fine (no per-message commit spam) -- this file just
gets written to; it rides along on whatever commit next touches
docs/observability/ (the routine sim-run/auto-process pipeline already
commits that directory regularly), matching the doc's own "piggyback on
existing commit moments" instruction. Rotation caps the file at
MAX_MIRROR_ENTRIES so it never bloats the repo.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
MIRROR_FILE = PROJECT_DIR / "docs" / "observability" / "ntfy-mirror.md"

_HEADER = (
    "# NTFY Message Mirror\n\n"
    "Outbound NTFYs and inbound from_rich messages, secret-scrubbed "
    "(topic/signatures never appear). See docs/staging/done/ADVISOR_VISIBILITY.md.\n"
    "Rotates at the most recent entries -- older history lives in git log for this file.\n\n"
)

# A bare 32+ hex-char run (HMAC digests, MD5/SHA content hashes) -- stripped
# unconditionally, not just when a known topic/key value happens to match.
_HEX_DIGEST_RE = re.compile(r"\b[0-9a-fA-F]{32,}\b")

MAX_MIRROR_ENTRIES = 2000


def scrub_secrets(text: str, topic: str | None = None) -> str:
    """Strip the actual NTFY topic value (if provided) and any long hex
    digest from `text` before it's ever written to a version-controlled
    file."""
    scrubbed = text
    if topic:
        scrubbed = scrubbed.replace(topic, "[topic-scrubbed]")
    scrubbed = _HEX_DIGEST_RE.sub("[hex-scrubbed]", scrubbed)
    return scrubbed


def _split_header_and_entries(content: str) -> list[str]:
    if not content.startswith("# NTFY Message Mirror"):
        return []
    parts = content.split("\n\n", 2)
    body = parts[2] if len(parts) > 2 else ""
    return [line for line in body.splitlines() if line.strip()]


def append_mirror_entry(direction: str, message: str, topic: str | None = None) -> None:
    """direction: 'out' (we sent it) or 'in' (Rich sent it). Appends one
    scrubbed, timestamped line and rotates down to MAX_MIRROR_ENTRIES
    (oldest entries dropped first) if the file has grown past that.

    Structural test-isolation guard (same pattern as tmux_relay.py, 2026-07-08
    tmux-leak incident): PYTEST_CURRENT_TEST is set for the duration of every
    test pytest runs -- if set, this is a silent no-op. Found live (2026-07-09)
    that several existing tests monkeypatch `subprocess.run` itself (a single
    shared stdlib module object), which also patches ntfy_utils.send_ntfy's own
    call even though the test never mentions ntfy_mirror at all -- the real
    send_ntfy() body, mirror call included, still ran and wrote test fixture
    strings into the real, version-controlled mirror file. Rather than relying
    on every test remembering to isolate MIRROR_FILE, the guard lives here
    once, so no test -- existing or future -- can pollute it even if it
    forgets."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    scrubbed = scrub_secrets(message, topic=topic).replace("\n", " ")
    entry = f"- [{ts}] [{direction.upper()}] {scrubbed}"

    existing = MIRROR_FILE.read_text(encoding="utf-8") if MIRROR_FILE.is_file() else ""
    entries = _split_header_and_entries(existing)
    entries.append(entry)
    entries = entries[-MAX_MIRROR_ENTRIES:]

    MIRROR_FILE.parent.mkdir(parents=True, exist_ok=True)
    MIRROR_FILE.write_text(_HEADER + "\n".join(entries) + "\n", encoding="utf-8")
