"""The supplier's hedging desk — the mandate, the decision, the book, the roll.

KNIFE pass 3, `A_composition_lift` step 23, 2026-08-13, disposition register
§3r. Before this, `simulation/run_phase2b.py::main()` WAS the trading desk: it
held the company's mandate floor and did the `1 - floor` arithmetic itself, ran
the VaR hedge decision at both commodity sites, decided whether the risk
committee's override survived that decision, assembled the VaR log entry,
computed the bid-ask cost and tenor, attributed a counterparty, constructed the
`ForwardContract`, held the `TradingBook`, settled every period against it, and
rolled the fraction forward from the completed term's P&L.

Three of that module's wall crossings (`company.trading.forward_book`,
`company.trading.hedge_decision`, `company.risk.hedge_policy`).

WHY THESE THREE ARE ONE DESK AND NOT THREE ITEMS. §3m's group test is "do they
feed ONE total?", and here they do: the mandate floors the fraction, the VaR
decision sets it, the fraction sizes the notional the position is opened at, the
position's P&L is decomposed onto that same term's settlement records, and the
term's realised P&L is what rolls the fraction to the next term. One number —
the fraction of a term the supplier has bought forward — passes through all
three modules and comes out the other side as next term's opening position.

WHAT THE WORLD KEEPS, deliberately. The point-in-time price view is the SIM's
blindfold machinery, not the desk's: the world builds it and hands over plain
`price_records`, exactly as §3n handed over spot histories. The desk therefore
imports nothing from `simulation/` or `sim/` — the read direction that makes
this a cut rather than a file move (§3f, §3i, §3l, §3m, §3n, §3p, §3q).

THE OVERRIDE IS THE DESK'S, NOT THE WORLD'S. Before the cut the world wrote
`if cid not in pending_committee_overrides: hf = _var_hf`, then computed the
realised VaR at whichever fraction survived. That ordering is load-bearing —
the VaR reported is the risk actually carried, not the risk the model asked
for — and it was previously visible only as two adjacent statements in a 2,900
line function. It is now one signature (`accept_decision`) and one documented
sequence inside `decide_term_hedge`.
"""

from __future__ import annotations

from dataclasses import dataclass

from company.risk.hedge_policy import (
    COMPANY_MIN_HEDGE_FLOOR,
    company_evolve_hedge_fraction,
)
from company.trading.forward_book import (
    ForwardContract,
    TradingBook,
    assign_default_counterparty,
)
from company.trading.hedge_decision import (
    compute_bid_ask_cost,
    compute_realized_var,
    decide_hedge_fraction,
)

__all__ = [
    "HedgeMandate",
    "TermHedge",
    "HedgeDesk",
    "build_hedge_desk",
    "hedge_mandate",
]


@dataclass(frozen=True)
class HedgeMandate:
    """What the supplier has told itself it will never go below.

    The `naked_fraction` here is the reason this is a value object rather than a
    re-exported float: `1 - floor` is the desk's own arithmetic, and the world
    used to do it (`naked_fraction=1 - MIN_HEDGE_FLOOR`) while pricing a gas
    renewal. A supplier's cost of capital is priced on the position it intends
    to leave open; that intention belongs to the desk that forms it.
    """

    minimum_hedged_fraction: float

    @property
    def opening_hedge_fraction(self) -> float:
        """Where every term starts before any decision is taken.

        A supply obligation is managed first and speculated on second, so the
        opening position is the mandate floor rather than a neutral 50/50.
        """
        return self.minimum_hedged_fraction

    @property
    def naked_fraction(self) -> float:
        """The share of volume the mandate leaves exposed to spot."""
        return 1.0 - self.minimum_hedged_fraction


@dataclass(frozen=True)
class TermHedge:
    """The desk's answer for one term: the fraction, whose it is, and the risk left."""

    hedge_fraction: float
    decision_accepted: bool
    var_log_entry: dict


def hedge_mandate() -> HedgeMandate:
    """The company's standing hedge mandate."""
    return HedgeMandate(minimum_hedged_fraction=COMPANY_MIN_HEDGE_FLOOR)


