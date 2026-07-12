"""Crisis-era bad-debt validator -- AFFORDABILITY_AS_SIM_PHYSICS.md thin start
(2026-07-12, director-adjudicated CFO cold-walk finding
coldwalk:bad_debt_implausibly_low_through_2021_22_crisis).

WHAT THIS IS
============
A harness-side (outside the wall -- the harness plays Ofgem/external auditor,
not the company) anchored check that asserts the sim's bad-debt/arrears
trajectory shows a REAL step-up through the 2021-22 UK energy crisis, the way
real UK suppliers did.

WHAT THIS IS NOT (R12, anti-goal-seek -- CLAUDE.md)
===================================================
This is a DIAGNOSTIC, never a target. It exists to MEASURE the gap the CFO
persona found -- it is EXPECTED TO FAIL against the current run output, and
that failure is the honest evidence the affordability mechanism is missing.
Nobody may tune a bad-debt parameter to make this pass (R12). Closure comes
only when arrears EMERGE from the household-budget-meets-price-shock model
(the W2_4.. atom cluster, deferred to M3), not from calibrating the output.

THE UNDERLYING MODELLING GAP (director's adjudication)
=====================================================
Payment behaviour is currently propensity-shaped; in reality arrears are the
OUTPUT of a household budget meeting a price shock. Both representations of
bad debt in the run output reflect this:
  - the HEADLINE arrears figure (years[*].bad_debt_gbp -> total_bad_debt_gbp,
    the number surfaced on supplier.json that the CFO flagged) is the
    behavioural arrears-engine write-off -- implausibly low and, critically,
    with NO crisis step-up;
  - the PnL ACCRUAL figure (management_accounts[*].income_statement.
    bad_debt_gbp) sits ~in-band as a % of revenue but is a broadly FLAT
    ~2% rate every year -- it tracks revenue, it does not spike in the
    crisis -- which is itself the propensity/rate-applied signature, not a
    budget-shock-emergent one.

ANCHORS (real published UK figures -- cite-your-source discipline, [L] tags
where magnitude is directional/low-confidence, no fabricated precision)
=======================================================================
  - Resi bad-debt rate band 1-3% of revenue; SME 0.5-2%
    (docs/market_research/ASSUMPTIONS.md; Ofgem Annual Report; Cornwall
    Insight). REUSED verbatim from domain_invariants.BAD_DEBT_RATE_RESI so
    the two never drift apart.
  - Real UK energy debt & arrears rose SHARPLY through the 2021-22 crisis
    -- Ofgem debt/affordability reporting and Citizens Advice put total
    domestic energy debt at ~GBP 4.43bn by June 2025, roughly DOUBLE its
    pre-crisis level (ASSUMPTIONS.md line ~74). [L] on the exact multiple.
  - Centrica plc's own CFO quantified the movement live in the FY2025 Q&A:
    bad-debt charge "went from 2.3 to 2.8% of revenue in the year ... about
    a 40 million pound increase" (ASSUMPTIONS.md line ~255) -- confirming
    that in the real crisis the bad-debt RATE itself steps up, it is not a
    constant fraction of revenue. [L] as a single-company data point.

So the two anchored assertions below are deliberately CONSERVATIVE:
  (1) crisis-era (2021-22) blended bad-debt rate >= 1.0% of revenue (the LOW
      end of the real resi band; the real crisis pushed it well above this);
  (2) crisis-era rate steps up to at least 1.2x the pre-crisis (2016-19)
      baseline [L] -- far short of the ~2x real energy debt actually moved,
      chosen so a PASS means a genuine, unmistakable crisis signal, not a
      benchmark-tuned one.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from company.compliance.domain_invariants import BAD_DEBT_RATE_RESI

# --- Anchored constants (see module docstring for provenance) ---

CRISIS_YEARS: tuple[int, ...] = (2021, 2022)
PRE_CRISIS_YEARS: tuple[int, ...] = (2016, 2017, 2018, 2019)

# Reused from the already-anchored domain invariant, not re-derived here.
CRISIS_BAD_DEBT_RATE_FLOOR: float = BAD_DEBT_RATE_RESI.low  # 0.01 (1% of revenue)
CRISIS_BAD_DEBT_RATE_FLOOR_SOURCE: str = (
    "domain_invariants.BAD_DEBT_RATE_RESI.low (Ofgem Annual Report; Cornwall "
    "Insight; ASSUMPTIONS.md) -- LOW end of the real resi 1-3% band; the real "
    "2021-22 crisis pushed rates well above this"
)

# [L] directional: real UK domestic energy debt roughly DOUBLED through the
# crisis; 1.2x is a deliberately conservative floor so a PASS is unambiguous.
CRISIS_STEP_UP_MIN_RATIO: float = 1.2
CRISIS_STEP_UP_SOURCE: str = (
    "[L] Ofgem/Citizens Advice domestic energy debt ~doubled 2020->2022 "
    "(~GBP4.43bn by 2025); Centrica CFO bad-debt charge 2.3%->2.8% of revenue "
    "-- ASSUMPTIONS.md. 1.2x is a conservative directional floor, not the ~2x "
    "the real figure moved"
)

Basis = Literal["headline", "pnl_accrual"]


@dataclass(frozen=True)
class YearRate:
    year: int
    bad_debt_gbp: float
    revenue_gbp: float

    @property
    def rate(self) -> float:
        # Revenue can legitimately be ~0 in the first partial year; guard it.
        return self.bad_debt_gbp / self.revenue_gbp if self.revenue_gbp else 0.0


@dataclass(frozen=True)
class CrisisBadDebtResult:
    """Outcome of the validator. `passed` is False when the current output
    lacks a real crisis step-up -- the EXPECTED state until the affordability
    mechanism exists (W2_4.. cluster, M3)."""
    basis: Basis
    passed: bool
    crisis_rate: float
    pre_crisis_rate: float
    step_up_ratio: float
    per_year: list[YearRate]
    failures: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"[{self.basis}] crisis(2021-22) bad-debt rate={self.crisis_rate:.4%} "
            f"vs pre-crisis(2016-19)={self.pre_crisis_rate:.4%} "
            f"(step-up x{self.step_up_ratio:.2f}); "
            f"floor>={CRISIS_BAD_DEBT_RATE_FLOOR:.1%}, "
            f"step-up>=x{CRISIS_STEP_UP_MIN_RATIO}; "
            f"{'PASS' if self.passed else 'FAIL: ' + '; '.join(self.failures)}"
        )


def _blended_rate(rows: list[YearRate]) -> float:
    """Revenue-weighted (blended) bad-debt rate across a set of years --
    sum(bad_debt)/sum(revenue), not the mean of per-year rates, so a big
    year isn't washed out by a tiny early one."""
    total_bd = sum(r.bad_debt_gbp for r in rows)
    total_rev = sum(r.revenue_gbp for r in rows)
    return total_bd / total_rev if total_rev else 0.0


