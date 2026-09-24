"""THE SUMMARY SAID `unattributed` WHILE THE ANSWER SAT IN THE NEXT FIELD OF THE SAME FILE.

THE DEFECT, verbatim off `docs/observability/.publish_gate_state.json` on 2026-09-24
-------------------------------------------------------------------------------------
    episode_failures          48
    citation_at_head          "not_established"
    citation_at_head_reason   "no red is named on this failure, so there is no citation to
                               re-ask. This is not evidence that HEAD is green."
    total_red                 0
    liveness_surface_refusal  {"cause": "push_never_landed",
                               "git_hash": "18cc753b76bccf07c65cf7e7178d066d9c248dac",
                               "evidence": "the commit was created here and `git ls-remote` says
                                origin did not advance to it (push rc=1, origin=bd98ca395,
                                head=6d8d7acf8) -- read the REF and not the push's own rc ..."}

`publish_freshness.describe()` is the line quoted into the delivery brief and the deadman's log.
Against that record it said nothing whatever about cause, because its one cause clause was keyed
to `citation_at_head == "dead"`. Three hours earlier, against the same file in its `dead` state,
it had said the other half of the defect out loud:

    "the red it cites is DEAD at HEAD, so the cause is unattributed"

which was FALSE in the direction that matters. A cause was held — attributed, stamped and
hash-keyed — two keys away in the same record. A module that exists to say why a publish did not
happen was the reason a human had to run pytest by hand to find out.

WHAT THESE CONTROLS ARE KEYED TO
---------------------------------
The PROPERTY, never today's vocabulary: *the summary of a failing publisher either names a cause
it is holding, or says which fields it held and why they were not enough.* There is no third
outcome, and `test_no_reading_of_the_citation_field_reaches_a_bare_unattributed` is the leg that
says so over the whole partition rather than one branch at a time — a clause that answered
correctly on `dead` and fell silent on `not_established` is exactly how this survived, and a
per-branch control would have passed throughout.
"""
from __future__ import annotations

import json

import pytest

from background import publish_cause
from background import publish_freshness as pf

#: The live record's shape, at the numbers it was observed at. `now` is the reader's clock.
NOW = 1_000_000.0
_LIVE_EVIDENCE = ("the commit was created here and `git ls-remote` says origin did not advance "
                  "to it (push rc=1, origin=bd98ca395, head=6d8d7acf8) -- read the REF and not "
                  "the push's own rc, which is the 3.5-hour origin-freeze of 2026-07-24")


def _refusal(cause="push_never_landed", ts=NOW - 800.0, git_hash="18cc753b76bccf07c65cf7e7178d0",
             evidence=_LIVE_EVIDENCE, label="Liveness heartbeat"):
    return {"cause": cause, "evidence": evidence, "git_hash": git_hash, "label": label, "ts": ts}


def _gate_state(tmp_path, **fields):
    """A `.publish_gate_state.json` in a SANDBOX — never the real one, which `production_surface
    _guard` names as manufacturing the evidence that zeroes `episode_failures`."""
    p = tmp_path / ".publish_gate_state.json"
    p.write_text(json.dumps(fields))
    return p


def _summary(tmp_path, monkeypatch, **fields):
    """The one line a reader actually gets, for a publisher in an open failing episode."""
    fields.setdefault("episode_failures", 48)
    fields.setdefault("episode_clean_publishes", 0)
    fields.setdefault("wedge_since", NOW - 64.2 * 3600)
    monkeypatch.setattr(pf, "PUBLISH_GATE_STATE_FILE", _gate_state(tmp_path, **fields))
    monkeypatch.setattr(pf, "last_published_ts", lambda: NOW - 66.6 * 3600)
    monkeypatch.setattr(pf, "last_committed_ts", lambda **k: NOW - 66.6 * 3600)
    return pf.describe(pf.snapshot(now=NOW))


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE TWO LIVE INSTANCES
# ═════════════════════════════════════════════════════════════════════════════════════════════

