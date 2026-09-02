"""Service quality monitor — tracks bill clarity, complaint probability, and bill shock.

A real energy supplier tracks these metrics through its own customer service systems:
- Bill clarity scores (from customer feedback / smart meter accuracy checks)
- Complaint probability (from CRM complaint log)
- Bill shock events (bills > prior period + threshold pct, flagged by billing system)

THE OFGEM ATTRIBUTION ON THESE THREE BANDS IS WITHDRAWN (2026-09-02). This docstring used to
read "Ofgem benchmarks: complaints < 2.5% of bills; clarity > 0.80; bill shock < 0.30%." Not one
of those three is a published Ofgem benchmark:

  * **bill shock.** `docs/market_research/BILL_SHOCK_EVENT_TYPES_ANCHORS.md` §3 searched for a
    formal Ofgem definition of bill shock -- a term, a threshold, or a comparison basis -- and
    recorded the answer verbatim: "Confirmed: no."
  * **complaints.** What Ofgem actually publishes is complaints per 100,000 ACCOUNTS (quarterly
    customer service data portal, `docs/market_research/satisfaction_drivers_and_the_three_bill_shocks.md`
    line 215). This module's quantity is a per-BILL probability. Different denominators, so the
    figure was not merely unsourced, it counted something else. It also never matched the
    constants it claimed to describe: the sentence said 2.5% while the code bands at 5% and 6%.
  * **clarity.** Ofgem publishes no bill-clarity score. It is a Poesys modelled quantity and
    there is nothing outside this repository for it to be a benchmark against.

All three are this project's own working thresholds. They are kept because a band that can fail
is worth more than no band, but none of them is evidence of a regulatory standard and none may be
cited as one. Consumer Duty (FCA 2023) is real and stays: good outcomes for customers — clarity
and bill predictability are direct indicators of compliance.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ServiceQualityRAG(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    #: "We cannot tell" is a result and belongs on the surface. Before 2026-09-02 a missing
    #: bill-shock measurement returned GREEN -- the best branch -- and `overall_rag` ORed it in,
    #: so an unmeasured leg silently improved the verdict.
    NOT_MEASURED = "NOT_MEASURED"


#: THIS PROJECT'S OWN WORKING BANDS, all six. See the module docstring for why the Ofgem
#: attribution they used to carry was withdrawn on 2026-09-02. Each is a BELIEF the company
#: holds about its own service quality; none is CITED, and the docstring says so rather than
#: leaving a reader to infer a regulator stands behind them.
_CLARITY_AMBER = 0.82
_CLARITY_RED = 0.80
_COMPLAINT_AMBER = 0.05
_COMPLAINT_RED = 0.06

#: PERCENTAGE POINTS, and the `_PCT` suffix is load-bearing. These were `_BILL_SHOCK_AMBER = 0.20`
#: carrying the comment `# pct` while every caller compared a FRACTION against them. That is the
#: same units defect that published "Worst bill shock: 2022 (0.58%)" and "| 2022 | 57.5% |" about
#: one number in one document -- see `saas/reporting/annual_report._fmt_shock_pct`. The sole
#: caller now speaks percentages, so a fraction-valued band here was a trap primed to fire: 43.5
#: passed into a 0.20/0.30 band is RED for every year forever. Same values as
#: `annual_report._SHOCK_BAND_AMBER_PCT` / `_SHOCK_BAND_RED_PCT`, in the same units, on purpose.
_BILL_SHOCK_AMBER_PCT = 20.0
_BILL_SHOCK_RED_PCT = 30.0


@dataclass(frozen=True)
class ServiceQualitySnapshot:
    year: int
    avg_clarity: float
    avg_complaint_probability: float
    #: PERCENTAGE POINTS, or `None` for "this year has no bill-shock measurement". Optional
    #: because the one live caller (`saas/reporting/annual_report`) genuinely cannot supply it:
    #: bill shock is two experiences in two populations and the mixed mean this field used to
    #: carry was superseded. `None` is the honest value and the type now admits it.
    avg_bill_shock_pct: Optional[float]
    bills_count: int
    shock_event_count: int

    @property
    def clarity_rag(self) -> ServiceQualityRAG:
        if self.avg_clarity >= _CLARITY_AMBER:
            return ServiceQualityRAG.GREEN
        if self.avg_clarity >= _CLARITY_RED:
            return ServiceQualityRAG.AMBER
        return ServiceQualityRAG.RED

    @property
    def complaint_rag(self) -> ServiceQualityRAG:
        if self.avg_complaint_probability < _COMPLAINT_AMBER:
            return ServiceQualityRAG.GREEN
        if self.avg_complaint_probability < _COMPLAINT_RED:
            return ServiceQualityRAG.AMBER
        return ServiceQualityRAG.RED

    @property
    def bill_shock_rag(self) -> ServiceQualityRAG:
        """FAILS CLOSED. An unmeasured year is `NOT_MEASURED`, never the flattering branch."""
        if self.avg_bill_shock_pct is None:
            return ServiceQualityRAG.NOT_MEASURED
        if self.avg_bill_shock_pct < _BILL_SHOCK_AMBER_PCT:
            return ServiceQualityRAG.GREEN
        if self.avg_bill_shock_pct < _BILL_SHOCK_RED_PCT:
            return ServiceQualityRAG.AMBER
        return ServiceQualityRAG.RED

    @property
    def overall_rag(self) -> ServiceQualityRAG:
        """RED > NOT_MEASURED > AMBER > GREEN, and that ordering is the whole point.

        An unmeasured leg outranks AMBER and GREEN because the verdict it would have produced
        could have been RED and nothing here can rule that out. It does NOT outrank RED: a known
        RED is already the worst answer, and demoting it to "cannot tell" would lose information
        rather than fail closed. The only verdict that survives an unmeasured leg is one that is
        already worse than anything the missing leg could have said.
        """
        rags = [self.clarity_rag, self.complaint_rag, self.bill_shock_rag]
        for verdict in (
            ServiceQualityRAG.RED,
            ServiceQualityRAG.NOT_MEASURED,
            ServiceQualityRAG.AMBER,
        ):
            if verdict in rags:
                return verdict
        return ServiceQualityRAG.GREEN

    @property
    def shock_rate_pct(self) -> Optional[float]:
        """Bill shock events as % of total bills, or `None` when there were no bills.

        FAILS CLOSED for the same reason `bill_shock_rag` does. This returned `0.0` on an empty
        book, which publishes a measured zero -- "no household had a shock" -- from a year where
        the incidence was not measurable at all. No bills is not an incidence of nought.
        """
        if self.bills_count == 0:
            return None
        return self.shock_event_count / self.bills_count * 100


class ServiceQualityMonitor:
    """Accumulates annual service quality snapshots and surfaces trends."""

    def __init__(self) -> None:
        self._snapshots: dict[int, ServiceQualitySnapshot] = {}

    def record(
        self,
        year: int,
        avg_clarity: float,
        avg_complaint_probability: float,
        avg_bill_shock_pct: Optional[float],
        bills_count: int,
        shock_event_count: int,
    ) -> ServiceQualitySnapshot:
        snap = ServiceQualitySnapshot(
            year=year,
            avg_clarity=avg_clarity,
            avg_complaint_probability=avg_complaint_probability,
            avg_bill_shock_pct=avg_bill_shock_pct,
            bills_count=bills_count,
            shock_event_count=shock_event_count,
        )
        self._snapshots[year] = snap
        return snap

    def get(self, year: int) -> Optional[ServiceQualitySnapshot]:
        return self._snapshots.get(year)

    @property
    def all_snapshots(self) -> list[ServiceQualitySnapshot]:
        return sorted(self._snapshots.values(), key=lambda s: s.year)

    @property
    def red_years(self) -> list[ServiceQualitySnapshot]:
        return [s for s in self.all_snapshots if s.overall_rag == ServiceQualityRAG.RED]

    @property
    def amber_years(self) -> list[ServiceQualitySnapshot]:
        return [s for s in self.all_snapshots if s.overall_rag == ServiceQualityRAG.AMBER]

    @property
    def worst_clarity_year(self) -> Optional[ServiceQualitySnapshot]:
        if not self._snapshots:
            return None
        return min(self.all_snapshots, key=lambda s: s.avg_clarity)

    @property
    def worst_complaint_year(self) -> Optional[ServiceQualitySnapshot]:
        if not self._snapshots:
            return None
        return max(self.all_snapshots, key=lambda s: s.avg_complaint_probability)

    @property
    def worst_bill_shock_year(self) -> Optional[ServiceQualitySnapshot]:
        """The worst MEASURED year, or `None` if no year was measured.

        Unmeasured years are skipped rather than compared. `max` over a key that can be `None`
        raises `TypeError` in Python 3, which was a fail-closed accident rather than a design --
        and it would have fired the moment anything called this, because the one live caller now
        records `None` for every year.
        """
        measured = [s for s in self.all_snapshots if s.avg_bill_shock_pct is not None]
        if not measured:
            return None
        return max(measured, key=lambda s: s.avg_bill_shock_pct)

    def is_improving(self) -> bool:
        """True if the last 2 recorded years show improving clarity."""
        snaps = self.all_snapshots
        if len(snaps) < 2:
            return False
        return snaps[-1].avg_clarity > snaps[-2].avg_clarity

    def quality_summary(self) -> str:
        snaps = self.all_snapshots
        if not snaps:
            return "No service quality data recorded."
        unmeasured = [s for s in snaps if s.avg_bill_shock_pct is None]
        lines = [
            "Service Quality Summary",
            "Years recorded: {}".format(len(snaps)),
            "RED years: {}".format(len(self.red_years)),
            "AMBER years: {}".format(len(self.amber_years)),
        ]
        if unmeasured:
            lines.append("Years with no bill-shock measurement: {}".format(len(unmeasured)))
        worst_c = self.worst_clarity_year
        if worst_c:
            lines.append("Worst clarity: {} ({:.3f})".format(worst_c.year, worst_c.avg_clarity))
        worst_s = self.worst_bill_shock_year
        if worst_s:
            lines.append("Worst bill shock: {} ({:.2f}%)".format(worst_s.year, worst_s.avg_bill_shock_pct))
        else:
            # Says so rather than dropping the line. A summary silently one line shorter reads as
            # "no bad year", which is the fail-silent cousin of the GREEN this module used to
            # return for an unmeasured leg.
            lines.append("Worst bill shock: not measured (no year carries a measurement)")
        lines.append("Improving: {}".format(self.is_improving()))
        return chr(10).join(lines)
