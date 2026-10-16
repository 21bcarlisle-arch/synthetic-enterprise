from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class DDAction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


# Variance beyond ±5% triggers a DD adjustment. The DUTY is Ofgem SLC 27.15 (set
# and revise the DD on "the best and most current information available"); the
# ±5% is NOT in the licence -- there is no SLC 27B, and SLC 27.13-27.16 name no
# numeric trigger. It is a widely used supplier review band, so it stands here as
# a MODELLING CONVENTION, not a licence requirement.
# Source: docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md
_VARIANCE_THRESHOLD_PCT = 5.0


@dataclass(frozen=True)
class DDReviewResult:
    customer_id: str
    review_date: date
    current_dd_gbp: float          # monthly DD amount
    actual_annual_spend_gbp: float # actual spend over 12 months
    recommended_monthly_gbp: float # rounded to nearest pound
    variance_pct: float            # (actual - implied_annual) / implied_annual * 100
    action: DDAction


def _recommended_monthly(actual_annual: float) -> float:
    """Round up to nearest pound for DD amount."""
    monthly = actual_annual / 12.0
    return round(monthly + 0.5)   # ceiling-round to pound


def priced_annual_inc_vat_at_rates(
    *,
    annual_kwh: float,
    days: int,
    unit_rate_per_mwh_ex_vat: float,
    standing_charge_per_day_ex_vat: float,
    billed_adjustments: float = 0.0,
) -> float:
    """`X`: the annual figure `consumption_at_rates_in_force` prices, before rounding to a monthly
    amount -- the completed year's billed kWh and days at the rates in force from the review date,
    grossed for VAT, plus any catch-up billed in the year. Exported so a reader of the figure (the
    DD book's own legs tool) prices the SAME number `reviewed_standing` does, rather than carrying
    a second copy of the arithmetic -- the VAT-rule shape of five implementations and one bug."""
    from company.compliance.domain_invariants import vat_rate_for_segment
    ex_vat = annual_kwh / 1000.0 * unit_rate_per_mwh_ex_vat + days * standing_charge_per_day_ex_vat
    return ex_vat * (1.0 + vat_rate_for_segment("resi")) + billed_adjustments


def _recommended_monthly_at_rates(
    *,
    annual_kwh: float,
    days: int,
    unit_rate_per_mwh_ex_vat: float,
    standing_charge_per_day_ex_vat: float,
    billed_adjustments: float = 0.0,
) -> float:
    """The completed year's consumption priced at the rates in force from the review date, grossed
    for VAT, plus any catch-up billed in the year, rounded as `_recommended_monthly` rounds.
    Published through `company.interfaces.dd_review_outcome.reviewed_monthly_amount_at_rates`."""
    return _recommended_monthly(priced_annual_inc_vat_at_rates(
        annual_kwh=annual_kwh, days=days,
        unit_rate_per_mwh_ex_vat=unit_rate_per_mwh_ex_vat,
        standing_charge_per_day_ex_vat=standing_charge_per_day_ex_vat,
        billed_adjustments=billed_adjustments,
    ))


def priced_annual_inc_vat_blended(
    *,
    annual_kwh: float,
    total_days: int,
    known_days: int,
    unit_rate_known_per_mwh_ex_vat: float,
    unit_rate_forward_per_mwh_ex_vat: float,
    standing_charge_per_day_ex_vat: float,
    billed_adjustments: float = 0.0,
) -> float:
    """`X` for `own_forecast_plus_balance`, before the balance addition and before rounding: the
    trailing-12-month billed kWh and days, priced at the account's own known rate for the days its
    current term still covers (`known_days`, clipped to `[0, total_days]`) and the company's own
    forward estimate for the days beyond it, grossed for VAT, plus any in-year catch-up.
    `known_days == total_days` collapses this to `priced_annual_inc_vat_at_rates` -- the shape when
    no term boundary falls inside the forecast year, or none is supplied."""
    from company.compliance.domain_invariants import vat_rate_for_segment
    known_days = max(0, min(total_days, known_days))
    forward_days = total_days - known_days
    blended_rate = (
        known_days * unit_rate_known_per_mwh_ex_vat + forward_days * unit_rate_forward_per_mwh_ex_vat
    ) / total_days
    ex_vat = annual_kwh / 1000.0 * blended_rate + total_days * standing_charge_per_day_ex_vat
    return ex_vat * (1.0 + vat_rate_for_segment("resi")) + billed_adjustments


