#!/usr/bin/env python3
"""Mirror the named state JSONs onto docs/ so GitHub Pages serves them.

Staged instruction (docs/staging/ADVISOR_GITHUBIO_MIRROR.md): the advisor's
egress path to poesys.net (Cloudflare Pages) persistently serves stale
content on their fetches specifically -- proven independent of any CD
incident, and matching the same split PROJECT_STATE.txt hit before it moved
to docs/status/ (GitHub Pages, published straight from this repo's docs/
folder on every push, no separate CDN in the path). This is a pure copy
step -- same generator pass, same run, same freshness stamps as the
site/ originals; it does not regenerate anything.

THE SHADOW HALF IS GONE, 2026-09-20 (seat, docs/staging/SEAT_FINDING_THE_PAGES_ROOT_
SERVES_A_RETIRED_MIRROR_AND_PATHS_IGNORE_IS_NOT_A_PUBLISH_FILTER_2026-09-20.md). This
module used to copy `site/shadow/` -> `docs/shadow/` as well. The director's 2026-08-20
ruling (03dd8c49e) deleted `site/shadow/` outright -- "I don't want hidden pages" -- which
left this copy a no-op and left `docs/shadow/` standing, frozen, and still served by the
Pages workflow for a month with a full internal P&L on it.

The copy is REMOVED rather than left inert, and that distinction is the point: a no-op
copy step is a loaded gun. It fires the moment anything recreates `site/shadow/`, and it
fires straight onto the public root, silently, on the next publish cycle. Deleting
`docs/shadow/` without deleting this would have fixed the instance and left the mechanism.
"""
import shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DOCS_STATE = PROJECT / "docs" / "state"

# (source, dest-filename-under-docs/state/)
_STATE_JSON_FILES = [
    (PROJECT / "site" / "state" / "customer_sample.json", "customer_sample.json"),
    (PROJECT / "site" / "state" / "billing_ledger.json", "billing_ledger.json"),
    (PROJECT / "site" / "state" / "population_anchoring.json", "population_anchoring.json"),
    (PROJECT / "site" / "data" / "sim_data.json", "sim_data.json"),
]


def mirror():
    """Copy the named state JSONs -> docs/state/.

    Returns the list of dest paths actually written (source-missing files are
    skipped, not errors -- some are optional depending on which phases have
    run)."""
    written = []

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
