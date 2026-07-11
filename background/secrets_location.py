"""Where secret env files actually live -- Option 2 floor (2026-07-11,
director in-console authorization, absorbing docs/design/
HARNESS_BEST_PRACTICE_ASSESSMENT.md's own recommendation rather than
re-deriving it): "move background/.env.ntfy and any other secret file out
of the repo working tree into a path never read by tool calls that touch
company/saas/site" -- reduces accidental secret exposure in commits/diffs
without requiring full container sandboxing.

New primary location: ~/.config/synthetic-enterprise/ (outside the git
working tree entirely, 700-permissioned directory, 600-permissioned files).
The OLD in-tree background/.env.* path is kept as a FALLBACK during the
transition, not removed outright -- CLAUDE.md's own "concurrent writers on
this one working tree" reality means daemon processes launched before this
change picked up will still have old code in memory until their own next
restart (R2); a hard cutover with no fallback risks a simultaneous outage
across the 6 daemons that share this exact dependency (the SPOF the
PRODUCTION_READINESS_EVIDENCE_PASS.md audit already named). Once every
consumer has been confirmed running the new-location-aware code for a
real cycle, the in-tree copies can be deleted for a true hard cutover --
tracked as a follow-up, not assumed done by this commit alone.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

NEW_SECRETS_DIR = Path.home() / ".config" / "synthetic-enterprise"
OLD_SECRETS_DIR = PROJECT_DIR / "background"


def resolve_secret_file(filename: str) -> Path:
    """Return the new (out-of-tree) path if it exists there, else fall back
    to the old in-tree path. `filename` is e.g. ".env.ntfy" or
    ".env.file-api"."""
    new_path = NEW_SECRETS_DIR / filename
    if new_path.is_file():
        return new_path
    return OLD_SECRETS_DIR / filename
