"""THE REGISTER'S LOW-WATER MARK — `removed_dispositions()`.

The defect each test names is a row that left the register itself. Every other rung iterates
either the hits or the rows, so a key in NEITHER is the subject of nothing: the register is the
high-water mark `eroded_dispositions()` rests its whole non-tautology argument on, and until
2026-09-05 nothing stopped the mark from falling.

The sharpest leg is `test_the_removal_check_sees_WHAT_THE_OTHER_FIVE_RUNGS_CANNOT` — the replay of
the measurement that motivated this, filed as a pre-registration before it was run.
"""

from __future__ import annotations

import json

import pytest

from background import self_clearing_alarm_census as census

_ROW = {"verdict": "benign", "why": "a latest-value watermark", "loader": "answered"}


@pytest.fixture
def live():
    return census.derive()


# ── the control itself ──


def test_a_row_that_left_the_register_without_a_reason_is_refused():
    """The whole point. MUTATION: return [] for a key absent from `dispositions` and this fires.

    The refusal now names its REGISTER as well as its key, because the shared mechanism this rung
    was re-pointed at on 2026-09-05 also speaks for the class register, the canon and the maturity
    map, and a line in a mixed report that names no register is a line a reader cannot act on.
    Asserted as both facts rather than as a `startswith` on the key: the old assertion was keyed to
    today's formatting, and the property is that the line identifies WHICH ROW OF WHICH REGISTER.
    """
    out = census.removed_dispositions({}, {}, baseline={"gone.json": _ROW})
    assert len(out) == 1
    assert out[0].startswith(census.REGISTER_REL_PATH + ":"), out[0]
    assert "gone.json" in out[0]
    assert "was in the register at HEAD and is not in it now" in out[0]


def test_a_row_still_in_the_register_is_not_a_removal():
    """The negative leg. Without it a control that refuses EVERYTHING passes every test above."""
    assert census.removed_dispositions({"s.json": _ROW}, {}, baseline={"s.json": _ROW}) == []


def test_a_removal_is_admitted_ONLY_WHEN_retired_SAYS_WHY():
    """The leg that stops this being keyed to today's answer rather than to the property.

    A carrier genuinely deleted from the tree SHOULD be removable, or this control goes red
    precisely when the code becomes more honest — this project's named backwards-control shape.
    The escape hatch is authored, in git, and reviewable, exactly like `declassified` one rung
    over.
    """
    assert census.removed_dispositions(
        {}, {"gone.json": "carrier deleted in abc1234; the module it belonged to is gone"},
        baseline={"gone.json": _ROW}) == []


@pytest.mark.parametrize("reason", ["", "   ", None])
def test_an_EMPTY_OR_NULL_retired_reason_does_not_open_the_hatch(reason):
    """`str(None)` is "None", which is TRUTHY: a `_retired` entry carrying an explicit JSON null
    would satisfy a naive truth test and the mandatory-reason requirement falls open. The same
    slip was live in two sibling rungs until 2026-09-05, so the new hatch is born with the
    treatment. MUTATION: drop the `or ""` and the None case survives."""
    out = census.removed_dispositions({}, {"gone.json": reason}, baseline={"gone.json": _ROW})
    assert len(out) == 1, "an unreasoned removal must not be admitted, whatever shape the null is"


def test_an_UNESTABLISHABLE_baseline_is_a_REFUSAL_not_a_clean_result(monkeypatch):
    """`_dispositions_at_head()` returns None, never {}, and the two are opposite claims.

    {} would say "HEAD's register was empty, so nothing can have been removed" and report CLEAN on
    every tree where git is unavailable — the fail-silent shape. Demand a refusal, not a zero.
    MUTATION: make the None branch return [] and this fires.
    """
    monkeypatch.setattr(census, "_dispositions_at_head", lambda: None)
    out = census.removed_dispositions({}, {})
    assert len(out) == 1 and "could not be established" in out[0]
    assert "refusal, not a clean result" in out[0]


# ── the replay: what motivated the rung ──


def _synthetic(paths: dict, hits: list) -> dict:
    return {"functions_scanned": 999, "state_paths": paths, "hits": hits}


def test_the_removal_check_sees_WHAT_THE_OTHER_FIVE_RUNGS_CANNOT():
    """THE MEASUREMENT, REPLAYED — pre-registered 2026-09-05 before it was run, and not refuted.

    A row and its hit leave TOGETHER, which is what any sweep that stops a path being seen looks
    like once somebody tidies the register to match. The path is still fully visible — written and
    read — so this is not even the census going blind; the subject has simply left the class with
    nobody holding a record that it was ever in it.

    If this test ever passes with the new rung removed, the rung is redundant and should go.
    """
    # The class KEEPS its other members, as it did on the live tree (49 of 50 survived): a census
    # emptied entirely is a different failure and `census_is_vacuous` already refuses it. The
    # erosion this rung is for takes ONE subject out of a class that still looks healthy.
    cen = _synthetic({"s.json": {"writers": ["a::f"], "readers": ["a::g"]},
                      "live.json": {"writers": ["a::f"], "readers": ["a::g"]}}, ["live.json"])
    baseline = {"s.json": _ROW, "live.json": _ROW}
    disp = {"live.json": _ROW}          # the victim's row went with its hit

    assert census.undispositioned(cen, disp) == []
    assert census.unguarded_real_hits(cen, disp) == []
    assert census.eroded_dispositions(cen, disp) == []
    assert census.unasked_loader_rows(cen, disp) == []
    assert census.census_is_vacuous(cen) is None
    assert census.removed_dispositions(disp, {}, baseline=baseline), (
        "the erosion that motivated this rung is invisible to all five of the others")


