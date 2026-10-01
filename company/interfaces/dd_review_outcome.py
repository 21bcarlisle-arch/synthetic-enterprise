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

__all__ = ["opening_monthly_amount", "reviewed_monthly_amount"]


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
