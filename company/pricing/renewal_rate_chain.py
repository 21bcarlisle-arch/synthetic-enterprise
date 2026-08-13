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
profitability uplift adds to that; the cap clamps the result. Five writers, one
number, and the arithmetic is a chain — reorder any two of them and the answer
changes. That is why they are one door and not five.

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

from dataclasses import dataclass, field
from datetime import date

from company.interfaces.customer_profitability import renewal_unit_rate_uplift
from company.pricing.margin_feedback import compute_margin_surcharge
from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date
from company.pricing.tariff_engine import (
    PORTFOLIO_PREMIUM_LOOKBACK,
    compute_portfolio_premium,
)

__all__ = ["RenewalRateChain", "decide_renewal_rate"]

# The premium and the surcharge both learn from COMPLETED terms, so neither can
# apply to a customer's first one. The world used to spell this as
# `term_index >= 1` at two call sites; it is one supplier rule, named once.
MIN_TERM_INDEX_FOR_LEARNED_ADJUSTMENT = 1

# The supplier's reading of who the domestic price cap binds. A cap is a ceiling
# on a standard domestic product; it is not the supplier's licence to ignore it
# on everything else, and a supplier that reads this wrong is the failure mode
# the compliance side of the coupled triad exists to catch.
CAPPED_TARIFF_TYPES = ("fixed",)


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
    components: list[dict] = field(default_factory=list)
    chain_entries: list[dict] = field(default_factory=list)
    dynamic_pricing_entries: list[dict] = field(default_factory=list)
    margin_feedback_entries: list[dict] = field(default_factory=list)
    profitability_uplift_entries: list[dict] = field(default_factory=list)
    decomposition: dict | None = None


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
    settled_records: list[dict],
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
    """
    unit_rate = struck_unit_rate_gbp_per_mwh
    rate_original = unit_rate

    result = RenewalRateChain(unit_rate_gbp_per_mwh=unit_rate)

    # WRITER 1 — the portfolio learning premium. The supplier looks at what it
    # actually earned on its last few completed terms of this commodity and
    # closes part of the gap to its target margin on the next rate it quotes.
    if (
        unit_rate is not None
        and term_index >= MIN_TERM_INDEX_FOR_LEARNED_ADJUSTMENT
        and len(portfolio_margin_rates) >= 1
    ):
        lookback = portfolio_margin_rates[-PORTFOLIO_PREMIUM_LOOKBACK:]
        portfolio_prem = compute_portfolio_premium(lookback)
        if abs(portfolio_prem) > 1e-6:
            rate_before = unit_rate
            unit_rate *= (1.0 + portfolio_prem)
            entry = {
                "customer_id": customer_id,
                "commodity": commodity,
                "term_start": term_start,
                "recent_margin_rates": [round(r, 4) for r in lookback],
                "mean_recent_margin_rate": round(sum(lookback) / len(lookback), 4),
                "portfolio_premium_pct": round(portfolio_prem * 100, 2),
                # This pair spans THIS writer's move only. The rate the customer
                # contracted is `unit_rate_contracted`, stamped on below once the
                # surcharge, the uplift and the cap have each had their turn.
                "unit_rate_original": round(rate_original, 4),
                "unit_rate_before": round(rate_before, 4),
                "unit_rate_after": round(unit_rate, 4),
            }
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

    # WRITER 4 — the Ofgem domestic price cap, the final ceiling and the only
    # writer that can move the rate DOWN. Keyed on the cap WINDOW containing the
    # term start, not the term-start calendar year: a term starting 15 Feb 2022
    # was struck under the Oct-2021 cap that ran to 31 Mar 2022, not under a
    # full-year 2022 blend that averages in the +54% April step it predates.
    if unit_rate is not None and is_domestic and tariff_type in CAPPED_TARIFF_TYPES:
        cap = get_cap_unit_rate_for_date(commodity, date.fromisoformat(term_start[:10]))
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

    result.unit_rate_gbp_per_mwh = unit_rate
    return result