def _recommended_monthly_forecast_plus_balance(
    *,
    annual_kwh: float,
    total_days: int,
    known_days: int,
    unit_rate_known_per_mwh_ex_vat: float,
    unit_rate_forward_per_mwh_ex_vat: float,
    standing_charge_per_day_ex_vat: float,
    billed_adjustments: float = 0.0,
    balance_to_clear_gbp: float = 0.0,
) -> float:
    """`priced_annual_inc_vat_blended` plus the balance the account carries into the review,
    recovered over the same twelve months it forecasts, rounded as `_recommended_monthly` rounds.
    The balance is added POST-vat (it is cash already on the statement, not a further supply) and
    symmetrically -- a credit lowers the debit exactly as a debit raises it. Neither the sign
    convention nor the twelve-month clearing period is published; both are modelling choices, filed
    as GAPs in `docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md` §6."""
    x = priced_annual_inc_vat_blended(
        annual_kwh=annual_kwh, total_days=total_days, known_days=known_days,
        unit_rate_known_per_mwh_ex_vat=unit_rate_known_per_mwh_ex_vat,
        unit_rate_forward_per_mwh_ex_vat=unit_rate_forward_per_mwh_ex_vat,
        standing_charge_per_day_ex_vat=standing_charge_per_day_ex_vat,
        billed_adjustments=billed_adjustments,
    )
    return _recommended_monthly(x + balance_to_clear_gbp)


def simple_balance_after_window(entering_balance_gbp: float, standing_gbp: float, window_bills: list) -> float:
    """The balance the account carries out of one completed 12-month window: what came in
    (`standing_gbp`, collected once for each of the window's twelve months) less what was billed
    over it, on top of whatever it carried in. No charge-recovery barring -- that is a separate,
    existing toggle (`simulation.dd_balance_book.build_dd_balance_book`'s `seek_balance_at_review`)
    applied afterwards against the book's own real collection calendar; this is the simple running
    figure a review clerk reads off the bills, and what `own_forecast_plus_balance` recovers."""
    billed = sum(float(b["total_amount_gbp"]) for b in window_bills)
    return entering_balance_gbp + standing_gbp * 12.0 - billed


#: Whether the annual review asks for the debit balance it finds and recovers it through the debit.
#: Ofgem (Direct Debit Market Compliance Review: Progress Update, 2 Feb 2023): "where a consumer
#: account is in a debit position, suppliers commonly add this amount on to the Direct Debit amount
#: and smooth the cost over the next 12 months." So True is the published practice; False is the
#: review as it ran until now, kept as the default until the 2026-10-19 publish lands. Source and
#: GAPs: docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md §8.
REVIEW_SEEKS_BALANCE = False
#: The same Ofgem sentence: "smooth the cost over the next 12 months".
BALANCE_RECOVERY_MONTHS = 12


def review_balance_step_up(debit_gbp: float, seeks_balance: bool | None = None) -> float:
    """What the review adds to the monthly debit to recover a debit balance of `debit_gbp` (positive
    = owed by the customer, after any part SLC 21BA bars at the review). Zero when the review does
    not seek the balance (`seeks_balance`, default `REVIEW_SEEKS_BALANCE`) or there is no debit."""
    seeks = REVIEW_SEEKS_BALANCE if seeks_balance is None else seeks_balance
    if not seeks or debit_gbp <= 0.0:
        return 0.0
    return debit_gbp / BALANCE_RECOVERY_MONTHS