class HedgeDesk:
    """One desk per run: it decides, it executes, it settles, and it rolls.

    Holds the run's `TradingBook`. The book is reachable as `.book` because the
    counterparty-collateral door (§3n) marks it and the report summarises it —
    the world carries an object it received from company code to another
    company door, and never learns its type.
    """

    def __init__(self, book: TradingBook | None = None) -> None:
        self._book = book if book is not None else TradingBook()
        self._mandate = hedge_mandate()

    @property
    def book(self) -> TradingBook:
        return self._book

    @property
    def mandate(self) -> HedgeMandate:
        return self._mandate

    def decide_term_hedge(
        self,
        *,
        customer_id: str,
        term_start: str,
        term_end: str,
        commodity: str,
        volume_kwh: float,
        forward_price_gbp_per_mwh: float,
        unit_rate_gbp_per_mwh: float,
        price_records: list[dict],
        term_days: int,
        current_fraction: float,
        accept_decision: bool,
    ) -> TermHedge | None:
        """Set the hedge fraction for a term and record the risk actually carried.

        `accept_decision` is False when the risk committee has already ruled on
        this customer: the committee's fraction stands and the model's is
        discarded. THE ORDER MATTERS — the realised VaR is computed at the
        fraction that SURVIVES, not at the one the model proposed, so a
        committee-overridden term reports the risk it is really running.

        RETURNS `None` WHEN THE DESK IS NOT RUNNING THE VaR LAYER AT ALL —
        KNIFE3 step 39 (§3ah). `run_phase2b` used to gate both call sites on
        `policy.use_var_hedge_decision`, reading the supplier's own Phase-43b
        switch off a `DecisionPolicy` it held, in order to decide whether to
        consult the supplier's desk. The world deciding whether to ask the
        company a question is the company's decision, sited in the world.

        Now the world always asks and the DESK declines, resolving the switch
        from the run's active policy on this side of the seam. `None` is the
        established shape for a company door that declines: the same term loop
        already reads `request_tou_offer(...) is not None` for "the supplier
        chose not to offer this customer a ToU product".

        WHY NOT `decision_accepted=False`, which already exists and looks free:
        that field means the RISK COMMITTEE overrode the model, and a term where
        the committee ruled still carries a `var_log_entry` reporting the risk
        actually run. A term where the VaR layer is switched off carries no
        entry at all, because no VaR decision was taken. Collapsing the two
        would put rows in `hedge_var_log` that no desk ever decided, and the
        naive arm's risk reporting would silently gain a decade of them.
        """
        from company.policy.decision_policy import active_policy

        if not active_policy().use_var_hedge_decision:
            return None

        decided = decide_hedge_fraction(
            volume_kwh,
            forward_price_gbp_per_mwh,
            unit_rate_gbp_per_mwh,
            price_records,
            term_days,
        )
        effective = decided if accept_decision else current_fraction
        realized = compute_realized_var(
            volume_kwh,
            forward_price_gbp_per_mwh,
            unit_rate_gbp_per_mwh,
            price_records,
            term_days,
            effective,
        )
        return TermHedge(
            hedge_fraction=effective,
            decision_accepted=accept_decision,
            var_log_entry={
                "customer_id": customer_id,
                "term_start": term_start,
                "term_end": term_end,
                "commodity": commodity,
                "hedge_fraction": round(effective, 4),
                **realized,
            },
        )

    def open_term_hedge(
        self,
        *,
        customer_id: str,
        term_start: str,
        term_end: str,
        volume_kwh: float,
        forward_price_gbp_per_mwh: float,
        hedge_fraction: float,
        term_days: int,
    ) -> ForwardContract:
        """Execute the hedge: size it, price the spread, name the counterparty, book it.

        `agreed_price` is the forward the company locked at tariff signing, and
        the notional is the hedged share of its own demand estimate — both
        company-observable, neither read from the world.
        """
        tenor_years = term_days / 365.25
        notional_mwh = (volume_kwh / 1000.0) * hedge_fraction
        bid_ask = compute_bid_ask_cost(forward_price_gbp_per_mwh, tenor_years) * notional_mwh
        counterparty = assign_default_counterparty(customer_id, term_start, notional_mwh)
        contract = ForwardContract(
            customer_id=customer_id,
            term_start=term_start,
            term_end=term_end,
            notional_mwh=notional_mwh,
            agreed_price_gbp_per_mwh=forward_price_gbp_per_mwh,
            hedge_fraction=hedge_fraction,
            bid_ask_cost_gbp=round(bid_ask, 4),
            counterparty_id=counterparty.counterparty_id,
            counterparty_type=counterparty.counterparty_type,
            clearing_status=counterparty.clearing_status,
            counterparty_rating=counterparty.counterparty_rating,
            broker_arranged=counterparty.broker_arranged,
        )
        self._book.open_hedge(contract)
        return contract

    def settle_period_pnl_gbp(
        self,
        customer_id: str,
        term_start: str,
        consumed_kwh: float,
        actual_spot_gbp_per_mwh: float,
    ) -> float:
        """Hedge P&L for one settlement period, £. Zero when no contract matches."""
        return self._book.settle_period(
            customer_id, term_start, consumed_kwh, actual_spot_gbp_per_mwh
        ).pnl_gbp

    def roll_hedge_fraction(
        self,
        current_fraction: float,
        naked_net_gbp: float,
        actual_net_gbp: float,
    ) -> tuple[float, str]:
        """Set the NEXT term's opening fraction from this term's outcome.

        The backward-looking arm of the same desk: the VaR decision asks what
        the market looks like now, this asks whether the last hedge was worth
        paying for. Floored at the mandate by `company_evolve_hedge_fraction`.
        """
        return company_evolve_hedge_fraction(
            current_fraction, naked_net_gbp, actual_net_gbp
        )

    def summary(self) -> dict:
        """The book's position summary, for the report."""
        return self._book.summary()


def build_hedge_desk() -> HedgeDesk:
    """One desk, one book, for one run."""
    return HedgeDesk()
