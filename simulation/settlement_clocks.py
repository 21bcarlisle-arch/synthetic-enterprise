"""The settlement clocks, and the refresh that stops a frozen scalar outliving its rows.

WHY THIS EXISTS — the class `figures_on_a_superseded_clock` (2026-08-28, R10).

`simulation/run_phase2b.py:2506-2510` folds five scalars out of `all_records` at the end of
the settlement loop and returns them in the run dict. `simulation/run_phase4c_on_phase2b.py`
then mutates `phase2b["all_records"]` IN PLACE — `apply_emergent_bad_debt` replaces the
flat-rate `get_bad_debt_rate()` provision in each row with the arrears model's realised
write-offs, `apply_debt_recovery` credits back the DCA proceeds, and
`simulation/arrears_engine.py:604-608` / `:709-710` carry the whole correction forward through
every later row's `treasury_cash_balance_gbp`. Nothing refreshed the scalars.

So one dict carried two clocks under one set of names, and which clock a reader got depended
on whether the code they happened to be reading walked the rows or read the summary. That
produced the same GBP 39,962.17 discrepancy TWICE IN TWO DAYS in two different artefacts:

* `docs/observability/value_cycle_ab_s1_three_arm.json` published `total_net_gbp` (frozen) and
  `gross_to_net_bridge…net_margin_gbp` (rows) for one arm on one run, 39,962.17 apart —
  repaired in `tools/run_value_cycle_ab.py` on 2026-08-28 (commit 4d935cb39).
* `docs/reports/run_output_latest.json` published `total_net_gbp` (rows) beside
  `final_treasury_gbp` (frozen), so `starting_treasury_gbp + total_net_gbp` did not equal
  `final_treasury_gbp` — on `site/data/supplier.json`, i.e. on the live surface, where a
  reader with a calculator can see that 250,000 + 153,245 is not 363,283.

REPAIRED AT THE SOURCE, NOT AT THE TWO CONSUMERS. Patching `annual_report.py` would have left
`tools/run_frozen_baseline.py` and `saas/reporting/segment_report.py` reading the same stale
names, and would have left the next consumer to be written free to reintroduce the defect. The
repair is that AFTER the mutation the scalar names no longer hold a superseded value:
`refresh_settlement_scalars()` re-derives each of them from the rows as the rows now stand, and
keeps the pre-mutation reads under `provisioned_*` names so a reader who wants the company's
calibrated provision can still have it — NAMED, and on a clock that says what it is.

R14 IN ONE SENTENCE: every one of these figures now travels beside the clock it is stated on,
and there are exactly two clocks. NOT three — in particular NOT `banked`, which this world does
not have as a distinct reading: `treasury_cash_balance_gbp` is a running total of settled net
margin, so `final_treasury - starting_treasury` reproduces settled net exactly rather than
measuring cash arriving on some other date. A `banked` label here would be a name invented for
a clock that does not exist, which is the more comfortable of the two available wrong answers.

THE EPISTEMIC WALL is untouched. Every quantity here is the WORLD's own settled record of what
it did; nothing the company believed appears, and `saas/` does not import this module (it never
imports `simulation/`) — it carries its own labels into the artefact it publishes, which is
also what keeps `tools/superseded_clock_audit.py` from grading a figure against the constant
that wrote it (R15 tautology).
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping, MutableMapping

#: The two clocks, and NO OTHERS. Published verbatim into artefacts so the definition travels
#: with the number to the reader, rather than living in a module the reader of the JSON never
#: opens.
SETTLED_REALISED = "settled-realised"
SETTLED_PROVISIONED = "settled-provisioned"

CLOCK_DEFINITIONS: dict[str, str] = {
    SETTLED_REALISED: (
        "SETTLED, on the world's realised payment behaviour. Summed over `phase2b.all_records` "
        "as they stand AFTER `simulation/run_phase4c_on_phase2b.py` has called "
        "`apply_emergent_bad_debt` and `apply_debt_recovery`, which replace the flat-rate "
        "provision in each row with the write-offs and DCA recoveries the arrears model "
        "actually produced and carry the difference through `treasury_cash_balance_gbp`. This "
        "is the clock every unprefixed figure in the run dict is on."
    ),
    SETTLED_PROVISIONED: (
        "SETTLED, on the flat-rate bad-debt PROVISION, and superseded within the same run. "
        "`simulation/run_phase2b.py:2506-2510` folds the same rows at the end of the "
        "settlement loop, before the arrears engine has touched them, so its `bad_debt_gbp` is "
        "still `get_bad_debt_rate()` x billed amount — a calibrated company assumption, not an "
        "outcome. Kept under a `provisioned_` name rather than dropped, because it is what the "
        "company provisioned and a reader comparing provision with outcome needs both."
    ),
}

#: The name every superseded read is preserved under.
PROVISIONED_PREFIX = "provisioned_"


def _sum_field(field: str) -> Callable[[list[Mapping[str, Any]]], float]:
    def fold(rows: list[Mapping[str, Any]]) -> float:
        return sum(float(r.get(field, 0.0) or 0.0) for r in rows)

    return fold


def _last_field(field: str) -> Callable[[list[Mapping[str, Any]]], float]:
    def fold(rows: list[Mapping[str, Any]]) -> float:
        return float(rows[-1].get(field, 0.0) or 0.0)

    return fold


#: EVERY scalar `run_phase2b` freezes that is an aggregation over `all_records`, mapped to the
#: aggregation that derives it. THIS IS THE CLASS BOUNDARY and the reason the control below
#: fails on the whole family rather than on the two figures that were caught: a future stage
#: that mutates a row field nothing currently touches still reds `scalar_row_disagreements`,
#: because the check is "does every frozen scalar still equal its own fold over the rows",
#: never "do these two published numbers happen to agree".
ROW_DERIVED_SCALARS: dict[str, Callable[[list[Mapping[str, Any]]], float]] = {
    "total_gross": _sum_field("margin_gbp"),
    "total_capital": _sum_field("capital_cost_gbp"),
    "total_bad_debt": _sum_field("bad_debt_gbp"),
    "total_net": _sum_field("net_margin_gbp"),
    "final_treasury": _last_field("treasury_cash_balance_gbp"),
}

#: Pence, near enough. `arrears_engine` rounds `net_margin_gbp` to 6dp and
#: `treasury_cash_balance_gbp` to 2dp per row, and each row's balance is recomputed from its own
#: base rather than accumulated from the previous rounded one, so the residual is bounded by a
#: penny and never grows with the book. Wide enough to absorb that, narrow enough that the
#: GBP 39,962.17 this class was named for reds by six orders of magnitude.
CLOCK_TOLERANCE_GBP = 0.05


def derive_from_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, float]:
    """Fold every `ROW_DERIVED_SCALARS` aggregation over `rows`, as the rows now stand.

    Raises on an empty book rather than returning zeros. A zero-filled fold is
    indistinguishable from a run that settled to nothing, and a control that passes on an
    empty input is R15's fail-open killer with the numbers filled in.
    """
    rows = list(rows)
    if not rows:
        raise ValueError(
            "cannot derive settlement scalars from an empty `all_records`: a zero-filled "
            "fold is indistinguishable from a run that genuinely settled to nothing"
        )
    return {name: fold(rows) for name, fold in ROW_DERIVED_SCALARS.items()}


def refresh_settlement_scalars(phase2b: MutableMapping[str, Any]) -> dict[str, dict[str, float]]:
    """Re-derive every frozen scalar from the rows, preserving the superseded read by name.

    Called ONCE, by `run_phase4c_on_phase2b`, immediately after the last stage that mutates
    `all_records`. After it returns, `phase2b["total_net"]`, `["final_treasury"]` and their
    siblings are on `settled-realised` and `phase2b["provisioned_total_net"]` etc. hold what
    the settlement loop froze — so no consumer, present or future, can read a superseded value
    out of an unprefixed name.

    IDEMPOTENT ON THE PROVISIONED SIDE. A second call must not overwrite the provisioned
    figures with the realised ones it wrote the first time; the earliest read is the
    provisioned one and it is kept. Returns the audit — per scalar, both clocks and the delta —
    which the caller records so a reader can see how far the two clocks were apart without
    re-deriving either.
    """
    rows = list(phase2b.get("all_records") or [])
    derived = derive_from_rows(rows)

    audit: dict[str, dict[str, float]] = {}
    for name, realised in derived.items():
        provisioned_key = f"{PROVISIONED_PREFIX}{name}"
        if provisioned_key not in phase2b:
            # `.get(name)` and not `[name]`: a run dict that never carried this scalar has no
            # provisioned reading to preserve, and inventing 0.0 for it would publish a
            # fabricated provision. `None` is carried through and the audit says so.
            phase2b[provisioned_key] = phase2b.get(name)
        provisioned = phase2b[provisioned_key]
        phase2b[name] = realised
        audit[name] = {
            "provisioned": provisioned,
            "realised": realised,
            "delta": (realised - provisioned) if isinstance(provisioned, (int, float)) else None,
        }

    phase2b["settlement_clocks"] = {
        "definitions": dict(CLOCK_DEFINITIONS),
        "realised_scalars": sorted(derived),
        "provisioned_scalars": sorted(f"{PROVISIONED_PREFIX}{n}" for n in derived),
        "audit": audit,
    }
    return audit


def scalar_row_disagreements(
    phase2b: Mapping[str, Any], tolerance: float = CLOCK_TOLERANCE_GBP
) -> list[str]:
    """THE CLASS INVARIANT. Every frozen scalar that no longer equals its own fold over the rows.

    Returns one message per disagreeing scalar; an empty list is the pass. This is what makes
    `figures_on_a_superseded_clock` fail automatically rather than these two files failing:
    it does not know which figures were published where, and it does not compare two artefacts
    to each other. It asks the one question the class is about — is this summary still a
    summary of this book — of EVERY scalar in `ROW_DERIVED_SCALARS`, so a stage added next
    month that mutates `margin_gbp` and forgets to refresh reds on `total_gross` without
    anyone extending this control.

    FAILS CLOSED, all three of R15's killers named and refused:

    * MISSING (fail-open): no `all_records`, an empty book, or a scalar absent from the dict is
      a FAILURE, never a silent pass. A run that cannot be reconciled has not been shown to
      reconcile.
    * TAUTOLOGY: the derivation walks the rows directly and never reads the scalar it is
      checking, so the two sides have independent sources — which is the whole point, since
      the defect is precisely that they stopped having a common one.
    * NON-FINITE: a NaN scalar compares false against everything, so an `abs(...) > tol` test
      alone would silently PASS it. Checked explicitly.
    """
    failures: list[str] = []
    rows = phase2b.get("all_records")
    if not isinstance(rows, list) or not rows:
        return [
            "no `all_records` on this run dict, so no frozen scalar can be reconciled against "
            "the book it summarises — an unavailable check is a FAILED check (R15)"
        ]

    derived = derive_from_rows(rows)
    for name, realised in derived.items():
        if name not in phase2b:
            failures.append(
                f"`{name}` is absent from the run dict, so nothing states which clock the "
                f"book's own {realised:,.2f} was published on"
            )
            continue
        published = phase2b[name]
        if not isinstance(published, (int, float)) or isinstance(published, bool):
            failures.append(f"`{name}` is {published!r}, which is not a figure")
            continue
        published = float(published)
        if published != published:  # NaN
            failures.append(f"`{name}` is NaN, which compares false against every tolerance")
            continue
        if abs(published - realised) > tolerance:
            failures.append(
                f"`{name}` published {published:,.6f} but the rows it summarises now fold to "
                f"{realised:,.6f} — a gap of {published - realised:,.2f}. This scalar is on a "
                f"SUPERSEDED clock: a later stage mutated `all_records` and nothing refreshed "
                f"it (see `refresh_settlement_scalars`)"
            )
    return failures


#: The three keys a published run output states the treasury identity in.
PUBLISHED_TREASURY_KEYS = ("starting_treasury_gbp", "total_net_gbp", "final_treasury_gbp")


def reconcile_published_run_output(
    payload: Mapping[str, Any], tolerance: float = CLOCK_TOLERANCE_GBP
) -> list[str]:
    """THE READER'S CHECK, applied to a published artefact: does the page add up.

    `starting_treasury_gbp + total_net_gbp == final_treasury_gbp`. This holds in this world
    because `treasury_cash_balance_gbp` is a running total of settled net margin and nothing
    else moves it — which is exactly why the identity is worth publishing a control on: it is
    the arithmetic a reader of `site/data/supplier.json` can do in their head.

    IF THIS EVER REDS FOR A REASON OTHER THAN A STALE SCALAR, that is a finding and not a false
    positive. It would mean the world has grown a cash flow outside net margin, and the
    published page has quietly stopped being addable — which is the defect this class is about,
    arriving from the other direction. Widen the identity then, with the new line named; do not
    widen the tolerance.

    Fails closed on a missing or non-numeric figure for the same reason as above.
    """
    failures: list[str] = []
    values: dict[str, float] = {}
    for key in PUBLISHED_TREASURY_KEYS:
        if key not in payload:
            failures.append(
                f"`{key}` is absent, so the published treasury identity cannot be checked — "
                "an unavailable check is a FAILED check (R15)"
            )
            continue
        value = payload[key]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value != value:
            failures.append(f"`{key}` is {value!r}, which is not a figure this identity can use")
            continue
        values[key] = float(value)
    if failures:
        return failures

    start = values["starting_treasury_gbp"]
    net = values["total_net_gbp"]
    final = values["final_treasury_gbp"]
    if abs(start + net - final) > tolerance:
        failures.append(
            f"the published run output does not add up: starting_treasury_gbp {start:,.2f} + "
            f"total_net_gbp {net:,.2f} = {start + net:,.2f}, but final_treasury_gbp is "
            f"{final:,.2f} — out by {start + net - final:,.2f}. Two figures for one book on "
            "two clocks under one label (class `figures_on_a_superseded_clock`); the net "
            "margin is summed from `all_records` as the arrears engine left them, so the "
            "treasury must be read from the same rows and not from the settlement loop's "
            "frozen scalar"
        )
    return failures
