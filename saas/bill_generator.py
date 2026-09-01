"""Bill generation — Phase 4c-4 / Phase 9a (physical simulation layer).

Aggregates a customer's per-settlement-period records (from
`simulation/settlement.run_settlement`) for one billing month into a bill:
total consumption, total amount due, average unit rate, and a *clarity
score* in [0, 1] (1 = very clear, 0 = very confusing).

Per the Key Domain Insight (CLAUDE.md): customer reaction to bills is
non-rational, and arithmetically correct bills frequently produce complaints
when they're hard to understand or jump unexpectedly month-to-month. Two
factors reduce clarity, both seed estimates pending real data:

1. **Tariff structure complexity** — `BASE_CLARITY_BY_CONTRACT_TYPE`. All
   current contracts are `"fixed_1yr"` (single flat rate) — maximally
   clear. Future multi-rate tariffs (e.g. Phase 5's time-of-use) would get a
   lower base.
2. **Consumption volatility within the month** — the coefficient of
   variation (stdev/mean) of daily consumption. A bill covering wildly
   uneven days (e.g. a cold spell, per Phase 4c-2/4c-3) is harder to
   reconcile against a flat unit rate than one covering steady days.
3. **Bill shock** — the percentage change in total amount due versus the
   previous month's bill, if supplied. A big swing is confusing even if both
   bills were individually correct.

Phase 9a: bills now include non-commodity pass-through (network charges +
levies), standing charge, and VAT via saas.non_commodity. The commodity
amount (from settlement records) is separated from non-commodity and
standing so the ledger can track pass-through costs correctly.

Standing-charge double-count fix (2026-07-11): the standing charge is sourced
from the settlement records' own year-calibrated field (folded there by
simulation/hedged_settlement.py / gas_settlement.py) and subtracted back out of
commodity_amount_gbp, rather than being independently recomputed from a flat
rate table and added a second time. See generate_bill() for detail. The
saas.non_commodity flat rate is retained only as a fallback for synthetic/
legacy records that carry no settlement-derived standing-charge field.

This module is pure: plain dicts/lists in, plain dict out. No imports from
`sim/`.
"""

import datetime
import statistics

from saas.non_commodity import non_commodity_rate, standing_charge_rate, vat_rate

BASE_CLARITY_BY_CONTRACT_TYPE = {
    "fixed_1yr": 1.0,
}
DEFAULT_BASE_CLARITY = 0.7

# Reduction in clarity score per unit of consumption coefficient-of-variation
# (stdev/mean of daily consumption_kwh across the billing period).
CONSUMPTION_CV_PENALTY_FACTOR = 0.5

# Reduction in clarity score per 100% change in total bill amount versus the
# previous month, capped at a 100% change (pct change beyond that doesn't
# further reduce clarity — the bill is already as confusing as it gets).
BILL_SHOCK_PENALTY_FACTOR = 0.5

#: The smallest |previous bill| worth expressing a percentage change against. Reused from the £5
#: materiality convention this codebase already applies twice (`monthly_bill_assembly.
#: CATCHUP_MATERIALITY_THRESHOLD_GBP`, `smart_meter_reconciliation.is_material`) for "below this a
#: real supplier does not act" — NOT a new number. Below it, `bill_shock_pct` is None: no
#: meaningful comparison exists, and None is already what a first bill carries.
BILL_SHOCK_BASELINE_FLOOR_GBP = 5.0

