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
import os
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


# THE READER'S CLOCK, PINNED JUST AFTER THE FIXTURES' OWN STAMPS.
#
# Every heartbeat in this module is stamped 2026-08-13, and until 2026-09-24 nothing here supplied
# a clock -- so the layer saw the REAL one and these fixtures quietly aged. They were four hours
# old the day they were written and six weeks old by the time the frozen-feed check arrived to
# read them, at which point nine of these tests went red on their own fixture dates rather than on
# anything about their subjects.
#
# That is this file's own lesson pointed at itself: an age nobody supplied is an age keyed to the
# day the test ran. The clock is an input, so it is passed like every other input, and these tests
# now assert what they were written to assert for as long as they exist.
#
# Tests whose SUBJECT is the reader's clock pass their own `now` and live in
# test_the_frozen_feed_cannot_report_its_own_freshness.py.
FIXTURE_NOW = "2026-08-13T21:00:00Z"


def render(prov=VERIFIED_PROVENANCE, heartbeat=None, figures=None, now=FIXTURE_NOW):
    """`figures="none"` renders as a page that declares it publishes no simulation figure."""
    result = subprocess.run(
        [NODE, str(HARNESS), str(ASSET)] + ([figures] if figures else []),
        input=json.dumps({PROV: prov, HEARTBEAT: heartbeat}),
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "POESYS_FRESHNESS_NOW": now},
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
    # RELATIVE TO THE PINNED CLOCK, not to the wall clock. These dates are read by the layer
    # against `Date.now()`, so once the reader's clock became an input (FIXTURE_NOW) a fixture
    # still anchored on the real one was measuring the gap between two different clocks. Same
    # defect as the one this module is about, one layer in.
    import datetime as _dt
    at = (_dt.datetime.strptime(FIXTURE_NOW, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)
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


# ═════════════════════════════════════════════════════════════════════════════════════════════
# "NOT DUE YET" IS NOT "TRIED AND FAILED" (2026-09-24)
# ═════════════════════════════════════════════════════════════════════════════════════════════
#
# WHAT WAS ON THE LIVE FEED, verbatim from `site/data/tick_heartbeat.json`:
#
#     state                : publishing
#     published_age_seconds: 219926      (61.1h)
#     stale_after_seconds  : 691200      (8 days)
#     queue_depth          : 3
#
# and beside it, in `.publish_gate_state.json`, `episode_failures: 45`,
# `episode_clean_publishes: 0`, `wedge_since` 59 hours earlier. Every publish attempt for two and
# a half days had been refused, and the banner rendered the ORDINARY HEALTHY BRANCH -- because the
# only fault it could name was an age, and at a weekly cadence that age was not due for another
# five days. Nothing on the page was false. Nothing on it was the news, either.
#
# The rendered DOM is the subject (R11): a publisher-failing field that reaches the feed and never
# reaches a sentence is the same defect one layer down.


def _failing_publisher(n=45, secs=59 * 3600.0, cited="dead", state="failing"):
    return {"state": state, "consecutive_failures": n, "failing_for_seconds": secs,
            "clean_publishes_this_episode": 0, "cited_red_at_head": cited}


def _heartbeat_with_publisher(publisher, cp_state="publishing", age_hours=61.1):
    hb = _heartbeat(cp_state, age_hours, as_at_utc="2026-09-21T18:15Z",
                    cadence_seconds=7 * 86400)
    if publisher is not None:
        hb["content_publish"]["publisher"] = publisher
    return hb


def test_the_front_door_reads_as_failing_while_the_publisher_is_failing():
    """THE DEFECT. Cadence not yet due, publisher refusing every attempt for 59 hours."""
    out = render(heartbeat=_heartbeat_with_publisher(_failing_publisher()))

    assert out["state"] == "stale", (
        "a publisher that has failed 45 consecutive attempts renders in the ordinary healthy "
        "state, because the only thing that can make this bar loud is an age eight days out")
    assert "PUBLISHING IS FAILING" in out["text"], out["text"]
    assert "45 attempts" in out["text"], (
        "the reader is told something is wrong without the count that establishes it: "
        "{!r}".format(out["text"]))
    assert "59.0h" in out["text"]
    assert "no live cause" in out["text"], (
        "the publisher cites a red that is DEAD at HEAD -- a failure with no named cause is "
        "worse news than one with a cause, and it is summarised away: {!r}".format(out["text"]))


def test_the_as_at_line_survives_beside_the_failure():
    """THE HALF THAT IS ALREADY RIGHT MUST STAY. The figures ARE from 2026-09-21 and a reader is
    entitled to that date; what was missing beside it is that nothing is coming to replace it.
    MUTATION: render the failure INSTEAD of the as-at sentence and this fires."""
    out = render(heartbeat=_heartbeat_with_publisher(_failing_publisher()))
    assert "Figures as at 2026-09-21 18:15Z" in out["text"], out["text"]
    assert out["text"].index("PUBLISHING IS FAILING") < out["text"].index("Figures as at"), (
        "the refusal reads below the as-at date, so a reader meets the reassuring half first")


def test_a_working_publisher_leaves_the_healthy_banner_alone():
    """R15 NULL CONTROL, and it is the one that matters: without it every test above passes on a
    banner that shouts on every visit, which is a banner nobody reads on the visit it means
    something. Same feed, same eight-day threshold, no open failure episode."""
    out = render(heartbeat=_heartbeat_with_publisher(
        _failing_publisher(n=0, secs=None, cited=None, state="no_open_episode")))

    assert "PUBLISHING IS FAILING" not in out["text"]
    assert out["state"] == "verified"
    assert "Figures as at 2026-09-21 18:15Z" in out["text"]


def test_an_absent_publisher_block_renders_exactly_as_before():
    """THE BACK CATALOGUE AND EVERY OLD FEED. A heartbeat written before this field existed --
    and the one served by any tree that has not restarted its tick -- must not acquire a failure
    claim from an absent field, in either direction."""
    out = render(heartbeat=_heartbeat_with_publisher(None))
    assert "PUBLISHING IS FAILING" not in out["text"]
    assert out["state"] == "verified"


def test_an_unknown_publisher_record_makes_no_claim_either_way():
    """The record is the publisher's SELF-REPORT: believed when it admits failure, worth nothing
    when it cannot be read. `unknown` must not render an alarm -- and must not render a
    reassurance, which is why the content clocks above keep the currency verdict."""
    out = render(heartbeat=_heartbeat_with_publisher(
        {"state": "unknown", "consecutive_failures": None, "failing_for_seconds": None,
         "clean_publishes_this_episode": None, "cited_red_at_head": None}))
    assert "PUBLISHING IS FAILING" not in out["text"]
    assert out["state"] == "verified"


def test_a_failure_with_no_recorded_duration_still_says_it_failed():
    """A MISSING START MUST NOT VETO THE FAILURE. The count is what establishes that attempts
    died; `wedge_since` only says since when, and it is legitimately absent on the first cycle
    of an episode. MUTATION: gate the sentence on the duration and this fires."""
    out = render(heartbeat=_heartbeat_with_publisher(
        _failing_publisher(n=1, secs=None, cited="reproduces")))
    assert out["state"] == "stale"
    assert "the last 1 attempt to publish failed" in out["text"], out["text"]
    assert "over" not in out["text"].split("PUBLISHING IS FAILING")[1].split(".")[0], (
        "a duration clause is rendered from a duration that was never recorded")
    assert "no live cause" not in out["text"], (
        "the publisher cites a red that DOES reproduce -- saying it names no cause is false")


def test_a_reference_page_carries_no_publisher_failure_either():
    """SCOPE, held on the new sentence too. A page that publishes no simulation figure has
    nothing for a failed publish to be about, and the 2026-08-24 ruling is that publishing
    status on such a page is noise that undermines the honest banners elsewhere."""
    out = render(heartbeat=_heartbeat_with_publisher(_failing_publisher()), figures="none")
    assert "PUBLISHING IS FAILING" not in out["text"]
    assert out["state"] == "reference"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# "NO LIVE CAUSE" WAS FALSE WHILE A CAUSE WAS HELD (2026-09-24)
# ═════════════════════════════════════════════════════════════════════════════════════════════
#
# The section above gave the publisher's refusal a sentence. This one is about what that sentence
# said NEXT, and it was wrong the same two ways `publish_freshness._cause_clause` was -- the
# banner is the second composer of one sentence, and it was repaired behind the Python one.
#
# WHAT WAS ON DISK, `.publish_gate_state.json`, 48 consecutive failures open:
#
#     citation_at_head         "not_established"
#     total_red                0
#     liveness_surface_refusal {"cause": "push_never_landed", "git_hash": "18cc753b7...",
#                               "evidence": "... git ls-remote says origin did not advance to
#                                it (push rc=1, origin=bd98ca395, head=6d8d7acf8) ..."}
#
# FIRST DEFECT: on the `dead` reading the banner rendered "The publisher names no live cause for
# it." while an attributed, stamped, hash-keyed cause sat in the next field of the same record.
#
# SECOND DEFECT, louder and fired less often: the clause was keyed to `dead` ALONE, and
# `not_established` is what the citation field says whenever no red is named at all -- i.e. on
# every push failure, provenance refusal and behind-origin refusal. On all of those the banner
# said nothing about cause in either direction.


def _held(cause="push_never_landed", git_hash="18cc753b76bccf07c65cf7e7178d066d9c248dac"):
    return {"field": "liveness_surface_refusal", "cause": cause, "git_hash": git_hash,
            "evidence": "the commit was created here and `git ls-remote` says origin did not "
                        "advance to it (push rc=1, origin=bd98ca395, head=6d8d7acf8)",
            "label": "Liveness heartbeat", "ts": 1790253554.99, "age_seconds": 800.2}


def _publisher_holding(cause_held, cited="dead"):
    p = _failing_publisher(n=48, secs=64.2 * 3600.0, cited=cited)
    p["held_refusal"] = cause_held
    p["held_refusal_reason"] = "" if cause_held else "liveness_surface_refusal is empty"
    return p


def test_a_dead_citation_beside_a_held_cause_names_the_cause_on_the_page():
    """THE SENTENCE THAT WAS FALSE, in the rendered DOM. MUTATION: restore
    `p.cited_red_at_head === "dead" ? " The publisher names no live cause for it." : ""` and
    both assertions fire."""
    out = render(heartbeat=_heartbeat_with_publisher(_publisher_holding(_held())))

    assert "push_never_landed" in out["text"], (
        "the record holds an attributed cause and the page says nothing about it: "
        "{!r}".format(out["text"]))
    assert "no live cause" not in out["text"], (
        "a cause WAS in hand -- telling a reader there is none sends them to look for "
        "something nobody has, which is how the real blocker went unnamed for three hours")


def test_a_citation_that_was_never_established_names_the_held_cause_too():
    """THE LOUDER DEFECT. `not_established` is the reading on EVERY push failure, provenance
    refusal and behind-origin refusal, and the old clause rendered nothing at all on it.

    MUTATION: narrow the branch back to `cited_red_at_head === "dead"` and this fires while the
    test above still passes. That pair IS the defect's shape.
    """
    out = render(heartbeat=_heartbeat_with_publisher(
        _publisher_holding(_held(), cited="not_established")))

    assert "push_never_landed" in out["text"] and "18cc753b7" in out["text"], (
        "the cause and the commit it is about must both reach the page -- a cause a reader "
        "cannot go and check is an unfalsifiable attribution: {!r}".format(out["text"]))


def test_every_citation_reading_but_reproduces_reaches_a_cause_sentence():
    """THE LEG THAT WOULD HAVE CAUGHT THIS, asserted over the WHOLE field rather than one
    branch. A clause that answered on `dead` and fell silent on `not_established` passes every
    per-branch control, which is exactly how this survived.

    `reproduces` is swept in as the one reading that must NOT gain the sentence, so the
    partition is asserted DISTINCT and not merely covered -- a version that rendered the cause
    unconditionally fails this, and so does one that rendered it never.

    MUTATION: drop any single reading from the branch and this fires naming it.
    """
    named, silent = [], []
    for reading in ("dead", "not_asked", "not_established", "reproduces", None):
        out = render(heartbeat=_heartbeat_with_publisher(
            _publisher_holding(_held(), cited=reading)))
        (named if "push_never_landed" in out["text"] else silent).append(reading)

    assert silent == ["reproduces"], (
        "only a citation that re-ran at HEAD and is still red is an answer in itself; every "
        "other reading leaves the question open and must go to the held cause. Silent "
        "on: {}".format(silent))
    assert len(named) == 4


def test_a_reproducing_citation_keeps_the_page_pointed_at_the_blocking_list():
    """The rare branch asserted REACHABLE, then asserted about. MUTATION: delete the
    `reproduces` early return and this fires -- two named causes for one fault give a reader
    two places to look, and the health page already carries the blocking list."""
    out = render(heartbeat=_heartbeat_with_publisher(
        _publisher_holding(_held(), cited="reproduces")))

    assert "PUBLISHING IS FAILING" in out["text"], (
        "the branch is not reachable at all, so what it renders is not yet a question")
    assert "push_never_landed" not in out["text"] and "no live cause" not in out["text"]


def test_with_nothing_held_the_page_still_says_no_live_cause():
    """THE ORIGINAL CLAUSE'S POINT IS KEPT. A failure with no named cause is worse news than one
    with a cause, and suppressing that to avoid an awkward sentence would be the opposite
    failure. MUTATION: return "" when nothing is held and this fires."""
    out = render(heartbeat=_heartbeat_with_publisher(_publisher_holding(None)))

    assert "no live cause" in out["text"], out["text"]


def test_the_state_files_internal_field_names_do_not_reach_the_page():
    """SCOPE, over BOTH ARMS of the branch. `held_refusal_reason` names internal fields of
    `.publish_gate_state.json` -- useful in a log line a seat reads, noise on a page a customer
    may read. The page gets the FACT; `publish_freshness.describe()` gets the fields.

    MUTATION: render `p.held_refusal_reason` into EITHER arm and this fires.

    WRITTEN THIS WAY BECAUSE THE FIRST VERSION COULD NOT FAIL. It exercised only the
    nothing-held arm, and the mutation that leaks the reason lands naturally in the OTHER one --
    the arm that composes a sentence is the arm a leak gets appended to. It went green on a
    live defect. In production `held_refusal_reason` is "" whenever a cause is held, so the
    leak would have rendered nothing and been invisible until the day that changed: keyed to
    the property (no internal field name reaches a reader, on any path), never to today's
    emptiness.
    """
    for held in (_held(), None):
        p = _publisher_holding(held)
        p["held_refusal_reason"] = "the publisher held liveness_surface_refusal is empty"
        out = render(heartbeat=_heartbeat_with_publisher(p))

        assert "liveness_surface_refusal" not in out["text"], (
            "an internal state-file field name is rendered to a reader with held={!r}: "
            "{!r}".format(bool(held), out["text"]))


def test_a_held_cause_with_no_readable_commit_still_names_the_cause():
    """Each clause is DROPPED rather than guessed when its value is missing -- the same rule the
    count and duration clauses above follow. MUTATION: gate the whole sentence on the hash and
    this fires: the cause is the news, the commit is the corroboration."""
    out = render(heartbeat=_heartbeat_with_publisher(
        _publisher_holding(_held(git_hash=None))))

    assert "push_never_landed" in out["text"]
    assert "at commit" not in out["text"], (
        "a commit clause rendered from a hash that was never recorded")
