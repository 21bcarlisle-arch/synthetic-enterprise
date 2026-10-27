"""The company's RENEWAL RATE CHAIN — every writer that moves the rate a
customer contracts at, in the order they fire.

WHY THIS MODULE EXISTS (KNIFE pass 3, design `A_composition_lift`, step 24)
-------------------------------------------------------------------------------
`simulation/run_phase2b.py::main()` used to import the company's portfolio
learning premium (`company.pricing.tariff_engine`), its realised-margin recovery
surcharge (`company.pricing.margin_feedback`) and its price-cap clamp
(`company.pricing.ofgem_price_cap`), and run all three inline in the world's
per-term loop — including the eligibility rules that decide WHICH renewals each
one applies to.

None of that is world physics. What the world owns is that a term ended, that a
renewal happened on a date, what the customer consumed and what the published
market and cap schedules said. What rate the supplier then quotes — how much it
adds back for a portfolio that has been under-earning, how much it recovers from
a term it lost money on, whether it reads the domestic cap as binding on this
product — is the supplier's own pricing policy, and it is ALLOWED TO BE WRONG.
That wrongness is the quantity the coupled triad scores.

THE GROUP TEST (§3m), APPLIED AND PASSED
----------------------------------------
§3m's test for a group is "do they feed ONE total?", and §3q's answer was no, so
it landed two doors and said so. Here the answer is yes, and the total is a
single number: **the unit rate the customer contracts at.** The term is struck at
one rate; the premium multiplies it; the surcharge multiplies that; the
profitability uplift adds to that; the VALUE ARM adds what this account is worth
rather than what it cost; the cap clamps the result. Six writers, one number, and
the arithmetic is a chain — reorder any two of them and the answer changes. That
is why they are one door and not six.

THE SIXTH WRITER IS THE REASON THIS DOOR EARNS ITS DESIGN (2026-08-26,
`docs/design/THE_VALUE_CYCLE_REALISED_AB.md`). The value arm was built on
2026-08-25 and had no caller but a harness tool, and the thing that made wiring
it safe was already here: it needs a CEILING, because run unbounded against the
real book it chose margins between £60 and £200/MWh against a flat £2, and the
cap clamp it needs is writer 4. Placing it at 3b rather than giving it its own
ceiling is the one-door argument paying for itself — "the cap clamps what the
uplift added" was written about writer 3 and turned out to be about this one.

The fourth writer, the unprofitability uplift, went behind its OWN door in step
22 (`company/interfaces/customer_profitability.py`) at a time when the other four
were still inline in the world. It is called from HERE now rather than from the
world, which is the whole reason the ORDER is no longer something the world can
get wrong: before this cut the sequence premium -> surcharge -> uplift -> cap was
four separate blocks in a 2,800-line function, and nothing anywhere asserted it.

WHAT CROSSES, PRECISELY
-----------------------
In: what a supplier genuinely has at a renewal — who the customer is, the term
start, the product, how many terms they have had, the rate the term was struck
at, its own realised margin rates on completed terms, its own prior-term margin
and revenue for this customer, whether this is a domestic account, and its own
settled records.

Out: a `RenewalRateChain` — the contracted rate, the decomposed spans, and the
per-writer log entries. No engine, no cap table, no premium coefficient, no
eligibility predicate.

THE ELIGIBILITY RULES THAT MOVED WITH THEM, named rather than left to be found
------------------------------------------------------------------------------
Each writer carries its own "does this renewal qualify" test, and each was a
condition in the world's loop before this cut:

  * the premium applies from the customer's SECOND term (`term_index >= 1`) and
    only where the supplier has at least one completed term to learn from;
  * the surcharge applies from the second term and only where a prior-term margin
    exists for this customer;
  * the cap clamp applies to DOMESTIC accounts on a FIXED product — the
    supplier's own reading of who the cap binds, which a real supplier can read
    wrong and be fined for;
  * every one of them is skipped where there is no locked rate to move (flex and
    deemed terms have none).

They are the supplier's rules about its own products, so they belong on this side
of the wall. Leaving them at the call site is what `A_composition_lift` means by
a composition problem: the import was not the crossing, the DECISION was.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import date

from company.compliance.domain_invariants import (
    refuse_discretionary_rate_below_own_cost_floor,
    vat_rate_for_segment,
)
from company.crm.churn_model import ARREARS_STATE_UNKNOWN
from company.interfaces.customer_profitability import renewal_unit_rate_uplift
from company.policy.decision_policy import DEFAULT_BELIEF_OWN_BOOK, active_policy
from company.pricing.margin_feedback import compute_margin_surcharge
from company.pricing.ofgem_price_cap import (
    get_cap_unit_rate_for_date,
    get_multi_register_cap_unit_rate_for_date,
    get_payment_method_cap_unit_rate_ex_vat,
)
from company.pricing.renewal_desk import pre_margin_unit_rate
from company.pricing.tariff_engine import (
    PORTFOLIO_PREMIUM_LOOKBACK,
    compute_portfolio_premium,
)
from company.pricing.tou_desk import offers_tou
from company.pricing.value_based_renewal import (
    STAGE_PRICED as VALUE_ARM_STAGE_PRICED,
)
from company.pricing.value_based_renewal import renewal_margin_uplift
from saas.payment_behaviour import CREDIT_RISK_BY_CUSTOMER, DEFAULT_CREDIT_RISK
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

__all__ = ["RenewalRateChain", "bill_the_shared_rise", "cap_ceiling_ex_vat", "decide_renewal_rate"]


def cap_ceiling_ex_vat(
    commodity: str, on_date: date, *, multi_register: bool, net_of_epg: bool = True,
    payment_method: str | None = None,
) -> float | None:
    """The domestic cap unit rate on the strike's own basis: EX-VAT, GBP/MWh.

    `get_cap_unit_rate_for_date` returns Ofgem's published figure, which INCLUDES VAT at 5%.
    Every rate this chain writes is ex-VAT: VAT is added on the bill. Clamping one against the
    other let a strike sit up to 5% above the legal ceiling once VAT was added, and the company's
    own check passed it. That was 28 of 117 first terms in the default world
    (`SEAT_FINDING_THE_28_ACCOUNTS_ABOVE_THE_CAP_ARE_EX_VAT_STRIKES_CEILINGED_AT_THE_INC_VAT_CAP_2026-10-01.md`).
    The world's `hedged_settlement` fixed the same defect on 2026-08-25.

    `multi_register` is REQUIRED, with no default: a term the company sells as ToU is graded
    against the multi-register benchmark (SLC 28AD.4), 0.4-8% below single-rate, and a default of
    single-rate is the fail-open that let 15 of 27 ToU first terms sit above their lawful ceiling.
    Gas has one benchmark, so `multi_register` on gas is refused rather than ignored.

    `net_of_epg` is passed through to the published lookup; see `get_cap_unit_rate_for_date`.

    `payment_method`, where given, lowers a single-rate ceiling to the method's own cap column
    when that is lower: min(published level, column), which is the published level for standard
    credit in every window and the prepayment column in most. Direct debit is the published level. Without it the
    ceiling is the published level, which is the DD column, and a prepayment default tariff raised
    by writers 1-2 was clamped back to the DD level, over its own cap: all 547 SVT unit-rate
    breaches on the 871f674a2 book (`docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`,
    choice 7). The multi-register benchmark takes no method column, because the commons carries
    none for it.

    The VAT divided out is the rate on `on_date` for this fuel: domestic electricity is zero-rated
    from 2026-10-01 to 2027-03-31, and dividing that window's cap by 1.05 understated the
    electricity ceiling by about 4.8%.
    """
    if multi_register:
        if commodity != "electricity":
            raise ValueError(f"no multi-register cap benchmark exists for {commodity!r}")
        inc_vat = get_multi_register_cap_unit_rate_for_date(on_date, net_of_epg=net_of_epg)
    else:
        inc_vat = get_cap_unit_rate_for_date(commodity, on_date, net_of_epg=net_of_epg)
    if inc_vat is None:
        return None
    ceiling = inc_vat / (1.0 + vat_rate_for_segment("resi", fuel=commodity, on=on_date))
    # Direct debit IS the published level; the model's own DD column sits up to 1.3% off it.
    if payment_method in (None, "direct_debit") or multi_register:
        return ceiling
    column = get_payment_method_cap_unit_rate_ex_vat(commodity, on_date, payment_method)
    return ceiling if column is None else min(ceiling, column)

# The premium and the surcharge both learn from COMPLETED terms, so neither can
# apply to a customer's first one. The world used to spell this as
# `term_index >= 1` at two call sites; it is one supplier rule, named once.
MIN_TERM_INDEX_FOR_LEARNED_ADJUSTMENT = 1

def _priced_for_target(lookback: list[float],
                       priced_for_rates: list[float | None] | None) -> float | None:
    """The mean margin rate the lookback's own terms were priced for, or `None` if any is unstated.

    THE TARGET ON THE SAME BASIS AS THE MEASUREMENT (2026-10-14). `PORTFOLIO_TARGET_MARGIN_RATE`
    (8%, no source) was compared with a margin that counted the standing charge as profit; no
    published source sets what margin a supplier should aim for, and the cap's EBIT allowance is a
    comparator, not an aim (`docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md`).
    What the company does know is what its own strike priced each term to earn. The premium closes
    the gap between that and what the term earned. All or nothing: a mean over the terms that
    happen to state it would compare one window of rates with another window of targets.
    """
    if priced_for_rates is None:
        return None
    window = priced_for_rates[-len(lookback):]
    if len(window) != len(lookback) or any(t is None for t in window):
        return None
    return sum(window) / len(window)


def portfolio_position(portfolio_margin_rates: list[float],
                       priced_for_rates: list[float | None] | None = None) -> dict | None:
    """What the supplier's own P&L says about its recent margin on this commodity, and the
    premium that reading implies — held CONTINUOUSLY, whether or not it moves a rate.

    `None` where the supplier has no completed term of this commodity yet: there is no position
    to hold, which is a different quantity from a position of zero, and a caller that wrote 0.0
    here would be recording a reading nobody took.

    SPLIT OUT OF WRITER 1, and the split is the point rather than tidiness. Both figures are
    things the company knows about its own book at every priced term. Writer 1 wrote them down
    only on the renewals where the premium happened to survive `abs(...) > 1e-6` and move the
    rate, so the record of a continuously-held quantity carried the shape of an event.

    Measured 2026-09-06 on `run_output_3851553ec`: `mean_recent_margin_rate` and
    `portfolio_premium_pct` reached 149 of 164 households, and the fifteen missing are not
    fifteen accounts the company knew nothing about — they are accounts where the premium
    rounded to nothing. That is the same accounting accident as `company_eac_kwh`, which the
    company computed for everyone and wrote down only at renewals, and which
    `tools/r1_inference_ceiling.py::OBSERVABLE_FIELD_SCOPE` declares a DEFECT rather than a
    truth about the field for exactly this reason.

    ONE IMPLEMENTATION, called by both writers of it. `decide_renewal_rate` below reads this
    function and so does the world's account-state record, through
    `company/interfaces/renewal_rate_chain.py`. A second inlined `sum(lookback)/len(lookback)`
    at the other call site is how one quantity becomes two that disagree.
    """
    if not portfolio_margin_rates:
        return None
    lookback = portfolio_margin_rates[-PORTFOLIO_PREMIUM_LOOKBACK:]
    target = _priced_for_target(lookback, priced_for_rates)
    premium = (compute_portfolio_premium(lookback) if target is None
               else compute_portfolio_premium(lookback, target=target))
    return {
        "recent_margin_rates": [round(r, 4) for r in lookback],
        "mean_recent_margin_rate": round(sum(lookback) / len(lookback), 4),
        # What the same terms were priced to earn, on the same basis. `None` where the history
        # does not say (a caller that handed rates alone), and then the 8% literal answers.
        "target_margin_rate": None if target is None else round(target, 4),
        "portfolio_premium_pct": round(premium * 100, 2),
        # THE UNROUNDED FRACTION, kept beside the published percentage because it is what
        # multiplies the rate. Rounding to 2dp first and dividing back would move the rate the
        # customer contracts at, which is not a presentation decision.
        "portfolio_premium_fraction": premium,
    }


# The supplier's reading of who the domestic price cap binds. A cap is a ceiling
# on a standard domestic product; it is not the supplier's licence to ignore it
# on everything else, and a supplier that reads this wrong is the failure mode
# the compliance side of the coupled triad exists to catch.
#
# `svt` is the product SLC 28AD binds first ("Evergreen (SVT), Deemed, and default fixed-term
# contracts", `docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`). It
# was missing until 2026-10-01, and writers 1-3 moved 630 of 2,333 capped-year SVT segments above
# the published cap, up to x1.38, at the rate settlement bills. A fixed tariff the customer CHOSE
# is outside 28AD, so a fixed renewal is no longer clamped (2026-10-02): the renewal desk's
# SVT-anchored competitive ceiling and the household's own churn decision bound it instead.
CAPPED_TARIFF_TYPES = ("svt",)
#: NOT the law: this supplier's ACQUISITION rule. A fix quoted to win a customer above the default
#: tariff they already have wins nobody, so the term a customer is won on is quoted no higher than
#: the published cap. Without it, writer 4's removal from `fixed` let first terms in 2021-22 sit up
#: to x3.55 the cap (`SEAT_FINDING_A_CHOSEN_FIXED_RENEWAL_IS_OUTSIDE_THE_CAP_AND_A_FIRST_TERM_IS_HELD_BY_THE_ACQUISITION_RULE_2026-10-02.md`).
ACQUISITION_HELD_AT_CAP_TARIFF_TYPES = ("fixed",)
#: The cap binds a default tariff on what the supplier RECEIVES, and during the EPG HM Treasury
#: paid the supplier the gap between the EPG and the cap. So an SVT segment's ceiling is the
#: published cap, not min(cap, EPG). The world's SVT strike is that cap, ex-VAT, with the receipt
#: as its own leg (`simulation/svt_rates`).
EPG_MADE_WHOLE_TARIFF_TYPES = ("svt",)


def held_at_published_cap(tariff_type: str, term_index: int) -> bool:
    """Whether a domestic term's rate is held at or under the published cap: always for a default
    tariff (the law), and for a fixed only on the term the customer is won on (`term_index == 0`,
    the acquisition rule above). A fixed RENEWAL is the customer's choice and is not held."""
    return tariff_type in CAPPED_TARIFF_TYPES or (
        term_index == 0 and tariff_type in ACQUISITION_HELD_AT_CAP_TARIFF_TYPES)


