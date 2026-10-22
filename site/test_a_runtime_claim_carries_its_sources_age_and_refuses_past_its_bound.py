"""A present-tense claim about runtime state, on a served page, states its source's age and
refuses past a bound (2026-10-22).

THE DEFECT. The front door said "PUBLISHING IS FAILING ... over 80.0h" from a publisher record
whose failure had ended three days earlier, and "How it's built" said "Right now nothing is
waiting on him" from a count written on 18 Sep. Both were copies of runtime state that reach the
site on the weekly publish and were read as live.

THE SWEEP. A served page reads runtime state from five feeds. `RUNTIME_FEEDS` names them and the
census below asks every served `.html`/`.js` which of them it fetches, so a new reader reds here
until it is classified. Each reader that makes a present-tense claim (failing, "right now",
"running current code", "nothing has moved") has a leg in `CLAIMS`. The rest are classified with
the reason they need none. (`delivery.json` is committed by the delivery seat several times a day,
so it is fed fresh at every deploy, and its renders already carry their own `live` flags.)

ONE ASSERTION OVER BOTH LEGS. Each claim is rendered by the page's own script from one feed at two
ages. The fresh render must make the claim AND state the source's day or age. The stale one must
not make it. A render that refuses everything fails the first leg, and one that never refuses fails
the second. Both legs are in one `assert`, so neither mutant can pass.

MUTATIONS, RUN 2026-10-22, each red here:
  * freshness-banner.js: the `recordAge > bound` refusal deleted -> the banner's stale leg reds.
  * freshness-banner.js: the refusal made unconditional (`return ""`) -> the banner's fresh leg reds.
  * harness: `renderDeployment`'s freshness test forced true -> the deployment stale leg reds.
  * harness: `renderDirectorDelta`'s freshness forced false -> the delta fresh leg reds.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

RUNTIME_FEEDS = ("tick_heartbeat", "publish_provenance", "director_reserved", "director_delta",
                 "delivery")

# Every served reader of a runtime feed, and how it is held. A path here with no claim leg must
# say why it needs none.
READERS = {
    ("assets/freshness-banner.js", "tick_heartbeat"): "claim: banner_failing",
    ("assets/freshness-banner.js", "publish_provenance"):
        "the Verified line names its own verified_at; the frozen-feed check ages it",
    ("harness/index.html", "director_reserved"): "claim: reserved_right_now",
    ("harness/index.html", "director_delta"): "claim: delta_since",
    ("harness/index.html", "delivery"): "fed fresh: committed by the delivery seat each landing",
}
# proof.json is a publish artefact; only its `deployment` block is a runtime reading, held below.
EXTRA_CLAIMS = {"deployment_running": ("harness/index.html", "proof")}


def _served_files():
    for p in SITE.rglob("*"):
        if p.suffix not in (".html", ".js") or "node_modules" in p.parts:
            continue
        if p.name.startswith("_") or p.name.startswith("test_"):
            continue
        yield p


def census() -> set:
    found = set()
    for p in _served_files():
        text = p.read_text(errors="replace")
        for feed in RUNTIME_FEEDS:
            if re.search(r"data/" + feed + r"\.json", text):
                found.add((str(p.relative_to(SITE)), feed))
    return found


def _iso(days_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _harness(fn: str, element: str, feed: dict) -> str:
    proc = subprocess.run(
        [NODE, str(SITE / "harness" / "_render_harness.mjs"), str(SITE / "harness" / "index.html"),
         fn, element], input=json.dumps(feed), capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[:400]
    return json.loads(proc.stdout)["innerHTML"]


def _banner(days_ago: float) -> str:
    now = datetime.now(timezone.utc)
    hb = {"ts_iso": _iso(days_ago), "content_publish": {
        "state": "publishing", "published_age_seconds": 3600.0, "cadence_seconds": 7 * 86400,
        "publisher": {"state": "failing", "consecutive_failures": 2,
                      "failing_for_seconds": 3 * 3600.0, "clean_publishes_this_episode": 0,
                      "cited_red_at_head": "reproduces"}}}
    verified = _iso(days_ago + 1)
    prov = {"schema": 1, "verification_state": "verified", "paused_since": None,
            "showing_run": {"run_id": "run_x", "verified_at": verified},
            "last_verified": {"run_id": "run_x", "verified_at": verified}, "annotation": {}}
    proc = subprocess.run(
        [NODE, str(SITE / "assets" / "_freshness_harness.mjs"),
         str(SITE / "assets" / "freshness-banner.js")],
        input=json.dumps({"/data/publish_provenance.json": prov, "/data/tick_heartbeat.json": hb}),
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "POESYS_FRESHNESS_NOW": now.strftime("%Y-%m-%dT%H:%M:%SZ")})
    assert proc.returncode == 0, proc.stderr[:400]
    return json.loads(proc.stdout)["text"]


def _deployment(days_ago: float) -> str:
    at = (datetime.now(timezone.utc) - timedelta(days=days_ago)).timestamp()
    return _harness("renderDeployment", "deployment", {"deployment": {
        "available": True, "measured_at_s": at, "summary": {"stale": 0, "observed": 1},
        "daemons": [{"session": "alpha", "running_age_s": 60, "loaded_code_age_s": 60,
                     "unincorporated_for_s": 0, "modules_behind": 0, "stale": False,
                     "mid_work": False, "session_hosting": False, "unresolved": None}]}})


def _day(days_ago: float) -> str:
    return _iso(days_ago)[:10]


# name -> (render at an age, the claim, how its age is stated at that age)
CLAIMS = {
    "banner_failing": (_banner, "PUBLISHING IS FAILING", lambda d: f"(recorded {d * 24:.1f}h ago)"),
    "reserved_right_now": (
        lambda d: _harness("renderReserved", "reserved-now",
                           {"generated_at": _iso(d), "open_count": 0}),
        "Right now", lambda d: "(counted on " + _day(d) + ")"),
    "delta_since": (
        lambda d: _harness("renderDirectorDelta", "director-delta",
                           {"generated_at": _iso(d), "last_look_at": _iso(60), "changes": []}),
        "Nothing has moved since that position.", lambda d: "Counted on " + _day(d)),
    "deployment_running": (_deployment, "observed daemons are running current code",
                           lambda d: "Measured on " + _day(d)),
}
FRESH_DAYS, STALE_DAYS = 0.05, 10.0


def test_every_runtime_reader_on_a_served_page_is_classified():
    found = census()
    print(f"\nRUNTIME-FEED READERS ON SERVED PAGES: {len(found)} "
          f"(+{len(EXTRA_CLAIMS)} runtime block inside a publish artefact)")
    for r in sorted(found):
        print("  ", r, "->", READERS.get(r, "UNCLASSIFIED"))
    unclassified = found - set(READERS)
    assert not unclassified, (
        f"a served page reads runtime state with no rule for how its claim is held: {unclassified}. "
        "Add a claim leg below, or say in READERS why it makes no present-tense claim.")
    named = {v.split(": ", 1)[1] for v in READERS.values() if v.startswith("claim: ")}
    assert named | set(EXTRA_CLAIMS) == set(CLAIMS)


def test_a_claim_states_its_sources_age_when_fresh_and_is_withdrawn_when_stale():
    results = {}
    for name, (render, claim, age_text) in CLAIMS.items():
        fresh, stale = render(FRESH_DAYS), render(STALE_DAYS)
        stated = age_text(FRESH_DAYS)
        results[name] = (claim in fresh and stated in fresh,
                         claim not in stale)
    assert all(made and withdrawn for made, withdrawn in results.values()), (
        "(claimed when fresh with its age, withdrawn when stale) per claim: " + repr(results))