#: WHICH DEFINITION OF BILL SHOCK APPLIES IS DECIDED ENTIRELY BY HOW THE HOUSEHOLD PAYS
#: (`docs/market_research/what_bill_shock_is.md`, 2026-09-01, sourced from Ofgem's credit-balance
#: and Direct Debit Market Compliance publications and SLC 27B/21BA). There are TWO experiences in
#: two populations, not one experience with three causes:
#:
#:   "payment"      — a level direct debit. The bill is a statement that arrives and is filed; the
#:                    shock is a MATERIAL CHANGE IN THE AMOUNT COLLECTED (±5% is the SLC 27B review
#:                    trigger; >100% was Ofgem's 2022 escalation cut), or a balance the household
#:                    does not understand. ~74% of GB domestic households.
#:   "bill"         — standard credit, and variable direct debit. The shock IS the bill. ~13%.
#:   "out_of_scope" — prepayment. No bill to be shocked by and no direct debit to be changed; the
#:                    equivalent experience is an unaffordable top-up or self-disconnection, a
#:                    different measurement with a different remedy. ~13%.
#:
#: THE "prepayment" BRANCH IS UNREACHABLE IN THIS WORLD TODAY and is written anyway.
#: `simulation.household_segments.PaymentChannel` has two members, so our book is 0% prepayment
#: against a published ~13%; the non-DD remainder is folded into standard credit. That fold is a
#: recorded simplification made for a DIFFERENT question (`dd_attribution_confound_w2_10.md`, DD
#: discount confounding) and it is the wrong one here, because bill shock is DEFINED by payment
#: method rather than merely correlated with it. Naming the branch is not the repair — adding the
#: channel or excluding those households explicitly is, and it is owed separately. It is written
#: because a definition with no place to put prepayment is exactly how prepayment got folded into
#: standard credit in the first place.
BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL = {
    "direct_debit": "payment",
    "standard_credit": "bill",
    "prepayment": "out_of_scope",
}

#: The value when NO channel was supplied. Its own value, never one of the two real ones: a caller
#: that did not say how the household pays has not told us which definition applies, and defaulting
#: that to either would publish an unmeasured attribution as a measured one.
UNKNOWN_BILL_SHOCK_POPULATION = "unknown"

MIN_CLARITY_SCORE = 0.0
MAX_CLARITY_SCORE = 1.0


def bill_movement(
    total_amount_gbp: float, previous_bill_total_gbp: float | None
) -> tuple[float | None, float | None, float | None]:
    """`(movement, shock, baseline)` for one bill against the one before it.

    THE ONE PLACE THIS ARITHMETIC LIVES. It was written twice — here and again in
    `company.billing.monthly_bill_assembly`, which recomputes it after folding a catch-up
    correction onto the bill. Two copies of one definition is the shape that put five
    implementations of the VAT rule in this tree and a defect fixed in one of them still live in
    another a month later. The recompute now calls this.

    **`movement` is SIGNED and positive means the bill went UP.** It is the honest quantity: the
    relative change between what the household was asked for this month and last. The denominator
    is a magnitude because the sign of the baseline is not information about how far the bill
    moved (an issued total can be negative — a catch-up credit — and 169 of this book's bills are).

    **`shock` is `None` when the bill FELL, and it is not `0.0`.** A shock is an increase. The
    established definition says so for both populations
    (`docs/market_research/what_bill_shock_is.md`): for standard credit the three published
    triggers — cold weather, a usage change, a catch-up after estimates — are all upward, and for
    a level direct debit the regulated trigger is a payment *rise*. Measured on the published
    record, **45.9% of the movements this codebase called shocks (5,161 of 11,255) are bills that
    went DOWN**, including catch-up refunds: the world read a supplier returning money as an event
    that reduced clarity, identically to one that took money.

    `None` rather than `0.0` because a bill that fell has not been measured at zero shock — no
    shock happened to it. `0.0` would enter every downstream mean and drag it toward a number no
    household experienced, which is this project's `a_default_zero_parameter_turns_an_unobservable
    _cause_into_a_published_measured_zero` class. `None` is already a fully supported value at
    every consumer, because a first bill has always carried it. A bill that did NOT move keeps
    `0.0`: that IS measured, and it is zero.

    THIS IS WHY `simulation.contact_propensity` KEEPS ITS `>= 0` REFUSAL RATHER THAN LOSING IT.
    That guard crashed the publish cycle for 75 minutes on 2026-09-01 on a shock of -1.4434, and
    the guard was right: a negative value should never have reached it. The repair is here, at the
    definition, not there — wrapping the consumer in another `abs()` or an `or 0` would have
    reinstated exactly the fold this removes while looking like resilience.

    `baseline` is `None`, and so are the other two, when the previous total is missing or too
    small to divide by (`BILL_SHOCK_BASELINE_FLOOR_GBP`).
    """
    if (
        previous_bill_total_gbp is None
        or abs(previous_bill_total_gbp) < BILL_SHOCK_BASELINE_FLOOR_GBP
    ):
        return None, None, None
    movement = (total_amount_gbp - previous_bill_total_gbp) / abs(previous_bill_total_gbp)
    return movement, (movement if movement >= 0.0 else None), previous_bill_total_gbp