def test_deleting_the_row_no_longer_CURES_the_erosion_refusal():
    """THE SECOND-ORDER SHAPE. `eroded_dispositions()` refuses a row whose path the census can no
    longer resolve — so before this rung, DELETING that row cleared its own refusal. A red
    clearable by deleting the evidence is a fail-open with an extra step.

    MUTATION: give `removed_dispositions` the tempting "allow it if the census no longer resolves
    the path" exception and this fires — which is exactly why that exception is not there.
    """
    baseline = {"gone.json": _ROW}
    # With the row present, the erosion rung refuses: the census cannot resolve the path.
    assert census.eroded_dispositions(_synthetic({}, []), baseline)
    # Delete the row to clear it — and the removal rung picks the subject straight back up.
    assert census.eroded_dispositions(_synthetic({}, []), {}) == []
    assert census.removed_dispositions({}, {}, baseline=baseline), (
        "row-deletion must not be a route out of the erosion refusal"
    )


# ── wiring and the live tree ──


def test_the_removal_check_is_WIRED_INTO_the_gate(monkeypatch, capsys):
    """MUTATION-PROVED IS NOT WIRED. The function can be perfect and never consulted; this drives
    `main() --check` on a census where NOTHING ELSE is wrong and asserts the exit code and the
    banner. Nothing else can fire here: the one live hit has a complete row."""
    monkeypatch.setattr("sys.argv", ["census", "--check"])
    cen = _synthetic({"live.json": {"writers": ["a::f"], "readers": ["a::g"]}}, ["live.json"])
    monkeypatch.setattr(census, "derive", lambda *a, **k: cen)
    monkeypatch.setattr(census, "load_dispositions", lambda *a, **k: {"live.json": _ROW})
    monkeypatch.setattr(census, "load_retired", lambda *a, **k: {})
    # The head reader's contract is a KEY SET, never a row map: the baseline's only job is to say
    # what WAS in the register, and the rows at HEAD are not evidence about anything else.
    monkeypatch.setattr(census, "_dispositions_at_head",
                        lambda: frozenset({"live.json", "swept.json"}))
    assert census.main() == 1
    out = capsys.readouterr().out
    assert "ROWS REMOVED FROM THE REGISTER WITHOUT A REASON" in out
    assert "swept.json" in out
    assert "subject set is shrinking" not in out, (
        "the banner must name the rung that fired, or a reader repairs the wrong thing")


def test_the_live_baseline_is_ESTABLISHABLE_from_this_tree():
    """The refusal above is only useful if the normal case can actually be answered. This asserts
    `git show HEAD:` resolves the register from whatever tree the suite runs in — including a
    LINKED WORKTREE, which is the only environment `seat_executor` runs in and the environment
    that made a sibling control red for a day."""
    base = census._dispositions_at_head()
    assert base is not None, "the register's baseline at HEAD could not be read from this tree"
    assert len(base) > 20, "HEAD's register is implausibly small — the baseline is not the register"


def test_no_live_row_has_left_the_register_unexplained():
    """The live tree. If this fails, either a row has been deleted — which is the finding, not the
    obstacle, and `git log -S` on the row's key will name the commit — or a carrier genuinely left
    the tree and nobody wrote down why. Never add an empty `_retired` reason to make it green."""
    removed = census.removed_dispositions()
    assert not removed, "rows removed from the register without a reason:\n  " + "\n  ".join(removed)


def test_the_retired_section_is_LOADED_from_the_register_not_invented():
    """`load_retired` reads the real file's real section. MUTATION: return {} unconditionally and
    the malformed/absent legs below stop distinguishing anything."""
    assert census.load_retired() == census.load_retired(census.DISPOSITIONS_PATH)
    assert isinstance(census.load_retired(), dict)


def test_a_malformed_register_yields_no_retired_reasons(tmp_path):
    """Fail toward WORK, never toward silence: an unreadable register must not hand out excuses.
    MUTATION: return a populated dict on the error path and every removal is admitted."""
    bad = tmp_path / "broken.json"
    bad.write_text("{not json")
    assert census.load_retired(bad) == {}
    missing = tmp_path / "absent.json"
    assert census.load_retired(missing) == {}
    wrong_type = tmp_path / "wrong.json"
    wrong_type.write_text(json.dumps({census.RETIRED_SECTION: ["a", "list"]}))
    assert census.load_retired(wrong_type) == {}