@dataclass
class RenewalRateChain:
    """What the supplier decided this renewal's rate is, and how it got there.

    Deliberately NOT frozen and deliberately holding the same dict objects in
    more than one list: `contracted` is stamped back onto every writer's own
    entry once the chain closes, so a reader of any single entry can see the
    rate the customer actually ended up on rather than mistaking one link for
    the whole. Copying them apart would break that stamp.
    """

    unit_rate_gbp_per_mwh: float | None
    #: The bad-debt allowance the fixed strike carries, GBP/MWh (B12); 0.0 where none is added.
    bad_debt_allowance_gbp_per_mwh: float = 0.0
    components: list[dict] = field(default_factory=list)
    chain_entries: list[dict] = field(default_factory=list)
    dynamic_pricing_entries: list[dict] = field(default_factory=list)
    margin_feedback_entries: list[dict] = field(default_factory=list)
    profitability_uplift_entries: list[dict] = field(default_factory=list)
    #: WRITER 3b's own log, kept apart from `profitability_uplift_entries` even though both are
    #: additive £/MWh moves. They answer different questions -- "is this account losing money"
    #: versus "what is this account worth" -- and a realised A/B has to be able to attribute a
    #: difference to ONE of them. Empty on the control arm, which is how a reader tells a run
    #: that priced flat from one that priced per customer and happened to land near flat.
    value_arm_entries: list[dict] = field(default_factory=list)
    #: ONE ROW PER RENEWAL THIS CHAIN SAW, whatever the arm did with it -- including the renewals
    #: the arm was never eligible to price, and including every renewal on the CONTROL arm.
    #:
    #: `value_arm_entries` above is the arm's DECISIONS; this is its DENOMINATOR, and until
    #: 2026-08-28 nothing carried one. `decision_shape.priced` read 25 on a book of 210 billing
    #: accounts, and the artefact had no way to say whether the other renewals were never offered
    #: by the world, refused by a guard, or priced flat -- three different facts that all present
    #: as an absent log line. A per-decision claim whose denominator cannot be counted is not a
    #: measurement, so the denominator is now written down at the same site as the decision.
    arm_funnel_entries: list[dict] = field(default_factory=list)
    decomposition: dict | None = None


