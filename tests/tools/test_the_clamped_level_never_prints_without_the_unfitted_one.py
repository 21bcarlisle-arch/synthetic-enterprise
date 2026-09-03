"""The fitted level may not reach a reader without the level an unfitted world would have.

THE DEFECT THIS EXISTS FOR (2026-09-03). `tools/fit_year_level_anchor.fit_whole_book` bisects a
per-year scalar until expected departures over accounts equals the published rate, so its
`achieved %` column equals its `record %` column to four decimal places in every fitted year. That
is the solver's definition, not a validation result — but printed on its own it reads as a world
passing a check. `DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31` §1: *"The one move that is
always wrong: clamping an aggregate to pass a check."* and rung 1: *"A world whose level sits on
the exact edge of the band every year has almost certainly been fitted to that edge."* Both are
true of this table and neither was visible in it.

`emergent_level_sweep` answers the opposite question — where the level would land at ONE constant
for every year, which is the shape a bottom-up world has. Measured on
`c6_second_pass_departure_factors.json`: 2 of 7 fitted years in band at the best constant, against
7 of 7 for the fit. The gap is the rung 1 debt, stated in the same output rather than in a document
somebody has to find.

WHY THE SUBJECT IS `main` AND NOT THE SWEEP FUNCTION. This project has already paid for the other
choice: a refusal added to a control and not to the caller that prints leaves the printed page
failing open, and the source-text check that was supposed to catch it passed on a mention in a
comment. So the assertion here is on the parsed AST of `main` — a `Call` node whose callee is
`emergent_level_sweep` — and deleting the call reds even if the name survives in a docstring.

R15 — the mutations, each run and reverted:
  * delete the `emergent_level_sweep(...)` call from `main` -> `test_the_fit_tools_own_output_
    computes_the_unfitted_level` reds. Leaving the identifier in a comment does not save it.
  * score `in_band` against the band's high endpoint alone -> `test_containment_is_against_both
    _endpoints_and_never_one` reds; that is the exact re-import of the point target the sweep
    exists to get away from. **THIS MUTATION SURVIVED THE FIRST DRAFT OF THIS FILE**, and the
    survival is kept here rather than tidied away: that test computed containment inline over the
    band midpoints and asserted its own arithmetic, so it was checking this file's expression and
    not the sweep's. It now drives the real scorer at an anchor of 0.01, where every year sits
    below its band -- a state the two rules disagree about (7 in band against 0).
  * make `published_departure_band` return `(hi, hi)` -> the same test reds, and it is the
    tautology this file is most exposed to: a band whose endpoints are equal turns containment
    back into equality without changing a single call site.
  * let the sweep score years `fit_whole_book` refuses -> `test_the_sweep_scores_only_the_years
    _the_fit_itself_will_solve` reds. Scoring 2022, which has no renewal population, would let the
    in-band count be moved by choosing the population after seeing the answer.
"""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

import tools.fit_year_level_anchor as F
from simulation.market_switching_propensity import published_departure_band

REPO = Path(__file__).resolve().parents[2]
CAPTURE = REPO / "docs" / "reports" / "c6_second_pass_departure_factors.json"
SVT_CAPTURE = REPO / "docs" / "reports" / (
    "c6_second_pass_departure_factors_svt_segment_decisions.json")


def _capture():
    if not (CAPTURE.is_file() and SVT_CAPTURE.is_file()):
        pytest.fail(
            "the c6 capture pair is missing, so the emergent-level reading is UNAVAILABLE -- "
            "reported as a failure and never skipped (R15)")
    return (json.loads(CAPTURE.read_text(encoding="utf-8")),
            json.loads(SVT_CAPTURE.read_text(encoding="utf-8")))


@pytest.fixture(scope="module")
def sweep():
    renewal, svt = _capture()
    return F.emergent_level_sweep(renewal, svt)


def test_the_fit_tools_own_output_computes_the_unfitted_level():
    """DEFECT: the clamped table prints alone and reads as a world that passed something.

    Asserted on the AST rather than on the source text. A `grep` for the function name passes on
    a comment that mentions it, which is how the analogous control failed in August: the refusal
    was added to the helper and never to the `main` that does the printing, and nothing red.
    """
    tree = ast.parse(inspect.getsource(F.main))
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "emergent_level_sweep" in called, (
        "tools/fit_year_level_anchor.main does not CALL emergent_level_sweep, so it prints a "
        "table whose `achieved %` equals `record %` by construction with nothing beside it. The "
        "name appearing in a comment or docstring does not satisfy this")


