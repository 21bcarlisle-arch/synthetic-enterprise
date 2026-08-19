"""The supplier's own customer-value view of its book — serve, retain, value, post.

WHY THIS LIVES COMPANY-SIDE (KNIFE pass 3, `A_composition_lift`, step 15,
2026-08-11, disposition register §3j). Four builders sat inlined in
`simulation/run_phase4c_on_phase2b.py`'s `main()`, and not one of them is world
physics:

  1. `saas.cost_to_serve.build_cost_to_serve` — what it costs this supplier to
     serve each account, and the net margin that leaves.
  2. `saas.churn_model.build_churn_risk` — the supplier's ESTIMATE of the
     probability each account walks at its next renewal.
  3. `saas.home_move_win_rate.build_home_move_win_rates` — the supplier's
     estimate of how often it wins the property when the occupant moves, and the
     effective retention that implies.
  4. `saas.enterprise_value.build_enterprise_value` — the CLV roll-up of the
     book those three produce.

A fifth call, `build_cost_to_serve_ledger_events`, is the same cost-to-serve
schedule shaped into monthly account-6100 postings. It is here for the reason
§3i gave for the close itself: a supplier's chart of accounts is its own.

EVERY ONE OF THESE IS A BELIEF, NOT A FACT, and that is the whole argument for
the cut. The world knows who actually churned; this module never asks it. It
reads the supplier's own settled records and its own customer book and produces
the supplier's OPINION about value and retention — an opinion a real supplier is
free to be wrong about, and frequently is. Leaving the composition world-side
made the world the thing that decides how the supplier values its customers.

THE READ DIRECTION IS THE TEST OF THE CUT, the same one §3f and §3i applied.
This module imports nothing from `simulation/` or `sim/`: the settled records
and the customer list arrive as plain dicts through `build_customer_value_view`'s
signature. Had the composition moved with a `simulation.*` import intact it would
have traded class-(b) crossings for class-(a) ones — the strictly forbidden
direction, which is at zero and stays there.

BEHAVIOUR IS UNCHANGED BY CONSTRUCTION. Nothing is reimplemented: the same five
functions are called with the same arguments in the same relative order,
including `build_enterprise_value`'s defaulted `n_draws`/`random_seed`, which the
inlined code also left defaulted. `price_differential_pct` is a RUN parameter and
stays one — it arrives through the signature rather than being read from a world
module, so no constant crosses.

THE ONE THING THAT DID MOVE, STATED RATHER THAN BURIED. In the pre-cut file
`build_cost_to_serve_ledger_events` was called ~50 lines LATER than the other
four, just above the accounting close. It is a pure function of
`(settlement_records, customers)`, and between the two pre-cut call sites `main()`
only reads `bills`/`payment_behaviour` and prints — it neither rebinds nor
mutates `all_records`. That is not left as an assertion: the seam test carries an
AST control over `main()` that fails if any statement between the view call and
the close mutates or rebinds the record list, and its mutation (an injected
`all_records.append(...)`) reds it. Without that control the identity claim would
rest on a reading of the file, which is exactly the shape R15 calls a tautology.

POINT-IN-TIME NOTE, because this module takes a whole run's records and that is
the shape of the 2026-07-10 hedge-volatility foresight bug. There is deliberately
no `as_of` bound and its absence is not an oversight: the customer-value view is
an after-the-fact aggregation over records that have ALREADY settled, and it is
the same full-record input `build_cost_to_serve` and `build_churn_risk` have
always taken. `enterprise_value` is forward-LOOKING in what it projects but not
in what it reads — it consumes only the two aggregates above. If a future caller
ever routes a point-in-time DECISION (a price, a hedge, a renewal offer) through
this output, that caller needs the bound; this module does not.
"""

from __future__ import annotations

from dataclasses import dataclass

from company.analytics.clv_three_horizon import (
    AccountObservables,
    BookCLV,
    RenewalPoint,
    estimate_book,
)
from saas.churn_model import CONTRACT_LENGTH_DAYS, build_churn_risk
from saas.cost_to_serve import build_cost_to_serve, build_cost_to_serve_ledger_events
from saas.enterprise_value import build_enterprise_value, ceased_billing_accounts
from saas.home_move_win_rate import build_home_move_win_rates

__all__ = ["CustomerValueView", "build_customer_value_view"]

#: Contract term in years, by the roster's own `contract_type`. Anything unmapped
#: takes 365 days — NOT as a silent default but as the assumption
#: `saas.churn_model` already makes for every account in the book: its renewal
#: points are annual anniversaries of `acquisition_date` and nothing else. Using a
#: different term here would value a contract over a horizon the company's own
#: churn model does not believe it has.
_CONTRACT_TERM_YEARS = {"fixed_1yr": 1.0, "fixed_2yr": 2.0, "fixed_3yr": 3.0}
_DEFAULT_TERM_YEARS = CONTRACT_LENGTH_DAYS / 365.0