def test_a_dead_citation_does_not_report_unattributed_while_a_cause_is_held(tmp_path, monkeypatch):
    """THE SENTENCE THAT WAS FALSE. `citation_at_head: "dead"` beside a live refusal record, and
    the summary said the cause was unattributed.

    MUTATION: restore the old clause — `" and the red it cites is DEAD at HEAD, so the cause is
    unattributed" if pub.get("cited_red_at_head") == "dead" else ""` — and this fires on both
    assertions.
    """
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead",
                    liveness_surface_refusal=_refusal())

    assert "push_never_landed" in line, (
        "the record holds an attributed cause and the summary did not name it -- this is the "
        "false negative the module exists to stop, not a missing feature")
    assert "unattributed" not in line, (
        "a cause was in hand; saying otherwise sends the reader to look for something nobody "
        "has, which is how the real blocker went unnamed for three hours")


def test_a_citation_that_was_never_established_names_the_held_cause_too(tmp_path, monkeypatch):
    """THE LOUDER DEFECT, which fired LESS often and so was noticed second. `not_established` is
    what the citation field says whenever no red is named at all — i.e. on EVERY push failure,
    provenance refusal and behind-origin refusal. The old clause was keyed to `dead`, so on all
    of those the summary said nothing about cause in either direction.

    MUTATION: narrow `_cause_clause`'s branch back to `cited == "dead"` and this fires while
    the test above still passes. That pair IS the defect's shape.
    """
    line = _summary(tmp_path, monkeypatch, citation_at_head="not_established", total_red=0,
                    blocking_tests=[], liveness_surface_refusal=_refusal())

    assert "push_never_landed" in line and "liveness_surface_refusal" in line, (
        "the summary must name the cause AND the field it came from -- 'where it came from' is "
        "the fact whose absence let this survive, because nobody knew there was a second field")
    assert "18cc753b7" in line, (
        "a cause without its commit cannot be checked by the reader, and an unfalsifiable "
        "attribution is the failure mode this module's `read_cause` already refuses")


def test_the_evidence_travels_with_the_cause(tmp_path, monkeypatch):
    """A cause NAME alone sends a reader to the right family and not to the right repair:
    `push_never_landed` and `lost_push_race` are a push to be MADE and a race to be WON, and for
    58 cycles this repo filed one as the other. The observation that separates them is in the
    evidence line.

    MUTATION: drop the evidence from the format string and this fires.
    """
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead",
                    liveness_surface_refusal=_refusal())

    assert "git ls-remote" in line and "push rc=1" in line, (
        "the evidence line holds the OBSERVATION that decided the cause; without it the reader "
        "has a label and no way to act on or refute it")


def test_a_quoted_evidence_line_that_was_cut_says_so(tmp_path, monkeypatch):
    """MUTATION: drop the `[...]` marker and this fires. A quote cut with no marker reads as a
    corrupt record, and a reader who believes the record is corrupt does not go and read the
    rest of it."""
    long_evidence = "x" * (pf.HELD_EVIDENCE_QUOTED_CHARS + 50)
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead",
                    liveness_surface_refusal=_refusal(evidence=long_evidence))

    assert "[...]" in line
    assert "x" * (pf.HELD_EVIDENCE_QUOTED_CHARS + 1) not in line, (
        "the bound is not being applied at all, so a 900-char evidence line lands whole in a "
        "one-line summary")


def test_an_over_budget_quote_keeps_the_END_of_the_evidence(tmp_path, monkeypatch):
    """A HOOK CHAIN PRINTS ITS REFUSAL LAST, so the head of its output is every gate that
    PASSED. `_refusal_evidence_kept` keeps the last 900 characters for exactly that reason,
    measured at 31 consecutive failures reading `unattributed` while the answer sat in the
    dropped tail — and this clause's first version quoted the HEAD of that kept tail, putting
    the elision marker and two green gates on the line where the verdict belongs.

    MUTATION: take `[:N]` instead of `[-N:]` and this fires.
    """
    kept_tail = ("[...earlier output dropped; this is the TAIL...]\n"
                 + "[test-gate] OK all targeted tests green\n" * 20
                 + "FAILED site/test_a_here_relative_pointer_has_one_home.py::test_one_home")
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead",
                    liveness_surface_refusal=_refusal(evidence=kept_tail))

    assert "test_one_home" in line, (
        "the verdict is the LAST thing a hook chain prints and it was dropped -- this is the "
        "defect `_refusal_evidence_kept` already paid for, re-entered one layer up")
    assert "earlier output dropped" not in line, (
        "the quote is showing the writer's own elision marker instead of the evidence")