def test_containment_is_against_both_endpoints_and_never_one(sweep):
    """DEFECT: the sweep scores against the band's high end, re-importing the point target.

    `market_departure_rate` returns the high endpoint by the director's anti-flattering tie-break,
    and that is right for a world that must sit on one number. It is wrong for a CHECK: scoring
    containment against `hi` alone calls a world sitting comfortably in the middle of the record a
    failure, and scoring against equality-with-hi is the clamp wearing a new name.

    So: the bands this sweep uses must be genuinely two-ended, and the scoring must accept a
    reading strictly inside them.
    """
    bands = sweep["bands"]
    assert bands, "the sweep scored no year against any band"
    widths = [hi - lo for lo, hi in bands.values()]
    assert all(w > 0 for w in widths), (
        "at least one band has zero width, so containment in it IS equality and this sweep is "
        "measuring the clamp it exists to expose: {}".format(bands))

    # AND THE SCORER IS DRIVEN, NOT RE-IMPLEMENTED HERE. The first draft of this test computed
    # containment inline over the midpoints and asserted its own arithmetic -- a tautology, and it
    # SURVIVED the `achieved <= hi` mutation, which is the one mutation this test exists for. So
    # the real sweep is run at an anchor low enough that every year is far BELOW its band. A
    # scorer testing only the upper endpoint counts all of them as in band; one testing
    # containment counts none.
    renewal, svt = _capture()
    floored = F.emergent_level_sweep(renewal, svt, anchors=[0.01])
    row = floored["sweep"][0]
    below = [y for y in floored["years"] if row["achieved_pct"][y] < floored["bands"][y][0]]
    assert below == floored["years"], (
        "an anchor of 0.01 does not put every year below its band, so this fixture cannot "
        "distinguish the two scoring rules -- got {}".format(
            {y: round(row["achieved_pct"][y], 2) for y in floored["years"]}))
    assert row["in_band"] == 0, (
        "{} year(s) scored as IN BAND while sitting below the band's low endpoint, so "
        "containment is being tested against the high endpoint alone -- which is the point "
        "target this sweep exists to get away from".format(row["in_band"]))


def test_the_sweep_scores_only_the_years_the_fit_itself_will_solve(sweep):
    """DEFECT: the in-band count is moved by choosing which years to count.

    2022 carries zero renewal decisions and an SVT floor above its published target; `fit_whole_
    book` refuses it on both counts. Including it here would compare an emergent level against a
    band the fit declines to solve on — and since 2022's band is the record's widest relative to
    its level, including it is the single cheapest way to make this reading look better than it
    is. The population is therefore taken FROM the fit, not declared beside it.
    """
    renewal, svt = _capture()
    solvable = {y for y, (anchor, _r, _d) in F.fit_whole_book(renewal, svt).items()
                if anchor is not None}
    assert set(sweep["years"]) <= solvable, (
        "the sweep scores year(s) the whole-book fit refuses: {} -- the emergent level is being "
        "compared against a band the fit itself will not solve on".format(
            sorted(set(sweep["years"]) - solvable)))
    assert sweep["years"], "the sweep scored no years at all, which is a failed check not a pass"


def test_the_reading_is_reported_and_not_silently_absorbed(sweep):
    """DEFECT: a sweep that reports its best constant and hides how badly it does.

    The number that matters is not the best anchor; it is how FEW years that anchor can put in
    band. This asserts the count is present and is a real count over the scored population, so a
    future edit cannot reduce the output to "best anchor: 2.8" — which reads as a result and is
    the same clamp with a smaller table.
    """
    best = sweep["best"]
    assert "in_band" in best and isinstance(best["in_band"], int), (
        "the sweep does not report how many years its best constant puts in band")
    assert 0 <= best["in_band"] <= sweep["n_years"]
    assert best["in_band"] == max(row["in_band"] for row in sweep["sweep"]), (
        "the reported `best` is not the best in the sweep it reports")
    assert len(best["achieved_pct"]) == sweep["n_years"], (
        "the best row does not carry a level for every scored year, so a reader cannot see WHICH "
        "years miss")
