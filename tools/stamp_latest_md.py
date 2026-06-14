"""Rewrite the "Last updated:" line in docs/status/LATEST.md to the current
UTC time. Called by the pre-commit hook (tools/git-hooks/pre-commit)
whenever LATEST.md is part of a commit, so the timestamp can never be
forgotten, stale-copied, or accidentally moved backwards.
"""

import re
from datetime import UTC, datetime
from pathlib import Path

LATEST_MD = Path("docs/status/LATEST.md")


def stamp() -> None:
    """Rewrite the Last updated line to the current UTC time."""
    text = LATEST_MD.read_text(encoding="utf-8")
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_text, count = re.subn(
        r"^Last updated: .*$", f"Last updated: {now}", text, count=1, flags=re.MULTILINE
    )
    if count == 0:
        raise ValueError(f"No 'Last updated:' line found in {LATEST_MD}")
    LATEST_MD.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    stamp()
