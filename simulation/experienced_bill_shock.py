"""The bill shock a household actually EXPERIENCES in the year before a renewal -- world-side.

PB4 build, 2026-10-01, from `docs/market_research/what_bill_shock_is.md`. The definition comes first
and the arithmetic follows from it, per population:

  * **A, direct debit** -- the bill shocks nobody; the PAYMENT does. The event is the supplier
    resetting the monthly DD at the annual review, read through the supplier's own door
    (`company.interfaces.dd_review_outcome`). In year one the reference is the amount set at
    sign-up (`opening_monthly_amount`), so "DD set wrong, then reset" -- the page's operational
    cause -- fires in a household's FIRST year, which is the year the old count was blind in.
  * **B, standard credit** -- the shock IS the bill. The event is the year's bills running above
    what the household was led to expect: the quote (the same sign-up amount) in year one, its own
    previous year after that.
  * **C, prepayment** -- out of scope of bill shock entirely. `None`, with the reason, never 0.

WHAT THIS REPLACES, and why it is not a patch to the old window. The world's hazard base today is
`saas.churn_model.build_churn_risk`, which counts MONTHS whose bill differs from the same month a
year earlier by more than 15%, by `abs()`. That is definition B's quantity applied to everybody,
counted per month, and blind until a prior year exists: k = 0 on 156/156 tenure-1 first renewals
against 6.86 shocked months at tenure 2+, which on its own carries the world's whole tenure and
bill-size gradients (`docs/staging/WORKER_FINDING_THE_WORLDS_BILL_SHOCK_COUNT_IS_BLIND_IN_A_
HOUSEHOLDS_FIRST_YEAR_AND_CARRIES_THE_WHOLE_TENURE_GRADIENT_2026-10-01.md`). Widening that window to
reach year one would keep the wrong quantity.

**This module is emitted as ground truth on each renewal event and does NOT yet drive the hazard.**
Swapping the base moves the departure LEVEL as well as its gradients -- `year_level_anchor` was
fitted against the old month count -- and two changes in one run cannot be attributed. The next
pass measures this quantity's tenure gradient on a run, then swaps the base.

A FALL IS NOT A SHOCK. Every trigger the page names is a rise: cold weather, a usage rise, a
catch-up after estimates, a renewal price rise, a DD increase, and Ofgem's own 2022 escalation was
on increases. A DD that falls is money back, and the experience it has -- a credit balance -- is
SLC 14's, handled in `simulation/credit_refund_events.py`, not a reason to leave.

NOT MODELLED, AND SAID SO. The balance a household "does not understand" (definition A's second
trigger) is a communication property, not an arithmetic one, and the world has no record of what
the household was told. The DD reset already carries the arithmetic of a balance -- a year that
ran into debit is exactly a year whose review raises the payment -- so that half is not lost, but
the "did not understand" half is a stated gap, not a zero.
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache

from company.interfaces.dd_review_outcome import opening_monthly_amount, reviewed_monthly_amount
from simulation.household import household_of
from simulation.household_segments import PaymentChannel, payment_channel_for_customer

# ORIGIN: INHERITED, NOT SOURCED. The same 15% the world's old count used
# (`saas.customer_reaction.score_experience_signals`' `bill_shock_threshold`), kept so that the
# swap changes the QUANTITY and not the cut as well -- one variable at a time. What the record
# does NOT establish is what size of rise a household notices: ±5% is a band of ours and Ofgem's
# >100% was an escalation cut, neither a measurement of noticing (`what_bill_shock_is.md`, "What is
# not settled" 4). Doing it properly takes a published noticing threshold, which nobody has.
MATERIAL_RISE_FRACTION = 0.15

POPULATION_LEVEL_PAYMENT = "A_direct_debit"
POPULATION_THE_BILL = "B_standard_credit"
POPULATION_OUT_OF_SCOPE = "C_prepayment"


def _shift_month(period: str, months: int) -> str:
    year, month = (int(part) for part in period.split("-"))
    total = year * 12 + (month - 1) + months
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


@lru_cache(maxsize=None)
def _opening_for_leg(as_of_iso: str, commodity: str, eac: float | None,
                     sold_rate: float | None = None) -> float | None:
    return opening_monthly_amount(
        as_of_iso=as_of_iso,
        commodity=commodity,
        registry_eac_kwh=eac if eac else None,
        band="MEDIUM" if not eac else None,
        contracted_unit_rate_per_mwh_ex_vat=sold_rate,
    )


def sold_unit_rate(customer_id: str, settlement_records: list[dict]) -> float | None:
    """The unit rate on this leg's FIRST bill (£/MWh ex-VAT): consumption-weighted over its first
    settled month, so a time-of-use split or a default tariff reads as what was charged. The
    household holds it on paper, so it crosses the door as a contract fact, not a computed price.
    None where no row of that month carries a rate."""
    rows = [r for r in settlement_records if r.get("customer_id") == customer_id]
    if not rows:
        return None
    first = min(r["settlement_date"][:7] for r in rows)
    kwh = cost = 0.0
    for r in rows:
        rate = r.get("unit_rate_gbp_per_mwh")
        if r["settlement_date"][:7] != first or rate is None:
            continue
        kwh += r.get("consumption_kwh") or 0.0
        cost += rate * (r.get("consumption_kwh") or 0.0)
    return cost / kwh if kwh > 0 else None


def opening_monthly_for_household(household: str, customers: list[dict],
                                  settlement_records: list[dict] | None = None) -> float | None:
    """The monthly amount the household was told at sign-up, summed over its legs -- or None if
    any leg has none (a dual-fuel household quoted for one fuel was not quoted).

    With `settlement_records`, each leg is annualised at the rate it was SOLD at (its first
    bill); without, the door falls back to the cap, which pre-2019 is no quote at all."""
    total = 0.0
    legs = [c for c in customers if household_of(c.get("customer_id", "")) == household]
    if not legs:
        return None
    for c in legs:
        commodity = c.get("commodity", "electricity")
        eac = c.get("eac_kwh") if commodity == "electricity" else c.get("aq_kwh")
        if not c.get("acquisition_date"):
            return None
        sold = (sold_unit_rate(c.get("customer_id", ""), settlement_records)
                if settlement_records is not None else None)
        amount = _opening_for_leg(c["acquisition_date"], commodity, float(eac) if eac else None,
                                  sold)
        if amount is None:
            return None
        total += amount
    return total


def monthly_bills_by_household(settlement_records: list[dict]) -> dict[str, dict[str, float]]:
    """{household: {"YYYY-MM": bill £}} -- the same per-period sum the old count read, keyed by
    the property rather than the supplier's billing grouping."""
    out: dict[str, dict[str, float]] = {}
    for r in settlement_records:
        periods = out.setdefault(household_of(r["customer_id"]), {})
        p = r["settlement_date"][:7]
        periods[p] = periods.get(p, 0.0) + r["revenue_gbp"]
    return out