def _stayer_default_ex_vat(commodity: str, term_start: str,
                           own_default_inc_vat: float | None) -> float | None:
    """What a domestic household that refuses this fix is billed: the company's OWN default
    tariff, ex-VAT. Before the cap (2019) there is no published ceiling but there is still a
    default the household rolls onto; from 2019 the cap is that default's price."""
    if own_default_inc_vat:
        return float(own_default_inc_vat) / (1.0 + vat_rate_for_segment("resi"))
    if commodity not in ("electricity", "gas"):
        return None
    return cap_ceiling_ex_vat(commodity, date.fromisoformat(term_start[:10]), multi_register=False)


def _floor_a_discount(rate_before: float, discounted: float, cost_floor: float | None) -> float:
    """`discounted`, raised no higher than `cost_floor` and never above `rate_before`: a discount
    stops at cost, and a rate that entered below cost is not lifted by a writer that only cuts."""
    if cost_floor is None or discounted >= rate_before:
        return discounted
    return max(discounted, min(rate_before, cost_floor))


def decide_renewal_rate(
    *,
    customer_id: str,
    billing_account: str,
    commodity: str,
    term_start: str,
    tariff_type: str | None,
    term_index: int,
    struck_unit_rate_gbp_per_mwh: float | None,
    portfolio_margin_rates: list[float],
    prior_term_margin_gbp: float | None,
    prior_term_revenue_gbp: float,
    is_domestic: bool,
    segment: str | None = None,
    settled_records: list[dict],
    customer: dict,
    arrears_state: str | None = None,
    receivable: dict | None = None,
    payment_method: str | None = None,
    default_belief_rate: float | None = None,
    own_default_tariff_inc_vat_gbp_per_mwh: float | None = None,
    company_forward_per_mwh: float | None = None,
    locked_policy_cost_per_mwh: float | None = None,
    locked_network_cost_per_mwh: float | None = None,
    portfolio_priced_for_rates: list[float | None] | None = None,
) -> RenewalRateChain:
    """Decide the rate this renewal is contracted at.

    Keyword-only on purpose: twelve positional arguments across a wall is how a
    caller ends up passing the wrong observable without either side noticing.

    `portfolio_margin_rates` is the supplier's own realised margin rate per
    completed term for this commodity, OLDEST FIRST — the whole history, not a
    window. How far back the supplier looks is its own parameter and is applied
    here; handing it a pre-sliced window would put the supplier's lookback depth
    back in the world's hands, which is the crossing this door removes.

    `prior_term_margin_gbp` is `None` where the supplier has no completed term
    for this customer — distinct from a completed term that made £0.

    `customer` is the record as the world holds it, read for METERING FACTS only, through the
    same `tou_desk.offers_tou` the ToU offer reads: it decides which cap benchmark writer 4 grades
    this term against. Required, so no caller can reach the single-rate benchmark by omission.

    `company_forward_per_mwh` and the two locked costs are what the company's own offer for
    this term priced off; with the capital charge, they are the term cost a discount stops at.
    `None` where the term has no offer to read them from, and then no discount is given (writer 1).
    """
    unit_rate = struck_unit_rate_gbp_per_mwh
    # THE STRIKE'S BAD-DEBT ALLOWANCE (B12, 2026-10-15): a fixed term carries the bad-debt charge the
    # company has learned per GBP billed off its own ledger (`default_belief_rate`, the same belief
    # the value arm reads), and so does the floor a discount stops at, because it is a cost of the
    # term. Not the settled lines' `bad_debt_gbp`: that is the world's incidence, which no supplier
    # sees. `None` (a business account: no published row) adds nothing. Knowledge: the
    # renewal-decision page, "What a fixed strike carries for levies and bad debt".
    believed_loss_share = (
        default_belief_rate
        if active_policy().renewal_default_belief == DEFAULT_BELIEF_OWN_BOOK else None)
    bad_debt_allowance = (unit_rate * believed_loss_share
                          if tariff_type == "fixed" and unit_rate is not None
                          and believed_loss_share is not None else 0.0)
    if bad_debt_allowance:
        unit_rate += bad_debt_allowance
    rate_original = unit_rate
    # THE FLOOR IS THE TERM'S OWN COST, CAPITAL INCLUDED (2026-10-13). It was `own_cost_floor`
    # (forward + the two locked costs), which leaves out the capital charge the strike prices in
    # (~1.2% of forward pre-2023, ~3.7% after). Writer 1 then cut 496 of 698 renewals on seed 61001
    # into that band: above the floor, under the term's cost
    # (`SEAT_FINDING_WRITER_ONE_DISCOUNTS_INTO_THE_CAPITAL_CHARGE_2026-10-13.md`). The same number
    # the value arm measures its margin from, so a discount and the arm stop at one cost.
    cost_floor = pre_margin_unit_rate(
        company_forward_per_mwh, term_start, locked_policy_cost_per_mwh,
        locked_network_cost_per_mwh)
    if cost_floor is not None:
        cost_floor += bad_debt_allowance

    result = RenewalRateChain(unit_rate_gbp_per_mwh=unit_rate,
                              bad_debt_allowance_gbp_per_mwh=bad_debt_allowance)

    # WRITER 1 — the portfolio learning premium. The supplier looks at what it
    # actually earned on its last few completed terms of this commodity and
    # closes part of the gap to its target margin on the next rate it quotes.
    if (
        unit_rate is not None
        and term_index >= MIN_TERM_INDEX_FOR_LEARNED_ADJUSTMENT
        and len(portfolio_margin_rates) >= 1
    ):
        position = portfolio_position(portfolio_margin_rates, portfolio_priced_for_rates)
        portfolio_prem = position["portfolio_premium_fraction"]
        # A DISCOUNT MAY COST MARGIN; IT MAY NEVER TAKE THE RATE UNDER COST (2026-10-12). The
        # desk struck this rate over `cost_floor` (`renewal_desk._apply_competitive_ceiling`), and
        # the headroom it leaves is the ~2% margin plus capital cost, so a premium below about -2%
        # crossed the floor: 15 of 18 electricity renewals to 2017-03-31
        # (`SEAT_FINDING_B8_Q5_WHY_THE_RENEWAL_FIX_SITS_BELOW_ITS_OWN_COST_FLOOR_2026-10-12.md`).
        # With no floor to check against, the discount is not given at all; a surcharge is.
        # It never LIFTS a rate that entered below the floor: this writer only discounts.
        discount_unchecked = portfolio_prem < 0 and cost_floor is None
        if abs(portfolio_prem) > 1e-6 and not discount_unchecked:
            rate_before = unit_rate
            unit_rate = _floor_a_discount(
                rate_before, rate_before * (1.0 + portfolio_prem), cost_floor)
            floored_at_cost = unit_rate > rate_before * (1.0 + portfolio_prem)
            entry = {
                "customer_id": customer_id,
                "commodity": commodity,
                "term_start": term_start,
                "recent_margin_rates": position["recent_margin_rates"],
                "mean_recent_margin_rate": position["mean_recent_margin_rate"],
                "portfolio_premium_pct": position["portfolio_premium_pct"],
                # This pair spans THIS writer's move only. The rate the customer
                # contracted is `unit_rate_contracted`, stamped on below once the
                # surcharge, the uplift and the cap have each had their turn.
                "unit_rate_original": round(rate_original, 4),
                "unit_rate_before": round(rate_before, 4),
                "unit_rate_after": round(unit_rate, 4),
            }
            if position["target_margin_rate"] is not None:
                # Only where the history stated what it was priced for; the pre-cut shape otherwise.
                entry["target_margin_rate"] = position["target_margin_rate"]
            if portfolio_prem < 0:
                # On a discount only: a surcharge has no floor to meet, and its entry keeps the
                # shape the pre-cut reproduction pins.
                entry["cost_floor"] = round(cost_floor, 4)
                entry["floored_at_cost"] = floored_at_cost
            result.dynamic_pricing_entries.append(entry)
            result.chain_entries.append(entry)
            result.components.append({
                "cause": "portfolio_premium",
                "basis": "pct",
                "magnitude": round(portfolio_prem * 100, 4),
                "rate_before": round(rate_before, 4),
                "rate_after": round(unit_rate, 4),
            })

    # WRITER 2 — the realised-margin recovery surcharge. A term the supplier lost
    # money on is recovered from the same customer's next one.
    if (
        unit_rate is not None
        and term_index >= MIN_TERM_INDEX_FOR_LEARNED_ADJUSTMENT
        and prior_term_margin_gbp is not None
    ):
        surcharge = compute_margin_surcharge(prior_term_margin_gbp, prior_term_revenue_gbp)
        if surcharge > 0:
            # `rate_before` is the rate as it ENTERS this writer — i.e. after the
            # portfolio premium above. It used to be re-read off the term dict,
            # which is never rebound, so the logged pair carried the premium's
            # move inside a span labelled with only the surcharge's coefficient
            # and the row failed its own arithmetic (28 of 29 rows, 2026-08-13).
            rate_before = unit_rate
            unit_rate *= (1.0 + surcharge)
            entry = {
                "customer_id": customer_id,
                "commodity": commodity,
                "term_start": term_start,
                "prev_margin_gbp": round(prior_term_margin_gbp, 4),
                "prev_revenue_gbp": round(prior_term_revenue_gbp, 4),
                "surcharge_pct": round(surcharge * 100, 2),
                "unit_rate_original": round(rate_original or 0.0, 4),
                "unit_rate_before": round(rate_before, 4),
                "unit_rate_after": round(unit_rate, 4),
            }
            result.margin_feedback_entries.append(entry)
            result.chain_entries.append(entry)
            result.components.append({
                "cause": "margin_surcharge",
                "basis": "pct",
                "magnitude": round(surcharge * 100, 4),
                "rate_before": round(rate_before, 4),
                "rate_after": round(unit_rate, 4),
            })

    # WRITER 3 — the activity-based uplift for net-negative customers. Behind its
    # own door since step 22 (§3q); called from here rather than from the world,
    # which is what puts the ORDER of the chain on this side of the wall.
    pnl_uplift = renewal_unit_rate_uplift(
        account_id=billing_account,
        commodity=commodity,
        tariff_type=tariff_type,
        term_index=term_index,
        term_start=term_start,
        locked_unit_rate=unit_rate,
        settled_records=settled_records,
    )
    if pnl_uplift > 0:
        rate_before = unit_rate
        unit_rate += pnl_uplift
        entry = {
            "customer_id": billing_account,
            "commodity": commodity,
            "term_start": term_start,
            "uplift_gbp_per_mwh": round(pnl_uplift, 4),
            "unit_rate_original": round(rate_original or 0.0, 4),
            "unit_rate_before": round(rate_before, 4),
            "unit_rate_after": round(unit_rate, 4),
        }
        result.profitability_uplift_entries.append(entry)
        result.chain_entries.append(entry)
        result.components.append({
            "cause": "profitability_uplift",
            "basis": "gbp_per_mwh",
            "magnitude": round(pnl_uplift, 4),
            "rate_before": round(rate_before, 4),
            "rate_after": round(unit_rate, 4),
        })

    # WRITER 3b — THE VALUE ARM: what this account is worth, rather than what it cost.
    #
    # It sits HERE, after the two learned adjustments and writer 3, and BEFORE the cap, and both
    # halves of that placement are load-bearing. After, because it prices against the rate this
    # supplier has actually arrived at rather than a hypothetical one. Before, because the cap is
    # the only writer that can move a rate DOWN and this arm is the one most able to need it: run
    # unbounded against the real book it chose margins between £60 and £200/MWh against a flat
    # £2, so a placement past the ceiling would publish a rate the supplier is not allowed to
    # charge. Inheriting writer 4 rather than growing its own ceiling is the whole argument for
    # the one-door design (`company/interfaces/renewal_rate_chain.py`: "the cap clamps what the
    # uplift added").
    #
    # THE ARM IS READ FROM THE RUN'S ACTIVE POLICY, not passed in, because this door must not
    # grow a company decision object: `active_policy()` exists for exactly the consumer that
    # cannot be handed one, and `run_phase2b.main` already REFUSES a run whose `policy` and whose
    # `policy_scope` disagree -- so the A/B cannot become a chimera without the run dying first.
    # On the control arm `renewal_margin_uplift` returns 0.0 before computing anything, so this
    # block is a single comparison and a no-op, which is what makes the control byte-identical.
    # THE CEILING THE ARM SEARCHES UNDER IS THE ONE WRITER 4 IS ABOUT TO APPLY, read here rather
    # than left to land afterwards (2026-08-26). Inheriting writer 4's ceiling was always the
    # design -- "the cap clamps what the uplift added" -- but inheriting it as a POST-HOC clamp is
    # not the same as deciding under it, and `decide_margin` refuses the distinction explicitly:
    # scoring a candidate the company may not lawfully offer and then clamping the winner reports
    # an expected value nobody can earn. On the first ten-year A/B that happened to 27 of 66
    # renewals, and `ceiling_bound` -- the flag whose entire job is to tell a reader the cap chose
    # the price -- could not fire, because the arm was never told there was a cap.
    #
    # SAME SOURCE, SAME KEY, SAME APPLICABILITY TEST as writer 4 below, deliberately: two readings
    # of one ceiling inside one chain is the shape where a rate gets decided under a bound it is
    # then clamped by a different one.
    cap_ceiling = None
    if is_domestic and held_at_published_cap(tariff_type, term_index):
        # THE BENCHMARK FOLLOWS THE PRODUCT SOLD. `tou_desk` strikes the ToU pair off the rate
        # this chain returns, revenue-neutral at its assumed split, so the pair is lawful only if
        # this rate is under the MULTI-REGISTER cap (SLC 28AD.4). Read from the same predicate
        # the offer uses, so the term graded as ToU is the term sold as ToU.
        cap_ceiling = cap_ceiling_ex_vat(
            commodity, date.fromisoformat(term_start[:10]),
            multi_register=(commodity == "electricity"
                            and offers_tou(customer, tariff_type=tariff_type)),
            net_of_epg=tariff_type not in EPG_MADE_WHOLE_TARIFF_TYPES,
            # SLC 28AD caps a default tariff at its payment method's own level; a fixed term the
            # acquisition rule holds is this supplier's choice, at the published level.
            payment_method=payment_method if tariff_type in CAPPED_TARIFF_TYPES else None)

    arm_uplift = renewal_margin_uplift(
        account_id=billing_account,
        commodity=commodity,
        tariff_type=tariff_type,
        term_index=term_index,
        term_start=term_start,
        locked_unit_rate=unit_rate,
        settled_records=settled_records,
        is_domestic=is_domestic,
        # The account's OWN segment, not the two-valued collapse of it. See
        # `renewal_margin_uplift`'s mapping comment: the churn model has an I&C branch that
        # the boolean could not reach, and that unreachability was 99.5% of the value arm's
        # measured loss. `None` keeps the old behaviour for a caller that does not know.
        segment=segment,
        arm=active_policy().renewal_margin_arm,
        max_offered_rate_gbp_per_mwh=cap_ceiling,
        # THE PRICE LADDER'S RUNG, resolved from the SAME active policy and at the same site as
        # the arm, because it is the same kind of fact and a second resolution path is how one
        # run comes to be executing two policies. `1.0` on every ordinary run.
        ladder_multiplier=active_policy().renewal_margin_ladder_multiplier,
        # THE FLAT-AT-LEVEL ARM'S LEVEL, resolved from the SAME active policy and at the SAME
        # site as the arm and the rung, for the reason stated above: the rate chain is a wall
        # door and must not gain a policy argument, and a second resolution path is how one run
        # comes to be executing two policies. `None` on every ordinary run.
        flat_level_gbp_per_mwh=active_policy().renewal_margin_flat_level_gbp_per_mwh,
        # The default tariff a domestic household is actually charged for this fuel on the day
        # (EPG-net, single-rate, ex-VAT like the offer). The churn belief reads the offer's gap
        # to it, whether or not this term is held at the cap: the household compares against it
        # either way.
        published_default_rate_gbp_per_mwh=(
            cap_ceiling_ex_vat(
                commodity, date.fromisoformat(term_start[:10]), multi_register=False)
            if is_domestic and commodity in ("electricity", "gas") else None),
        # WHAT THIS ACCOUNT HAS AND HAS NOT PAID, which the arm priced blind to until 2026-10-03.
        # The credit-risk segment is the company's own register and is read here rather than
        # crossing: it never left `company/`.
        arrears_state=arrears_state or ARREARS_STATE_UNKNOWN,
        credit_risk=CREDIT_RISK_BY_CUSTOMER.get(customer_id, DEFAULT_CREDIT_RISK),
        unpaid_bills_by_age=tuple((receivable or {}).get("unpaid_bills_by_age") or ()),
        billed_last_year_gbp=(receivable or {}).get("billed_last_year_gbp"),
        payment_method=payment_method,
        # THE BOOK'S OWN DEFAULT RATE, resolved from the SAME active policy as the arm, at the
        # same site and for the same reason: the run supplies the number, the policy decides
        # whether the price reads it. `None` on every ordinary run.
        default_belief_rate=(
            default_belief_rate
            if active_policy().renewal_default_belief == DEFAULT_BELIEF_OWN_BOOK else None),
        # A HOUSEHOLD THAT STAYS PAYS AT MOST THE DEFAULT, which the licence makes true of every
        # domestic fix: it cannot auto-renew, and doing nothing lands on the default. Resolved
        # from the same active policy, at the same site. Only a fixed term can be refused.
        stayer_default_rate_gbp_per_mwh=(
            _stayer_default_ex_vat(commodity, term_start, own_default_tariff_inc_vat_gbp_per_mwh)
            if (active_policy().renewal_stayer_pays_at_most_default and tariff_type == "fixed"
                and is_domestic) else None),
        # WHAT THE ARM'S MARGIN IS MEASURED FROM: this term's own cost before margin, not the rate
        # writers 1-3 left less GBP 2. The arm's rate is then `base + chosen`, the rate it scored.
        # The same number writer 1's discount stops at (`cost_floor` above), read once.
        # Less the strike's bad-debt allowance: the arm nets the same belief off its own value, so
        # measuring from a floor that already carries it would charge the loss twice (B12).
        pre_margin_rate_gbp_per_mwh=(
            cost_floor - bad_debt_allowance if cost_floor is not None else None),
    )
    # THE DENOMINATOR, WRITTEN AT THE SAME SITE AS THE DECISION. Unconditional and before the two
    # branches below, so a renewal cannot reach the funnel through one path and miss it through
    # another: every renewal this chain saw appears here exactly once, on every arm including the
    # control. `stage` is the arm's own machine-readable guard key (`FUNNEL_STAGES`), taken from
    # the adapter rather than re-derived here -- a second copy of the eligibility rule in the
    # counter is how a funnel comes to report a population its subject does not have.
    result.arm_funnel_entries.append({
        "customer_id": billing_account,
        "commodity": commodity,
        "term_start": term_start,
        "term_index": term_index,
        "tariff_type": tariff_type,
        "arm": active_policy().renewal_margin_arm,
        "stage": (
            VALUE_ARM_STAGE_PRICED if arm_uplift.decision is not None
            else arm_uplift.not_run_stage),
        "reason": arm_uplift.not_run_reason,
    })
    if arm_uplift.declined:
        # A DECLINE IS A DECISION AND IT GOES IN THE LOG. The rate is untouched -- a supplier
        # that cannot form a defensible view charges what it already charges -- but "the arm
        # declined this renewal" and "the arm never looked at it" must not read the same in the
        # run output, or the A/B cannot tell a book the arm priced from one it walked past.
        result.value_arm_entries.append({
            "customer_id": billing_account,
            "commodity": commodity,
            "term_start": term_start,
            # THE ARM THAT DECLINED, not a constant. This read `"value_based"` while that was the
            # only arm that COULD decline; since 2026-09-18 `flat_at_level` refuses at the same
            # frontier, and a level-arm decline published under the value arm's name would put
            # the wrong arm's name on every row of `declined_renewals`.
            "arm": active_policy().renewal_margin_arm,
            "declined": True,
            "reason": arm_uplift.not_run_reason,
            "unit_rate_unchanged": None if unit_rate is None else round(unit_rate, 4),
        })
    if unit_rate is not None and arm_uplift.decision is not None:
        rate_before = unit_rate
        # THE SAME FLOOR AS WRITER 1 (2026-10-12). Added when the arm measured its margin from the
        # handed rate less GBP 2, which writer 1 had already cut: a level under GBP 2 then sold up
        # to GBP 1.50 under cost. Since 2026-10-13 the base IS this floor, so with offer components
        # it binds only on a margin below zero, which no rung offers; it stays as the writer-local
        # half of the class check below, for a base that ever parts from the floor.
        unit_rate = _floor_a_discount(
            rate_before, rate_before + arm_uplift.uplift_gbp_per_mwh, cost_floor)
        arm_floored_at_cost = unit_rate > rate_before + arm_uplift.uplift_gbp_per_mwh
        decision = arm_uplift.decision
        entry = {
            "customer_id": billing_account,
            "commodity": commodity,
            "term_start": term_start,
            "arm": decision.arm,
            "chosen_margin_gbp_per_mwh": round(decision.margin_gbp_per_mwh, 4),
            "flat_rule_margin_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
            "arm_base_gbp_per_mwh": round(arm_uplift.base_rate_gbp_per_mwh, 4),
            "arm_base_source": arm_uplift.base_source,
            "uplift_gbp_per_mwh": round(arm_uplift.uplift_gbp_per_mwh, 4),
            # THE BELIEF, LABELLED AS ONE. `expected_value_gbp` is the company's own number and
            # is never evidence the decision was right -- the realised A/B is. Carried so the
            # two can be compared afterwards, which is the only way to find out whether this
            # company's beliefs are worth acting on.
            "believed_p_retain": round(decision.p_retain, 4),
            "believed_expected_value_gbp": round(decision.expected_value_gbp, 2),
            # WHAT THE PAYMENT HISTORY COST THIS DECISION, so a run shows the ledger reached the
            # price rather than every default standing in for it (2026-10-03).
            "believed_bad_debt_gbp_per_year": round(decision.costs.bad_debt_gbp, 2)
            if decision.costs else None,
            "receivable_expected_loss_gbp": round(decision.receivable_expected_loss_gbp, 2),
            "receivable_provision_unsourced": decision.receivable_provision_unsourced,
            "endpoint_bound": decision.endpoint_bound,
            "endpoint_side": decision.endpoint_side,
            # WHICH BOUND ACTUALLY DECIDED, carried out of the decision rather than inferred from
            # the rate afterwards. `endpoint_side` says the answer sat at an end of the searchable
            # interval; these two say WHY that interval ended there -- the lawful cap, or the
            # frontier of what the churn model has evidence for. A reader given only the first
            # cannot tell a supplier that obeyed the price cap from one whose belief ran out.
            "ceiling_bound": decision.ceiling_bound,
            "extrapolation_bound": decision.extrapolation_bound,
            "withheld_reason": decision.withheld_reason,
            "unit_rate_original": round(rate_original or 0.0, 4),
            "unit_rate_before": round(rate_before, 4),
            "unit_rate_after": round(unit_rate, 4),
            # ── THE COMPANY'S OWN PRICE REFERENCE, published per decision ──────────────────
            # `rate_increase_pct` is the quantity `churn_model.estimate_churn_probability` keys
            # on: a DELTA against this customer's own prior rate. The WORLD keys on a LEVEL
            # against the published SVT (`simulation/customer_events._price_differential_vs_
            # market`), and the 2026-08-27 section of THE_VALUE_CYCLE_REALISED_AB.md established
            # that those two disagree in BOTH directions -- cheap-supplier-moves-to-average reads
            # as a large rise here and as parity there; dear-supplier-barely-moves reads as flat
            # here and as +30% there. That inversion took a four-row bucket table to detect and
            # is one column once both are logged.
            #
            # ONLY THE COMPANY'S SIDE IS WRITTEN HERE, deliberately. `rate_vs_svt_pct` is joined
            # in by the harness (`tools/run_price_ladder.py`) from the world's own event log, not
            # computed here: whether a supplier can see its own position against the published
            # SVT is a question about the world's observables and is recorded for the director
            # under R13, not answered by this writer giving the company the number.
            "company_current_rate_gbp_per_mwh": (
                None if decision.current_rate_gbp_per_mwh is None
                else round(decision.current_rate_gbp_per_mwh, 4)),
            "offered_rate_gbp_per_mwh": (
                None if decision.offered_rate_gbp_per_mwh is None
                else round(decision.offered_rate_gbp_per_mwh, 4)),
            "rate_increase_pct": (
                None if decision.rate_increase_pct is None
                else round(decision.rate_increase_pct, 4)),
            # ── THE RUNG ──────────────────────────────────────────────────────────────────
            "ladder_multiplier": decision.ladder_multiplier,
            "unscaled_margin_gbp_per_mwh": (
                None if decision.unscaled_margin_gbp_per_mwh is None
                else round(decision.unscaled_margin_gbp_per_mwh, 4)),
            "ladder_ceiling_clamped": decision.ladder_ceiling_clamped,
            "ladder_above_support_bound": decision.ladder_above_support_bound,
        }
        if arm_uplift.uplift_gbp_per_mwh < 0:
            # On a cut only, as writer 1: the arm's belief above is for the rate it CHOSE, and this
            # says the contracted rate was raised to cost instead.
            entry["floored_at_cost"] = arm_floored_at_cost
        result.value_arm_entries.append(entry)
        result.chain_entries.append(entry)
        result.components.append({
            "cause": "value_arm",
            "basis": "gbp_per_mwh",
            "magnitude": round(unit_rate - rate_before if arm_floored_at_cost
                               else arm_uplift.uplift_gbp_per_mwh, 4),
            "rate_before": round(rate_before, 4),
            "rate_after": round(unit_rate, 4),
        })

    # WRITER 4 — the Ofgem domestic price cap, the final ceiling and the only
    # writer that can move the rate DOWN. Keyed on the cap WINDOW containing the
    # term start, not the term-start calendar year: a term starting 15 Feb 2022
    # was struck under the Oct-2021 cap that ran to 31 Mar 2022, not under a
    # full-year 2022 blend that averages in the +54% April step it predates.
    if unit_rate is not None:
        # THE SAME OBJECT the arm above searched under, not a second lookup of the same thing.
        # Two reads of one ceiling inside one chain is how a rate comes to be decided under one
        # bound and clamped by another; `cap_ceiling` already carries the applicability test.
        cap = cap_ceiling
        if cap is not None:
            if cap < unit_rate:
                # Nothing logged the cap before, so a capped renewal's published
                # "after" was a rate above the one the customer was charged.
                result.components.append({
                    "cause": "price_cap",
                    "basis": "gbp_per_mwh",
                    "magnitude": round(cap - unit_rate, 4),
                    "rate_before": round(unit_rate, 4),
                    "rate_after": round(cap, 4),
                })
            unit_rate = min(unit_rate, cap)

    # Close the chain. One decomposed span per renewal — original -> contracted,
    # causes named in the order they fired — and the contracted rate stamped back
    # onto every writer's own entry so no reader has to mistake a link for the
    # whole.
    if result.components:
        contracted = round(unit_rate, 4)
        for entry in result.chain_entries:
            entry["unit_rate_contracted"] = contracted
        result.decomposition = {
            "customer_id": customer_id,
            "billing_account": billing_account,
            "commodity": commodity,
            "term_start": term_start,
            "unit_rate_original": round(rate_original or 0.0, 4),
            "unit_rate_contracted": contracted,
            "components": result.components,
        }

    # THE CLASS, checked where the chain returns: whatever writer moved it, the rate leaves no
    # lower than its own cost floor unless it entered lower or the cap (the law) put it there.
    refuse_discretionary_rate_below_own_cost_floor(
        unit_rate, entered=rate_original, cost_floor=cost_floor, cap=cap_ceiling,
        where=f"{customer_id} {commodity} {term_start}")

    result.unit_rate_gbp_per_mwh = unit_rate
    return result