#: How the annual review sizes next year's debit. `last_year_spend` resets it to what the completed
#: year cost at the prices it was billed at. `consumption_at_rates_in_force` prices that year's
#: billed kWh and days at the rates on the first bill of the year being set (SLC 27.15, "most
#: current information"). `own_forecast_plus_balance` is the director's ruling of 2026-10-11
#: (console, 04:20Z): the company's own twelve-month forecast (the same trailing-12-month billed
#: kWh and days `consumption_at_rates_in_force` reads), priced at the account's known rate for the
#: days its current term still covers and the company's own forward estimate beyond -- degrading to
#: the whole year at the known rate when no term boundary or forward estimate is supplied (both are
#: supplied by `review_forecast_inputs` from the run's term records and the company's own forward,
#: wired 2026-10-13; `docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md` §7) --
#: plus the balance the
#: account carries into the review, recovered over the same twelve months. All three agree when
#: prices are flat and the account carries no balance. Moved here from
#: `simulation/dd_balance_book.py` (2026-10-12): which rule the review applies is the supplier's
#: review policy; the world chooses only which policy arm a run is on.
REVIEW_RULES = ("last_year_spend", "consumption_at_rates_in_force", "own_forecast_plus_balance")
DEFAULT_REVIEW_RULE = "last_year_spend"


def bill_days(b) -> int:
    """Days a bill covers, as printed on it (`days_in_period`), else from its period dates."""
    if b.get("days_in_period"):
        return int(b["days_in_period"])
    end = date.fromisoformat(b["period_end"][:10])
    start = date.fromisoformat(b["period_start"][:10]) if b.get("period_start") else end.replace(day=1)
    return (end - start).days + 1


def _review_date(first_of_new) -> date:
    """The day the reviewed amount starts to be collected: the new window's first bill's start."""
    if first_of_new.get("period_start"):
        return date.fromisoformat(first_of_new["period_start"][:10])
    return date.fromisoformat(first_of_new["period_end"][:10]).replace(day=1)


def forward_readings_by_fuel(term_forwards: list) -> dict[str, list[tuple[str, float]]]:
    """The company's own 12-month forward, one reading per fuel per as-of date, sorted by date.

    In: the run's `basis_risk_terms` rows -- the forward the company priced each term from, dated
    by that term's start. Only `company_fwd_gbp_per_mwh` is read; the world's own forward on the
    same row never is. Where one date carries more than one reading (two terms priced the same day
    from different books), the median stands for the date."""
    by_day: dict[tuple[str, str], list[float]] = {}
    for r in term_forwards:
        v = r.get("company_fwd_gbp_per_mwh")
        if v is None or not r.get("term_start"):
            continue
        by_day.setdefault((r.get("commodity", "electricity"), r["term_start"][:10]), []).append(float(v))
    out: dict[str, list[tuple[str, float]]] = {}
    for (fuel, day), vals in sorted(by_day.items()):
        vals.sort()
        mid = len(vals) // 2
        out.setdefault(fuel, []).append(
            (day, vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2.0))
    return out


def _reading_on(readings: list[tuple[str, float]], day: date) -> float | None:
    """The latest reading dated on or before `day`; None before the first."""
    iso = day.isoformat()
    got = None
    for d, v in readings:
        if d > iso:
            break
        got = v
    return got


