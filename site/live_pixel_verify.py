#!/usr/bin/env python3
"""LIVE-surface pixel verification for the public doors (SITE1_expert_doors, R11 gate (b)).

WHY THIS EXISTS
---------------
`SITE1_expert_doors` has sat at level 2 with three named residuals. One of them,
recorded in the atom itself, is:

    "(b) R11 live-pixel verify (no autonomous network)"

R11 says a user-visible change is done only when the LIVE deployed surface has been
fetched and the actual RENDERED value asserted -- never the code, the file on origin,
or the deploy log. Every site test in this repo verifies the repo: it reads
`site/**/index.html` off disk and drives it with `site/data/*.json` off disk. That is
a real control, but it is structurally incapable of noticing the failure that actually
reaches a reader:

    the door deploys, its JSON feed 404s or drifts schema, and every panel on the
    live page sits on "Loading..." or "Could not load proof.json" indefinitely.

Both halves are green in the repo. The live page is empty. This module closes that gap
by fetching the LIVE html and the LIVE json from the deployed host and driving the
door's OWN boot path with them (site/_live_harness.mjs), then asserting on what the
door actually put on screen.

GUARANTEES
----------
G1  reachability -- every canonical door returns 200 DIRECTLY from the live host.
    A door that only resolves via a redirect is not a canonical door; the sitemap
    would be advertising a URL that is not the real one.
G2  rendered pixel (R11) -- each door is driven by its LIVE feeds and must render
    real content. No element the door's own script wrote may contain an error or
    placeholder token.
G3  feed integrity -- every `../data/*.json` a door fetches must itself be live,
    200, and parse as JSON with a non-empty payload.

FAIL-CLOSED, DELIBERATELY (R15)
-------------------------------
An unavailable check is a FAILED check. If the host is unreachable, if node is
missing, if a feed is empty, if the harness errors -- this verifier FAILS. It has no
"skip" verdict and no offline pass. That is the single most important property here:
the whole point is that a live check which quietly no-ops when the network is down is
worth less than no check at all, because it reports green.

Correspondingly this is a TOOL, invoked at door close and recorded as evidence -- it
is NOT wired into the pre-commit or publish gate. A network-dependent control in the
commit path would wedge every offline commit, which is the control-false-positive
class this project has already been bitten by.

ANTI-PIN (the other half of R15)
--------------------------------
Nothing here pins a figure, a count, a date or a stamp. The door list is DERIVED from
`site/sitemap.xml` (itself the canonical published list, kept honest by
tests/tools/test_site1_proof_crawlability.py) rather than hand-typed, and every
assertion is a relationship -- "the door rendered something that is not an error" --
never "the door rendered £1,501,001". A control that pins generated output turns every
legitimate regeneration into a false alarm.

Usage:
    python3 site/live_pixel_verify.py                 # verify every canonical door
    python3 site/live_pixel_verify.py --door /proof/  # one door
    python3 site/live_pixel_verify.py --json          # machine-readable report
Exit status: 0 all doors verified, 1 any failure (including "could not check").
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

SITE = Path(__file__).resolve().parent
SITEMAP = SITE / "sitemap.xml"
HARNESS = SITE / "_live_harness.mjs"
CANONICAL_HOST = "https://poesys.net"
TIMEOUT = 30

# Tokens that mean "this door did not actually render". Matched case-insensitively.
#
# HARD tokens are a defect ANYWHERE in the rendered content: they are the doors' own
# `.catch()` error text, the un-replaced loading state, and the unmistakable signature
# of an object concatenated into a string. No prose contains these by accident.
HARD_TOKENS = (
    "could not load",
    "failed to load",
    "error loading",
    "unavailable at generation time",
    "[object object]",
    "loading…",
    "loading...",
    "loading&hellip;",
)

# VALUE tokens are only a defect in a VALUE POSITION -- a rendered leaf that IS the bad
# value (`<div class="kpi-v">NaN</div>`), or an element whose whole text is the token.
#
# They are deliberately NOT substring-matched. This site's whole proposition is showing
# its own defects, so its honest-hold notes and retro entries discuss NaN fail-opens in
# plain English: an earlier draft of this control flagged 11 such notes on /proof/ and
# would have wedged the door on its most honest content. A control that fires on the
# artefact being described rather than the artefact itself is a false positive, and a
# false positive on a publish path is how this project has stalled before.
VALUE_TOKENS = ("nan", "undefined", "null")

PLACEHOLDER_TOKENS = ("loading…", "loading...", "loading&hellip;")


def rendered_defects(text: str) -> list[str]:
    """Failure tokens genuinely present in a door's rendered content."""
    low = text.lower()
    hits = [f"failure token {t!r}" for t in HARD_TOKENS if t in low]
    stripped = re.sub(r"<[^>]+>", "", low).strip()
    for t in VALUE_TOKENS:
        if stripped == t or re.search(rf">\s*{re.escape(t)}\s*<", low):
            hits.append(f"rendered value is {t!r}")
    return hits

