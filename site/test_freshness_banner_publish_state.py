"""The banner must not say "Verified" over figures that have not moved (2026-08-13).

WHAT WAS ON THE LIVE SITE. `site/data/publish_provenance.json` on origin read:

    verification_state : verified
    showing_run        : run_output_f232c3480_20260813T164721Z.json
    verified_at        : 2026-08-13T17:17:05Z

and it was TRUE, by that file's own contract: the scoped gate WAS green at 17:17. Meanwhile the
publish path had not landed for 21.7 hours -- `git log --grep="Auto-process run complete"` on
origin stops at 2026-08-12 21:28 -- because every content commit was dying on the pre-commit hook
deadline while the banner's own commit, which had a larger deadline, kept getting through.

So the site made a fresh-sounding claim about a run whose figures it was not serving, which is
the fake-fresh sin `publish_provenance.py` names as cardinal -- reached not through a bug in that
module but through a gap between what it measures (was the GATE green) and what a visitor wants
to know (are these numbers current).

These drive the REAL asset through a DOM (R11): the assertion is on what a browser renders, not
on a string in the file.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
ASSET = SITE / "assets" / "freshness-banner.js"
HARNESS = SITE / "assets" / "_freshness_harness.mjs"

PROV = "/data/publish_provenance.json"
HEARTBEAT = "/data/tick_heartbeat.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

# The provenance file exactly as origin carried it during the freeze: green gate, fresh stamp.
VERIFIED_PROVENANCE = {
    "schema": 1,
    "verification_state": "verified",
    "paused_since": None,
    "showing_run": {"run_id": "run_output_f232c3480_20260813T164721Z.json",
                    "verified_at": "2026-08-13T17:17:05Z"},
    "last_verified": {"run_id": "run_output_f232c3480_20260813T164721Z.json",
                      "verified_at": "2026-08-13T17:17:05Z"},
    "annotation": {},
}


def _heartbeat(state, age_hours=0.0, committed_but_unpublished=False):
    return {
        "ts_iso": "2026-08-13T17:52:31Z",
        "verdict": "drew",                      # the tick was healthy the entire time
        "content_publish": {
            "state": state,
            "published_age_seconds": age_hours * 3600,
            "committed_but_unpublished": committed_but_unpublished,
        },
    }


def render(prov=VERIFIED_PROVENANCE, heartbeat=None):
    result = subprocess.run(
        [NODE, str(HARNESS), str(ASSET)],
        input=json.dumps({PROV: prov, HEARTBEAT: heartbeat}),
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_a_green_gate_over_frozen_figures_renders_STALE_not_verified():
    """The incident. Gate green, tick drawing, figures 21.7h old."""
    out = render(heartbeat=_heartbeat("stale", 21.7))

    assert out["state"] == "stale", (
        "the banner rendered a verification state over figures that had not reached the site for "
        "21.7 hours -- which is what it looked like on the live site"
    )
    assert "PUBLISHING IS DOWN" in out["text"]
    assert "21.7h" in out["text"]
    # The verification sentence is not deleted -- it is true, and it is no longer the whole story.
    assert "Verified 2026-08-13T17:17:05Z" in out["text"]


def test_a_healthy_publish_leaves_the_verified_banner_alone():
    """MUTATION both ways: the stale state is real measurement, not a constant."""
    out = render(heartbeat=_heartbeat("publishing", 0.2))
    assert out["state"] == "verified"
    assert "PUBLISHING IS DOWN" not in out["text"]
    assert "Verified 2026-08-13T17:17:05Z" in out["text"]


def test_the_tick_verdict_alone_cannot_make_the_page_look_current():
    """THE WHOLE POINT (director): alive-but-unchanged and alive-and-publishing must not look the
    same. The heartbeat below says `verdict: drew` in BOTH cases -- exactly as it did all day on
    2026-08-13 -- and only the content-publish state separates them."""
    frozen = render(heartbeat=_heartbeat("stale", 18.0))
    live = render(heartbeat=_heartbeat("publishing", 0.1))
    assert frozen["state"] != live["state"]


def test_an_unmeasurable_publish_age_says_so_rather_than_going_quiet():
    for state, phrase in (("unknown", "Publishing status unknown"),
                          ("unpublished", "No verified publish is on record")):
        out = render(heartbeat=_heartbeat(state))
        assert out["state"] == "stale"
        assert phrase in out["text"]


def test_a_missing_heartbeat_leaves_the_verification_banner_standing():
    """The one place this layer is deliberately QUIET, and why.

    A missing provenance file blanks the page's only freshness claim, so it escalates to UNKNOWN.
    A missing heartbeat does not: the verified/paused sentence is still true and still useful, and
    letting one absent file suppress a banner that is telling the truth would trade a real signal
    for a theoretical one.
    """
    out = render(heartbeat=None)
    assert out["state"] == "verified"
    assert "Verified 2026-08-13T17:17:05Z" in out["text"]
    assert out["error"] is None


def test_a_missing_provenance_file_still_fails_LOUD():
    """The pre-existing guarantee, re-asserted through the new two-fetch boot: adding a second
    feed must not turn the fail-loud path into a fail-silent one."""
    out = render(prov=None, heartbeat=_heartbeat("publishing", 0.1))
    assert out["state"] == "unknown"
    assert "Freshness unknown" in out["text"]
    assert out["error"]
