#!/usr/bin/env python3
"""LIVE-surface verification for the director-window DELTA PANEL.

WHY THIS EXISTS -- a control that passed for the wrong reason
------------------------------------------------------------
`SITE_director_window_delta_view`'s own mint note makes R11 the L2 bar:

    "done means fetching the LIVE deployed page and asserting the rendered delta
     changed as intended -- not the code, not the JSON on origin."

The obvious way to discharge that is the generic door verifier:

    $ python3 site/live_pixel_verify.py --door /director/
    [PASS] /director/  http=200 feeds=6 rendered_elements=24
    1/1 doors verified on the LIVE surface.

That PASS was recorded on 2026-08-03 while the delta feature was **not deployed at
all**: `poesys.net/data/director_delta.json` was returning 404 and the live page was
the pre-feature version. It passed because `live_pixel_verify` derives the feed list
from whatever HTML the host is currently serving, so an OLD page simply advertises
OLD feeds and every one of them is healthy. Nothing in it can express "the deployed
page is a version that predates the thing I am verifying".

That is the R15 TAUTOLOGY shape: the checked value (which feeds must be live) is
derived from the same source it is checking (the live page). Passing it is evidence
the site is not broken. It is NOT evidence this atom shipped, and stamping L2 on it
would have been a stale cell backed by a green control.

GUARANTEES (each fails on its own named defect; see test_live_delta_verify.py)
-----------------------------------------------------------------------------
D1  DEPLOYED VERSION -- the LIVE door HTML must itself fetch `../data/director_delta.json`.
    This is the guarantee the generic verifier structurally cannot make, and the one
    that catches "verified green against last week's page".
D2  FEED LIVENESS -- the delta feed AND the last-look stamp feed must each serve 200,
    parse as JSON, and carry their required keys. The stamp is checked even though the
    page does not boot from it, for two reasons: it is the DURABLE half of this feature
    (a 404 there means the baseline that is supposed to survive a publish did not), and
    the panel's passport cites it as an evidence link -- this site has already shipped
    evidence links that 404 (SITE1/MAJOR-7), so a cited artefact that does not resolve
    is a defect in its own right.
D3  RENDERED DELTA (R11) -- the live HTML is driven by the live feeds through the
    door's OWN boot path, and the delta panel must render one of its real states.
D4  MACHINE-DISTINGUISHABLE STATE -- the verdict is read from the panel's `data-state`
    attribute, never from its prose. This is not fastidiousness: the failure copy
    deliberately QUOTES the phrase "nothing has changed" in order to deny it, so any
    substring test over the rendered text is unfalsifiable. `feed-absent` and
    `stamp-lost` are FAILURES here; `changed` and `quiet` are the healthy states.

FAIL-CLOSED (R15), DELIBERATELY
-------------------------------
An unavailable check is a FAILED check. Host unreachable, node missing, harness
error, empty feed -- all exit non-zero. There is no skip verdict and no offline pass.

ANTI-PIN (the other half of R15)
--------------------------------
Nothing here pins a count, a timestamp or a stamp value. `quiet` and `changed` are
BOTH accepted, because which one is correct depends on whether anything has actually
happened since the last recorded look -- pinning either would turn an honest quiet
interval into a false alarm, or an honest change into one. What is asserted is the
RELATIONSHIP: the panel resolved to a real state, from live data, on the deployed page.

Usage:
    python3 site/director/live_delta_verify.py           # verify the live delta panel
    python3 site/director/live_delta_verify.py --json    # machine-readable report
Exit status: 0 verified, 1 any failure (including "could not check").
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from live_pixel_verify import (  # noqa: E402  (path shim above is deliberate)
    CANONICAL_HOST,
    LiveCheckUnavailable,
    PLACEHOLDER_TOKENS,
    _http_get,
    _resolve,
    feed_urls,
    run_harness,
)

DOOR = "/director/"
DELTA_FEED = "../data/director_delta.json"
STAMP_FEED = "../data/director_last_look.json"

# The panel element the door renders its delta into.
PANEL_ID = "lastlook-body"
KPI_ID = "lastlook-kpis"

# Read from `data-state`, never from prose (D4).
HEALTHY_STATES = ("changed", "quiet")
FAILURE_STATES = ("feed-absent", "stamp-lost")

# Keys without which the feed cannot substantiate a delta at all. Presence is
# required, values are NOT pinned.
DELTA_REQUIRED_KEYS = ("stamp_status", "last_look_at", "changed", "counts")
STAMP_REQUIRED_KEYS = ("stamp_version", "recorded_at", "state")

_STATE_RE = re.compile(r'data-state="([a-z-]+)"')


@dataclass
class DeltaResult:
    ok: bool = False
    http_status: int | None = None
    deployed_version: bool = False
    feed_status: dict[str, int] = field(default_factory=dict)
    rendered_state: str | None = None
    failures: list[str] = field(default_factory=list)
    sample: str = ""

    def as_dict(self) -> dict:
        return {
            "door": DOOR,
            "ok": self.ok,
            "http_status": self.http_status,
            "deployed_version": self.deployed_version,
            "feed_status": self.feed_status,
            "rendered_state": self.rendered_state,
            "failures": self.failures,
            "sample": self.sample[:400],
        }


def _get_json(url: str, fetcher=None) -> tuple[int, object]:
    """Fetch and parse. A non-200, an unparseable body or an empty payload all
    surface as a failure to the caller -- never as a silently-empty dict."""
    status, body = _http_get(url, fetcher)
    if status != 200:
        return status, None
    try:
        payload = json.loads(body.decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return status, None
    if payload in ({}, [], None, ""):
        return status, None
    return status, payload


def verify_delta(fetcher=None) -> DeltaResult:
    """Fetch the LIVE director door and its LIVE feeds, render, judge the delta panel."""
    res = DeltaResult()

    status, body = _http_get(CANONICAL_HOST + DOOR, fetcher)
    res.http_status = status
    if status != 200:
        res.failures.append(f"D1 live door does not serve 200 (got {status})")
        return res
    html = body.decode("utf-8", errors="replace")

    # ---- D1: is the DEPLOYED page even the version that has this feature? ----
    discovered = feed_urls(html)
    res.deployed_version = DELTA_FEED in discovered
    if not res.deployed_version:
        res.failures.append(
            "D1 the deployed page does not fetch {} -- it predates the delta view. "
            "A generic door check passes happily here, which is exactly why this "
            "guarantee exists.".format(DELTA_FEED)
        )
        return res

    # ---- D2: both feeds live, parseable, and carrying their required keys ----
    feeds: dict[str, object] = {}
    for feed, required in ((DELTA_FEED, DELTA_REQUIRED_KEYS), (STAMP_FEED, STAMP_REQUIRED_KEYS)):
        fstatus, payload = _get_json(_resolve(DOOR, feed), fetcher)
        res.feed_status[feed] = fstatus
        if payload is None:
            res.failures.append(
                f"D2 {feed} did not serve usable JSON (status {fstatus})"
            )
            continue
        missing = [k for k in required if k not in payload]
        if missing:
            res.failures.append(f"D2 {feed} is missing required key(s): {missing}")
        feeds[feed] = payload

    # Every other feed the door boots from, so its own render path completes.
    for feed in discovered:
        if feed in feeds:
            continue
        fstatus, payload = _get_json(_resolve(DOOR, feed), fetcher)
        res.feed_status[feed] = fstatus
        if payload is not None:
            feeds[feed] = payload

    if res.failures:
        return res

    # ---- D3/D4: drive the door's own boot path and read the rendered state ----
    rendered = run_harness(html, feeds)
    panel = rendered.get(PANEL_ID) or {}
    inner = str(panel.get("innerHTML") or "")
    res.sample = inner
    if not inner.strip():
        res.failures.append(f"D3 #{PANEL_ID} rendered nothing on the live surface")
        return res

    low = inner.lower()
    for token in PLACEHOLDER_TOKENS:
        if token in low:
            res.failures.append(
                f"D3 #{PANEL_ID} is still on its placeholder ({token!r}) -- the panel "
                "never resolved against live data"
            )
            return res

    match = _STATE_RE.search(inner)
    if not match:
        res.failures.append(
            f"D4 #{PANEL_ID} rendered no data-state attribute, so its outcome is only "
            "readable as prose. The failure copy quotes 'nothing has changed' in order "
            "to deny it, so a prose read is unfalsifiable."
        )
        return res
    res.rendered_state = match.group(1)

    if res.rendered_state in FAILURE_STATES:
        res.failures.append(
            f"D4 the live delta panel is in failure state {res.rendered_state!r} -- "
            "it is rendering honestly, but the feature is not working in production"
        )
        return res
    if res.rendered_state not in HEALTHY_STATES:
        res.failures.append(
            f"D4 unrecognised data-state {res.rendered_state!r} (expected one of "
            f"{HEALTHY_STATES + FAILURE_STATES})"
        )
        return res

    # A 'changed' delta must actually carry its diagnostic KPIs; a 'quiet' one must
    # NOT fabricate them. Both directions are asserted, because the fail-open form of
    # this feature is a fabricated 0/0/0 from a lost baseline.
    kpis = str((rendered.get(KPI_ID) or {}).get("innerHTML") or "")
    if res.rendered_state == "changed" and not kpis.strip():
        res.failures.append("D3 state is 'changed' but the KPI row rendered empty")
        return res

    res.ok = True
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    try:
        res = verify_delta()
    except LiveCheckUnavailable as e:
        # An unavailable check is a FAILED check (R15). No skip verdict exists.
        if args.json:
            print(json.dumps({"door": DOOR, "ok": False, "failures": [f"unavailable: {e}"]}))
        else:
            print(f"[FAIL] {DOOR} delta panel -- check could not be performed: {e}")
        return 1

    if args.json:
        print(json.dumps(res.as_dict(), indent=2))
        return 0 if res.ok else 1

    if res.ok:
        print(f"[PASS] {DOOR} delta panel  http={res.http_status} "
              f"state={res.rendered_state} feeds={len(res.feed_status)}")
        print(f"         pixel #{PANEL_ID}: {res.sample[:200]}")
        print("Live delta panel verified on the deployed surface (R11).")
        return 0

    print(f"[FAIL] {DOOR} delta panel  http={res.http_status} "
          f"deployed_version={res.deployed_version} state={res.rendered_state}")
    for f in res.failures:
        print(f"         {f}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