def consumption_coefficient_of_variation(settlement_records: list[dict]) -> float:
    """Coefficient of variation (population stdev / mean) of total daily
    consumption_kwh across the distinct settlement_dates in
    `settlement_records`. Returns 0.0 if there's only one day or the mean is
    zero (no variation to report)."""
    daily_totals: dict[str, float] = {}
    for record in settlement_records:
        daily_totals[record["settlement_date"]] = (
            daily_totals.get(record["settlement_date"], 0.0) + record["consumption_kwh"]
        )

    totals = list(daily_totals.values())
    if len(totals) < 2:
        return 0.0
    mean = statistics.mean(totals)
    if mean == 0:
        return 0.0
    return statistics.pstdev(totals) / mean


def generate_bill(
    customer_id: str,
    settlement_records: list[dict],
    contract_type: str,
    previous_bill_total_gbp: float | None = None,
    segment: str = "resi",
    commodity: str = "electricity",
    payment_channel: str | None = None,
) -> dict:
    """Aggregate one customer's `settlement_records` for one billing month.

    Phase 9a: bills include non-commodity pass-through, standing charge, VAT.

    Returns:
      {customer_id, period_start, period_end, total_consumption_kwh,
       commodity_amount_gbp, non_commodity_amount_gbp, standing_charge_gbp,
       vat_gbp, total_amount_gbp, average_unit_rate_gbp_per_mwh,
       clarity_score, bill_shock_pct, payment_channel,
       bill_shock_population, segment, commodity}

    `payment_channel` (2026-09-01) is how this household pays — the one attribute that decides
    WHICH DEFINITION of bill shock applies to it (`BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL`). A
    real supplier knows it: it set the mandate up with the customer. It is passed IN rather than
    looked up, because this is company/SaaS-side code and the channel lives world-side — the same
    injection shape `saas/opex_ledger.py` already uses for this same field.

    THIS ARGUMENT CHANGES NO ARITHMETIC. `bill_shock_pct` is still the difference between two bills
    for every household including the ~70% for whom the bill is not what they pay. The bill now
    SAYS which definition it should have been measured under; making the measurement follow the
    definition is a separate change that moves published figures, pre-registered in
    `WORKER_PREREGISTRATION_WHAT_TELLING_THE_SHOCK_MEASURE_HOW_THE_HOUSEHOLD_PAYS_MUST_SHOW_
    2026-09-01`. This step exists so that split can be attributed when it happens.

    Raises ValueError if `settlement_records` is empty.
    """
    if not settlement_records:
        raise ValueError("settlement_records must be non-empty")

    dates = sorted(record["settlement_date"] for record in settlement_records)
    total_consumption_kwh = sum(record["consumption_kwh"] for record in settlement_records)
    raw_revenue_gbp = sum(record["revenue_gbp"] for record in settlement_records)

    period_start_date = datetime.date.fromisoformat(dates[0])
    period_end_date = datetime.date.fromisoformat(dates[-1])
    days_in_period = (period_end_date - period_start_date).days + 1

    # Standing charge -- SINGLE authoritative source (2026-07-11 double-count
    # fix). Real settlement records (simulation/hedged_settlement.py,
    # gas_settlement.py) already fold the year-calibrated, Ofgem-sourced daily
    # standing charge into `revenue_gbp` AND expose it as its own per-record
    # field (`standing_charge_gbp` for electricity, `gas_standing_charge_gbp`
    # for gas). We take the standing charge from that field and SUBTRACT it back
    # out of revenue so `commodity_amount_gbp` is genuinely pure commodity
    # revenue -- what the field name and its tests already claim it to be.
    #
    # Before this fix generate_bill() ADDITIONALLY recomputed a flat,
    # non-year-varying standing charge from saas.non_commodity and added it a
    # second time, so every resi/SME bill charged the standing charge twice
    # (once hidden inside commodity_amount_gbp, once as the visible line) and
    # every I&C bill charged a resi-rate standing charge that should be zero.
    #
    # The flat saas.non_commodity fallback is used ONLY for synthetic/legacy
    # records that carry no settlement-derived standing-charge field (test
    # fixtures pre-dating Phase 62); those records also never fold a standing
    # charge into revenue_gbp, so nothing is subtracted in that path.
    sc_field = "gas_standing_charge_gbp" if commodity == "gas" else "standing_charge_gbp"
    records_carry_sc = any(sc_field in record for record in settlement_records)
    if records_carry_sc:
        standing_charge_gbp = sum(record.get(sc_field, 0.0) for record in settlement_records)
        commodity_amount_gbp = raw_revenue_gbp - standing_charge_gbp
    else:
        standing_charge_gbp = days_in_period * standing_charge_rate(commodity, segment)
        commodity_amount_gbp = raw_revenue_gbp

    # Effective per-day standing charge for the calculation-transparency
    # breakdown (director's "Days x standing charges" ask): derived from the
    # actual billed standing charge so days_in_period x this == standing_charge_gbp
    # exactly, even across a year boundary where the daily rate itself changes.
    standing_charge_gbp_per_day = (
        standing_charge_gbp / days_in_period if days_in_period > 0 else 0.0
    )

    # Non-commodity pass-through: network charges + environmental levies
    billing_year = int(dates[0][:4])
    non_commodity_amount_gbp = total_consumption_kwh / 1000 * non_commodity_rate(commodity, segment, year=billing_year)

    # VAT on full pre-tax bill (5% domestic, 20% business)
    subtotal_gbp = commodity_amount_gbp + non_commodity_amount_gbp + standing_charge_gbp
    vat_gbp = subtotal_gbp * vat_rate(segment)
    total_amount_gbp = subtotal_gbp + vat_gbp

    average_unit_rate_gbp_per_mwh = (
        commodity_amount_gbp / (total_consumption_kwh / 1000) if total_consumption_kwh > 0 else 0.0
    )

    clarity_score = BASE_CLARITY_BY_CONTRACT_TYPE.get(contract_type, DEFAULT_BASE_CLARITY)
    clarity_score -= consumption_coefficient_of_variation(settlement_records) * CONSUMPTION_CV_PENALTY_FACTOR

    # THE BASELINE IS PUBLISHED BESIDE THE RATIO, and that is the whole of this change
    # (2026-09-01, `WORKER_FINDING_BILL_SHOCK_IS_THREE_CAUSES_AND_A_SIGN_COLLAPSED_INTO_ONE_ABS`).
    # `bill_shock_pct` is a ratio against `previous_bill_total_gbp`, and that number reached no
    # artefact -- so on the published book the stored value could be reproduced from the published
    # bills on only 3,198 of 10,654 consecutive pairs (30.0%). The 70% that could not are the ones
    # whose PREVIOUS bill was ESTIMATED (89% of them): that bill's total was later revised by the
    # catch-up reconciliation, so the stored ratio is a difference against a number that no longer
    # exists anywhere. A figure frozen before the rows it summarises were mutated is this project's
    # `figures_on_a_superseded_clock` class, and it was sitting inside the field that drives
    # satisfaction, clarity and contact propensity.
    #
    # Publishing the denominator does not fix the conflation of causes or the `abs()` -- both are
    # separately owed and both move published figures, so both are their own pre-registered
    # one-variable changes. It fixes the thing that has to come first: until the denominator is on
    # the bill, NOTHING can check either of them, because the ratio cannot be recomputed by anyone.
    # This change moves no financial figure; it only makes an existing one checkable.
    # A BASELINE TOO SMALL TO DIVIDE BY IS REFUSED, not divided by anyway.
    #
    # Moving the baseline to the ISSUED bill made near-zero denominators reachable: a catch-up can
    # settle a month to a few pence. The published run then carried a maximum `bill_shock_pct` of
    # **7,575.8** and an "average bill shock" for 2022 of **6.2 (620%)** against 0.3-0.6 in every
    # other year — a headline figure on the dashboard and in the annual report, dominated entirely
    # by division by nearly nothing. A percentage change against a baseline of £0.05 is not a
    # quantity; it is this project's most-filed publishing defect wearing a ratio's clothes.
    #
    # `None` IS ALREADY A SUPPORTED VALUE — a first bill has no baseline, so every consumer already
    # handles it (`contact_propensity` takes `float | None`, the annual report filters on
    # `is not None`, and clarity is only penalised when a shock exists). Refusing is therefore
    # cheaper than capping AND more honest: a cap would publish a bounded wrong number where the
    # truth is that no meaningful comparison exists.
    #
    # THE £5 IS NOT A NEW CONSTANT. It is the materiality convention this codebase already applies
    # twice — `monthly_bill_assembly.CATCHUP_MATERIALITY_THRESHOLD_GBP` and
    # `smart_meter_reconciliation.is_material` — for "below this, a real supplier does not act".
    # A bill a supplier would not bother correcting is a bill it should not be dividing by either.
    # THE DIRECTION IS CARRIED, and it decides whether a shock happened at all -- see
    # `bill_movement`, which is now the one place this arithmetic lives. The numerator used to be
    # wrapped in `abs()`, so a bill that FELL was reported as a shock of the same size as one that
    # rose, and the clarity penalty below was applied to a household the supplier had just
    # refunded.
    bill_movement_pct, bill_shock_pct, bill_shock_baseline_gbp = bill_movement(
        total_amount_gbp, previous_bill_total_gbp
    )
    if bill_shock_pct is not None:
        clarity_score -= min(bill_shock_pct, 1.0) * BILL_SHOCK_PENALTY_FACTOR

    clarity_score = max(MIN_CLARITY_SCORE, min(MAX_CLARITY_SCORE, clarity_score))

    return {
        "customer_id": customer_id,
        "period_start": dates[0],
        "period_end": dates[-1],
        "total_consumption_kwh": total_consumption_kwh,
        "commodity_amount_gbp": commodity_amount_gbp,
        "non_commodity_amount_gbp": non_commodity_amount_gbp,
        "standing_charge_gbp": standing_charge_gbp,
        "vat_gbp": vat_gbp,
        "total_amount_gbp": total_amount_gbp,
        "average_unit_rate_gbp_per_mwh": average_unit_rate_gbp_per_mwh,
        "clarity_score": clarity_score,
        #: The INCREASE, or None where the bill did not rise. Never a negative "shock" and never
        #: a `0.0` standing in for one — see `bill_movement`.
        "bill_shock_pct": bill_shock_pct,
        #: THE SIGNED MOVEMENT, always present when a baseline exists, positive meaning the bill
        #: went up. The decrease is NOT deleted by the sign fix: 45.9% of what this codebase used
        #: to call a shock is here, under a name that says what it is. What a large DECREASE does
        #: to a household is a real question with no published magnitude behind it — Ofgem's
        #: definition-A experience is "a credit or debit balance they do not understand", which is
        #: about the payment and the balance rather than the bill — so it drives nothing here. A
        #: named gap rather than an invented coefficient.
        "bill_movement_pct": bill_movement_pct,
        #: The denominator both ratios were actually taken against. None exactly when
        #: `bill_movement_pct` is None (a first bill has nothing to be measured against), so the
        #: pair is either both-present or both-absent and a reader never has to guess which.
        "bill_shock_baseline_gbp": bill_shock_baseline_gbp,
        #: How the household pays, and therefore which of the two definitions of bill shock its
        #: `bill_shock_pct` should be read under. `None`/"unknown" exactly when the caller did not
        #: say — see UNKNOWN_BILL_SHOCK_POPULATION for why that is not silently one of the two.
        "payment_channel": payment_channel,
        "bill_shock_population": BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL.get(
            payment_channel, UNKNOWN_BILL_SHOCK_POPULATION
        ),
        "segment": segment,
        "commodity": commodity,
        # Calculation-transparency breakdown (2026-07-10, director page comment
        # on /customers/: "Days x standing charges. Prices x days at that
        # price. We need to be able to explain the maths properly"). Both
        # days_in_period and standing_charge_gbp_per_day were already computed
        # locally above to derive standing_charge_gbp -- simply never exposed.
        # standing_charge_gbp_per_day is now derived from the actual billed
        # standing charge (standing_charge_gbp / days_in_period) rather than a
        # separate rate-table lookup, so the two can never disagree.
        # Full time-of-use (multiple rate bands per day) is a separate,
        # larger architecture gap -- the tariff engine has no multi-rate-per-
        # day concept at all yet -- registered separately, not attempted here.
        "days_in_period": days_in_period,
        "standing_charge_gbp_per_day": standing_charge_gbp_per_day,
    }