def decide_renewal_rate_from(inputs) -> RenewalRateChain:
    """`decide_renewal_rate` for a `company.interfaces.renewal_decision_inputs.RenewalDecisionInputs`.

    The record's names are market-neutral (the seam's portability law); the desk's carry the
    book's currency. This is the one place the two are mapped, field for field.
    """
    return decide_renewal_rate(
        customer_id=inputs.customer_id,
        billing_account=inputs.billing_account,
        commodity=inputs.commodity,
        term_start=inputs.term_start,
        tariff_type=inputs.tariff_type,
        term_index=inputs.term_index,
        struck_unit_rate_gbp_per_mwh=inputs.struck_unit_rate_per_mwh,
        portfolio_margin_rates=inputs.portfolio_margin_rates,
        prior_term_margin_gbp=inputs.prior_term_margin,
        prior_term_revenue_gbp=inputs.prior_term_revenue,
        is_domestic=inputs.is_domestic,
        segment=inputs.segment,
        settled_records=inputs.settled_records,
        customer=inputs.customer,
        arrears_state=inputs.arrears_state,
        receivable=inputs.receivable,
        payment_method=inputs.payment_method,
        default_belief_rate=inputs.default_belief_rate,
        own_default_tariff_inc_vat_gbp_per_mwh=inputs.own_default_tariff_inc_vat_per_mwh,
        # Already market-neutral on both sides: the seam door carries them under the same names.
        company_forward_per_mwh=inputs.company_forward_per_mwh,
        locked_policy_cost_per_mwh=inputs.locked_policy_cost_per_mwh,
        locked_network_cost_per_mwh=inputs.locked_network_cost_per_mwh,
        portfolio_priced_for_rates=inputs.portfolio_priced_for_rates,
    )