def review_forecast_inputs(completed: list, first_of_new, account_terms: list,
                           forward_readings: list[tuple[str, float]]) -> dict:
    """`own_forecast_plus_balance`'s term end and forward rate for one review, from what the
    company holds at the review date: its own record of the term it sold the account, and its own
    forward readings for the account's fuel.

    The term end is that of the account's term in force on the review date. It is returned only
    when it falls inside the forecast year (the completed window's billed days from the review
    date); a term running the whole year needs no forward. The forward rate is the known unit rate
    on the new window's first bill moved by the change in the company's 12-month forward between
    the start of that term (when the known rate was set) and the review date. That 1:1
    pass-through of wholesale into the retail unit rate, with no losses uplift, is a stated belief,
    not a published figure: `docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md`
    §7. Without a forward reading at both dates only the term end is returned, and
    `reviewed_standing` then prices the whole year at the known rate.

    Returns `{}` when there is no first bill, no rate on it, or no term in force; otherwise
    `term_end_iso` and, where the readings allow, `forward_rate_per_mwh_ex_vat`."""
    if first_of_new is None or not first_of_new.get("average_unit_rate_gbp_per_mwh"):
        return {}
    review = _review_date(first_of_new)
    in_force = [t for t in account_terms
                if t.get("term_start") and t.get("term_end")
                and date.fromisoformat(t["term_start"][:10]) <= review < date.fromisoformat(t["term_end"][:10])]
    if not in_force:
        return {}
    term = max(in_force, key=lambda t: t["term_start"][:10])
    term_end = date.fromisoformat(term["term_end"][:10])
    if (term_end - review).days >= sum(bill_days(b) for b in completed):
        return {}
    out: dict = {"term_end_iso": term_end.isoformat()}
    now = _reading_on(forward_readings, review)
    then = _reading_on(forward_readings, date.fromisoformat(term["term_start"][:10]))
    if now is not None and then is not None:
        out["forward_rate_per_mwh_ex_vat"] = max(
            0.0, float(first_of_new["average_unit_rate_gbp_per_mwh"]) + now - then)
    return out


def priced_annual_for_review(
    rule: str,
    completed: list,
    first_of_new,
    *,
    term_end_iso: str | None = None,
    forward_rate_per_mwh_ex_vat: float | None = None,
) -> tuple[float, bool]:
    """`X`, the annual figure the review prices before any balance and before rounding, and whether
    it was priced at rates (False: the review fell back to last year's spend, which it does for
    `last_year_spend`, with no first bill, or where that bill or the year's bills lack the fields).
    The one implementation `reviewed_standing` rounds and `tools/dd_book_legs` decomposes."""
    if rule not in REVIEW_RULES:
        raise ValueError(f"unknown DD review rule {rule!r}; expected one of {REVIEW_RULES}")
    spend = sum(float(b["total_amount_gbp"]) for b in completed)
    if rule == "last_year_spend" or first_of_new is None:
        return spend, False
    unit = first_of_new.get("average_unit_rate_gbp_per_mwh")
    sc = first_of_new.get("standing_charge_gbp_per_day")
    if not unit or sc is None or any(b.get("total_consumption_kwh") is None for b in completed):
        return spend, False
    annual_kwh = sum(float(b["total_consumption_kwh"]) for b in completed)
    days = sum(bill_days(b) for b in completed)
    billed_adjustments = sum(float(b.get("catchup_adjustment_gbp") or 0.0)
                              for b in completed if b.get("catchup_applied"))
    if rule == "consumption_at_rates_in_force":
        return priced_annual_inc_vat_at_rates(
            annual_kwh=annual_kwh, days=days,
            unit_rate_per_mwh_ex_vat=float(unit),
            standing_charge_per_day_ex_vat=float(sc),
            billed_adjustments=billed_adjustments,
        ), True
    # own_forecast_plus_balance
    known_days = days
    if term_end_iso is not None:
        known_days = (date.fromisoformat(term_end_iso[:10]) - _review_date(first_of_new)).days
    forward_rate = (float(forward_rate_per_mwh_ex_vat)
                     if forward_rate_per_mwh_ex_vat is not None and known_days < days
                     else float(unit))
    return priced_annual_inc_vat_blended(
        annual_kwh=annual_kwh, total_days=days, known_days=known_days,
        unit_rate_known_per_mwh_ex_vat=float(unit),
        unit_rate_forward_per_mwh_ex_vat=forward_rate,
        standing_charge_per_day_ex_vat=float(sc),
        billed_adjustments=billed_adjustments,
    ), True


