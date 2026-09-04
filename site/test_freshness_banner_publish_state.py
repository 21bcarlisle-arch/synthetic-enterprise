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


def _heartbeat(state, age_hours=0.0, committed_but_unpublished=False, *,
               as_at_utc=None, cadence_seconds=None):
    return {
        "ts_iso": "2026-08-13T17:52:31Z",
        "verdict": "drew",                      # the tick was healthy the entire time
        "content_publish": {
            "state": state,
            "published_age_seconds": age_hours * 3600,
            "committed_but_unpublished": committed_but_unpublished,
            # Carried since 2026-09-04 so a healthy banner can STATE its as-at date rather than
            # saying nothing -- see test_a_healthy_weekly_banner_states_its_as_at_date.
            **({"as_at_utc": as_at_utc} if as_at_utc else {}),
            **({"cadence_seconds": cadence_seconds} if cadence_seconds else {}),
        },
    }


def render(prov=VERIFIED_PROVENANCE, heartbeat=None, figures=None):
    """`figures="none"` renders as a page that declares it publishes no simulation figure."""
    result = subprocess.run(
        [NODE, str(HARNESS), str(ASSET)] + ([figures] if figures else []),
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


# ── the director's two banner findings on /knowledge/price-cap/, 2026-08-24 ──────────────────

def _two_clock_heartbeat(push_hours, figures_hours):
    """A heartbeat where the two clocks disagree, which is the ordinary state of a wedge: the
    publish path keeps pushing provenance commits while the figures themselves sit still."""
    return {
        "ts_iso": "2026-08-24T15:00:00Z",
        "verdict": "drew",
        "content_publish": {
            "state": "stale",
            "published_age_seconds": push_hours * 3600,
            "committed_age_seconds": figures_hours * 3600,
            "committed_but_unpublished": False,
        },
    }


def test_the_verdict_and_the_number_come_from_the_same_clock():
    """THE SENTENCE THAT CONTRADICTED ITSELF. `publish_freshness.snapshot()` decides `stale` on
    the OLDER of two ages — the push, and when the figures last moved in git — precisely so "a
    push landed" cannot pass for "the figures moved". The banner printed the YOUNGER one, so the
    director was shown "PUBLISHING IS DOWN — the figures on this page last reached the site 0.3h
    ago": down on one clock and eighteen minutes fresh on the other, in one sentence."""
    out = render(heartbeat=_two_clock_heartbeat(push_hours=0.3, figures_hours=9.2))

    assert out["state"] == "stale"
    assert "9.2h" in out["text"], (
        "the banner is still reporting the push clock (0.3h) while its verdict rests on the "
        "figures clock (9.2h) — the two halves of the sentence disagree")
    assert "0.3h" not in out["text"]
    assert "last changed" in out["text"], (
        "the sentence says the figures 'reached the site' when what it measured is when they "
        "last CHANGED — naming the wrong clock is how the contradiction started")


def test_when_the_push_is_the_older_clock_the_sentence_says_so():
    """R15 null control on the above: if it always said "changed" it would be a different fixed
    wording, not a sentence that reports which clock decided."""
    out = render(heartbeat=_two_clock_heartbeat(push_hours=14.0, figures_hours=2.0))

    assert "14.0h" in out["text"]
    assert "reached the site" in out["text"]


def test_a_reference_page_carries_no_publishing_status_at_all():
    """Director, 2026-08-24: "its own footer says no simulation figure appears there, so a
    freshness warning about figures is noise that undermines the honest banners elsewhere.
    Reference pages shouldn't carry publishing status." """
    out = render(heartbeat=_two_clock_heartbeat(push_hours=0.3, figures_hours=9.2),
                 figures="none")

    assert "PUBLISHING IS DOWN" not in out["text"]
    assert "Verified" not in out["text"]
    assert out["state"] == "reference"
    assert "Reference page" in out["text"]


def test_a_reference_page_still_renders_a_banner():
    """NOT an opt-out from the banner, only from a claim it cannot honestly make. This file's
    own asset says presence is how a reader tells the layer is alive from the layer having
    failed to load; a reference page that rendered nothing would forfeit that."""
    out = render(heartbeat=_two_clock_heartbeat(0.3, 9.2), figures="none")

    assert out["text"].strip(), "the layer rendered nothing at all on a reference page"
    assert out["error"] is None


def test_a_figures_page_is_unaffected_by_the_reference_opt_out():
    """The opt-out must be opt-IN. A page that does not declare itself a reference page keeps
    every warning it had."""
    out = render(heartbeat=_two_clock_heartbeat(0.3, 9.2))

    assert "PUBLISHING IS DOWN" in out["text"]
    assert out["state"] == "stale"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE RED COUNT'S TREE, RENDERED (2026-08-31)
# ═════════════════════════════════════════════════════════════════════════════════════════════
#
# `nonblocking_reds_total: 66` was served in the same object as `git_commit: "d1ba6bd46"`, and the
# banner rendered "66 non-blocking test reds elsewhere in the repository". A reader joins those and
# concludes 66 reds at that commit. The count was taken by a pytest run with `cwd=PROJECT_DIR` --
# the shared working tree, which that evening also held an uncommitted guard widening reddening
# ~1,760 tests. The number was about neither object.
#
# THESE ARE HERE RATHER THAN BESIDE THE PRODUCER BECAUSE THE PRODUCER-SIDE VERSION DID NOT WORK.
# Its assertions grepped the asset for the field name; mutation M5 -- leave `redTreeClause`
# defined and stop calling it -- SURVIVED, because every grepped string still existed in dead
# code. Rendering is the only thing that can tell a called function from an uncalled one.

_REDS_PROVENANCE = dict(VERIFIED_PROVENANCE)


def _with_annotation(annotation):
    prov = json.loads(json.dumps(VERIFIED_PROVENANCE))
    prov["annotation"] = annotation
    return prov


def test_the_tree_the_red_count_was_taken_on_is_rendered():
    """The dirty case, which is the ordinary one on this machine: several lanes always have
    uncommitted work in the shared tree when the remainder suite runs."""
    out = render(prov=_with_annotation({
        "open_findings": 47,
        "nonblocking_reds": ["FAILED tests/x.py::test_y"],
        "nonblocking_reds_total": 66,
        "nonblocking_reds_measured_on": {"git_commit": "d1ba6bd46",
                                         "tree_state": "working-tree"},
    }))
    assert "66 non-blocking test reds" in out["text"]
    assert "working tree at d1ba6bd46" in out["text"], (
        "the count is rendered beside the published commit with nothing saying it was taken on "
        "a different tree -- the reader joins them and gets a number about neither: {!r}".format(
            out["text"]))
    assert "not a property of that commit" in out["text"]


def test_a_count_taken_on_the_commit_itself_says_so_and_does_not_hedge():
    """NULL CONTROL. Without it the test above passes on a renderer that appends the caveat
    unconditionally -- a warning on every count is a warning on none, and it would make the
    honest case unreadable to stop the dishonest one."""
    out = render(prov=_with_annotation({
        "open_findings": 47,
        "nonblocking_reds": ["FAILED tests/x.py::test_y"],
        "nonblocking_reds_total": 66,
        "nonblocking_reds_measured_on": {"git_commit": "d1ba6bd46", "tree_state": "commit"},
    }))
    assert "counted at d1ba6bd46" in out["text"]
    assert "not a property of that commit" not in out["text"]


def test_an_annotation_written_before_this_field_renders_as_unrecorded():
    """THE BACK CATALOGUE. Every artefact published before 2026-08-31 carries a red count and no
    `measured_on`. Defaulting those to the showing commit would retro-fit the exact claim nobody
    made -- the misattribution, applied to everything already served. It must read as unknown."""
    out = render(prov=_with_annotation({
        "open_findings": 47,
        "nonblocking_reds": ["FAILED tests/x.py::test_y"],
        "nonblocking_reds_total": 66,
    }))
    assert "counted on an unrecorded tree" in out["text"]
    assert "d1ba6bd46" not in out["text"].split("non-blocking test red")[-1]


# ─────────────────────────────────────────────────────────────────────────────────────────
# WHEN the red count was taken, not only which tree (2026-09-03).
#
# `checked_at` has been in this feed since the annotation existed and no reader has ever met
# it. The count is produced by a suite that runs inside whatever the publish path has LEFT, so
# when that suite stops finishing, the annotation block stops moving — inside a
# `publish_provenance.json` that is rewritten every cycle, which is exactly what made it
# invisible. Observed live: a red counted at 06:22Z on 2026-09-01 was still being published on
# 2026-09-03, beside a provenance file with that afternoon's mtime, and the banner said nothing.
#
# The tree clause could not catch it. It names the COMMIT, and a commit hash does not tell a
# reader the count is two days old.


def _aged_annotation(days_old, **over):
    import datetime as _dt
    at = (_dt.datetime.now(_dt.timezone.utc)
          - _dt.timedelta(days=days_old, hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ann = {
        "nonblocking_reds_checked_at": at,
        "open_findings": 47,
        "nonblocking_reds": ["FAILED tests/x.py::test_y"],
        "nonblocking_reds_total": 66,
        "nonblocking_reds_measured_on": {"git_commit": "d1ba6bd46", "tree_state": "commit"},
    }
    ann.update(over)
    return ann


def test_a_red_count_days_old_says_so_on_the_page():
    """DEFECT: a two-day-old count is published as though it were this cycle's.

    The age is computed against the reader's own clock rather than against anything in the
    feed, so a producer that freezes cannot also freeze the thing that would report it.
    """
    out = render(prov=_with_annotation(_aged_annotation(2)))
    assert "last counted 2 days ago" in out["text"], (
        "a red count taken two days ago reaches the reader with no indication of its age, so a "
        "frozen annotation inside a freshly-written file is invisible: {!r}".format(out["text"]))
    assert "may no longer be true" in out["text"]


def test_a_count_taken_today_does_not_grow_the_caveat():
    """NULL CONTROL, and it is the one that matters here. Without it the test above passes on a
    renderer that appends the age clause unconditionally — and a page that says "may no longer
    be true" on every visit trains a reader to skip the sentence on the one visit it means
    something. The count is refreshed hourly at best, so "0 days" is noise by construction."""
    out = render(prov=_with_annotation(_aged_annotation(0)))
    assert "last counted" not in out["text"], (
        "a count taken within the day carries an age caveat, which makes the caveat "
        "meaningless: {!r}".format(out["text"]))
    assert "66 non-blocking test reds" in out["text"]


def test_an_annotation_with_no_clock_says_the_clock_is_missing():
    """DEFECT: absent reads as current, which is the failure this whole clause exists for.

    Dropping the clause when `checked_at` is absent would publish an ageless count and let the
    back catalogue — every artefact written before the field existed — read as fresh.
    """
    ann = _aged_annotation(2)
    del ann["nonblocking_reds_checked_at"]
    out = render(prov=_with_annotation(ann))
    assert "when it was counted is unrecorded" in out["text"], (
        "an annotation with no `checked_at` renders without any age statement, so absent reads "
        "as current: {!r}".format(out["text"]))


def test_an_unparseable_clock_says_unreadable_rather_than_going_quiet():
    """DEFECT: a malformed timestamp silently drops the caveat.

    `Date.parse` returns NaN and every comparison against NaN is false, so a naive age check
    falls through to the no-caveat branch — the fail-silent that reads as a fresh count.
    """
    out = render(prov=_with_annotation(_aged_annotation(2, nonblocking_reds_checked_at="not-a-date")))
    assert "when it was counted is unreadable" in out["text"], (
        "an unparseable `checked_at` renders as though the count were current: {!r}".format(
            out["text"]))


def test_the_age_clause_never_appears_without_a_red_to_qualify():
    """SCOPE. The clause qualifies the RED count, which is the number produced by the suite that
    freezes. `open_findings` is a directory listing refreshed every cycle on every path,
    including the failure path, so attaching an age to it would caveat a number that is not
    stale and hide that the two halves have different clocks."""
    out = render(prov=_with_annotation({
        "nonblocking_reds_checked_at": "2026-09-01T06:22:09Z",
        "open_findings": 47,
    }))
    assert "47 open findings" in out["text"]
    assert "last counted" not in out["text"]
    assert "unrecorded" not in out["text"]


def test_a_healthy_weekly_banner_states_its_as_at_date():
    """SILENCE IMPLIES CURRENCY, AND AT A WEEKLY CADENCE THAT IS A FALSE IMPRESSION.

    Director, 2026-09-04, moving numbers and runs to a weekly cadence: *"the staleness banner
    matters more, not less: a week-old site saying 'as at Monday' is honest, one that implies
    currency is not."*

    The healthy branch returned `""`. That was defensible while the site republished every half
    hour -- nothing to say, because everything was minutes old -- and it becomes a lie the moment
    the same silence sits beside figures that are six days old. A number with nothing said about
    its age reads as now.

    MUTATION: return "" for the publishing state again and this fires.
    """
    out = render(heartbeat=_heartbeat("publishing", 0.2,
                                      as_at_utc="2026-09-01T07:00Z", cadence_seconds=7 * 86400))

    assert "Figures as at 2026-09-01 07:00Z" in out["text"], out["text"]
    assert "every week" in out["text"], "the reader is not told what cadence to expect"
    assert "PUBLISHING IS DOWN" not in out["text"], (
        "a site publishing exactly on cadence was rendered as an outage")
    assert out["state"] != "stale"


def test_a_healthy_banner_with_no_as_at_date_says_nothing_rather_than_guessing():
    """FAIL-CLOSED on the sentence, not on the page. If the snapshot could not date the figures,
    the banner must not invent a date -- and must not print a half-sentence either. MUTATION:
    render the cadence clause without the date and this fires."""
    out = render(heartbeat=_heartbeat("publishing", 0.2))
    assert "Figures as at" not in out["text"]
    assert "every week" not in out["text"]
