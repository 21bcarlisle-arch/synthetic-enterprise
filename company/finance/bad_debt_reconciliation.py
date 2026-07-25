"""Bad-debt reconciliation bridge -- the estimate-vs-realised GAP across clocks.

WHY THIS MODULE EXISTS (steer DIRECTOR_STEER_DUNNING_DEBT_PROVISIONING_2026-07-25,
§F3 / D2 / D3; mint PLANNER_MINTED_bad_debt_reconciliation_bridge_2026-07-25).
A UK supplier's published bad-debt line is only meaningful as *estimate-vs-realised
variance across clocks*. Today four expected-loss numbers exist and NOTHING
reconciles them:

  1. FLAT HAIRCUT  (`saas.payment_behaviour.bad_debt_provision_gbp`) -- LIVE,
     BILLED clock: rate x billed revenue per bill. "Structurally incapable of
     ever being wrong" (steer §F1) -- no outcome ever feeds back into it, so
     its error cannot be measured. THAT is the defect this bridge exposes.
  4. REALISED      (`simulation.arrears_engine.compute_emergent_bad_debt`) -- the
     TRUTH, SETTLED clock: GBP actually written off, per (customer, write-off year).

  2. AGING MATRIX  (`company.finance.bad_debt_provision`) and
  3. STAGE RECOVERY(`company.finance.debt_collection`) are fully built but WIRED
     TO NOTHING -- no run-data input path feeds them aged positions / debt-stage
     records. They CANNOT yet be reconciled, and *that they cannot* is the finding
     (steer D4: retire-or-wire is decided BY this reconciliation, not ahead of it).
     This module reports them as `unwired` with the input each would need; it NEVER
     fabricates aged positions or stage records to feed them (that would invent
     inputs and make a fake number -- R12).

This is the same defect CLASS the two-revenue-pipelines finding closed with a
reconciliation bridge (MARGIN_REALISM_E2_TWO_PIPELINES_FINDING.md). Revenue has a
bridge; bad debt had none. This is the bridge (report-first: it MOVES NO PUBLISHED
FIGURE -- it measures a disagreement and registers a fidelity-ledger row).

THE WALL (why this module is PURE over PRIMITIVES, imports NEITHER side).
This is HARNESS measurement code. The flat provision is computed from the
company's OWN bills; the realised write-off is the SIM's settled-clock truth
(`simulation.arrears_engine`). A module under `company/` that imported
`simulation.*` would breach the epistemic wall AND trip `tools.epistemic_verifier`
(a Tier-1 import-direction check -- `company/` may reach SIM only through
`company/interfaces/sim_interface.py`). So, exactly like
`background/live_fidelity_evidence.py` (which takes already-measured primitives so
the wall is not merely respected but *structurally unreachable*), this module
takes the two per-year figure dicts as PRIMITIVES and computes the gap over them.
The both-sides COLLECTION -- reading `saas.build_payment_behaviour` and
`simulation.compute_emergent_bad_debt` and handing the primitives in -- lives in
`background/bad_debt_reconciliation_run.py` (the `background/` path is
verifier-exempt harness, exactly where `background/live_payment_triad.py` legitimately
holds both sides). Splitting it this way keeps the finance math wall-clean and the
one file that touches SIM internals on the exempt harness side.

R12 (anti-goal-seek): the variance is a DIAGNOSTIC, never a target (steer D1/D2).
Nothing here tunes a figure toward a benchmark. A SMALLER *measured* variance is
the honesty target; a company that *believes* it provisions perfectly is a wider
hidden gap wearing a better number -- so the variance control (below) must be able
to FAIL (R15 both ways): it trips when realised loss is zeroed, and it trips when
the estimate is made to track the outcome tautologically (a figure that cannot be
wrong is the defect, not a pass).

R14 (no figure without its clock): every per-year row carries `provision_clock`
("billed") and `realised_clock` ("settled") -- the disagreement is partly a
genuine estimate error and partly a two-clock timing difference, and the report
never collapses the two.

C-S2 (determinism): this module makes no clock or random draw. `as_of` /`seed`
are gathered by the caller and passed straight through.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Tuple

# ---------------------------------------------------------------------------
# The two unwired methods (2 & 3). Reported, never fed fabricated inputs.
# ---------------------------------------------------------------------------
# steer D4 / §F2: two fully-built zero-caller modules holding competing answers
# to the same question. This bridge names them `unwired` with the exact input
# each would need to become reconcilable -- it does NOT invent that input.
UNWIRED_METHODS: Dict[str, Dict[str, str]] = {
    "aging_matrix": {
        "module": "company/finance/bad_debt_provision.py",
        "status": "unwired -- no run-data input path exists yet",
        "needs": (
            "aged arrears positions per customer as_of a date "
            "(ArrearsLedgerItem: outstanding_gbp + days_outstanding), which no "
            "run currently emits -- the arrears cascade in simulation.arrears_engine "
            "carries stage DATES but no aged open-balance snapshot the company observes."
        ),
        "clock": "would be as-of/positional (a point-in-time aged balance), distinct "
                 "from both the billed and settled clocks below",
    },
    "stage_recovery": {
        "module": "company/finance/debt_collection.py",
        "status": "unwired -- no run-data input path exists yet",
        "needs": (
            "debt records by dunning stage (DebtRecord: amount_gbp + DebtStage + "
            "stage_date), i.e. a live dunning ladder placing accounts into "
            "initial_reminder/warning/pre_legal/DCA/legal/write_off -- the ladder "
            "module has zero live callers, so no run produces stage-classified records."
        ),
        "clock": "would be process/stage-indexed (expected loss = amount - expected "
                 "recovery by stage), distinct from billed and settled",
    },
}

PROVISION_CLOCK = "billed"
REALISED_CLOCK = "settled"

# rel_id for the fidelity-ledger row (steer D2). Kept stable so re-emission
# read-merge-updates the same row rather than proliferating.
LEDGER_REL_ID = "bad_debt_provision_vs_realised_variance"
LEDGER_ATOM_ID = "bad_debt_reconciliation_bridge"

# R10 named simplification carried on the emitted evidence: the bridge reconciles
# only methods 1 & 4 (the two live/computable numbers). Methods 2 & 3 are unwired
# (reported, not reconciled), and the billed-vs-settled clock offset is NAMED but
# not timing-adjusted away -- the variance is reported as the raw disagreement.
LEDGER_SIMPLIFICATION_ID = (
    "bad_debt_recon_flat_vs_realised_only__aging_and_stage_unwired__clocks_named_not_adjusted"
)


@dataclass(frozen=True)
class YearReconciliation:
    """One year's flat-provision-vs-realised reconciliation row.

    `variance_gbp` is estimate - realised (positive => the flat haircut
    OVER-provisions relative to what was actually written off; negative =>
    under-provisions). `variance_ratio` is estimate / realised, or None when
    realised is zero (an undefined ratio, never silently 0 or inf -- reported
    as None with the raw variance still meaningful)."""

    year: int
    flat_provision_gbp: float
    realised_written_off_gbp: float
    variance_gbp: float
    variance_ratio: Optional[float]
    provision_clock: str = PROVISION_CLOCK
    realised_clock: str = REALISED_CLOCK

    def as_dict(self) -> dict:
        return {
            "year": self.year,
            "flat_provision_gbp": round(self.flat_provision_gbp, 2),
            "realised_written_off_gbp": round(self.realised_written_off_gbp, 2),
            "variance_gbp": round(self.variance_gbp, 2),
            "variance_ratio": (
                None if self.variance_ratio is None else round(self.variance_ratio, 4)
            ),
            "provision_clock": self.provision_clock,
            "realised_clock": self.realised_clock,
        }


@dataclass(frozen=True)
class ControlResult:
    """The R15-failable variance control's verdict. `passed` is False iff any
    `reasons` is present (never empty on a fail, always empty on a pass)."""

    passed: bool
    reasons: Tuple[str, ...] = field(default_factory=tuple)


# Below this the two per-year figures are treated as equal everywhere -- i.e. the
# estimate is not an independent measurement of the outcome but a copy of it.
_TAUTOLOGY_EPS_GBP = 1e-6


def _year_variance(flat: float, realised: float) -> Tuple[float, Optional[float]]:
    variance = flat - realised
    ratio = (flat / realised) if realised != 0 else None
    return variance, ratio


def reconcile_by_year(
    flat_provision_by_year: Mapping[int, float],
    realised_by_year: Mapping[int, float],
) -> List[YearReconciliation]:
    """Per-year reconciliation over the UNION of years present in either input
    (a year with a provision but no realised loss, or vice-versa, is a real
    reconciling row, not a dropped one -- missing side treated as 0.0)."""
    years = sorted(set(flat_provision_by_year) | set(realised_by_year))
    rows: List[YearReconciliation] = []
    for y in years:
        flat = float(flat_provision_by_year.get(y, 0.0))
        realised = float(realised_by_year.get(y, 0.0))
        variance, ratio = _year_variance(flat, realised)
        rows.append(
            YearReconciliation(
                year=y,
                flat_provision_gbp=flat,
                realised_written_off_gbp=realised,
                variance_gbp=variance,
                variance_ratio=ratio,
            )
        )
    return rows


def variance_control(
    flat_provision_by_year: Mapping[int, float],
    realised_by_year: Mapping[int, float],
) -> ControlResult:
    """The R15-failable control on the provision-vs-realised variance. It must be
    ABLE TO FAIL -- a control that always passes is theatre (R15). It trips on:

      FAIL-CLOSED: either input missing/empty -> nothing was reconciled, so the
        result is NOT a clean 'reconciled' (an absent input is a failed check,
        never a silent pass -- R15 fail-open doctrine).

      MUTATION 1 (realised zeroed): total realised loss is 0 while a positive
        provision is being raised -> the estimate cannot be validated against ANY
        outcome. A company that provisions yet realises no loss is the
        structurally-incapable-of-being-wrong defect (steer §F1), not a pass.

      MUTATION 2 (tautology): the estimate reproduces the outcome to within
        `_TAUTOLOGY_EPS_GBP` in EVERY year -> the variance is not an INDEPENDENT
        measurement of the estimate's error, it is the outcome copied back onto
        the estimate (R15 TAUTOLOGY doctrine -- checked value derived from the
        same source it checks). Steer §D2: a figure that cannot be wrong is the
        defect. The provision (billed clock, at issue) and the realised write-off
        (settled clock, post-churn) are computed from DIFFERENT sources by
        construction; if they are equal everywhere, independence has been broken.
    """
    reasons: List[str] = []

    if not flat_provision_by_year or not realised_by_year:
        reasons.append(
            "fail-closed: a required input is missing/empty "
            f"(flat_provision entries={len(flat_provision_by_year or {})}, "
            f"realised entries={len(realised_by_year or {})}) -- nothing reconciled, "
            "not a clean 'reconciled' result"
        )
        # Fail-closed short-circuits: with a missing side, the checks below are
        # ill-defined, so report the fail-closed reason alone.
        return ControlResult(passed=False, reasons=tuple(reasons))

    provision_total = sum(float(v) for v in flat_provision_by_year.values())
    realised_total = sum(float(v) for v in realised_by_year.values())

    if realised_total == 0 and provision_total > 0:
        reasons.append(
            "realised written-off total is 0 while flat provision is "
            f"{provision_total:.2f} -- the estimate cannot be validated against any "
            "outcome (structurally-incapable-of-being-wrong, steer §F1)"
        )

    rows = reconcile_by_year(flat_provision_by_year, realised_by_year)
    max_abs_variance = max((abs(r.variance_gbp) for r in rows), default=0.0)
    if max_abs_variance <= _TAUTOLOGY_EPS_GBP:
        reasons.append(
            "estimate reproduces the realised outcome to within "
            f"{_TAUTOLOGY_EPS_GBP} GBP in every year (max |variance|="
            f"{max_abs_variance:.6f}) -- the variance is not an independent "
            "measurement of the estimate's error but the outcome copied onto the "
            "estimate (R15 tautology; steer §D2)"
        )

    return ControlResult(passed=not reasons, reasons=tuple(reasons))


def build_report(
    flat_provision_by_year: Mapping[int, float],
    realised_by_year: Mapping[int, float],
    *,
    generated_from: str,
) -> dict:
    """Build the reconciliation report artifact (steer D3 -- the bridge). No I/O:
    the caller writes it. R14: every figure carries its clock; the two unwired
    methods carry their `unwired` status. `generated_from` documents the data
    source used (a run-output note), so a reader can tell fixture from real run."""
    rows = reconcile_by_year(flat_provision_by_year, realised_by_year)
    provision_total = round(sum(r.flat_provision_gbp for r in rows), 2)
    realised_total = round(sum(r.realised_written_off_gbp for r in rows), 2)
    overall_variance = round(provision_total - realised_total, 2)
    overall_ratio = (
        round(provision_total / realised_total, 4) if realised_total != 0 else None
    )
    control = variance_control(flat_provision_by_year, realised_by_year)

    return {
        "generated_from": generated_from,
        "clocks": {
            "provision": PROVISION_CLOCK,
            "realised": REALISED_CLOCK,
            "note": (
                "R14: the flat-haircut provision sits on the BILLED clock (raised at "
                "bill issue, rate x revenue); the realised write-off sits on the "
                "SETTLED clock (booked post-churn). The variance is therefore part "
                "genuine estimate error and part billed-vs-settled timing offset -- "
                "named here, not adjusted away."
            ),
        },
        "years": [r.as_dict() for r in rows],
        "provision_total_gbp": provision_total,
        "realised_total_gbp": realised_total,
        "provision_vs_realised_variance_gbp": overall_variance,
        "provision_vs_realised_variance_ratio": overall_ratio,
        "unwired_methods": UNWIRED_METHODS,
        "control": {
            "passed": control.passed,
            "reasons": list(control.reasons),
        },
        "reconciled_methods": [
            "flat_haircut (saas.payment_behaviour.bad_debt_provision_gbp, billed)",
            "realised (simulation.arrears_engine.compute_emergent_bad_debt, settled)",
        ],
        "r12_note": (
            "The variance is a DIAGNOSTIC, never a target (steer D1/D2). It is "
            "published, never tuned toward a benchmark. This report moves NO "
            "published figure (report-first, steer §6)."
        ),
    }


def build_ledger_record(report: Mapping) -> dict:
    """Shape the fidelity-evidence ledger row for the provision-vs-realised
    variance (steer D2 -- a first-class measured quantity). Matches the ledger
    schema (`background.fidelity_evidence_ledger._validate_record`): required top
    keys rel_id/atom_id/relationship, and relationship.{kind,provenance,
    simplification_id}. Provenance is `estimated_from_data` -- the variance is a
    genuinely measured live quantity (the two figures are each computed from real
    run data, not asserted). It STILL carries a `simplification_id` naming what is
    NOT yet reconciled (methods 2 & 3 unwired; clocks named not adjusted) --
    honest beyond the gate's minimum, matching background/live_fidelity_evidence.py."""
    return {
        "rel_id": LEDGER_REL_ID,
        "atom_id": LEDGER_ATOM_ID,
        "relationship": {
            "kind": "bad_debt_provision_vs_realised_variance",
            "provenance": "estimated_from_data",
            "simplification_id": LEDGER_SIMPLIFICATION_ID,
            "provision_total_gbp": report["provision_total_gbp"],
            "realised_total_gbp": report["realised_total_gbp"],
            "provision_vs_realised_variance_gbp": report["provision_vs_realised_variance_gbp"],
            "provision_vs_realised_variance_ratio": report.get(
                "provision_vs_realised_variance_ratio"
            ),
            "provision_clock": PROVISION_CLOCK,
            "realised_clock": REALISED_CLOCK,
            "n_years_reconciled": len(report.get("years", [])),
            "unwired_methods": ["aging_matrix", "stage_recovery"],
            "control_passed": report.get("control", {}).get("passed"),
            "generated_from": report.get("generated_from"),
        },
    }