# The page-relative feed URLs a door's inline script fetches.
_FEED_RE = re.compile(r"""fetch\(\s*["']([^"']*?\.json[^"']*)["']""")


class LiveCheckUnavailable(RuntimeError):
    """The check could not be performed. NOT a pass -- callers must treat this as a
    failure. Named as its own type so no caller can accidentally except-and-continue
    it into a green result."""


@dataclass
class DoorResult:
    path: str
    ok: bool = False
    http_status: int | None = None
    static: bool = False
    feeds: dict[str, int] = field(default_factory=dict)
    rendered_elements: int = 0
    failures: list[str] = field(default_factory=list)
    sample: dict[str, str] = field(default_factory=dict)


def _http_get(url: str, fetcher=None) -> tuple[int, bytes]:
    """Return (status, body). Redirects are NOT followed -- G1 needs to see a 301 as
    a 301, not as the 200 of wherever it lands."""
    if fetcher is not None:
        return fetcher(url)

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *_a, **_k):
            return None

    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": "poesys-live-pixel-verify"})
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise LiveCheckUnavailable(f"{url}: {e}") from e


def canonical_doors(sitemap: Path = SITEMAP) -> list[str]:
    """Door paths DERIVED from the published sitemap -- never a hand-typed list, so a
    door added to or removed from the public IA is picked up without editing this file.

    Fail-closed: an unreadable, malformed or empty sitemap raises rather than yielding
    an empty door list. Verifying zero doors and reporting success is the classic
    fail-open shape this whole module exists to refuse.
    """
    try:
        root = ET.fromstring(sitemap.read_text(encoding="utf-8"))
    except (OSError, ET.ParseError) as e:
        raise LiveCheckUnavailable(f"sitemap unreadable: {e}") from e
    doors = []
    for loc in root.iter():
        if loc.tag.endswith("loc") and loc.text:
            url = loc.text.strip()
            if url.startswith(CANONICAL_HOST):
                doors.append(url[len(CANONICAL_HOST):] or "/")
    if not doors:
        raise LiveCheckUnavailable("sitemap advertises no canonical doors")
    return doors


# Live doors that are deliberately NOT in the sitemap, and therefore invisible to
# canonical_doors() above. They are off-nav/noindex by design (the sitemap's own
# exclusion rule, mirrored by NEVER_ADVERTISED in
# tests/tools/test_site1_proof_crawlability.py) -- but "not advertised to crawlers"
# is not "not deployed": both serve 200 to anyone with the URL.
#
# Deriving coverage from the sitemap ALONE was a fail-open: an internal door could
# only ever be checked by someone remembering `--door /director/` by hand, so the
# R11 evidence for /director/ rested on a manual invocation that nothing repeated.
# A default run now covers every deployed door, advertised or not.
INTERNAL_DOORS = ("/director/", "/shadow/")


def all_doors(sitemap: Path = SITEMAP) -> list[str]:
    """Every DEPLOYED door: the advertised canonical set plus the internal surfaces.

    Fail-closed via canonical_doors(); the internal list is additive, so a broken
    sitemap still raises rather than silently degrading to internal-only coverage.
    """
    doors = canonical_doors(sitemap)
    return doors + [d for d in INTERNAL_DOORS if d not in doors]


def feed_urls(html: str) -> list[str]:
    """The `../data/*.json` URLs the door's own inline script fetches, de-duplicated,
    with the cache-busting query stripped."""
    seen, out = set(), []
    for raw in _FEED_RE.findall(html):
        url = raw.split("?")[0]
        if url and url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _resolve(door_path: str, feed: str) -> str:
    """Resolve a page-relative feed URL against the door's live URL."""
    base = CANONICAL_HOST + door_path
    return urllib.parse.urljoin(base, feed)


