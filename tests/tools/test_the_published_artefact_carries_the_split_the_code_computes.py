"""The defect: the split was computed by the code and never reached the file a reader is served.

`98db658f2` split the monthly shock series and `2118135e5` split the annual one. `2118135e5`
closed with "no mean spanning both populations is published on this surface without its two
component means beside it" -- and at the moment this file was written that sentence was **false of
`site/data/dashboard.json`**, which carried the monthly split and not the annual one. The last
publish predated the annual code. The grading was computed; it was never published.

WHY THE SUBJECT IS THE SERVED FILE AND NOT THE GENERATOR, which is the opposite choice from
`site/test_the_reason_mix_interval_reaches_the_reader.py` and is deliberate. That control owns the
claim *the generator's row reaches the reader*, so the generator is rightly its subject. **The claim
this file owns is the one that was missing: that the artefact a reader is served is not on an older
clock than the code that computes it.** Taking the generator as subject here would reproduce the
exact hole being closed -- every existing control for either split feeds synthetic fixtures to
`extract_financial` / `extract_monthly_ops`, and all of them were green while the served file had no
annual split at all.

THE FLAPPING RISK IS REAL AND IS ANSWERED BY THE PROPERTY, NOT BY THE SUBJECT. A control keyed to
today's published values would red every time the publish lane regenerates the file, and this
repository has "a gate slower than the tree's landing cadence never converges" written down. Nothing
here reads a value: every assertion is about SHAPE -- that a mean names its population or carries its
split, that a count and a bound travel with it, that an unobserved cell refuses rather than reports a
zero. A republish from any run satisfies all of it; only a republish that drops the split, or a
publish from a generator that predates it, can fail.

R15 -- the mutations, and the discrimination proof that matters most:
  * THE CONTROL WAS RUN AGAINST THE ARTEFACT BEFORE THE REGENERATION THAT FIXED IT.
    `test_every_published_shock_mean_names_its_population_or_carries_its_split` was RED on the
    annual series and GREEN on the monthly one -- the same assertion, two series, one already
    correct. That is the proof it discriminates rather than passing on everything, and it was
    obtained from the real file rather than from a fixture.
  * drop `bill_shock_by_population` from the publisher -> RED again, which is the state it was
    written in.
  * publish `avg_pct: 0.0` for a population with no bills -> `test_an_unobserved_population_is
    _never_published_as_a_measured_zero` red.
  * publish a mean for a cell too thin to bound with a fabricated interval instead of null ->
    `test_a_cell_too_thin_to_bound_itself_still_publishes_its_count` red.
  * re-point the split at the FLAGGED bills (the monthly subject) while leaving it beside the
    all-computable mean -> `test_the_published_split_reconciles_with_the_mean_it_sits_beside` red,
    because the counts would no longer sum to the mixed total.

REUSE: `test_the_annual_shock_mean_stops_spanning_two_populations.py` and
`test_the_shock_series_stops_averaging_two_populations.py` are the unit-level siblings and this
shares their vocabulary on purpose. Neither can fail for this defect: both take an in-process
function as their subject and neither opens `site/data/`. `site/test_home_door.py` reads this same
artefact but only its `portfolio` block. No existing control asserts anything about the shock fields
of the served file.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
ARTEFACT = PROJECT / "site" / "data" / "dashboard.json"

# The four definitions from docs/market_research/what_bill_shock_is.md: the household pays a level
# amount (`payment`), pays the bill (`bill`), has no bill and no direct debit (`out_of_scope`,
# prepayment), or is unattributed (`unknown`). Never folded into each other.
POPULATIONS = ("payment", "bill", "out_of_scope", "unknown")
STAT_KEYS = ("n", "avg_pct", "median_pct", "max_pct", "ci95_low", "ci95_high")


@pytest.fixture(scope="module")
def served():
    if not ARTEFACT.exists():
        pytest.fail(
            "site/data/dashboard.json is not present. This control's subject is the file a reader "
            "is served; its absence is a publish failure, not a reason to skip."
        )
    return json.loads(ARTEFACT.read_text(encoding="utf-8"))


def _annual_rows(served):
    return [r for r in served.get("financial", {}).get("annual", []) if "avg_bill_shock_pct" in r]


def _monthly_rows(served):
    return [
        r
        for r in served.get("monthly_ops", {}).get("monthly", [])
        if r.get("avg_shock_pct") is not None
    ]


# --------------------------------------------------------------------------
# The property: a published mean either names its population or carries its split
# --------------------------------------------------------------------------


def test_every_published_shock_mean_names_its_population_or_carries_its_split(served):
    """A mean over both definitions of bill shock, standing alone, is the mixed-subject defect.

    Two escapes, and a series needs exactly one of them: say which single population the figure
    is over (`avg_shock_pct_definition`), or publish both populations beside it. This is the
    assertion that was red on the annual series and green on the monthly one.
    """
    offenders = []
    for r in _annual_rows(served):
        named = r.get("avg_bill_shock_pct_definition") in POPULATIONS
        split = isinstance(r.get("bill_shock_by_population"), dict) and r["bill_shock_by_population"]
        if not (named or split):
            offenders.append(f"financial.annual[{r.get('year')}].avg_bill_shock_pct")
    for r in _monthly_rows(served):
        named = r.get("avg_shock_pct_definition") in POPULATIONS
        split = isinstance(r.get("shock_by_population"), dict) and r["shock_by_population"]
        if not (named or split):
            offenders.append(f"monthly_ops.monthly[{r.get('month')}].avg_shock_pct")
    assert not offenders, (
        "published shock means that are neither attributed to one population nor split across "
        "both -- bill shock is two experiences in two populations and a single mean over them "
        "cannot tell a badly-run supplier from an expensive one:\n  "
        + "\n  ".join(offenders)
    )


def test_every_published_split_carries_a_count_and_a_bound_for_every_population(served):
    """`n` and an interval travel with every cell, or the figure is a point with no sample behind it."""
    missing = []
    for r in _annual_rows(served):
        block = r.get("bill_shock_by_population") or {}
        if not block:
            continue
        for pop in POPULATIONS:
            cell = block.get(pop)
            if not isinstance(cell, dict):
                missing.append(f"annual[{r.get('year')}].{pop}: absent")
                continue
            for k in STAT_KEYS:
                if k not in cell:
                    missing.append(f"annual[{r.get('year')}].{pop}: no {k}")
    assert not missing, "published population cells missing their count or bound:\n  " + "\n  ".join(
        missing
    )


def test_an_unobserved_population_is_never_published_as_a_measured_zero(served):
    """`out_of_scope` is prepayment, excluded by definition, and the world has none of it.

    A cell with no bills must publish nulls beside `n: 0`. A `0.0` there is an unobservable
    published as a measurement, which is this project's own named defect and would read to a
    reader as "prepayment households experience no bill shock" -- a finding, from an absence.
    """
    bad = []
    for r in _annual_rows(served):
        for pop, cell in (r.get("bill_shock_by_population") or {}).items():
            if isinstance(cell, dict) and cell.get("n") == 0:
                for k in ("avg_pct", "median_pct", "max_pct", "ci95_low", "ci95_high"):
                    if cell.get(k) is not None:
                        bad.append(f"annual[{r.get('year')}].{pop}.{k} = {cell[k]!r} with n=0")
    for r in _monthly_rows(served):
        for pop, cell in (r.get("shock_by_population") or {}).items():
            if isinstance(cell, dict) and cell.get("n") == 0:
                for k in ("avg_pct", "median_pct", "max_pct", "ci95_low", "ci95_high"):
                    if cell.get(k) is not None:
                        bad.append(f"monthly[{r.get('month')}].{pop}.{k} = {cell[k]!r} with n=0")
    assert not bad, "unobservable published as a measured value:\n  " + "\n  ".join(bad)


def test_a_cell_too_thin_to_bound_itself_still_publishes_its_count(served):
    """"We cannot tell" is a result and belongs on the page in the reader's own units.

    A cell that cannot carry an interval publishes a null interval BESIDE A REAL COUNT -- never a
    null count, which would hide that anything was measured at all, and never a fabricated
    interval. The monthly series exercises this branch on real data: single-bill months publish a
    mean with null bounds.
    """
    bad = []

    def _check(label, cell):
        if not isinstance(cell, dict):
            return
        if cell.get("ci95_low") is None and cell.get("avg_pct") is not None:
            if not isinstance(cell.get("n"), int) or cell["n"] < 1:
                bad.append(f"{label}: unbounded mean with no honest count (n={cell.get('n')!r})")

    for r in _annual_rows(served):
        for pop, cell in (r.get("bill_shock_by_population") or {}).items():
            _check(f"annual[{r.get('year')}].{pop}", cell)
    for r in _monthly_rows(served):
        for pop, cell in (r.get("shock_by_population") or {}).items():
            _check(f"monthly[{r.get('month')}].{pop}", cell)
    assert not bad, "a refusal that hides its own sample:\n  " + "\n  ".join(bad)


def test_the_published_split_reconciles_with_the_mean_it_sits_beside(served):
    """The split must be a partition of the SAME subject, checkable from the artefact alone.

    This is what stops a correct split of the wrong population being published beside a mean over
    a different one -- the two series read different parts of the run output (all computable bills
    against the flagged ones), which is precisely how one got split and the other did not.
    """
    bad = []
    for r in _annual_rows(served):
        block = r.get("bill_shock_by_population") or {}
        mixed = block.get("mixed_all_population")
        if not isinstance(mixed, dict):
            continue
        parts = sum(
            (block.get(p) or {}).get("n", 0) or 0 for p in POPULATIONS
        )
        if parts != mixed.get("n"):
            bad.append(
                f"annual[{r.get('year')}]: populations sum to {parts} but the mixed total is "
                f"{mixed.get('n')!r} -- the split is not a partition of the mean it sits beside"
            )
    assert not bad, "\n  ".join(bad)


def test_the_mixed_total_is_in_the_same_units_as_the_field_it_reconciles(served):
    """`avg_bill_shock_pct` is a FRACTION under a `_pct` name; the split publishes percentages.

    A block that is internally consistent and in the wrong units is not about the field it sits
    beside, and a reader comparing the two would read a hundredfold discrepancy as a defect in the
    world rather than in the naming. The factor is asserted, so the day either side changes units
    the other must follow.
    """
    bad = []
    for r in _annual_rows(served):
        mixed = (r.get("bill_shock_by_population") or {}).get("mixed_all_population")
        published = r.get("avg_bill_shock_pct")
        if not isinstance(mixed, dict) or mixed.get("avg_pct") is None or published is None:
            continue
        # `avg_bill_shock_pct` is rounded to 2dp as a fraction, so one unit of its rounding is
        # 0.5 of a percentage point. The tolerance is that rounding, never a fudge factor.
        if abs(mixed["avg_pct"] / 100.0 - published) > 0.005 + 1e-9:
            bad.append(
                f"annual[{r.get('year')}]: split mixed mean {mixed['avg_pct']}% is not the "
                f"published {published} as a fraction"
            )
    assert not bad, "\n  ".join(bad)


def test_the_mixed_mean_points_the_reader_at_the_split(served):
    """The note is the half that misled and it has to carry its own correction.

    A note that answers the population question in the wrong dimension -- which BILLS, silent on
    which HOUSEHOLDS -- reads as a field whose population question is settled. Keyed to the note
    NAMING the split field rather than to any sentence, so a rewrite that keeps the pointer passes
    and one that drops it fails.
    """
    bad = []
    for r in _annual_rows(served):
        if not r.get("bill_shock_by_population"):
            continue
        note = r.get("avg_bill_shock_pct_population") or ""
        if "bill_shock_by_population" not in note:
            bad.append(
                f"annual[{r.get('year')}]: the mixed mean's note does not point at "
                "bill_shock_by_population, so a reader meets the mixed figure with no route to "
                "the two it is made of"
            )
    assert not bad, "\n  ".join(bad)
