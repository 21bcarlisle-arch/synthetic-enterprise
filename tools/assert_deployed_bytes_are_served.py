#!/usr/bin/env python3
"""After a deploy, assert a reader actually gets the bytes we just published.

REUSE: tools/assert_deployed_bytes_are_served.py
CLASS: CUSTOM
INDEX: searched "deploy", "verify", "live", "freshness", "publish". The nearest existing
       module is `site/live_pixel_verify.py`, which is a different question: it asks
       whether a door RENDERS (headless browser, feed wiring, rendered-value tokens) and
       runs against whatever is live whenever it is invoked. This asks the narrower
       deploy-time question -- are the exact bytes of THIS push what the edge is handing
       out -- and it needs no browser, so it can run inside the deploy job.

WHY THIS EXISTS
---------------
It replaces the zone cache purge that stood here from 2026-07-11 to 2026-08-20. That step
was written to stop a stale `/data/dashboard.json` being served after a successful deploy.
Three things were then measured on 2026-08-20:

  * It had never once worked. `secrets.CLOUDFLARE_ZONE_ID` is empty, so every call went to
    `/zones//purge_cache` and came back code 7003 -- and the step printed `Purge FAILED`
    and exited 0, so the publish path reported success while purging nothing for its whole
    life. That is the FAIL-OPEN pattern R15 names.
  * Purging would not have fixed the incident it was blamed for anyway. Run by hand with
    working credentials, `purge_everything` returned `success: true` twice while eight
    deleted pages went on being served 200 with `age` climbing through both purges. Those
    ghosts live in Pages' own asset cache for the custom domain; a zone purge does not
    reach it, and eight deployments in one day did not evict it.
  * Its original job now belongs to `site/_headers`, which sets `no-cache,
    must-revalidate` on `/`, `/*.html`, `/*/`, `/data/*.json`, `/state/*` and `/shadow/*`.

So the purge went, and this took its place: not an action that hopes, but a control that
can FAIL for the right reason.

WHAT IT CHECKS, AND WHY IN THIS DIRECTION
-----------------------------------------
For every file this push changed under `site/`, fetch the URL a reader would use and
compare sha256 against the file in the checkout.

The direction matters and is not a style choice. Through a cached copy:

  * "the NEW bytes are present" is SOUND -- a copy stored in the past cannot contain
    something that did not exist when it was stored;
  * "the old thing is ABSENT" is NOT -- absence and staleness are indistinguishable.

So a modified or added file is asserted positively. A DELETED file is only reported, never
failed: this deploy cannot prove a ghost is gone, because eight of them are provably still
being served. Saying so out loud beats a check that quietly passes.

Every fetch carries `?cb=<nonce>`. Without it the check can be answered by the very cache
it is meant to see past, and a freshness check a stale copy can satisfy is theatre.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = "https://poesys.net"
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Pages promotes a new deployment onto the custom domain a moment after wrangler exits.
#: Poll rather than sleep once; give up loudly rather than quietly (R15 FAIL-SILENT).
ATTEMPTS = 10
GAP_SECONDS = 15

#: Served by the platform as configuration, not as assets. Fetching them 404s by design,
#: which would be a false failure, not a finding.
NOT_ASSETS = {"_headers", "_redirects", "_routes.json", "functions"}


def changed_files(base: str | None) -> list[tuple[str, str]]:
    """[(git status letter, path)] for `site/**` in this push.

    Fail CLOSED: if the diff cannot be computed, raise. A deploy check that silently
    decides nothing changed and reports success is the fail-open shape this file replaced.
    """
    head = os.environ.get("GITHUB_SHA", "HEAD")
    if not base or set(base) == {"0"}:      # first push to the branch: no base commit
        base = f"{head}^"
    out = subprocess.run(
        ["git", "diff", "--name-status", base, head, "--", "site/"],
        cwd=PROJECT, capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise SystemExit(f"FAILED: cannot diff {base}..{head}: {out.stderr.strip()}")
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0][0], parts[-1]))
    return rows


def url_for(path: str) -> str | None:
    """Repo path -> the URL a reader would request, or None if it is not served.

    `site/x/index.html` is reached as `/x/`, NOT as `/x/index.html` -- measured
    2026-08-20: the explicit index.html 404s while the directory URL serves.
    """
    rel = path[len("site/"):]
    if not rel or rel.split("/")[0] in NOT_ASSETS or os.path.basename(rel) in NOT_ASSETS:
        return None
    if rel == "index.html":
        return f"{HOST}/"
    if rel.endswith("/index.html"):
        return f"{HOST}/{rel[:-len('index.html')]}"
    return f"{HOST}/{rel}"


def fetch(url: str, nonce: str) -> bytes:
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        f"{url}{sep}cb={nonce}",
        headers={"User-Agent": "poesys-deploy-assert"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def main() -> int:
    rows = changed_files(os.environ.get("DEPLOY_BASE_REF"))
    wanted: dict[str, str] = {}     # url -> expected sha256
    deleted: list[str] = []
    for status, path in rows:
        url = url_for(path)
        if url is None:
            continue
        if status == "D":
            deleted.append(url)
            continue
        full = os.path.join(PROJECT, path)
        if not os.path.isfile(full):
            continue
        with open(full, "rb") as fh:
            wanted[url] = hashlib.sha256(fh.read()).hexdigest()

    if deleted:
        print(
            "NOT ASSERTED -- these URLs were deleted by this push, and a deploy cannot\n"
            "prove absence through an edge cache that serves last-known-good:\n  "
            + "\n  ".join(deleted)
        )

    if not wanted:
        print("no served asset changed under site/ in this push; nothing to assert")
        return 0

    outstanding = dict(wanted)
    for attempt in range(ATTEMPTS):
        nonce = f"deploy-{os.environ.get('GITHUB_RUN_ID', 'local')}-{attempt}"
        for url, want in list(outstanding.items()):
            try:
                got = hashlib.sha256(fetch(url, nonce)).hexdigest()
            except (urllib.error.URLError, OSError) as exc:
                print(f"  attempt {attempt}: {url}: {exc}")
                continue
            if got == want:
                print(f"  serving the deployed bytes: {url}")
                del outstanding[url]
        if not outstanding:
            print(f"all {len(wanted)} changed asset(s) confirmed live")
            return 0
        if attempt < ATTEMPTS - 1:
            time.sleep(GAP_SECONDS)

    print(
        f"FAILED: {len(outstanding)} of {len(wanted)} changed asset(s) are still not what\n"
        f"poesys.net serves after ~{ATTEMPTS * GAP_SECONDS // 60} minutes:\n  "
        + "\n  ".join(sorted(outstanding)),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