def bill_the_shared_rise(*, unit_rate_gbp_per_mwh: float, rise_gbp_per_month: float | None,
                         annual_mwh: float | None,
                         headroom_gbp_per_month: float | None) -> tuple[float, str]:
    """WRITER 7, THE SHARED RISE (C34's price half, 2026-10-24): the fix this account is billed once
    C34 advises it with a retention rise, and why.

    C34 ranks on joint value, and our floor refused every B11-scale case, because the advice costs us
    and creates value for the household. `next_best_action.price_retention_rise` finds the smallest
    monthly rise that brings our side to zero under both floors. This writer bills that rise on the
    fix, as GBP/MWh over the account's own annual volume, and only inside the headroom under the
    published default. A rise above the headroom would send a stayer to the default, so the rate is
    left as struck. It fires after the chain closes, at the renewal notice, because the rise is
    priced on the churn belief that reads the struck rate. Knowledge:
    `a_retention_price_that_shares_the_value_an_action_creates.md` §4e.

    `rise_gbp_per_month` None means C34 priced no rise (it did not advise, or advised at no cost
    to us), and nothing is billed. Every refusal leaves the struck rate and names its reason.
    """
    if rise_gbp_per_month is None or rise_gbp_per_month <= 0.0:
        return unit_rate_gbp_per_mwh, "no action: C34 priced no rise on this renewal"
    if headroom_gbp_per_month is None or not annual_mwh:
        return unit_rate_gbp_per_mwh, ("refused: the headroom under the published default is "
                                       "unknown, so no rise is billed")
    if rise_gbp_per_month > headroom_gbp_per_month + 1e-9:
        return unit_rate_gbp_per_mwh, (
            f"refused: the rise ({rise_gbp_per_month:.2f} GBP/month) is above the headroom under "
            f"the published default ({headroom_gbp_per_month:.2f} GBP/month)")
    return (unit_rate_gbp_per_mwh + rise_gbp_per_month * 12.0 / annual_mwh,
            f"shared: {rise_gbp_per_month:.2f} GBP/month billed inside "
            f"{headroom_gbp_per_month:.2f} GBP/month of headroom")


