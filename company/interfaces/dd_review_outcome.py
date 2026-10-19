"""The company's DD-REVIEW surface — the one place the world may learn what the
supplier SET a customer's monthly Direct Debit to.

WHY THIS MODULE EXISTS (KNIFE pass 3, design B4_billing_mechanics_reached_directly)
-----------------------------------------------------------------------------------
`simulation/dd_balance_book.py` used to do this:

    from company.billing.dd_review import _recommended_monthly

— a **private function**, which the register's B4 block named as the worst of that
design's four crossings and said should go first. It is worse than an ordinary
crossing for a reason that has nothing to do with the edge count: a private helper is
a routine the company is free to change without notice, and a dependency on it is the
one property a real supplier does not grant the world. Renaming `_recommended_monthly`
would have broken the simulated world.

WHAT THE WORLD LEGITIMATELY KNOWS, AND WHAT IT DOES NOT
--------------------------------------------------------
  * Known — **the amount.** A real customer is told their new monthly Direct Debit
    after an annual review ("we're changing your payments to £64 a month"). The
    household's bank balance, its seasonal credit position and the refund it is owed
    at closure all follow from that number, so the world must be able to see it.
  * Not known — **the routine.** The ±5% variance band (a modelling convention
    under the SLC 27.15 duty, not a licence threshold), the increase /
    decrease / maintain classification, the rounding convention, `DDReviewResult`.
    Those are the supplier's review policy. A customer receives the letter; they do
    not receive the pricing desk's spreadsheet.

Importing the private helper handed the world the routine and let it re-derive the
amount for itself. This module publishes only the amount.

WHAT CROSSES, PRECISELY
-----------------------
In: one number the supplier and the customer both already have — the customer's
actual spend over a completed 12-month period, which the supplier billed and the
customer paid.

Out: one number — the standing monthly DD in force after that review. No
`DDReviewResult`, no `DDAction`, no threshold, and deliberately no re-export of
`_recommended_monthly` or `review`. `tests/company/interfaces/
test_dd_review_outcome_seam.py` exists to keep that true and is mutation-proven: a
widened `__all__` or a `review`-returning convenience would restore the removed
dependency WITHOUT creating a single wall edge, because the import would still
terminate on the exempt seam package and the ratchet is blind to that by
construction.

**This is a cut, not laundering.** `company/interfaces/` and `company/billing/` are
both WALKED by `tools/epistemic_wall.py` byte for byte. Nothing moved out of the
instrument's reach; the edge is exempt because it terminates on the sanctioned
crossing surface — the ratchet's own published `SEAM_PACKAGE` remedy — and not
because the measurement stopped looking. Contrast
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §2b, where relocating a
composition root to `tools/` was REFUSED for the reason that does not apply here:
`tools/` is outside `WALL_DIRS` and the walker never looks there.

THE HONEST LIMIT — this is a PULL, and B4 asks for a PUSH
----------------------------------------------------------
B4 as written says the company should EMIT the reviewed amount as an instruction over
the async wall contract (C-S3), with the world's books applying what they receive. This
module does not achieve that half and does not pretend to: the world still asks, per
customer per completed year, at the moment it needs the answer.

The blocker is the same structural one B5 measured and recorded, not a fresh judgement:
the bill dicts `build_dd_balance_book` reads are assembled by
`simulation/run_phase4c_on_phase2b.py::build_monthly_bills`, a SIM composition root
carrying 14 owed edges of its own, so there is no company-side emitter to carry a
`reviewed_monthly_amount` instruction. Stamping one from inside the SIM would mean the
world writing a value it had just pulled from the company and reading its own stamp
back — the shape of a push with the substance of a pull, and a worse artefact than an
honest pull, because the next reader would believe the event contract existed. The push
is owed to `A_composition_lift` and is recorded as owed in §3a of the register.

THE BLOCKER ABOVE IS GONE — UPDATED 2026-08-10 (KNIFE pass 3, `A_composition_lift` step 11).
`build_monthly_bills` is no longer a SIM composition root: bill assembly moved to
`company/billing/monthly_bill_assembly.py`, behind `company/interfaces/bill_assembly.py`.
The company-side emitter this module named as its blocker exists.

This module is still a PULL and the push is still owed — step 11 moved the emitter and
built neither push on top of it, on purpose. Whoever draws that work:
`assemble_monthly_bills` is where a `reviewed_monthly_amount` instruction would be carried,
with `build_dd_balance_book` applying what it receives instead of calling
`reviewed_monthly_amount` per customer-year.

What the pull buys now: the private helper, the review policy and its result type are
unreachable from the SIM, and the remaining dependency is one float at one reviewable
chokepoint.
"""
from __future__ import annotations