@dataclass(frozen=True)
class CustomerValueView:
    """What the supplier believes its book is worth, and what that costs to post.

    Field-for-field the same four objects `main()` used to build inline, plus the
    account-6100 schedule. Frozen because it is a VIEW: recomputing it is cheap
    and mutating one field while the others stay stale is the defect this shape
    removes.
    """

    cost_to_serve: dict
    churn_risk: dict
    home_move_win_rates: dict
    enterprise_value: dict
    cost_to_serve_ledger_events: list[dict]
    #: EP1 — the same book on three valuation bases, each carrying its time model
    #: and its population. It sits BESIDE `enterprise_value` rather than replacing
    #: it: `enterprise_value` is the figure the board and the live site are
    #: published from today, and swapping the number under a published surface is
    #: a VERIFY-stage act needing evidence on the rendered value (R11), not a
    #: side effect of building the estimator. What this field buys now is that
    #: EP1 is EXERCISED on the real book on every run — against the live
    #: population's blanks and ceased accounts, not only against a fixture —
    #: which is the difference between built and dark.
    three_horizon_clv: BookCLV


def build_customer_value_view(
    settlement_records: list[dict],
    customers: list[dict],
    price_differential_pct: float,
) -> CustomerValueView:
    """Build the supplier's customer-value view over its own settled records.

    `settlement_records` and `customers` are DATA the world hands over — what
    physically flowed, and who the supplier's customers are. Everything derived
    from them here is the supplier's own belief.

    `price_differential_pct` is the run's market-position parameter (how this
    supplier's price sits against the market it competes in), which both the
    home-move and enterprise-value models need. It is passed rather than read so
    that no world constant crosses the wall to set it.
    """
    cost_to_serve = build_cost_to_serve(settlement_records, customers)
    churn_risk = build_churn_risk(settlement_records, customers)
    home_move_win_rates = build_home_move_win_rates(
        churn_risk, customers, price_differential_pct
    )
    # The supplied book, read off the supplier's OWN settled records. Note what
    # this does NOT do: the world's `churned_billing_accounts` sits in the same
    # run output and is not consulted, so the note at the top of this file
    # ("The world knows who actually churned; this module never asks it") still
    # holds. What changed is that the supplier now notices its own meters have
    # stopped settling, which it always could have.
    ceased = ceased_billing_accounts(settlement_records)
    enterprise_value = build_enterprise_value(
        churn_risk, cost_to_serve, customers, price_differential_pct,
        ceased_accounts=ceased,
    )
    cost_to_serve_ledger_events = build_cost_to_serve_ledger_events(
        settlement_records, customers
    )
    three_horizon_clv = estimate_book(
        _clv_observables(churn_risk, enterprise_value, customers, ceased)
    )
    return CustomerValueView(
        cost_to_serve=cost_to_serve,
        churn_risk=churn_risk,
        home_move_win_rates=home_move_win_rates,
        enterprise_value=enterprise_value,
        cost_to_serve_ledger_events=cost_to_serve_ledger_events,
        three_horizon_clv=three_horizon_clv,
    )


def _clv_observables(
    churn_risk: dict,
    enterprise_value: dict,
    customers: list[dict],
    ceased: set[str],
) -> list[AccountObservables]:
    """Assemble EP1's inputs from beliefs this view has ALREADY formed.

    Nothing new is read and nothing new crosses the wall: the renewal
    trajectories are the supplier's own churn estimate, the margins are the ones
    its own valuation already published per account, and the roster is the
    customer list handed in through the signature. EP1 is a re-reading of what
    the company already believes, not a new observation of the world.

    THE BLANKS ARE CARRIED, NOT DROPPED, and that is the whole point of routing
    through this function rather than iterating `enterprise_value["by_customer"]`.
    That dict excludes ceased accounts and accounts with no renewal history — on
    the live book, 5 of 13 — so an estimator fed from it would see a population
    with no blanks in it and every population control over that population would
    be degenerate. Here an account absent from it arrives with
    `annual_margin_gbp=None`, which EP1 excludes under a NAMED reason instead of
    counting as the number zero.
    """
    by_account = enterprise_value["by_customer"]
    roster = {c["customer_id"]: c for c in customers}
    observables: list[AccountObservables] = []
    for account_id, renewals in churn_risk.items():
        # The roster is keyed per commodity ("C1g"), the book per billing account
        # ("C1"); an account with no roster row is a real possibility and takes
        # the empty dict, so every field below falls to a stated default rather
        # than raising inside a run.
        row = roster.get(account_id, {})
        margin = by_account.get(account_id, {}).get("avg_annual_net_margin_gbp")
        acquisition_date = str(row.get("acquisition_date", ""))
        observables.append(
            AccountObservables(
                account_id=account_id,
                segment=str(row.get("segment", "unsegmented")),
                # The roster carries no acquisition channel. Naming that absence
                # is the honest move: inventing a channel here would put a
                # fabricated observable into a valuation.
                channel=str(row.get("acquisition_type", "unobserved")),
                acquisition_year=(
                    int(acquisition_date[:4]) if acquisition_date[:4].isdigit() else 0
                ),
                contract_term_years=_CONTRACT_TERM_YEARS.get(
                    row.get("contract_type"), _DEFAULT_TERM_YEARS
                ),
                renewal_history=tuple(
                    RenewalPoint(
                        renewal_period=r["renewal_period"],
                        churn_probability=r["churn_probability"],
                    )
                    for r in renewals
                ),
                annual_margin_gbp=(
                    None if margin is None else float(margin)
                ),
                still_supplied=account_id not in ceased,
            )
        )
    return observables
