"""A stopped publisher freezes the evidence of its own stopping (2026-09-24).

THE DEFECT, reproduced against the real asset at origin/main before the repair. A heartbeat
frozen on 2026-09-01, read by a browser on 2026-09-24 -- twenty-three days of nothing reaching
the site -- rendered:

    state : verified
    text  : "Verified 2026-09-01T07:00:00Z · showing run run_x
             Figures as at 2026-09-01 07:00Z -- numbers and runs publish every week."

Nothing loud, nothing false, and nothing a reader could act on.

WHY NONE OF THE THREE EXISTING REPAIRS CAN FIRE THERE. `site/assets/freshness-banner.js` had, by
the end of 2026-09-24, three separate sentences about publish health: the as-at line, the
"PUBLISHING IS DOWN" age, and the "PUBLISHING IS FAILING" refusal record landed that morning.
Every one of them is read out of `tick_heartbeat.json` -- and that file reaches a reader ONLY
when a publish succeeds. So in the one outage that matters most, the browser is serving the last
copy that made it out, in which `published_age_seconds` is near zero and `publisher.state` is
healthy, because at the instant of that last successful publish they were. Each sentence asks the
frozen artefact how old the frozen artefact is, and the answer is always "fresh", for as long as
the dark runs.

The two repairs that morning made the publisher's refusal VISIBLE. They could not make it
DELIVERABLE, and that is not a gap in them -- it is the shape of the channel.

THE PROPERTY, which is what these controls are keyed to rather than any of today's numbers:

    a page whose freshness feed has not been replaced within the feed's own declared publish
    interval must say so to its reader, and that verdict must come from a clock the outage
    cannot stop.

The reader's clock is that clock, and `ts_iso` -- stamped into the file when it is WRITTEN -- is
the one number in the feed an outage cannot keep re-writing. Their difference is the true age of
the last known good publish. It grows on its own, whatever the feed says about itself.

MUTATION DISCIPLINE. The load-bearing pair here is the two arms over ONE fixture: identical feed
bytes, identical self-reported ages, identical healthy publisher, and only the reader's clock
moved. A repair that hard-coded the alarm passes the first arm and fails the second; a repair
that never fires passes the second and fails the first. `test_the_verdict_is_a_function_of_the
_readers_clock_alone` asserts the partition is genuinely two-sided over one input, which is the
control this file would be worthless without.

These drive the REAL asset through a DOM (R11): the assertions are on what a browser renders.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
ASSET = SITE / "assets" / "freshness-banner.js"
HARNESS = SITE / "assets" / "_freshness_harness.mjs"
LIVE_HEARTBEAT = SITE / "data" / "tick_heartbeat.json"

PROV = "/data/publish_provenance.json"
HEARTBEAT = "/data/tick_heartbeat.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")

NOT_ARRIVING = "THIS PAGE IS NOT ARRIVING"

VERIFIED_PROVENANCE = {
    "schema": 1,
    "verification_state": "verified",
    "paused_since": None,
    "showing_run": {"run_id": "run_x", "verified_at": "2026-09-01T07:00:00Z"},
    "last_verified": {"run_id": "run_x", "verified_at": "2026-09-01T07:00:00Z"},
    "annotation": {},
}

# THE FEED EXACTLY AS A DEAD PUBLISHER LEAVES IT: every self-report healthy, because each was
# true at the moment of the last publish that succeeded. This is the fixture the whole file
# turns on -- it is never varied, only read at different times.
FROZEN_BUT_HEALTHY_LOOKING = {
    "ts_iso": "2026-09-01T07:00:00Z",
    "verdict": "drew",
    "content_publish": {
        "state": "publishing",
        "published_age_seconds": 120.0,
        "committed_age_seconds": 150.0,
        "stale_after_seconds": 691200,          # 8 days: the weekly cadence plus its grace
        "as_at_utc": "2026-09-01T07:00Z",
        "cadence_seconds": 604800,
        "committed_but_unpublished": False,
        "queue_depth": 0,
        "publisher": {
            "state": "publishing",
            "consecutive_failures": 0,
            "failing_for_seconds": 0.0,
            "clean_publishes_this_episode": 4,
            "cited_red_at_head": "not_established",
        },
    },
}

WITHIN_CADENCE = "2026-09-04T07:00:00Z"        # 3 days after the stamp, tolerance is 8
LONG_PAST_CADENCE = "2026-09-24T21:00:00Z"     # 23.6 days after the stamp


def _render(heartbeat, now, prov=VERIFIED_PROVENANCE, figures=None):
    result = subprocess.run(
        [NODE, str(HARNESS), str(ASSET)] + ([figures] if figures else []),
        input=json.dumps({PROV: prov, HEARTBEAT: heartbeat}),
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "POESYS_FRESHNESS_NOW": now},
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _deep_copy(payload):
    return json.loads(json.dumps(payload))


def test_a_feed_frozen_long_past_its_own_cadence_reaches_the_reader_as_an_outage():
    """THE DEFECT. Twenty-three days of nothing arriving, every field in the feed still cheerful."""
    out = _render(FROZEN_BUT_HEALTHY_LOOKING, now=LONG_PAST_CADENCE)

    assert out["state"] == "stale", (
        "a page that has not been replaced for 23 days rendered in its ordinary verified state, "
        "because every clock it consults is inside the file that stopped arriving: "
        "{!r}".format(out["text"]))
    assert NOT_ARRIVING in out["text"], out["text"]
    # The measured age, not a restatement of the feed's own 120 seconds.
    assert "23.6 days" in out["text"], (
        "the reader is told something is wrong without the measurement that establishes it: "
        "{!r}".format(out["text"]))
    # The interval it is judged against, so the reader can check the arithmetic themselves.
    assert "8.0 days" in out["text"], out["text"]


def test_the_same_frozen_feed_says_nothing_while_it_is_still_within_cadence():
    """THE ANTI-TAUTOLOGY ARM, and it is keyed to the STATE as well as the phrase.

    A repair that simply always shouted would pass the test above. Asserting only that the
    phrase is absent would still pass a repair keyed to some word of the positive fixture, so
    the verdict itself is asserted too: a site three days into a weekly cadence is healthy and
    must render as healthy.
    """
    out = _render(FROZEN_BUT_HEALTHY_LOOKING, now=WITHIN_CADENCE)

    assert NOT_ARRIVING not in out["text"], out["text"]
    assert out["state"] == "verified", (
        "a site three days into a weekly publish cadence was rendered as an outage: "
        "{!r}".format(out))
    assert "days, measured on your clock" not in out["text"]


def test_the_verdict_is_a_function_of_the_readers_clock_alone():
    """THE CONTROL OVER THE WHOLE PARTITION -- the one this file would be worthless without.

    ONE fixture, unmodified, read at a sequence of times. The feed's self-reports are constant
    across every reading: it always claims a 120-second publish age and a healthy publisher. If
    the verdict ever stopped being a function of the clock -- pinned to a literal, keyed to a
    field inside the feed, or made unreachable -- this collapses to a single outcome and fires,
    whereas a per-branch assertion would still pass on whichever branch survived.
    """
    clocks = ["2026-09-01T08:00:00Z",   # an hour later: plainly fresh
              WITHIN_CADENCE,           # 3 days: inside tolerance
              "2026-09-09T08:00:00Z",   # 8.04 days: just past it
              LONG_PAST_CADENCE]        # 23.6 days: long dark
    seen = {}
    for clock in clocks:
        out = _render(FROZEN_BUT_HEALTHY_LOOKING, now=clock)
        seen[clock] = (out["state"], NOT_ARRIVING in out["text"])

    quiet = [c for c, (_, loud) in seen.items() if not loud]
    alarmed = [c for c, (_, loud) in seen.items() if loud]
    assert quiet and alarmed, (
        "the frozen-feed branch is one-sided over a range where both sides must occur, so it is "
        "either unreachable or unconditional: {!r}".format(seen))
    # The boundary falls where the feed's OWN declared tolerance puts it, not where a literal
    # in the layer does: everything past 8 days is loud, everything inside it is quiet.
    assert seen["2026-09-09T08:00:00Z"][1] is True, seen
    assert seen[WITHIN_CADENCE][1] is False, seen
    assert all(state == "stale" for state, loud in seen.values() if loud), seen


def test_the_feeds_own_self_report_stays_healthy_in_both_arms():
    """WHY THE CLOCK HAD TO BE THE SUBJECT. This asserts the premise of the whole file: the
    fixture that renders as an outage above is, by its own account, in perfect health. If a
    future change made this feed self-report staleness, the two arms above would start passing
    for a reason that has nothing to do with the reader's clock, and this file would go on
    reporting success while testing something else.
    """
    cp = FROZEN_BUT_HEALTHY_LOOKING["content_publish"]
    assert cp["state"] == "publishing"
    assert cp["publisher"]["state"] == "publishing"
    assert cp["published_age_seconds"] < 300
    assert cp["published_age_seconds"] < cp["stale_after_seconds"]


def test_a_reader_clock_behind_the_stamp_is_not_read_as_fresh_or_as_stale():
    """A clock skewed far enough to make the age negative cannot establish anything. It must not
    alarm -- an ordinary laptop an hour out would train readers past the line -- and it must not
    be taken as evidence of health either.
    """
    out = _render(FROZEN_BUT_HEALTHY_LOOKING, now="2026-08-20T07:00:00Z")
    assert NOT_ARRIVING not in out["text"], out["text"]


def test_a_feed_that_declares_no_interval_makes_no_claim_here():
    """THE NARROWING, asserted so it is visible rather than discovered later.

    Without a declared cadence there is no interval to judge an age against, so this clause is
    silent -- deliberately, because a sentence on every feed that omits the field would fire on
    healthy pages and is the 2026-08-24 noise ruling arriving through its own repair. The gap it
    leaves is real and belongs on the producer's surface; the control below is what keeps the
    live path from falling into it.
    """
    hb = _deep_copy(FROZEN_BUT_HEALTHY_LOOKING)
    del hb["content_publish"]["stale_after_seconds"]
    del hb["content_publish"]["cadence_seconds"]

    out = _render(hb, now=LONG_PAST_CADENCE)
    assert NOT_ARRIVING not in out["text"], out["text"]


def test_the_cadence_alone_is_enough_when_the_grace_bearing_field_is_absent():
    """`stale_after_seconds` is the feed's tolerance and `cadence_seconds` is its interval. A feed
    carrying only the latter is still gradable, and falling back to it keeps the narrowing above
    as small as it can be.
    """
    hb = _deep_copy(FROZEN_BUT_HEALTHY_LOOKING)
    del hb["content_publish"]["stale_after_seconds"]

    assert NOT_ARRIVING in _render(hb, now=LONG_PAST_CADENCE)["text"]
    assert NOT_ARRIVING not in _render(hb, now=WITHIN_CADENCE)["text"]


def test_the_live_published_feed_carries_the_two_fields_this_check_needs():
    """THE LIVE PATH, keyed to the property rather than to today's values.

    Every control above drives a fixture. This one asks the artefact a browser actually fetches
    whether it can be graded at all -- because the narrowing two tests up means a producer that
    quietly stopped emitting `ts_iso` or its interval would disable the outage sentence on the
    real site without reddening a single fixture-driven test above.

    It asserts PRESENCE and TYPE, never a value: the stamp moves every tick and the cadence is
    the publisher's to choose.
    """
    feed = json.loads(LIVE_HEARTBEAT.read_text())
    cp = feed.get("content_publish") or {}

    assert isinstance(feed.get("ts_iso"), str) and feed["ts_iso"], (
        "the published heartbeat carries no write stamp, so the one freshness check that "
        "survives a dead publisher cannot run on the live site")
    interval = cp.get("stale_after_seconds") or cp.get("cadence_seconds")
    assert isinstance(interval, (int, float)) and interval > 0, (
        "the published heartbeat declares no publish interval, so its age has nothing to be "
        "judged against and the outage sentence is silently disabled: {!r}".format(cp))
