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

#: Pages promotes a new deployment onto the custom domain some time after wrangler exits, and
#: "some time" is the whole difficulty. MEASURED, not assumed:
#:
#:   * 2026-08-20 15:47, two `.py` assets: live on the FIRST attempt, under 15s.
#:   * 2026-08-20 15:50, `/harness/` (a directory URL): NOT live after 2m17s of polling, which
#:     failed this deploy -- and verified live by hand a few minutes later. The bytes were
#:     right; the window was wrong.
#:
#: So an HTML directory URL can take minutes where a direct file takes seconds, which is the
#: same asymmetry that ran through the whole 2026-08-20 incident: extensionless paths go
#: through Pages' path resolution and direct files do not.
#:
#: 8 minutes is deliberately generous. The failure this control exists to catch is a deploy
#: that leaves readers on OLD content indefinitely -- eight pages did exactly that for a day --
#: and that failure is still caught at eight minutes. What a tight window buys is false reds on
#: ordinary variance, and a control that cries wolf gets bypassed, which costs more than the
#: minutes. Widen the clock, never the claim.
#:
#: MEASURED AGAIN 2026-09-04, from the 60 most recent Cloudflare Pages runs (2026-09-01 22:28
#: to 2026-09-04 10:00) -- 50 green, 10 red -- and the 462 `serving the deployed bytes after Ns`
#: observations those runs printed, which is the distribution the note at `main()` asked the next
#: person to collect. Three things it settles, and the third is why ATTEMPTS is NOT touched here:
#:
#:   * The UPLOAD has never failed. In all 10 red runs `wrangler pages deploy` exited success and
#:     only this assertion failed. Every red on the deploy path for three days has been a
#:     verification failure, not a publication failure.
#:   * Direct file routes are fast and the 8-minute clock is 3.8x more than they have ever
#:     needed: min 0s, median 25s, p90 91s, max 126s across all 462 observations.
#:   * A directory URL has NEVER ONCE been confirmed -- 0 of those 462 observations is a
#:     `/`-terminated URL. Every push that changed a `site/**/index.html` went red (4 of 4 where
#:     the head commit shows the change directly; the other 6 reds are merge commits whose push
#:     RANGE contained one, confirmed for `ded79e205` from its own `DEPLOY_BASE_REF`), and not
#:     one of the 50 green runs changed a directory-index page at all.
#:
#: So the 2026-08-20 remedy -- widen the clock from 2m17s to 8m -- did not work, and the reason
#: it cannot be fixed by widening it again HERE is that there is no upper bound to widen TO: a
#: clock has to be set from a distribution, and the distribution of successful directory-URL
#: promotions is EMPTY. Choosing a bigger number would be a number picked because a number was
#: needed. What is missing is an observation of a directory URL going live at all, so what this
#: file does instead is make the refusal NAME which of the two worlds it is in (below), so the
#: next red carries the evidence a bound could be set from.
#:
#: CORRECTED 2026-09-04 12:30, and the paragraph above is left standing because the correction
#: is the point: the clock is not the subject at all, so that missing observation would not have
#: settled anything. Red run 33858118312 printed `serving the deployed bytes after 0s` for TWO
#: assets of the same push whose third asset never arrived in 467s -- one deployment, one edge.
#: **No window explains 0s and >467s together**, and that line was in the log of the run that
#: failed, on both occasions the clock was blamed. What fits is a path-resolved route serving a
#: cached resolution while direct-file routes are already new. `ATTEMPTS` stays untouched, now
#: for a better reason than the absent distribution: it is not the variable.
#: Full workings: docs/staging/SEAT_FINDING_TWO_ASSETS_OF_ONE_PUSH_ARRIVED_AT_0S_...md
ATTEMPTS = 32
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


def bytes_at(ref: str, path: str) -> bytes | None:
    """The committed bytes of `path` at `ref`, or None if that cannot be read.

    None is the honest answer for a ref this checkout does not have (a force-push, a first
    push with no base) and it is NOT treated as "unchanged" anywhere -- see `classify`.
    """
    out = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=PROJECT, capture_output=True,
    )
    return out.stdout if out.returncode == 0 else None


