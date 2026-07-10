"""Segment capital-employed allocation + ROCE discipline (Maturity Map B2,
B2_OPEX_TAXONOMY_EXPANSION.md "SEGMENT DISCIPLINE", 2026-07-10 director-direct NTFY).

"Allocate capital employed per segment (working capital, credit/settlement
exposure, collateral) and report segment ROCE against a director-set hurdle;
persistent under-hurdle forces a governed decision artefact (reprice / fix /
exit) -- cross-subsidy must be visible and decided, never silent."

Design choices, made honest rather than invented:

- WORKING CAPITAL per segment is directly attributable: it is that segment's
  real outstanding customer balance (accounts receivable), summable per
  customer -> segment with no allocation key needed.
- CREDIT/SETTLEMENT EXPOSURE and COLLATERAL are portfolio-level wholesale
  trading figures (company/trading/wholesale_credit_exposure.py,
  initial_margin_register.py) with no direct per-segment attribution in this
  codebase -- there is no real mechanism linking a specific segment's
  consumption to a specific counterparty's margin call. These are therefore
  ALLOCATED pro-rata by each segment's share of total revenue (a documented,
  reasoned allocation basis, not a directly-measured figure) -- callers must
  treat capital_employed_gbp as partially allocated, not fully bottom-up.

- The director's own ROCE hurdle rate is required input, never invented (same
  discipline as B2(b)'s AI-compute costing-basis precedent) -- hurdle_pct=None
  means "not yet set"; every check returns None/unknown rather than a
  fabricated pass/fail in that case.

R12 (anti-goal-seek) applies: these figures are a diagnostic of where capital
is tied up and whether it earns its keep, never tuned toward a target.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def segment_capital_employed_gbp(
    segment_working_capital_gbp: dict[str, float],
    segment_revenue_share: dict[str, float],
    total_collateral_and_exposure_gbp: float,
) -> dict[str, float]:
    """working capital (directly attributable) + a pro-rata share of the
    portfolio's total collateral + credit/settlement exposure, allocated by
    each segment's real revenue share. segment_revenue_share values should sum
    to ~1.0 across the whole book; a segment absent from one input but present
    in the other is treated as 0.0 for the missing side."""
    segments = set(segment_working_capital_gbp) | set(segment_revenue_share)
    result = {}
    for seg in segments:
        working_capital = segment_working_capital_gbp.get(seg, 0.0)
        allocated_exposure = segment_revenue_share.get(seg, 0.0) * total_collateral_and_exposure_gbp
        result[seg] = round(working_capital + allocated_exposure, 2)
    return result


def segment_roce_pct(
    segment_net_profit_gbp: dict[str, float],
    segment_capital_employed: dict[str, float],
) -> dict[str, float | None]:
    """Return on Capital Employed per segment. None (not 0.0 or an error) when
    capital employed is zero or negative -- ROCE is genuinely undefined there,
    a real diagnostic finding rather than a divide-by-zero to hide."""
    result: dict[str, float | None] = {}
    for seg, capital in segment_capital_employed.items():
        profit = segment_net_profit_gbp.get(seg, 0.0)
        if capital <= 0:
            result[seg] = None
        else:
            result[seg] = round(profit / capital * 100.0, 2)
    return result


def segments_under_hurdle(
    segment_roce: dict[str, float | None], hurdle_pct: float | None
) -> dict[str, Any]:
    """Which segments currently sit below the director's hurdle. hurdle_pct=None
    means the director hasn't set one yet -- returns hurdle_set=False and an
    empty under_hurdle list rather than silently picking a default (never guess
    a number that is explicitly the director's own risk appetite to set)."""
    if hurdle_pct is None:
        return {"hurdle_set": False, "hurdle_pct": None, "under_hurdle": []}
    under = sorted(
        seg for seg, roce in segment_roce.items()
        if roce is not None and roce < hurdle_pct
    )
    return {"hurdle_set": True, "hurdle_pct": hurdle_pct, "under_hurdle": under}


@dataclass
class SegmentROCEHistory:
    """Tracks segment ROCE across runs/years so PERSISTENT (not one-off)
    under-hurdle performance can be distinguished -- a single bad year isn't
    grounds for a reprice/fix/exit decision, but the same segment missing the
    hurdle repeatedly is."""
    _by_year: dict[str, dict[str, float | None]] = field(default_factory=dict)

    def record(self, year: str, segment_roce: dict[str, float | None]) -> None:
        self._by_year[year] = dict(segment_roce)

    def consecutive_years_under_hurdle(self, segment: str, hurdle_pct: float, as_of_years: list[str]) -> int:
        """Counts back from the END of as_of_years (most recent last) while the
        segment stays strictly under hurdle; stops at the first year it isn't
        (or is missing/None, i.e. unmeasured -- doesn't count as evidence
        either way, but breaks the streak since it isn't confirmed-under)."""
        count = 0
        for year in reversed(as_of_years):
            roce = self._by_year.get(year, {}).get(segment)
            if roce is not None and roce < hurdle_pct:
                count += 1
            else:
                break
        return count


def decision_artefacts_needed(
    history: SegmentROCEHistory,
    segments: list[str],
    years_in_order: list[str],
    hurdle_pct: float | None,
    min_consecutive_years: int = 2,
) -> list[dict[str, Any]]:
    """Governed decision artefact: segments persistently below hurdle force a
    NAMED decision (reprice / fix / exit) -- this function only FLAGS the need
    for one, it never picks the decision itself (that stays with the director/
    board, per B2_OPEX_TAXONOMY_EXPANSION.md's 'cross-subsidy must be visible
    and decided, never silent'). Returns [] if hurdle_pct is None (not set)."""
    if hurdle_pct is None:
        return []
    artefacts = []
    for seg in segments:
        streak = history.consecutive_years_under_hurdle(seg, hurdle_pct, years_in_order)
        if streak >= min_consecutive_years:
            artefacts.append({
                "segment": seg,
                "years_below_hurdle": streak,
                "hurdle_pct": hurdle_pct,
                "decision_needed": "reprice | fix cost-to-serve | exit segment",
                "status": "AWAITING DIRECTOR/BOARD DECISION",
            })
    return artefacts