def test_a_multi_line_evidence_is_flattened_to_one_line(tmp_path, monkeypatch):
    """`describe()` returns ONE human line for a page, a banner or a log — the whole module
    docstring rests on that. Hook output is multi-line, so quoting it raw would break every
    consumer that reads a line at a time.

    MUTATION: drop the whitespace collapse and this fires.
    """
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead",
                    liveness_surface_refusal=_refusal(evidence="rc=1\nFAILED tests/x.py::test_y"))

    assert "\n" not in line, "the one-line summary is no longer one line: {!r}".format(line)
    assert "FAILED tests/x.py::test_y" in line


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE OTHER HALF OF THE CONTRACT: SAY WHAT YOU HELD
# ═════════════════════════════════════════════════════════════════════════════════════════════

def test_with_no_usable_record_the_summary_names_the_fields_it_held(tmp_path, monkeypatch):
    """`unattributed` is this module's most valuable answer and it must still be reachable — but
    only WITH its working. An empty latch and an absent one are different facts.

    MUTATION: return a bare `" so the cause is unattributed"` with no reason and this fires.
    """
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead", liveness_surface_refusal=None)

    assert "unattributed" in line, (
        "nothing was held, so `unattributed` is the honest answer and suppressing it here would "
        "be the opposite failure")
    assert "liveness_surface_refusal" in line and "empty" in line, (
        "the reader is owed which inputs were consulted -- otherwise 'unattributed' is "
        "indistinguishable from 'nobody looked', which is what it actually meant on 2026-09-24")


def test_a_state_with_no_refusal_field_at_all_says_that_and_not_that_head_is_green(
        tmp_path, monkeypatch):
    """FAIL-CLOSED WORDING. MUTATION: shorten the sentence to "no cause recorded" and this fires
    — silence about a cause is not evidence there was none, and this module has paid for that
    inversion on `red_at_head_reason` and `citation_at_head_reason` already."""
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead")

    assert "NOT evidence" in line, (
        "a summary that reports an absent record without saying what the absence does not prove "
        "will be read as an all-clear")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE PARTITION — over the WHOLE field, not one branch at a time
# ═════════════════════════════════════════════════════════════════════════════════════════════

def test_no_reading_of_the_citation_field_reaches_a_bare_unattributed(tmp_path, monkeypatch):
    """THE LEG THAT WOULD HAVE CAUGHT THIS. Every reading the citation field can hold, against a
    record that IS holding a cause — and the property asserted over all of them at once.

    Written this way because a per-branch control is what failed: the clause answered correctly
    on `dead`, fell silent on `not_established`, and no test asked the two together. `reproduces`
    is in the sweep as the one reading that must NOT gain a cause clause, so the partition is
    asserted DISTINCT rather than merely covered — a version that returned "" for everything
    would pass a coverage-shaped control and fail this one.

    MUTATION: make `_cause_clause` return "" for any single reading and this fires naming it.
    """
    holds_cause, silent = [], []
    for reading in ("dead", "not_asked", "not_established", "reproduces", None, "a_new_word"):
        line = _summary(tmp_path, monkeypatch,
                        **({"citation_at_head": reading} if reading is not None else {}),
                        liveness_surface_refusal=_refusal())
        (holds_cause if "push_never_landed" in line else silent).append(reading)

    assert silent == ["reproduces"], (
        "every reading that does NOT answer 'why did this publish fail' must go and look at the "
        "refusal record; only `reproduces` is an answer in itself. Silent on: {}".format(silent))
    assert len(holds_cause) == 5, (
        "the branches collapsed -- {} readings reached the cause clause".format(len(holds_cause)))


