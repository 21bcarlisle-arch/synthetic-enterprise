"""Customer Profitability Register.

Computes per-customer annual contribution margin from observable data:
  contribution = revenue - wholesale_cost - levies - operating_costs

This is the company's view of which customers are net-positive or net-negative.
Flat margin pricing makes some customers net-negative when their cost-to-serve
(volume-driven levies + operating costs) exceeds the margin earned on their tariff.

All inputs are company-observable: billing records, tariff rates, forward costs,
CTS breakdowns. No simulation internals used.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# THE SUPPLIER'S OWN BILLING GROUPING — which of its supply points bill as one account. Reused
# rather than re-derived here, because a second copy of that rule is how one company comes to
# hold two answers to it. Nothing about the world crosses with it.
from saas.customer_reaction import _billing_account_id


@dataclass(frozen=True)
class CustomerProfitabilityRecord:
    """Annual profitability for one customer account."""
    account_id: str
    year: int
    annual_revenue_gbp: float
    annual_wholesale_cost_gbp: float
    annual_levy_cost_gbp: float
    annual_operating_cost_gbp: float

    @property
    def gross_margin_gbp(self) -> float:
        return round(self.annual_revenue_gbp - self.annual_wholesale_cost_gbp, 2)

    @property
    def net_contribution_gbp(self) -> float:
        return round(
            self.annual_revenue_gbp
            - self.annual_wholesale_cost_gbp
            - self.annual_levy_cost_gbp
            - self.annual_operating_cost_gbp,
            2,
        )

    @property
    def is_net_negative(self) -> bool:
        return self.net_contribution_gbp < 0.0

    @property
    def gross_margin_pct(self) -> float:
        if self.annual_revenue_gbp == 0:
            return 0.0
        return round(self.gross_margin_gbp / self.annual_revenue_gbp * 100, 2)

    @property
    def net_margin_pct(self) -> float:
        if self.annual_revenue_gbp == 0:
            return 0.0
        return round(self.net_contribution_gbp / self.annual_revenue_gbp * 100, 2)


class CustomerProfitabilityBook:
    """Register of per-customer annual profitability assessments.

    The company records a CustomerProfitabilityRecord for each account/year
    as billing and cost-to-serve data becomes available.
    """

    def __init__(self) -> None:
        self._records: list[CustomerProfitabilityRecord] = []

    def record(self, rec: CustomerProfitabilityRecord) -> CustomerProfitabilityRecord:
        self._records.append(rec)
        return rec

    def latest_for(self, account_id: str) -> Optional[CustomerProfitabilityRecord]:
        matches = [r for r in self._records if r.account_id == account_id]
        return max(matches, key=lambda r: r.year) if matches else None

    def history_for(self, account_id: str) -> list[CustomerProfitabilityRecord]:
        return sorted(
            [r for r in self._records if r.account_id == account_id],
            key=lambda r: r.year,
        )

    def net_negative_accounts(self, year: Optional[int] = None) -> list[str]:
        records = self._for_year(year)
        return sorted({r.account_id for r in records if r.is_net_negative})

    def top_n_by_contribution(self, n: int = 5, year: Optional[int] = None) -> list[CustomerProfitabilityRecord]:
        records = self._for_year(year)
        seen: dict[str, CustomerProfitabilityRecord] = {}
        for r in records:
            if r.account_id not in seen or r.year > seen[r.account_id].year:
                seen[r.account_id] = r
        return sorted(seen.values(), key=lambda r: r.net_contribution_gbp, reverse=True)[:n]

    def total_net_contribution_gbp(self, year: Optional[int] = None) -> float:
        records = self._for_year(year)
        return round(sum(r.net_contribution_gbp for r in records), 2)

    def net_negative_rate_pct(self, year: Optional[int] = None) -> float:
        records = self._for_year(year)
        if not records:
            return 0.0
        net_neg = sum(1 for r in records if r.is_net_negative)
        return round(net_neg / len(records) * 100, 2)

    def profitability_summary(self, year: Optional[int] = None) -> dict:
        records = self._for_year(year)
        if not records:
            return {"accounts_assessed": 0}
        net_neg = [r for r in records if r.is_net_negative]
        total_rev = sum(r.annual_revenue_gbp for r in records)
        total_net = sum(r.net_contribution_gbp for r in records)
        return {
            "accounts_assessed": len(records),
            "net_negative_count": len(net_neg),
            "net_negative_rate_pct": self.net_negative_rate_pct(year),
            "total_net_contribution_gbp": round(total_net, 2),
            "total_revenue_gbp": round(total_rev, 2),
            "portfolio_net_margin_pct": round(total_net / total_rev * 100, 2) if total_rev else 0.0,
        }

    def _for_year(self, year: Optional[int]) -> list[CustomerProfitabilityRecord]:
        if year is None:
            return list(self._records)
        return [r for r in self._records if r.year == year]



# Phase 44a constants for net-negative profitability feedback.
# Applied as a unit-rate uplift at renewal when prior term is net-negative.
MIN_RECORDS_FOR_JUDGEMENT: int = 3  # minimum settlement records to form a view
NET_NEGATIVE_UPLIFT_GBP_PER_MWH: float = 5.0  # uplift applied for net-negative prior term


def estimate_prior_term_net_margin(
    cid: str,
    term_start_str: str,
    all_records: list[dict],
    commodity: str = "electricity",
) -> Optional[float]:
    """Estimate total net margin from the most recent prior completed term.

    Returns the sum of net_margin_gbp for records matching:
      - the record BILLS UNDER `cid` (see the filter below — not string equality)
      - commodity == commodity
      - settlement_date < term_start_str (point-in-time blindfold)
    grouped by term_start, using only the most recent such term.

    Returns None if:
      - No matching records exist
      - The most recent prior term has fewer than MIN_RECORDS_FOR_JUDGEMENT records
    """
    eligible = [
        r for r in all_records
        # A RECORD BELONGS TO THIS ACCOUNT IF IT BILLS UNDER IT, and string equality is not
        # that test (2026-09-07). Settled rows are stamped with the SUPPLY POINT
        # (`simulation/hedged_settlement.py`, `simulation/gas_settlement.py`), and writer 3 is
        # called with the BILLING ACCOUNT — `renewal_rate_chain` passes `billing_account`,
        # which `simulation/run_phase2b.py:1539` fills from `household_of(cid)`. The two ids
        # are the same string on every electricity-only supply point and differ by the gas
        # suffix on every gas leg, so `==` answered `None` for every gas renewal and
        # `compute_profitability_uplift` returned 0.0 — which is ALSO its answer for "this
        # account is profitable", so no run output could tell the policy declining to fire
        # from the policy being unable to see the book at all.
        #
        # `_billing_account_id` is the supplier's OWN grouping rule, reused rather than
        # re-derived — the same repair `value_based_renewal.observed_account_state` took a
        # writer along on the same day. It is emphatically not `household_of`: that is the
        # world's fact about the property, and the supplier's billing grouping must stay free
        # to disagree with it. No wall is crossed — a supplier knows how it groups its own
        # bills.
        #
        # THE COMMODITY FILTER IS WHAT KEEPS THIS FROM WIDENING THE ELECTRICITY BOOK. Both
        # legs of a dual-fuel account now reach the filter and the line below removes the
        # other one. Its `"electricity"` default is a fallback for unstamped rows and not a
        # policy: both settlement writers stamp `commodity` on every row they emit.
        #
        # THE as_of BOUND IS UNCHANGED AND STILL THE THIRD LINE HERE: nothing that settled on
        # or after `term_start_str` reaches the answer. Widening WHICH supply points bill
        # together does not widen the clock.
        if (_billing_account_id(r.get("customer_id") or "") == cid
            and r.get("commodity", "electricity") == commodity
            and r.get("settlement_date", "") < term_start_str
            and r.get("net_margin_gbp") is not None)
    ]
    if not eligible:
        return None

    # Find most recent prior term_start
    prior_term_starts = {r.get("term_start", "") for r in eligible if r.get("term_start")}
    if not prior_term_starts:
        return None
    latest_term = max(prior_term_starts)
    term_records = [r for r in eligible if r.get("term_start") == latest_term]

    if len(term_records) < MIN_RECORDS_FOR_JUDGEMENT:
        return None
    return sum(r["net_margin_gbp"] for r in term_records)


def compute_profitability_uplift(
    cid: str,
    term_start_str: str,
    # The whole settled book; the as_of bound is applied downstream, at
    # `settlement_date < term_start_str`. See the clock paragraph below.
    all_records: list[dict],
    commodity: str = "electricity",
) -> float:
    """Return a unit-rate uplift (GBP/MWh) for net-negative customers.

    Phase 44a: called at renewal term signing. Returns NET_NEGATIVE_UPLIFT_GBP_PER_MWH
    if the most recent prior term was net-negative; 0.0 otherwise.

    `commodity` selects WHICH BOOK the prior term is read from, and it is the same
    argument `estimate_prior_term_net_margin` has always taken. It defaults to
    electricity for callers that predate gas eligibility; the eligibility door
    below passes the renewal's own commodity and never the default.

    THE as_of BOUND IS UNCHANGED BY THAT ARGUMENT and stays where it has always
    been applied — one call down, where `settlement_date < term_start_str` keeps
    only what had settled when the term was struck. Selecting a commodity narrows
    the book; it does not widen the clock.
    """
    prior_margin = estimate_prior_term_net_margin(
        cid, term_start_str, all_records, commodity=commodity)
    if prior_margin is None or prior_margin >= 0.0:
        return 0.0
    return NET_NEGATIVE_UPLIFT_GBP_PER_MWH


# ---------------------------------------------------------------------------
# KNIFE pass 3, `A_composition_lift` step 22 (register §3q).
#
# Until step 22 the WORLD decided which renewals this pricing policy applied to.
# `simulation/run_phase2b.py::main()` carried the eligibility test in its own
# renewal loop — first term or later, electricity, fixed or pass-through, and a
# locked unit rate to adjust — and only then asked the company for a number.
# That is the supplier deciding which of its own products it will reprice for
# unprofitability, which is a pricing decision, not world physics. It now lives
# here, with the two constants it was always separated from.
#
# WHAT STAYS THE WORLD'S: whether the term happened, what commodity it was for,
# what tariff type was struck and what the rate was. Those are observations. What
# they MEAN for the supplier's pricing is behind this function.
#
# POINT-IN-TIME: this function reads no settlement history itself. The blindfold
# is applied one call down, in `estimate_prior_term_net_margin`, where the
# as_of bound is the term start — it keeps only records with
# `settlement_date < term_start` and then takes the single most recent completed
# term. The parameter is named `settled_records` rather than "everything" for
# that reason: the supplier is handed its own settled book and is bounded to the
# part of it that had already settled when the term was struck.
# ---------------------------------------------------------------------------

# The products this uplift can be applied to. Deemed and flexible terms have no
# locked unit rate to adjust.
UPLIFTABLE_TARIFF_TYPES: frozenset[str] = frozenset({"fixed", "pass_through"})

# THE COMMODITIES THIS ELIGIBILITY RULE ADMITS. Gas was excluded here from the
# start on the stated ground that it "is priced off a book this policy has never
# been calibrated against" — true when written, and no longer true of any input
# either writer behind this gate needs (2026-09-07):
#
#   * the churn model has had gas constants all along and branches on them
#     (`company/crm/churn_model.py`: a gas base rate and rate sensitivity written
#     for a stickier dual-fuel product). A gas renewal answered on the
#     electricity branch is answered by the WRONG curve, not by a missing one;
#   * `saas/cost_to_serve.cost_to_serve_for_period` already takes `commodity` and
#     switches cadence on it — gas settles daily, electricity half-hourly;
#   * `saas/non_commodity.STANDING_CHARGE_GBP_PER_DAY["gas"]` has carried
#     resi/SME rates since it was written;
#   * `company/pricing/ofgem_price_cap.get_cap_unit_rate_for_date` resolves 'gas'
#     as a first-class fuel, so a gas renewal has a real lawful ceiling to be
#     decided UNDER rather than an electricity one borrowed for it. The two are
#     not close: GBP 33.40/MWh against GBP 190-odd at 2021-06.
#
# WHAT THIS COST WHILE IT STOOD, measured on the world this company runs against:
# 346 of 1,953 offered renewals — 17.7%, and the largest exclusion this company's
# own code owns — refused at `not_the_arms_commodity`, against 120 the value arm
# priced. Both instruments that can speak to the value thesis came back "cannot
# tell" and both attributed it to how few decisions there are to score.
#
# WIDENING IT IS NOT ENOUGH BY ITSELF, and that is why this comment is here. Each
# per-commodity input above has to be READ per-commodity at the call site. A gate
# that admits gas while a writer behind it keeps passing the electricity literal
# prices a gas renewal off an electricity book and says nothing — the same defect
# `test_the_defect_this_control_guards_would_change_a_real_answer` was written
# for, moved one level down, and worse here because on a book that is 87 dual-fuel
# of 164 accounts the electricity leg EXISTS, so the wrong answer is a populated
# plausible one rather than an empty one. See `commodity=` threaded through
# `compute_profitability_uplift` below and through
# `value_based_renewal.observed_account_state`, which now REQUIRES it.
UPLIFTABLE_COMMODITIES: frozenset[str] = frozenset({"electricity", "gas"})
# Term 0 is the acquisition term: there is no prior term to have been negative.
MIN_TERM_INDEX_FOR_UPLIFT: int = 1


def renewal_unit_rate_uplift(
    account_id: str,
    commodity: str,
    tariff_type: Optional[str],
    term_index: int,
    term_start: str,
    locked_unit_rate: Optional[float],
    settled_records: list[dict],
) -> float:
    """Return the £/MWh the supplier adds to THIS renewal for unprofitability.

    `term_start` is the as_of bound applied downstream; nothing that settled on
    or after it can reach the answer.

    Returns 0.0 — not an error, and not a raised exception — for every renewal
    the policy does not apply to, so the caller adds a number rather than
    re-implementing the supplier's eligibility rule at the call site.
    """
    if locked_unit_rate is None:
        return 0.0
    if term_index < MIN_TERM_INDEX_FOR_UPLIFT:
        return 0.0
    if commodity not in UPLIFTABLE_COMMODITIES:
        return 0.0
    if tariff_type not in UPLIFTABLE_TARIFF_TYPES:
        return 0.0
    # THE COMMODITY GOES DOWN WITH IT. While this gate admitted electricity only,
    # `compute_profitability_uplift`'s default WAS the gate's own answer and the
    # omission could not show. It can now: a gas renewal whose prior term is read
    # off the electricity leg of the same dual-fuel household is repriced against
    # a book that is not its own.
    return compute_profitability_uplift(
        account_id, term_start, settled_records, commodity=commodity)