def reviewed_standing(
    rule: str,
    completed: list,
    first_of_new,
    *,
    term_end_iso: str | None = None,
    forward_rate_per_mwh_ex_vat: float | None = None,
    balance_to_clear_gbp: float = 0.0,
) -> float:
    """The standing monthly debit the review after `completed` (one window's bills) sets.

    Where the rates in force cannot be read off the window's first bill (no such bill, or a bill
    without the rate fields), the review falls back to last year's spend: there is nothing more
    current to price at.

    `term_end_iso`, `forward_rate_per_mwh_ex_vat` and `balance_to_clear_gbp` are read only by
    `own_forecast_plus_balance`, and are each optional there too: with no `term_end_iso` (or one
    that does not fall inside the forecast year) and no `forward_rate_per_mwh_ex_vat`, the whole
    year prices at the known rate -- the same figure `consumption_at_rates_in_force` returns -- and
    with no `balance_to_clear_gbp` (default 0.0) nothing is added for it. The two existing rules
    ignore all three; a caller that does not pass them sees byte-identical behaviour to before this
    rule existed. `review_forecast_inputs` forms the first two from the records the company holds.
    """
    x, priced = priced_annual_for_review(
        rule, completed, first_of_new,
        term_end_iso=term_end_iso, forward_rate_per_mwh_ex_vat=forward_rate_per_mwh_ex_vat)
    if priced and rule == "own_forecast_plus_balance":
        return _recommended_monthly(x + balance_to_clear_gbp)
    return _recommended_monthly(x)


def review(
    customer_id: str,
    review_date: date,
    current_dd_gbp: float,
    actual_annual_spend_gbp: float,
) -> DDReviewResult:
    """Compute the ADDR outcome for a single customer."""
    implied_annual = current_dd_gbp * 12.0
    if implied_annual == 0:
        variance_pct = 0.0
    else:
        variance_pct = (actual_annual_spend_gbp - implied_annual) / implied_annual * 100.0
    recommended = _recommended_monthly(actual_annual_spend_gbp)
    if variance_pct > _VARIANCE_THRESHOLD_PCT:
        action = DDAction.INCREASE
    elif variance_pct < -_VARIANCE_THRESHOLD_PCT:
        action = DDAction.DECREASE
    else:
        action = DDAction.MAINTAIN
    return DDReviewResult(
        customer_id=customer_id,
        review_date=review_date,
        current_dd_gbp=current_dd_gbp,
        actual_annual_spend_gbp=actual_annual_spend_gbp,
        recommended_monthly_gbp=recommended,
        variance_pct=round(variance_pct, 1),
        action=action,
    )


@dataclass
class DDReviewBook:
    """Tracks annual direct debit review outcomes across the portfolio."""

    _reviews: List[DDReviewResult] = field(default_factory=list)

    def record(self, result: DDReviewResult) -> None:
        self._reviews.append(result)

    def run_review(
        self,
        customer_id: str,
        review_date: date,
        current_dd_gbp: float,
        actual_annual_spend_gbp: float,
    ) -> DDReviewResult:
        result = review(customer_id, review_date, current_dd_gbp, actual_annual_spend_gbp)
        self._reviews.append(result)
        return result

    def latest_review(self, customer_id: str) -> Optional[DDReviewResult]:
        matches = [r for r in self._reviews if r.customer_id == customer_id]
        return max(matches, key=lambda r: r.review_date) if matches else None

    def overdue_for_review(
        self,
        as_of: date,
        last_review_dates: Dict[str, date],
        months: int = 12,
    ) -> List[str]:
        """Customer IDs whose last review was >months months ago."""
        overdue = []
        for cid, last in last_review_dates.items():
            months_elapsed = (as_of.year - last.year) * 12 + (as_of.month - last.month)
            if months_elapsed > months:
                overdue.append(cid)
        return overdue

    def summary(self) -> dict:
        n = len(self._reviews)
        if n == 0:
            return {
                "total_reviews": 0,
                "increase_count": 0,
                "decrease_count": 0,
                "maintain_count": 0,
                "avg_variance_pct": 0.0,
            }
        return {
            "total_reviews": n,
            "increase_count": sum(1 for r in self._reviews if r.action == DDAction.INCREASE),
            "decrease_count": sum(1 for r in self._reviews if r.action == DDAction.DECREASE),
            "maintain_count": sum(1 for r in self._reviews if r.action == DDAction.MAINTAIN),
            "avg_variance_pct": round(
                sum(r.variance_pct for r in self._reviews) / n, 1
            ),
        }