#: The tariffs whose completed terms teach the portfolio premium: the product whose strike it moves.
FIXED_PREMIUM_BOOK_TARIFF_TYPES = ("fixed",)


class PortfolioMarginBook:
    """The supplier's realised margin rate per term, per fuel: the history its portfolio premium
    reads, holding a term back until it has ENDED, and admitting no term a save kept.

    MOVED FROM THE RUN LOOP (2026-10-12). This was `simulation.run_phase2b.EndedTermMargins` plus
    the save rule written inline beside its one `.settled()` call. Both are the company's own
    bookkeeping over its own P&L; the run loop now reports what happened and the book decides what
    it admits.

    ENDED, NOT SETTLED. The run walks terms in START order and settles each one to its end inside
    its own iteration, so a list appended at settlement handed a renewal priced in July 2024 the
    whole-term margin of a term that ran to February 2025: days no supplier has seen. The premium
    reads the last N *completed* terms, and `as_of` is what makes "completed" true at the moment of
    reading. Found 2026-10-01 when a 2025-only standing-charge change moved renewals priced in 2024.

    A SAVE DOES NOT TEACH THE PREMIUM (director, 2026-10-08: a save must never be paid for by
    raising the price of customers who stay). A term held on a save has a margin thinner by the
    save's cut, and so does every later term of that account, because its next renewal is priced
    off the save rate. Admitting either recovered the save from the stayers through the premium
    (measured 2026-10-11, tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py: 372
    stayer prices moved). So an account is excluded for good once a save, or a followed home move
    priced as one, has held it.
    """

    def __init__(self) -> None:
        self.electricity: list[float] = []
        self.gas: list[float] = []
        # Index-aligned with the two lists above: the margin rate each released term's own strike
        # priced for, on the same basis as its realised rate. `None` where it was not stated.
        self._priced_for = {"electricity": [], "gas": []}
        self._pending: list[tuple[str, int, str, float, float | None]] = []
        self._sequence = 0
        self._held_on_a_save: set[str] = set()

    def rates(self, commodity: str) -> list[float]:
        """The released history for `commodity`, oldest first. The live list, not a copy."""
        return self.electricity if commodity == "electricity" else self.gas

    def priced_for(self, commodity: str) -> list[float | None]:
        """What each term in `rates(commodity)` was priced to earn, index for index. Live list."""
        return self._priced_for["electricity" if commodity == "electricity" else "gas"]

    def account_held_on_a_save(self, billing_account: str) -> None:
        """Record that a save kept this account: none of its terms teaches the premium again."""
        self._held_on_a_save.add(billing_account)

    def term_ended(self, *, billing_account: str, commodity: str, last_settled_day: str,
                   net_margin: float, revenue: float, standing_charge_revenue: float,
                   volume_mwh: float, held_on_a_save: bool, tariff_type: str) -> None:
        """Take one term's outcome off the company's own P&L, and admit it unless a save held it
        or its unit rate earned nothing. `held_on_a_save` is this term's own flag; the
        account-level exclusion is the book's.

        THE UNIT-RATE MARGIN, NOT THE BILL'S (2026-10-14). The standing charge is in `revenue` and
        in `net_margin` in full, with no cost against it: the term's P&L carries neither the
        operating costs nor the fixed network share it recovers (by the cap's construction the
        standing charge IS that nil-consumption allowance). Read as margin, it put the book at
        18-20% against an 8% target on a book priced at cost, and the premium took the full -5%
        off 21 of 21 held electricity renewals on four seeds, every one onto its floor
        (`SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_..._2026-10-14.md`). So the standing charge
        comes out of both sides, and the rate is set beside what the term's own strike priced for
        on the same basis: `TARGET_MARGIN_GBP_PER_MWH` on each MWh, over the unit-rate revenue.

        FIXED TERMS ONLY (B12, 2026-10-15). The premium moves a fixed strike, and its target is what
        a fixed strike priced for, but a default term's margin is the cap's headroom over cost, not
        anything a strike priced. Default terms outnumbered fixed ones about 10 to 1 in the lookback,
        so the fixed premium was learning the cap's headroom (2019-20, 2023-24 read 14-18% against a
        ~1.7% target). Which book a desk compares with: the renewal-decision knowledge page.
        """
        unit_revenue = revenue - standing_charge_revenue
        if (tariff_type in FIXED_PREMIUM_BOOK_TARIFF_TYPES and unit_revenue > 0
                and not held_on_a_save and billing_account not in self._held_on_a_save):
            self.settled(last_settled_day, commodity,
                         (net_margin - standing_charge_revenue) / unit_revenue,
                         TARGET_MARGIN_GBP_PER_MWH * volume_mwh / unit_revenue)

    def settled(self, last_settled_day: str, commodity: str, margin_rate: float,
                priced_for: float | None = None) -> None:
        heapq.heappush(self._pending,
                       (last_settled_day[:10], self._sequence, commodity, margin_rate, priced_for))
        self._sequence += 1

    def as_of(self, day: str) -> None:
        """Release, in end order, every term whose last settled day is before `day`."""
        while self._pending and self._pending[0][0] < day[:10]:
            _, _, commodity, rate, priced_for = heapq.heappop(self._pending)
            self.rates(commodity).append(rate)
            self.priced_for(commodity).append(priced_for)