def test_a_reproducing_citation_is_left_alone(tmp_path, monkeypatch):
    """The rare branch asserted REACHABLE and then asserted about, in that order. A citation that
    re-ran at HEAD and is still red IS the answer; adding a second cause beside it would give the
    reader two places to look for one fault.

    MUTATION: drop the `CITATION_ANSWERS` early return and this fires.
    """
    line = _summary(tmp_path, monkeypatch, citation_at_head="reproduces",
                    blocking_tests=["tests/x.py::test_y"], total_red=1,
                    liveness_surface_refusal=_refusal())

    assert "PUBLISHER REFUSING" in line, (
        "the branch is not reachable at all, so what it does is not yet a question")
    assert "push_never_landed" not in line and "unattributed" not in line


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE READER'S OWN SCREENS — each one fails closed
# ═════════════════════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("field,record,why", [
    ("liveness_surface_refusal", _refusal(cause="gremlins"), "an unrecognised cause"),
    ("liveness_surface_refusal", _refusal(ts=None), "no readable stamp"),
    ("liveness_surface_refusal", _refusal(ts=True), "a bool, which reads as 1970 numerically"),
    ("liveness_surface_refusal", _refusal(ts=float("nan")), "NaN, which defeats an age bound"),
    ("liveness_surface_refusal", _refusal(ts=NOW - 10 * 3800), "a stamp past the age bound"),
])
def test_an_unusable_refusal_record_is_refused_rather_than_cited(field, record, why):
    """MUTATION: drop any one screen in `held_refusal` and its row here fires. Each is a separate
    way for a record about a DIFFERENT cycle to be presented as this one's cause — the
    carried-forward-blocking-list defect arriving through a new field name."""
    held, reason = publish_cause.held_refusal({field: record}, now=NOW)

    assert held is None, "cited a record carrying {}".format(why)
    assert field in reason, "refused it without saying which field was held or why"


def test_a_refusal_its_own_surface_has_since_published_past_is_not_cited(tmp_path, monkeypatch):
    """THE RETIREMENT SCREEN. `liveness_surface_refusal` is a latch cleared by
    `_record_liveness_surface_publish`; a latch that fails to clear would have this function
    naming a surface that has since recovered. The two stamps are compared rather than the
    clearing being assumed.

    MUTATION: delete the `cleared >= recorded` screen and this fires.
    """
    line = _summary(tmp_path, monkeypatch, citation_at_head="dead",
                    liveness_surface_refusal=_refusal(ts=NOW - 3000.0),
                    liveness_surface_last_publish={"ts": NOW - 600.0, "git_hash": "abc123def",
                                                   "label": "Liveness heartbeat"})

    assert "push_never_landed" not in line, (
        "that surface published AFTER the refusal, so the refusal describes a cycle that closed")
    assert "retired" in line, (
        "and the reader must be told that is why, or they will assume nothing was looked at")


def test_the_newest_of_several_live_refusals_is_the_one_cited():
    """A dict ordering is not a clock. MUTATION: `min` for `max` (or take the first survivor)
    and this fires — citing the older of two live refusals is the carried-forward defect again,
    reached by a route the age bound cannot see because BOTH records are in date."""
    held, _ = publish_cause.held_refusal({
        "liveness_surface_refusal": _refusal(cause="push_never_landed", ts=NOW - 4000.0),
        "content_surface_refusal": _refusal(cause="behind_origin", ts=NOW - 100.0),
    }, now=NOW)

    assert held is not None and held["cause"] == "behind_origin", (
        "the newer refusal is the one this publisher is stopped on now")
    assert held["field"] == "content_surface_refusal"


def test_the_scan_is_by_suffix_so_a_new_surface_is_read_the_day_it_is_written():
    """KEYED TO THE PROPERTY, not to today's one field. MUTATION: hard-code
    `state.get("liveness_surface_refusal")` and this fires.

    The defect being repaired is that nobody remembered to look in the field beside the one they
    read; a hard-coded list would need remembering again on the day the second surface starts
    recording refusals, which is the same bet that just lost.
    """
    held, _ = publish_cause.held_refusal(
        {"some_future_surface_refusal": _refusal(cause="deadline_kill")}, now=NOW)

    assert held is not None and held["cause"] == "deadline_kill"
    assert held["field"] == "some_future_surface_refusal"


def test_a_publish_record_is_never_mistaken_for_a_refusal():
    """`liveness_surface_last_publish` carries a nested `cleared_refusal` — a RETIRED record, by
    construction. MUTATION: scan nested dicts, or match on the presence of a `cause` key rather
    than on the field suffix, and this fires: the summary would cite the very refusal the publish
    resolved."""
    held, reason = publish_cause.held_refusal({
        "liveness_surface_last_publish": {"ts": NOW - 100.0, "git_hash": "aff39ff16",
                                          "cleared_refusal": _refusal(ts=NOW - 200.0)},
    }, now=NOW)

    assert held is None, "cited a refusal that a recorded publish had already cleared"
    assert "no refusal record at all" in reason