def classify(
    url: str, want: str, path: str, base: str | None, deployment_is_live: bool = False
) -> str:
    """Why is this URL still not the deployed bytes? Name it, rather than implying one.

    A timeout collapses worlds that need different responses, and printing one sentence for
    all of them is what made ten red deploys unreadable:

      * REPLACED -- the edge is serving exactly the bytes this push overwrote. That is the
        defect this control was built for: the deploy landed and readers still have the old
        page. It is a statement about the reader, and it is actionable immediately.
      * STALE -- the edge is serving neither, AND some other asset from THIS SAME PUSH was
        confirmed live here. See `deployment_is_live` below: that makes it a statement about
        the reader too, where on its own it would not be.
      * UNCONFIRMED -- the edge is serving neither, and nothing from this push has been
        confirmed live, so this control cannot separate "the deploy has not arrived" from
        "this route is stale". Saying so is a result.
      * RESOLVED -- it arrived after the clock; the window is the suspect, not the deploy.

    `deployment_is_live` is the evidence this control was already collecting and throwing
    away. MEASURED 2026-09-04 from the logs of red run 33865355906's predecessor
    `33858118312` (head `b0bceffae`, base `1b98c836…`), which changed three served assets:

        serving the deployed bytes after 0s: https://poesys.net/data/proof.json
        serving the deployed bytes after 0s: https://poesys.net/harness/test_the_...py
        FAILED: ... https://poesys.net/harness/            (never, in 467s)

    Two assets of that push were served NEW on the FIRST attempt, immediately after wrangler
    exited; the third never arrived. One push, one deployment, one edge. **A window cannot
    explain 0s and >467s for the same deployment**, which is what the 2026-08-20 remedy
    (widen the clock) and the 2026-09-04 reading of it both assumed. What it does explain is
    a path-resolved route serving a cached resolution while direct-file routes are already
    new -- the same Pages asset cache that kept eight deleted pages alive through eight
    deployments on 2026-08-20.

    So a confirmed sibling is a sound premise, in the one direction that survives a cache:
    NEW bytes cannot come from a copy stored before they existed, so if any asset of this
    push is being served here, this push IS live at this edge. A route that is then not
    serving it is stale -- and the reader is on neither this push nor the one it overwrote.

    It defaults False, which is the conservative direction: with no sibling confirmed, the
    verdict stays UNCONFIRMED and claims nothing about the reader.

    The exit code does NOT depend on which verdict it is: an unproven deploy stays red in
    every case. Only the sentence changes, because a refusal that names its reason is how
    the refusal itself gets found to be wrong -- and this one was, twice.
    """
    try:
        got = hashlib.sha256(fetch(url, "classify")).hexdigest()
    except (urllib.error.URLError, OSError) as exc:
        return f"UNCONFIRMED (the edge did not answer: {exc})"
    if got == want:
        return "RESOLVED after the clock ran out -- the window is too short, not the deploy"
    if base:
        previous = bytes_at(base, path)
        if previous is not None and hashlib.sha256(previous).hexdigest() == got:
            return "REPLACED -- the edge is still serving the bytes this push overwrote"
    if deployment_is_live:
        return (
            "STALE -- another asset of this same push is being served here, so this push is "
            "live at this edge and this route is not serving it"
        )
    return "UNCONFIRMED (serving neither the new bytes nor the ones this push overwrote)"


def fetch(url: str, nonce: str) -> bytes:
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(
        f"{url}{sep}cb={nonce}",
        headers={"User-Agent": "poesys-deploy-assert"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def main() -> int:
    base = os.environ.get("DEPLOY_BASE_REF")
    rows = changed_files(base)
    wanted: dict[str, str] = {}     # url -> expected sha256
    source: dict[str, str] = {}     # url -> the repo path it came from, for `classify`
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
        source[url] = path

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
    started = time.monotonic()
    for attempt in range(ATTEMPTS):
        nonce = f"deploy-{os.environ.get('GITHUB_RUN_ID', 'local')}-{attempt}"
        for url, want in list(outstanding.items()):
            try:
                got = hashlib.sha256(fetch(url, nonce)).hexdigest()
            except (urllib.error.URLError, OSError) as exc:
                print(f"  attempt {attempt}: {url}: {exc}")
                continue
            if got == want:
                # The elapsed figure is the POINT of printing this, not decoration: the
                # promotion latency is the number this control's timeout has to be set from,
                # and it was guessed once already. Every green deploy now contributes an
                # observation, so the next person adjusting ATTEMPTS has a distribution
                # instead of an anecdote.
                print(f"  serving the deployed bytes after "
                      f"{time.monotonic() - started:.0f}s: {url}")
                del outstanding[url]
        if not outstanding:
            print(f"all {len(wanted)} changed asset(s) confirmed live "
                  f"in {time.monotonic() - started:.0f}s")
            return 0
        if attempt < ATTEMPTS - 1:
            time.sleep(GAP_SECONDS)

    # Whether ANY asset of this push reached the edge is the difference between a verdict
    # about the reader and a shrug, and it was being computed and dropped. See `classify`.
    deployment_is_live = len(outstanding) < len(wanted)
    named = [
        f"{url}\n    {classify(url, outstanding[url], source[url], base, deployment_is_live)}"
        for url in sorted(outstanding)
    ]
    print(
        f"FAILED: {len(outstanding)} of {len(wanted)} changed asset(s) are still not what\n"
        f"poesys.net serves after {ATTEMPTS * GAP_SECONDS // 60} minutes:\n  "
        + "\n  ".join(named),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