# The rule NAMES only: which arm a run puts the review on is the run's choice. What each rule does
# stays behind `reviewed_standing`.
from company.billing.dd_review import DEFAULT_REVIEW_RULE, REVIEW_RULES

__all__ = [
    "DEFAULT_REVIEW_RULE",
    "REVIEW_RULES",
    "billing_account_of",
    "dual_fuel_offset",
    "forward_readings_by_fuel",
    "opening_monthly_amount",
    "reviewed_monthly_amount",
    "reviewed_monthly_amount_at_rates",
    "review_forecast_inputs",
    "review_balance_step_up",
    "review_seeks_balance",
    "reviewed_standing",
    "simple_balance_after_window",
]


def review_seeks_balance() -> bool:
    """Whether the supplier's annual review asks for the debit balance it finds. The policy is the
    supplier's (`company.billing.dd_review.REVIEW_SEEKS_BALANCE`); a run arm may override it."""
    from company.billing.dd_review import REVIEW_SEEKS_BALANCE

    return REVIEW_SEEKS_BALANCE


def dual_fuel_offset(recoverable_debit: float, other_leg_credit: float, on, offers: bool) -> float:
    """What the supplier sets off from a household's credit on its other fuel against this leg's
    recoverable debt at a charge recovery action. See `company.billing.dd_review.dual_fuel_offset_amount`."""
    from company.billing.dd_review import dual_fuel_offset_amount

    return dual_fuel_offset_amount(recoverable_debit, other_leg_credit, on, offers)


def billing_account_of(customer_id: str) -> str:
    """The supplier's billing account for one leg. See `company.billing.dd_review.billing_account_of`."""
    from company.billing.dd_review import billing_account_of as _billing_account_of

    return _billing_account_of(customer_id)


def review_balance_step_up(debit: float, seeks_balance: bool | None = None) -> float:
    """The amount the review adds to the monthly debit to recover a debit balance -- the figure on
    the customer's letter. See `company.billing.dd_review.review_balance_step_up`."""
    from company.billing.dd_review import review_balance_step_up as _step_up

    return _step_up(debit, seeks_balance)


def simple_balance_after_window(entering_balance: float, standing_amount: float, window_bills: list) -> float:
    """The balance a direct-debit account carries out of one completed 12-month window -- what it
    carried in, plus what came in at the standing monthly amount, less what was billed. The world
    already holds every figure this touches (its own issued bills, the standing amount it set); the
    one judgement call -- whether and how a review recovers it -- stays behind `reviewed_standing`,
    which is why this is bookkeeping at the seam rather than a policy decision crossing it. See
    `company.billing.dd_review.simple_balance_after_window` for the one implementation."""
    from company.billing.dd_review import (
        simple_balance_after_window as _simple_balance_after_window,
    )

    return _simple_balance_after_window(entering_balance, standing_amount, window_bills)


def reviewed_monthly_amount(actual_annual_spend_gbp: float) -> float:
    """The standing monthly Direct Debit in force after the supplier reviewed a
    completed year of this customer's actual spend.

    This is the number on the letter. How it was arrived at — what the supplier
    rounds to, what variance band makes it act at all, whether it calls the move an
    increase or a decrease — stays behind this door.
    """
    # Imported INSIDE the function, and the control that found this is the reason.
    # At module level the name lands in this module's namespace, so
    # `from company.interfaces.dd_review_outcome import _recommended_monthly` would
    # hand the world the private routine straight back — with the epistemic ratchet
    # still green, because that import terminates on the exempt seam package. The
    # walker descends into function bodies (`ast.walk`), so nothing about the
    # measurement changes; only the door's namespace narrows to what it exports.
    from company.billing.dd_review import _recommended_monthly

    return _recommended_monthly(actual_annual_spend_gbp)


def reviewed_monthly_amount_at_rates(
    *,
    annual_kwh: float,
    days: int,
    unit_rate_per_mwh_ex_vat: float,
    standing_charge_per_day_ex_vat: float,
    billed_adjustments: float = 0.0,
) -> float:
    """The standing monthly Direct Debit after a review that prices the completed year's
    CONSUMPTION at the rates in force from the review date.

    `reviewed_monthly_amount` resets the debit to what the year cost at the prices it was
    billed at. When prices have risen across the year that sets next year's debit at last
    year's prices, and the shortfall is kept for ever, because the review does not seek the
    balance. On the single-levy run that is about -£11k of the DD book's -£17.8k review lag at
    2018-06 (`SEAT_FINDING_EVERY_SETTLED_BILL_CHARGED_THE_LEVIES_TWICE_2026-10-10.md`). SLC 27.15
    asks for "the best and most current information available", and at the review the
    supplier knows the tariff it is about to charge.

    In: what is on the customer's own bills. That is the year's billed kWh and its days, the
    unit rate (all-in, ex-VAT, per MWh) and the standing charge (per day, ex-VAT) in force from
    the review date, and any catch-up correction billed in the year, which is kept as billed
    (it settles earlier energy at the earlier price). Out: the amount on the letter, rounded as
    the other review rounds it. So under flat rates the two reviews set the same debit.
    """
    from company.billing.dd_review import _recommended_monthly_at_rates

    return _recommended_monthly_at_rates(
        annual_kwh=annual_kwh,
        days=days,
        unit_rate_per_mwh_ex_vat=unit_rate_per_mwh_ex_vat,
        standing_charge_per_day_ex_vat=standing_charge_per_day_ex_vat,
        billed_adjustments=billed_adjustments,
    )


