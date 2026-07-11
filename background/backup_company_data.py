"""Back up company/data/*.db to the PRIVATE synthetic-enterprise-ops repo --
closes the "unrecoverable canonical data" gap PRODUCTION_READINESS_EVIDENCE_
PASS.md's Part A found: these SQLite files (the company's own operational
financial/customer state -- invoices, registry, direct debit, service log)
are correctly gitignored from the PUBLIC repo but had no off-machine copy
at all, matching the immediate-action carve-out criteria
(docs/staging/done/PRODUCTION_READINESS_BASELINE.md) even though the
finding wasn't imminent-danger tier.

Not a general-purpose backup system -- just these 4 known files, copied
verbatim (binary-safe) into the ops repo's own backups/ directory, committed
and pushed via the same background/ops_repo.py helpers used elsewhere this
session (director_input_log.py, the relocated ntfy_mirror.py). Safe to run
repeatedly: a byte-identical DB produces "nothing to commit" (ops_repo.py's
commit_and_push() already handles that cleanly), so wiring this into a
periodic cycle later is low-risk.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from background.ops_repo import OPS_REPO_DIR, commit_and_push, ops_tree_lock

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_DIR / "company" / "data"
BACKUP_DIR = OPS_REPO_DIR / "backups" / "company_data"

DB_FILES = ["invoices.db", "registry.db", "direct_debit.db", "service_log.db"]


def backup_once() -> list[str]:
    """Copy each of DB_FILES from company/data/ to the ops repo's backups/
    directory, commit, and push. Returns the list of files actually backed
    up (skips any that don't exist locally rather than failing)."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backed_up = []
    with ops_tree_lock():
        for name in DB_FILES:
            src = SOURCE_DIR / name
            if not src.is_file():
                continue
            shutil.copy2(src, BACKUP_DIR / name)
            backed_up.append(name)
        if backed_up:
            relpaths = [f"backups/company_data/{name}" for name in backed_up]
            commit_and_push(relpaths, "company/data backup")
    return backed_up


if __name__ == "__main__":
    done = backup_once()
    print(f"Backed up: {done}" if done else "Nothing to back up (no source files found)")