def _year_monthly_mean(bills: dict[str, float], start: str, end: str) -> float | None:
    months = [v for p, v in bills.items() if start <= p <= end]
    return sum(months) / len(months) if months else None


def experienced_bill_shock(
    *,
    bills: dict[str, float],
    payment_channel: str,
    renewal_period: str,
    first_renewal: bool,
    opening_monthly_gbp: float | None,
) -> dict:
    """The shock experienced in the twelve months before `renewal_period`, by definition.

    Returns {population, shocked (bool | None), rise_fraction, reference, reason}. `shocked` is
    None -- never False -- when the definition cannot be applied, and `reason` says why.
    """
    if payment_channel == PaymentChannel.PREPAYMENT.value:
        return {"population": POPULATION_OUT_OF_SCOPE, "shocked": None, "rise_fraction": None,
                "reference": None, "reason": "prepayment: no bill and no DD -- out of scope"}
    level_payment = payment_channel == PaymentChannel.DIRECT_DEBIT.value
    population = POPULATION_LEVEL_PAYMENT if level_payment else POPULATION_THE_BILL

    this_year = _year_monthly_mean(bills, _shift_month(renewal_period, -12),
                                   _shift_month(renewal_period, -1))
    if this_year is None:
        return {"population": population, "shocked": None, "rise_fraction": None,
                "reference": None, "reason": "no bills in the year before this renewal"}
    if first_renewal:
        reference = opening_monthly_gbp
        if reference is None:
            return {"population": population, "shocked": None, "rise_fraction": None,
                    "reference": "quote", "reason": "no amount was set at sign-up for this "
                    "household (no sold rate and no cap to annualise against, or no consumption)"}
        ref_label = "quote"
    else:
        prior = _year_monthly_mean(bills, _shift_month(renewal_period, -24),
                                   _shift_month(renewal_period, -13))
        if prior is None:
            return {"population": population, "shocked": None, "rise_fraction": None,
                    "reference": "prior_year", "reason": "the prior year is not observed"}
        # Under a level DD the payment in force through this year is the one set at the last
        # review, from the prior year's spend; under standard credit the reference is that
        # year's bills themselves.
        reference = reviewed_monthly_amount(prior * 12.0) if level_payment else prior
        ref_label = "prior_review" if level_payment else "prior_year"
    if not reference or reference <= 0:
        return {"population": population, "shocked": None, "rise_fraction": None,
                "reference": ref_label, "reason": "the reference amount is zero"}

    # What the household meets at this renewal: under DD the new payment on the review letter,
    # under standard credit the year's bills themselves.
    met = reviewed_monthly_amount(this_year * 12.0) if level_payment else this_year
    rise = (met - reference) / reference
    return {"population": population, "shocked": rise > MATERIAL_RISE_FRACTION,
            "rise_fraction": round(rise, 6), "reference": ref_label, "reason": None}


def experienced_bill_shock_at_renewal(
    customer_id: str, commodity: str, renewal_period: str,
    settlement_records: list[dict], customers: list[dict],
) -> dict:
    """The world's call: one household, one renewal. `settlement_records` stop before the
    renewal's own term (Point-in-Time, as `roll_lifecycle_event` already guarantees)."""
    household = household_of(customer_id)
    acquisition = next((c.get("acquisition_date") for c in customers
                        if c.get("customer_id") == customer_id), None)
    # The first anniversary exactly as `saas.churn_model._renewal_periods` dates it (365 days, not
    # twelve calendar months), so the two counts agree on which renewal is a household's first.
    first_renewal = bool(acquisition) and (
        (date.fromisoformat(acquisition) + timedelta(days=365)).isoformat()[:7] == renewal_period
    )
    household_records = [r for r in settlement_records if household_of(r["customer_id"]) == household]
    bills = monthly_bills_by_household(household_records).get(household, {})
    return experienced_bill_shock(
        bills=bills,
        payment_channel=payment_channel_for_customer(customer_id, commodity).value,
        renewal_period=renewal_period,
        first_renewal=first_renewal,
        opening_monthly_gbp=(opening_monthly_for_household(household, customers, household_records)
                             if first_renewal else None),
    )