def run_harness(html: str, feeds: dict[str, object]) -> dict:
    """Drive the door's own boot path with the supplied feeds; return rendered elements."""
    if not HARNESS.exists():
        raise LiveCheckUnavailable(f"render harness missing: {HARNESS}")
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as fh:
        fh.write(html)
        tmp = fh.name
    try:
        proc = subprocess.run(
            ["node", str(HARNESS), tmp],
            input=json.dumps(feeds), capture_output=True, text=True, timeout=120,
        )
    except FileNotFoundError as e:
        raise LiveCheckUnavailable("node is not available") from e
    except subprocess.TimeoutExpired as e:
        raise LiveCheckUnavailable("render harness timed out") from e
    finally:
        Path(tmp).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise LiveCheckUnavailable(f"render harness exited {proc.returncode}: {proc.stderr[:400]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise LiveCheckUnavailable(f"render harness produced no JSON: {e}") from e


def verify_door(door_path: str, fetcher=None) -> DoorResult:
    """Fetch the LIVE door and its LIVE feeds, render, and judge the rendered pixels."""
    res = DoorResult(path=door_path)

    status, body = _http_get(CANONICAL_HOST + door_path, fetcher)
    res.http_status = status
    if status != 200:
        res.failures.append(f"G1 door does not serve 200 directly (got {status})")
        return res
    html = body.decode("utf-8", errors="replace")
    if not html.strip():
        res.failures.append("G1 door served an empty body")
        return res

    # Feed discovery is TWO-PASS, and it has to be. A static scan of the markup only
    # finds `fetch("../data/x.json")` written literally; several doors fetch through a
    # helper (`jget(url)`, `j(url)`) or build the URL from a variable
    # (`"../data/customers/"+id+".json"`), which no regex can resolve. Pass 1 renders
    # with what was found and lets the harness REPORT every url the door actually
    # asked for; pass 2 fetches those for real and re-renders.
    #
    # Without this the verifier reports its own blind spot as a live outage -- which is
    # exactly what the first run did, failing five healthy doors on feeds it had simply
    # never looked for.
    feeds: dict[str, object] = {}

    def _load(feed: str) -> None:
        if feed in feeds or feed in res.feeds:
            return
        fstatus, fbody = _http_get(_resolve(door_path, feed), fetcher)
        res.feeds[feed] = fstatus
        if fstatus != 200:
            res.failures.append(f"G3 feed {feed} returned {fstatus}")
            return
        try:
            payload = json.loads(fbody.decode("utf-8", errors="replace"))
        except json.JSONDecodeError as e:
            res.failures.append(f"G3 feed {feed} is not valid JSON: {e}")
            return
        # An empty payload is a fail-open: the door renders "nothing recorded"
        # everywhere and every structural assertion passes vacuously.
        if payload in ({}, [], None, ""):
            res.failures.append(f"G3 feed {feed} served an empty payload")
            return
        feeds[feed] = payload

    for feed in feed_urls(html):
        _load(feed)

    rendered = run_harness(html, feeds)
    discovered = [u for u in (rendered.get("_meta", {}) or {}).get("requested", [])
                  if u not in feeds and u not in res.feeds]
    if discovered:
        for feed in discovered:
            _load(feed)
        rendered = run_harness(html, feeds)

    meta = rendered.pop("_meta", {}) or {}
    res.static = bool(meta.get("static"))
    if meta.get("scriptError"):
        res.failures.append(f"G2 door script raised: {meta['scriptError']}")
    for missing in meta.get("unresolved", []):
        res.failures.append(f"G3 door fetched {missing}, which was not live")

    for elem_id, content in rendered.items():
        text = f"{content.get('innerHTML', '')} {content.get('textContent', '')}".strip()
        if not text:
            continue
        res.rendered_elements += 1
        for defect in rendered_defects(text):
            res.failures.append(f"G2 #{elem_id}: {defect}")
        if len(res.sample) < 3:
            res.sample[elem_id] = text[:160]

    if res.static:
        # A deliberately static door (Front Door, /privacy/) has no client render to
        # drive, so G2 is judged on the markup the live host actually SERVED. The
        # floor is a real one: a door reduced to a nav-and-footer shell -- the shape a
        # broken build ships -- has almost no body text and fails here.
        body = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", html, flags=re.I)
        visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()
        res.rendered_elements = len(visible.split())
        for defect in rendered_defects(visible):
            res.failures.append(f"G2 static door: {defect}")
        if len(visible.split()) < 50:
            res.failures.append(
                f"G2 static door served only {len(visible.split())} words of visible text "
                "-- that is a shell, not a page")
        if visible:
            res.sample["<served markup>"] = visible[:160]
    elif res.rendered_elements == 0:
        res.failures.append("G2 the door rendered NOTHING -- no element received content")

    res.ok = not res.failures
    return res


def verify_all(doors: list[str] | None = None, fetcher=None) -> list[DoorResult]:
    # Default coverage is EVERY deployed door (advertised + internal), not just the
    # advertised set -- see INTERNAL_DOORS.
    return [verify_door(d, fetcher) for d in (doors or all_doors())]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--door", action="append", help="door path, e.g. /proof/ (repeatable)")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    try:
        results = verify_all(args.door)
    except LiveCheckUnavailable as e:
        # THE point of this module: could-not-check is a FAILURE, never a skip.
        if args.json:
            print(json.dumps({"ok": False, "unavailable": str(e)}, indent=2))
        else:
            print(f"LIVE CHECK UNAVAILABLE -- reported as FAILURE (R15): {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(
            {"ok": all(r.ok for r in results),
             "doors": [r.__dict__ for r in results]}, indent=2, default=str))
    else:
        for r in results:
            mark = "PASS" if r.ok else "FAIL"
            print(f"[{mark}] {r.path}  http={r.http_status} "
                  f"feeds={len(r.feeds)} rendered_elements={r.rendered_elements}")
            for f in r.failures:
                print(f"         - {f}")
            for k, v in r.sample.items():
                print(f"         pixel #{k}: {v}")
        bad = [r.path for r in results if not r.ok]
        print(f"\n{len(results) - len(bad)}/{len(results)} doors verified on the LIVE surface.")
        if bad:
            print("FAILED: " + ", ".join(bad))
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
