"""The typed record the run loop hands the company when it asks what a renewal costs.

WHY A RECORD (director, 2026-10-11 principles; 2026-10-12: "the typed seam record for run-loop
inputs"). Until 2026-10-12 `simulation/run_phase2b.py` handed `decide_renewal_rate` nineteen loose
keyword values. Every one was company-observable, but nothing on the seam SAID so: a twentieth
keyword carrying a world-only quantity would have crossed with every instrument green, because the
call terminates on the exempt seam package. This record is the declaration. The run loop builds it,
`company.interfaces.renewal_rate_chain.decide_renewal` takes it, and its field list is an allow-list
held by `tests/architecture/test_the_run_loop_hands_the_company_a_typed_record.py`.

WHAT MAY NEVER BE ADDED. A field a real supplier could not hold: the household's true consumption,
its hidden price sensitivity or income stress, a draw the world made and did not report. If the
desk needs one, the answer is a new observable reported through the seam, not a field here. This
module imports nothing from `sim/` or `simulation/`, and the control above refuses one that does.

THE FIELDS, each something the supplier itself holds:
  customer_id, billing_account   -- its own account keys.
  commodity, term_start          -- the fuel on the contract and the day the new term begins.
  tariff_type, term_index        -- the product the term is on and how many terms the account has had.
  struck_unit_rate_per_mwh       -- the unit rate the run struck before the desk adjusts it, or None.
  portfolio_margin_rates         -- its own realised margin rate per COMPLETED term on this fuel,
                                    oldest first (`PortfolioMarginBook`). Passed by reference: the
                                    desk reads it during the call and does not keep it.
  prior_term_margin, prior_term_revenue
                                 -- this account's last term on its own P&L (net margin, revenue), in
                                    the book's currency; the margin is None for an account's first term.
  is_domestic, segment           -- what the account was signed as.
  settled_records                -- its own settled records for the account so far.
  customer                       -- the customer record it holds (metering facts the ToU offer reads).
  arrears_state, receivable      -- read off its own ledger through the payment triad, or None.
  payment_method                 -- as the payment-method seam reports it, or None if not asked.
  default_belief_rate            -- its own book's default rate, asked only under that policy.
  own_default_tariff_inc_vat_per_mwh
                                 -- its own default tariff on the day, for a domestic account.
  company_forward_per_mwh, locked_policy_cost_per_mwh, locked_network_cost_per_mwh
                                 -- what the company's own offer for this term priced off: its own
                                    forward and the two pass-through costs it locked. Their sum is
                                    the cost floor its desk struck over, and no discount in the chain
                                    may go under it (2026-10-12). None where the term has no offer.
  portfolio_priced_for_rates     -- index for index with `portfolio_margin_rates`: the margin rate
                                    each of those terms' own strike priced for, on the same basis
                                    (`PortfolioMarginBook.priced_for`, 2026-10-14). None leaves the
                                    premium on its old 8% literal.

FROZEN, SHALLOWLY. The record cannot be re-pointed after it is built. The lists and dicts it carries
are the run's own objects, passed by reference exactly as the keywords were, so the decision is
unchanged byte for byte.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["RenewalDecisionInputs"]


@dataclass(frozen=True)
class RenewalDecisionInputs:
    customer_id: str
    billing_account: str
    commodity: str
    term_start: str
    tariff_type: str | None
    term_index: int
    struck_unit_rate_per_mwh: float | None
    portfolio_margin_rates: list[float]
    prior_term_margin: float | None
    prior_term_revenue: float
    is_domestic: bool
    settled_records: list[dict]
    customer: dict
    segment: str | None = None
    arrears_state: str | None = None
    receivable: dict | None = None
    payment_method: str | None = None
    default_belief_rate: float | None = None
    own_default_tariff_inc_vat_per_mwh: float | None = None
    company_forward_per_mwh: float | None = None
    locked_policy_cost_per_mwh: float | None = None
    locked_network_cost_per_mwh: float | None = None
    portfolio_priced_for_rates: list[float | None] | None = None
