#!/usr/bin/env python3
"""UserPromptSubmit hook: log every user prompt to the director input log
(background/director_input_log.py -- DIRECTOR_INPUT_LOG.md, P2, Lane H).

Reads the prompt-submit JSON Claude Code passes on stdin (field: "prompt").
Observe-only: never blocks or modifies the prompt (always exits 0), so a
failure in this hook can never interrupt real work -- provenance logging is
strictly best-effort, matching the doc's DoD ("Hook live") without adding a
new way for a session to get stuck.

Scope limit (see director_input_log.py's own module docstring): this fires
for genuine fresh-turn prompts. Claude Code's UserPromptSubmit payload has
no field distinguishing that from a message queued mid-tool-execution and
delivered later -- both classify as channel "window" here, not a silent
gap, an honestly-scoped one.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_DIR / "background" / ".env.ntfy"


def _load_env_file() -> None:
    """A Claude Code hook subprocess does NOT inherit background/.env.ntfy
    the way a daemon launched via start_worker.sh does (that script
    exports it into the shell before spawning; this hook has no such
    shell). Confirmed live (2026-07-11): this session's own process env
    lacks SE_NTFY_TOPIC/SE_WAKE_HMAC_KEY, which would otherwise make
    every single classify_and_log_message() call silently no-op forever
    (ntfy_utils.py raises at import time if SE_NTFY_TOPIC is unset --
    caught by this hook's own best-effort try/except below, so the
    failure would never surface). Load it directly here instead of
    assuming inheritance."""
    if not ENV_FILE.is_file():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    prompt = payload.get("prompt")
    if not prompt:
        return 0

    try:
        _load_env_file()
        sys.path.insert(0, str(PROJECT_DIR))
        # Imported lazily so a broken/uninstalled ops-repo checkout can
        # never turn a logging failure into a blocked prompt.
        from background.director_input_log import classify_and_log_message
        classify_and_log_message(prompt)
    except Exception:
        pass  # best-effort: never block or fail the user's actual prompt

    return 0


if __name__ == "__main__":
    sys.exit(main())
