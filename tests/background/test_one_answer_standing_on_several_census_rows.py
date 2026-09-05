"""THE DEFECT: one loader answer stood verbatim on TWELVE rows of the self-clearing-alarm census
and every rung was green (2026-09-05).

`_scope_of_resemblance` and its re-audit were built against a reason that CITES the sibling it was
graded from -- "same shape as X", "same reasoning as run_history.json". They are blind to the
inheritance that does not cite. The sentence "ASKED AND CLEAN -- measured across the whole
partition ... no state raises and none is a read-modify-write" stood on twelve rows, through the
resemblance re-audit that ran the same day (that pass swept `why`; this was in `loader`), and
`unasked_loader_rows()` -- the rung that made the field mandatory -- asks only that it be non-empty.

Re-opened against the twelve carriers: "no state raises" true of all twelve, "none is a
read-modify-write" false of three, and "CLEAN" answering a different question from the one
`_scope_of_benign` commissioned the field for. No verdict moved, which is precisely why nothing
would ever have re-asked them.

These tests key to the PROPERTY -- one claim, one row -- and never to today's twelve sentences, so
they stay meaningful after the register is repaired and fire on the thirteenth copy of anything.
"""
from __future__ import annotations

import json

import pytest

from background import self_clearing_alarm_census as census

# Long enough to clear MIN_CLAIM_CHARS, and deliberately NOT one of the sentences the 2026-09-05
# sweep found: a rung keyed to today's answer would pass this test while missing the next copy.
INVENTED_CLAIM = ("Its loader answers the absent question and the unreadable question with one "
                  "value, and the writer never rebuilds the record from it.")
ALSO_INVENTED = ("Every unreadable member of the partition returns the empty mapping without "
                 "raising, and the caller treats that as a clean prior.")


def _doc(rows, declared=None):
    out = {"dispositions": rows}
    if declared is not None:
        out[census.PROVENANCE_SECTION] = {"sentences": declared}
    return out


def test_one_claim_on_two_rows_is_refused_and_the_refusal_names_both_rows():
    """THE RUNG. Two carriers cannot both have been opened if one sentence answers for both."""
    refusals = census.shared_loader_answers(_doc({
        "a.json": {"verdict": "benign", "loader": INVENTED_CLAIM},
        "b.json": {"verdict": "benign", "loader": INVENTED_CLAIM},
    }))
    assert len(refusals) == 1
    # Naming BOTH rows is the whole use of the refusal -- "something is duplicated" is not
    # actionable, and a refusal that cites nothing is the shape this file exists to refuse.
    assert "a.json" in refusals[0] and "b.json" in refusals[0]
    assert census.PROVENANCE_SECTION in refusals[0]


def test_the_same_claim_in_why_and_in_loader_is_caught_in_both_fields():
    """The 2026-09-05 copy was in `loader` and survived a re-audit that swept `why`. Neither field
    is the privileged one -- both carry claims about one carrier."""
    assert census.shared_loader_answers(_doc({
        "a.json": {"why": INVENTED_CLAIM},
        "b.json": {"why": INVENTED_CLAIM},
    }))
    # ...and ACROSS the two fields, which is how a copied answer hides from a per-field sweep.
    assert census.shared_loader_answers(_doc({
        "a.json": {"why": INVENTED_CLAIM},
        "b.json": {"loader": INVENTED_CLAIM},
    }))


def test_one_row_keeping_its_own_claim_is_not_refused():
    """The negative direction of the same partition: the rung must not fire on a register that is
    doing the right thing, or it is a rung nobody can satisfy and someone deletes it."""
    assert census.shared_loader_answers(_doc({
        "a.json": {"loader": INVENTED_CLAIM},
        "b.json": {"loader": ALSO_INVENTED},
    })) == []


def test_a_declared_provenance_sentence_may_stand_on_many_rows():
    """THE EXEMPTION BRANCH, and it is load-bearing rather than a hole: `Control: tests/...` and
    "RESTORED 2026-09-05 ..." genuinely ARE the same fact about many rows. Without this branch the
    rung refuses the honest register and gets deleted. Declaring a line is the act of saying out
    loud "this is provenance, not an answer" -- the judgement the twelve-row sentence skipped."""
    rows = {"a.json": {"loader": INVENTED_CLAIM}, "b.json": {"loader": INVENTED_CLAIM}}
    assert census.shared_loader_answers(_doc(rows, declared=[INVENTED_CLAIM[:40]])) == []
    # A PREFIX, so a citation with a trailing clause does not need re-declaring...
    assert census.shared_loader_answers(_doc(
        {"a.json": {"loader": INVENTED_CLAIM + " And a tail."},
         "b.json": {"loader": INVENTED_CLAIM + " And another."}},
        declared=[INVENTED_CLAIM[:40]])) == []
    # ...but the declaration must MATCH. A stale entry must not blanket-exempt the register, which
    # is the fail-open shape an allowlist invites.
    assert census.shared_loader_answers(_doc(rows, declared=["Some other sentence entirely."]))