def reviewed_standing(rule: str, completed: list, first_of_new, **kwargs) -> float:
    """The standing monthly Direct Debit the supplier's annual review sets after a completed window.

    In: the review rule the run put the desk on, the window's bills as issued, and the first bill
    of the window being set (or None). All three are what the supplier issued. Out: the amount on
    the letter. Which bills are summed, which rates are read off which bill, and when the review
    falls back to last year's spend are the supplier's review policy, in
    `company/billing/dd_review.py`. Until 2026-10-12 that policy was computed inside
    `simulation/dd_balance_book.py`; the world now asks and is told.

    `**kwargs` carries `own_forecast_plus_balance`'s optional `term_end_iso`,
    `forward_rate_per_mwh_ex_vat` and the balance to clear straight through -- see
    `dd_review.reviewed_standing` for what each does and what each defaults to.
    """
    from company.billing.dd_review import reviewed_standing as _reviewed_standing

    return _reviewed_standing(rule, completed, first_of_new, **kwargs)


def forward_readings_by_fuel(term_forwards: list) -> dict:
    """The supplier's own twelve-month forward readings, per fuel, by the date each was taken --
    from the forward it priced each term from. The world's forward on the same records is never
    read. See `company.billing.dd_review.forward_readings_by_fuel`."""
    from company.billing.dd_review import forward_readings_by_fuel as _forward_readings_by_fuel

    return _forward_readings_by_fuel(term_forwards)


def review_forecast_inputs(completed: list, first_of_new, account_terms: list,
                           forward_readings: list) -> dict:
    """What the supplier's own-forecast review reads besides the bills: the end of the term the
    account is on at the review, and the forward rate it prices the days beyond it at. In: the
    window's bills, the first bill of the window being set, the supplier's own record of the terms
    it sold this account, and its own forward readings for the account's fuel -- all things the
    supplier holds. Out: keyword arguments for `reviewed_standing`, empty where there is nothing
    to split. How the forward rate is formed stays behind this door, in
    `company/billing/dd_review.py`."""
    from company.billing.dd_review import review_forecast_inputs as _review_forecast_inputs

    return _review_forecast_inputs(completed, first_of_new, account_terms, forward_readings)