def validate_crisis_bad_debt(
    bad_debt_by_year: dict[int, float],
    revenue_by_year: dict[int, float],
    basis: Basis = "headline",
) -> CrisisBadDebtResult:
    """Assert the bad-debt trajectory shows a real 2021-22 crisis step-up.

    Pure function -- no I/O. `bad_debt_by_year`/`revenue_by_year` are keyed by
    integer year. Returns a CrisisBadDebtResult; check `.passed`.
    """
    def rows(years: tuple[int, ...]) -> list[YearRate]:
        out = []
        for y in years:
            if y in bad_debt_by_year and y in revenue_by_year:
                out.append(YearRate(y, float(bad_debt_by_year[y]), float(revenue_by_year[y])))
        return out

    crisis_rows = rows(CRISIS_YEARS)
    pre_rows = rows(PRE_CRISIS_YEARS)

    crisis_rate = _blended_rate(crisis_rows)
    pre_rate = _blended_rate(pre_rows)
    step_up = (crisis_rate / pre_rate) if pre_rate > 0 else float("inf")

    failures: list[str] = []
    if not crisis_rows:
        failures.append("no crisis-year (2021/2022) data present")
    if crisis_rate < CRISIS_BAD_DEBT_RATE_FLOOR:
        failures.append(
            f"crisis bad-debt rate {crisis_rate:.4%} below anchored floor "
            f"{CRISIS_BAD_DEBT_RATE_FLOOR:.1%} ({CRISIS_BAD_DEBT_RATE_FLOOR_SOURCE})"
        )
    if step_up < CRISIS_STEP_UP_MIN_RATIO:
        failures.append(
            f"crisis step-up x{step_up:.2f} below required x{CRISIS_STEP_UP_MIN_RATIO} "
            f"({CRISIS_STEP_UP_SOURCE})"
        )

    all_rows = sorted(pre_rows + crisis_rows, key=lambda r: r.year)
    return CrisisBadDebtResult(
        basis=basis,
        passed=not failures,
        crisis_rate=crisis_rate,
        pre_crisis_rate=pre_rate,
        step_up_ratio=step_up,
        per_year=all_rows,
        failures=failures,
    )


def extract_series_from_run_output(
    run_output: dict, basis: Basis = "headline"
) -> tuple[dict[int, float], dict[int, float]]:
    """Pull (bad_debt_by_year, revenue_by_year) out of a run_output_latest.json
    dict for the requested basis.

    basis="headline"  -> years[*].bad_debt_gbp / years[*].revenue_gbp
                         (the behavioural arrears-engine figure the CFO flagged,
                         summed into the surfaced total_bad_debt_gbp).
    basis="pnl_accrual" -> management_accounts[*].income_statement.bad_debt_gbp
                         / .revenue_gbp (the ledger P&L accrual).
    """
    bd: dict[int, float] = {}
    rev: dict[int, float] = {}
    if basis == "headline":
        for y, blk in run_output.get("years", {}).items():
            bd[int(y)] = float(blk.get("bad_debt_gbp", 0.0))
            rev[int(y)] = float(blk.get("revenue_gbp", 0.0))
    elif basis == "pnl_accrual":
        for y, blk in run_output.get("management_accounts", {}).items():
            inc = blk.get("income_statement", {})
            bd[int(y)] = float(inc.get("bad_debt_gbp", 0.0))
            rev[int(y)] = float(inc.get("revenue_gbp", 0.0))
    else:  # pragma: no cover - guarded by Literal typing
        raise ValueError(f"unknown basis: {basis!r}")
    return bd, rev


def validate_run_output(
    run_output: dict, basis: Basis = "headline"
) -> CrisisBadDebtResult:
    """Convenience: extract the requested basis from a run_output dict and
    validate it in one call."""
    bd, rev = extract_series_from_run_output(run_output, basis)
    return validate_crisis_bad_debt(bd, rev, basis=basis)
