"""Source-wiring guard for W1_reveal_over_time -- the point-in-time blindfold
AT THE SOURCE for the SECOND reveal surface: the semi-annual mark-to-market
(MtM) credit-exposure sampling loop, which KNIFE pass 3 step 19 moved out of
simulation/run_phase2b.py into company/risk/counterparty_collateral_desk.py.

THIS GUARD FOLLOWED ITS SUBJECT, and it did not have to be told to: when the
loop left run_phase2b.py, `test_mtm_sample_loop_is_present` and
`test_all_three_asof_reads_present_in_loop` both FAILED. The fail-silent guards
below are the reason the move could not quietly blind the reveal-boundary check
-- which is what would have happened had they been written as "assert every read
found uses the loop date" over an empty set.

Companion to test_run_phase2b_reveal_source_wiring.py, which guards the two
hedge-decision `PointInTimeView(decision_time=...)` constructions. This file
guards a DISTINCT source-level reveal boundary the sibling does not reach.

The VALUE_CHAIN multi-period sampling loop (added 2026-07-24) walks a series of
`_sample_dates` and, at EACH sample date, reconstructs the calendar-live book
and marks it:

    for _sd in _sample_dates:
        ... _mark_engine.get_forward_price(_fuel, _sd, _recs) ...
        _live_sd = trading_book.live_contracts_as_of(_sd)
        ... trading_book.exposure_by_counterparty_as_of(_mp_sd, _sd) ...

The point-in-time discipline of this whole surface lives ENTIRELY in the wiring:
`get_forward_price` only reads spot history strictly before its `delivery_date`
argument (tariff_engine.py: `end_lookback = start_date - 1`), and the two
`*_as_of` reads filter the book by their date argument. So the blindfold holds
IFF every one of those three reads is passed the PER-SAMPLE loop date `_sd` --
not `effective_end`, not any later date.

Today that guarantee is asserted only by a PROSE COMMENT ("get_forward_price
reads only spot history before each mark date -> point-in-time discipline
holds"). A prose-only point-in-time claim is an R15 fail-open: a regression
swapping `_sd` for `mark_date` (the end-of-run date, a str Name in scope
throughout the same function -- a plausible copy-paste) would mark every mid-run sample at END-OF-RUN forward
prices -- gross look-ahead into the board-headline PEAK credit exposure -- and
NO test would fail. The existing mechanism test
(tests/company/trading/test_multi_period_exposure_sampling.py) RE-IMPLEMENTS its
own sample loop, so it cannot catch a regression in the desk's actual
wiring -- exactly the "at the source, not just company/ code" boundary the atom
names.

This guard parses the desk module's AST, locates the sample loop by its iterator
(`_sample_dates`), and asserts each of the three as-of reads inside it is passed
the loop's own sample-date variable. R15: proven to FIRE on the `_sd ->
mark_date` swap for each read by re-running the same analyzer over a mutated
copy of the live source. Independent of the mechanism under test: it reads the
SOURCE's own wiring, never the reads' behaviour (R15 tautology guard).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

_SOURCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "company" / "risk" / "counterparty_collateral_desk.py"
)

# The three as-of reads whose reveal boundary is wired at the source. Each must
# receive the per-sample loop date as its as-of/delivery argument.
_ASOF_READS = ("get_forward_price", "live_contracts_as_of", "exposure_by_counterparty_as_of")


def _attr_or_id(n: ast.AST) -> str | None:
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        return n.attr
    return None


def _arg_name_ids(call: ast.Call) -> set[str]:
    """The set of bare-Name ids passed to `call` (positional + keyword)."""
    ids: set[str] = set()
    for a in call.args:
        if isinstance(a, ast.Name):
            ids.add(a.id)
    for kw in call.keywords:
        if isinstance(kw.value, ast.Name):
            ids.add(kw.value.id)
    return ids


def _analyze(source: str) -> dict:
    """Find the MtM sampling `for <var> in _sample_dates:` loop and, within its
    body, record for each targeted as-of read whether it is passed the loop's
    own `<var>`. Reports enough to detect FAIL-SILENT (loop/reads missing) as
    well as the reveal-boundary drift itself."""
    tree = ast.parse(source)

    sample_loop = None
    loop_var = None
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) \
                and "sample_dates" in node.iter.id and isinstance(node.target, ast.Name):
            sample_loop = node
            loop_var = node.target.id
            break

    result: dict = {"loop_found": sample_loop is not None, "loop_var": loop_var,
                    "reads": {name: [] for name in _ASOF_READS}}
    if sample_loop is None:
        return result

    for node in ast.walk(sample_loop):
        if not isinstance(node, ast.Call):
            continue
        name = _attr_or_id(node.func)
        if name in _ASOF_READS:
            result["reads"][name].append(loop_var in _arg_name_ids(node))
    return result


@pytest.fixture(scope="module")
def live() -> dict:
    return _analyze(_SOURCE_PATH.read_text())


def test_mtm_sample_loop_is_present(live):
    """FAIL-SILENT guard: the analyzer must actually find the sampling loop, or
    every downstream assertion passes vacuously."""
    assert live["loop_found"], (
        "could not locate the `for <var> in _sample_dates:` MtM sampling loop in "
        "company/risk/counterparty_collateral_desk.py -- the reveal-boundary guard "
        "is blind; re-check the wiring (and see this file's header: it MOVED once)"
    )


def test_all_three_asof_reads_present_in_loop(live):
    """FAIL-SILENT guard: each as-of read must appear inside the loop, else a
    rename/removal would let the boundary check pass on an empty set."""
    for name in _ASOF_READS:
        assert live["reads"][name], (
            f"the as-of read `{name}` was not found inside the MtM sampling loop "
            "-- either it was renamed/removed (update this guard) or the "
            "point-in-time reconstruction was dropped"
        )


def test_every_asof_read_uses_the_per_sample_date(live):
    """The core source-wiring invariant: at each sample date, every as-of read is
    marked AS OF that same per-sample loop date -- never effective_end or any
    later date (which would leak end-of-run prices into a mid-run mark)."""
    lv = live["loop_var"]
    for name in _ASOF_READS:
        assert all(live["reads"][name]), (
            f"an as-of read `{name}` in the MtM sampling loop is NOT passed the "
            f"per-sample loop date `{lv}` -- the mark's reveal boundary has "
            "drifted off the sample date (look-ahead into future prices)"
        )


# --- R15: the guard must FIRE on the named defect (mutation both ways) ---

def _mutant_swaps_sd_for_mark_date(needle: str) -> dict:
    live_src = _SOURCE_PATH.read_text()
    mutant = live_src.replace(needle, needle.replace("_sd", "mark_date"))
    assert mutant != live_src, (
        f"mutation was a no-op -- the exact call `{needle}` is no longer present "
        "verbatim in the desk module; update this mutation string"
    )
    return _analyze(mutant)


def test_MUTATION_forward_mark_dated_at_the_end_of_run_is_caught():
    """`get_forward_price(_fuel, _sd, _recs)` -> `(_fuel, mark_date, _recs)`
    marks every sample at end-of-run forward prices; the guard must flag it."""
    res = _mutant_swaps_sd_for_mark_date(
        "_mark_engine.get_forward_price(_fuel, _sd, _recs)"
    )
    assert res["loop_found"], "mutant lost the sampling loop -- guard blind"
    assert not all(res["reads"]["get_forward_price"]), (
        "the end-of-run-dated forward mark slipped past "
        "test_every_asof_read_uses_the_per_sample_date -- the boundary control "
        "does not actually fire"
    )


def test_MUTATION_live_contracts_dated_at_the_end_of_run_is_caught():
    """`live_contracts_as_of(_sd)` -> `live_contracts_as_of(mark_date)`
    reconstructs the end-of-run book at every sample; the guard must flag it."""
    res = _mutant_swaps_sd_for_mark_date("live_contracts_as_of(_sd)")
    assert res["loop_found"], "mutant lost the sampling loop -- guard blind"
    assert not all(res["reads"]["live_contracts_as_of"]), (
        "the end-of-run-dated live-book reconstruction slipped past the "
        "per-sample-date control -- it does not actually fire"
    )