def opening_monthly_amount(
    *,
    as_of_iso: str,
    commodity: str,
    registry_eac_kwh: float | None = None,
    band: str | None = None,
    contracted_unit_rate_per_mwh_ex_vat: float | None = None,
    contracted_standing_charge_per_day_ex_vat: float | None = None,
) -> float | None:
    """The standing monthly Direct Debit the supplier SET when the account
    opened — or `None` where nothing it holds established one.

    The counterpart to `reviewed_monthly_amount` at the other end of the
    account's life, and the same door in both directions: a real customer is
    told "your payments will be £62 a month" at sign-up exactly as they are told
    the reviewed figure afterwards, so the world must be able to see the amount.

    WHAT CROSSES, PRECISELY
    -----------------------
    In: REGISTRATION FACTS ONLY — the date, the fuel, the industry EAC/AQ where
    the flow carried one, and the consumption band where it did not. Both are
    something the two parties already have.

    THIS DOOR USED TO ACCEPT FOUR SOURCES AND CARRY TWO (2026-09-03). It took
    `metered_annual_kwh` and `declared_annual_kwh` as well, and no caller ever
    passed either, because neither exists at the instant an account opens —
    reasons in `company/billing/annual_consumption_estimate.
    NOT_REACHABLE_AT_OPENING`. They are gone from the signature rather than
    documented as unused: a door whose parameters advertise sources the routine
    behind it cannot reach tells the world something false about the supplier,
    which is the one thing a seam exists to prevent.

    Out: one number, the opening monthly amount.

    What stays behind the door is the whole ROUTINE: the SLC 27.15 precedence
    over those sources, the date-keyed Ofgem TDCV series, **and the price the
    supplier annualised at**. That last one is why this function takes no unit
    rate and no standing charge, and it is not a convenience — the first draft
    of this door DID accept them, which made
    `simulation/run_phase4c_on_phase2b.py` import `company.pricing.
    ofgem_price_cap` and `company.pricing.tariff_comparison` to work them out.
    Two live wall crossings with no disposition, refused by the register at the
    gate. A supplier's own tariff is not something the world computes on its
    behalf; the world asks what the payment was set to and is told.

    **The household's true annual consumption is not a parameter here and must
    never become one** — this door is exactly where that breach would be easiest
    to make by accident.

    THE ONE RATE THAT MAY CROSS (2026-10-01): `contracted_unit_rate_per_mwh_ex_vat`,
    the unit rate on the account's contract, as the supplier's settled book
    carries it (ex-VAT). That is not the excluded case above. The excluded case was
    the world WORKING OUT a price on the supplier's behalf. This is the price
    the supplier already struck and printed on the customer's first bill, so
    both parties hold it. Without it the door annualised every account at the
    default-tariff cap. A fixed deal is not sold at the cap, and before 2019
    there is no cap, so 27 of 31 in-scope first renewals had no quote at all
    (SEAT_FINDING_THE_EXPERIENCED_BILL_SHOCK_IS_STILL_BLIND_IN_YEAR_ONE_...).
    The cap is now only the fallback when no contracted rate is supplied. It is
    not re-applied as a clamp: the renewal desk already ceilings a resi fixed
    strike at it, and a default-tariff rate IS it.

    ...AND THE STANDING CHARGE BESIDE IT (2026-10-01, same day):
    `contracted_standing_charge_per_day_ex_vat`, per day, in the currency's major unit, as the
    settled book carries it. It is printed on the same first bill and crosses for the same
    reason. Without it every leg was quoted the 53p 2024 resi figure, for both fuels and every
    year, while the bills carried the world's dated charge (22p gas in 2016). So a year-one
    quote was over-set and a year-one rise under-read
    (SEAT_FINDING_THE_YEAR_ONE_QUOTE_AND_THE_REVIEW_IT_IS_MET_BY_ARE_ON_DIFFERENT_BASES_...).
    Absent, the 53p fallback stands. It is grossed by the same VAT rule as the rate, so the
    whole quote stays inc-VAT, as the customer is told it.

    `None` is a RESULT and callers must carry it as one: the DD books count
    those customers as unestimated rather than opening them from a bill. It is
    returned when nothing establishes a consumption, and also when no
    contracted rate is supplied and the company holds no published rate for
    that date — before the price cap began in January 2019 there is none in
    this repository, and inventing one to fill the gap is the defect this whole
    atom removes.
    """
    from datetime import date

    from company.billing.annual_consumption_estimate import (
        estimate_annual_consumption,
        opening_monthly_dd_gbp,
    )
    from company.compliance.domain_invariants import vat_rate_for_segment
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date
    from company.pricing.tariff_comparison import STANDING_CHARGE_RESI_P_PER_DAY

    as_of = date.fromisoformat(as_of_iso)

    if contracted_unit_rate_per_mwh_ex_vat is not None:
        # Grossed up so this path stays on the cap's inc-VAT basis: one variable
        # (the rate's LEVEL) moves, not the basis as well.
        rate_per_mwh_inc_vat = contracted_unit_rate_per_mwh_ex_vat * (1.0 + vat_rate_for_segment("resi"))
    else:
        rate_per_mwh_inc_vat = get_cap_unit_rate_for_date(commodity, as_of)
    if rate_per_mwh_inc_vat is None:
        return None

    estimate = estimate_annual_consumption(
        as_of=as_of,
        commodity=commodity,
        registry_eac_kwh=registry_eac_kwh,
        band=band,
    )
    return opening_monthly_dd_gbp(
        estimate,
        # £/MWh -> p/kWh.
        unit_rate_p_kwh=rate_per_mwh_inc_vat / 10.0,
        # The fallback is REUSED, not re-declared: the repo already carries exactly one published
        # resi standing charge, and a fifth declaration of it is a filed finding
        # of its own. It is a 2024 figure applied across the window — a known
        # limitation of that constant, not of this call site.
        standing_charge_p_day=(
            STANDING_CHARGE_RESI_P_PER_DAY
            if contracted_standing_charge_per_day_ex_vat is None
            # major unit/day -> minor unit/day, grossed onto the quote's inc-VAT basis.
            else contracted_standing_charge_per_day_ex_vat * 100.0 * (1.0 + vat_rate_for_segment("resi"))
        ),
    )
