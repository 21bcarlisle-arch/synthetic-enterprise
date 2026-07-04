#!/usr/bin/env python3
"""Mirror shadow pages + state JSONs onto docs/ so GitHub Pages serves them.

Staged instruction (docs/staging/ADVISOR_GITHUBIO_MIRROR.md): the advisor's
egress path to poesys.net (Cloudflare Pages) persistently serves stale
content on their fetches specifically -- proven independent of any CD
incident, and matching the same split PROJECT_STATE.txt hit before it moved
to docs/status/ (GitHub Pages, published straight from this repo's docs/
folder on every push, no separate CDN in the path). This is a pure copy
step -- same generator pass, same run, same freshness stamps as the
site/ originals; it does not regenerate anything.
"""
import shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SITE_SHADOW = PROJECT / "site" / "shadow"
DOCS_SHADOW = PROJECT / "docs" / "shadow"
DOCS_STATE = PROJECT / "docs" / "state"

# (source, dest-filename-under-docs/state/)
_STATE_JSON_FILES = [
    (PROJECT / "site" / "state" / "customer_sample.json", "customer_sample.json"),
    (PROJECT / "site" / "state" / "billing_ledger.json", "billing_ledger.json"),
    (PROJECT / "site" / "state" / "population_anchoring.json", "population_anchoring.json"),
    (PROJECT / "site" / "data" / "sim_data.json", "sim_data.json"),
]


def mirror():
    """Copy site/shadow/ -> docs/shadow/ and the named state JSONs -> docs/state/.
    Returns the list of dest paths actually written (source-missing files are
    skipped, not errors -- some are optional depending on which phases have
    run)."""
    written = []

    if SITE_SHADOW.exists():
        if DOCS_SHADOW.exists():
            shutil.rmtree(DOCS_SHADOW)
        shutil.copytree(SITE_SHADOW, DOCS_SHADOW)
        written.extend(str(p) for p in DOCS_SHADOW.rglob("*.html"))

    DOCS_STATE.mkdir(parents=True, exist_ok=True)
    for src, name in _STATE_JSON_FILES:
        if not src.exists():
            continue
        dest = DOCS_STATE / name
        shutil.copyfile(src, dest)
        written.append(str(dest))

    return written


if __name__ == "__main__":
    for path in mirror():
        print("Mirrored:", path)