def test_the_live_registers_allowlist_is_reachable_and_load_bearing():
    """ASSERT THE RARE BRANCH CAN BE TAKEN, over the whole partition rather than one leg per side.
    A declared exemption that exempts NOTHING is a dead branch that would pass every test above
    while the rung was really running unexempted -- and a rung that is green because its subject is
    empty is this project's most-repeated control failure.

    Keyed to the PROPERTY, not to today's answer: it asserts the live register needs its allowlist
    and is clean with it, never that the count is any particular number."""
    live = json.loads(census.DISPOSITIONS_PATH.read_text())
    assert census.shared_loader_answers(live) == [], (
        "the live register carries an answer standing on more than one row")
    stripped = {k: v for k, v in live.items() if k != census.PROVENANCE_SECTION}
    assert census.shared_loader_answers(stripped), (
        "the allowlist exempts nothing, so the exemption branch above is never taken and the "
        "green above is not evidence the rung ran")


def test_a_null_field_does_not_fall_open():
    """`str(None)` is "None", truthy, and the slip the older rungs carry `or ""` to close.

    HONEST NOTE ON WHAT HOLDS THIS UP: mutating `or ""` out of `_claim_sentences` does NOT fail
    this test, and the reason is an equivalence, not a gap -- "None" is four characters and
    MIN_CLAIM_CHARS drops it anyway. So this test is keyed to the OUTCOME (a null field cannot
    manufacture a shared claim) and is deliberately indifferent to which of the two mechanisms
    delivers it. Also: a row that is not a mapping is skipped, never a crash."""
    assert census.shared_loader_answers(_doc({
        "a.json": {"loader": None, "why": None},
        "b.json": {"loader": None, "why": None},
    })) == []
    assert census.shared_loader_answers(_doc({"a.json": "not a mapping", "b.json": None})) == []


def test_a_short_repeated_phrase_is_not_a_finding():
    """A floor on noise. Below MIN_CLAIM_CHARS a repeat is a turn of phrase, not a claim -- and a
    rung that reds on "Nothing raises." is a rung that trains its reader to ignore it."""
    short = "Nothing raises here."
    assert len(short) < census.MIN_CLAIM_CHARS
    assert census.shared_loader_answers(_doc({
        "a.json": {"loader": short}, "b.json": {"loader": short},
    })) == []


def test_an_unreadable_register_does_not_fabricate_a_refusal():
    """FAIL TOWARD WORK WITHOUT DOUBLE-REPORTING. An unreadable register is already
    `load_dispositions()`'s refusal -- it returns {}, every hit goes undispositioned and --check is
    RED. Reporting the same fault twice here would put a shared-answer refusal on a register nobody
    could read, which is a refusal naming a cause that is not the cause."""
    assert census.shared_loader_answers({"dispositions": "not a mapping"}) == []
    assert census.shared_loader_answers("not a document") == []


def test_the_rung_is_wired_into_check_and_not_merely_importable():
    """A rung that is correct and unreferenced is a rung that never runs. Mutating `main()`'s
    `or shared` must fail something, or the whole control survives on an import."""
    census_stub = {
        "functions_scanned": 5000,
        "state_paths": {"x.json": {"writers": ["m::w"], "readers": ["m::r"], "hit": True}},
        "hits": ["x.json"],
    }
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(census, "derive", lambda *a, **k: census_stub)
        mp.setattr(census, "load_dispositions",
                   lambda *a, **k: {"x.json": {"verdict": "benign", "why": "w", "loader": "l"}})
        mp.setattr(census, "undispositioned", lambda *a, **k: [])
        mp.setattr(census, "unguarded_real_hits", lambda *a, **k: [])
        mp.setattr(census, "eroded_dispositions", lambda *a, **k: [])
        mp.setattr(census, "unasked_loader_rows", lambda *a, **k: [])
        mp.setattr(census, "removed_dispositions", lambda *a, **k: [])
        mp.setattr("sys.argv", ["self_clearing_alarm_census", "--check"])

        mp.setattr(census, "shared_loader_answers", lambda *a, **k: [])
        assert census.main() == 0, "every other rung is stubbed clean, so this must be green"

        mp.setattr(census, "shared_loader_answers", lambda *a, **k: ["a.json, b.json share a claim"])
        assert census.main() == 1, "the shared-answer rung does not reach --check's exit code"
