"""C34 — next best action: one decision per customer, chosen by its effect on forward value.

WHAT THE DECISION IS, SAID BEFORE IT IS GRADED. For one account at one moment, choose ONE action
from the menu the company already takes — debt support, tariff advice, carbon advice — or do
nothing, which is always on the menu. What is ranked is the CHANGE an action makes against doing
nothing (its uplift), never the level of an outcome: ranking on who is likely to leave is
propensity, and targeting on risk is the rule the field trials found inferior to targeting on lift
(Ascarza 2018, `docs/market_research/next_best_action_and_cross_sell.md` §2).

THE CUSTOMER'S BENEFIT FIRST, THEN OURS. An action the company estimates leaves the customer worse
off is not a candidate, whatever it does for us. Among the rest, the one that raises the account's
forward value most is taken, and only if it raises it at all. Charging someone more moves value
without making any; the gate is what stops this rule from choosing that.

FORWARD VALUE has B11's shape (`company/analytics/forward_clv.py`): the sum over the horizon of
P(supplied at the month's start) × monthly margin, that probability being (1 − h)^t after t
months. An action
moves the monthly margin, the monthly departure hazard, or both. Undiscounted, like B11.

DEBT SUPPORT IS A CONSTRAINT AT THE TRIGGER, NOT A CANDIDATE. When the licence requires contact
(SLC 27.5B: two consecutive missed monthly payments), it is taken whatever any other action scores.
Below the trigger it is an ordinary candidate, because for a customer drifting into arrears the
right action may be a tariff or an insulation suggestion (director, 2026-10-05).

LEFT OUT ON PURPOSE. The retention discount at an SVT-to-fix conversion is the director's open
row; it is not on this menu. Cross-sell of non-energy products has no world counterpart and no
established causality (research §3.3) and is not on it either.

AN UNKNOWN EFFECT IS A NAMED None. No published source gives the uplift of a supplier's own offer
to its own customer (research §7 gap 1), and the company runs no holdout that could estimate one
(atom B8). An estimate with any None is UNSCORED, carries its reason onto the decision, and is
never chosen — so with today's inputs every non-debt decision is "nothing", and says why.

THE FLAT BASELINE is B11's flat rule carried over: ONE action for every account, the one with the
best mean estimated effect across the book. The per-customer rule has to beat it on the TRUE
effect of what each rule chose, paired over the same accounts, with an interval; a tie or an
interval straddling zero is "cannot tell".

EPISTEMIC WALL. Pure functions of the company's own estimates. No world state, no socket. Grading
against a true counterfactual (`grade`) is a harness instrument, as `tools/decision_probe.py` is:
the company never holds the truth argument.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from company.analytics.forward_clv import PairedComparison, _paired

# SLC 27.5B: proactive contact is required after two consecutive missed monthly payments. Quoted
# in docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md C1-C2 and
# docs/market_research/next_best_action_and_cross_sell.md §4.4.
SLC_27_5B_CONSECUTIVE_MISSED_MONTHLY_PAYMENTS = 2


class Action(str, Enum):
    DEBT_SUPPORT = "debt_support"
    TARIFF_ADVICE = "tariff_advice"
    CARBON_ADVICE = "carbon_advice"
    NOTHING = "nothing"


@dataclass(frozen=True)
class ActionEstimate:
    """The company's estimate of what one action does to one account, against doing nothing."""

    action: Action
    customer_benefit_gbp_per_year: float | None
    margin_change_gbp_per_month: float | None
    hazard_change_per_month: float | None
    unknown_because: str = ""

    def __post_init__(self) -> None:
        if self.action is Action.NOTHING:
            raise ValueError("doing nothing is the reference every estimate is against, not an estimate")
        if self.missing() and not self.unknown_because:
            raise ValueError(f"{self.action.value}: an unknown effect must name why it is unknown")

    def missing(self) -> tuple[str, ...]:
        return tuple(
            name for name in ("customer_benefit_gbp_per_year", "margin_change_gbp_per_month",
                              "hazard_change_per_month")
            if getattr(self, name) is None
        )


@dataclass(frozen=True)
class AccountState:
    account_id: str
    monthly_margin_gbp: float
    monthly_departure_hazard: float
    consecutive_missed_monthly_payments: int
    estimates: tuple[ActionEstimate, ...]


@dataclass(frozen=True)
class Decision:
    account_id: str
    action: Action
    value_change_gbp: float
    customer_benefit_gbp_per_year: float
    reason: str
    unscored: tuple[tuple[Action, str], ...] = ()


def forward_value(monthly_margin_gbp: float, monthly_hazard: float, horizon_months: int) -> float:
    """B11's forecast shape: sum over months of P(still supplied) × margin."""
    if not 0.0 <= monthly_hazard <= 1.0:
        raise ValueError(f"a monthly hazard must lie in [0, 1], got {monthly_hazard}")
    if horizon_months < 1:
        raise ValueError(f"a horizon must be at least one month, got {horizon_months}")
    survive = 1.0 - monthly_hazard
    # As B11 counts it: margin is earned in a month the account starts supplied, and a departure
    # takes effect at the month's end, so the first month is earned in full.
    return sum(monthly_margin_gbp * survive ** t for t in range(horizon_months))


def value_change(state: AccountState, est: ActionEstimate, horizon_months: int) -> float:
    """Forward value with the action minus forward value without it."""
    with_action = forward_value(
        state.monthly_margin_gbp + est.margin_change_gbp_per_month,
        state.monthly_departure_hazard + est.hazard_change_per_month,
        horizon_months,
    )
    return with_action - forward_value(
        state.monthly_margin_gbp, state.monthly_departure_hazard, horizon_months
    )


def _scored(state: AccountState, horizon_months: int):
    scored, unscored = [], []
    for est in state.estimates:
        if est.missing():
            unscored.append((est.action, f"{', '.join(est.missing())} unknown: {est.unknown_because}"))
        else:
            scored.append((est, value_change(state, est, horizon_months)))
    return scored, tuple(unscored)


def _debt_constraint(state: AccountState, horizon_months: int) -> Decision | None:
    if state.consecutive_missed_monthly_payments < SLC_27_5B_CONSECUTIVE_MISSED_MONTHLY_PAYMENTS:
        return None
    est = next((e for e in state.estimates if e.action is Action.DEBT_SUPPORT), None)
    known = est is not None and not est.missing()
    return Decision(
        state.account_id, Action.DEBT_SUPPORT,
        value_change(state, est, horizon_months) if known else 0.0,
        est.customer_benefit_gbp_per_year if known else 0.0,
        f"licence-required: {state.consecutive_missed_monthly_payments} consecutive missed monthly "
        "payments reach the SLC 27.5B trigger, which pre-empts every other action",
    )


def decide(state: AccountState, horizon_months: int) -> Decision:
    """The per-customer rule."""
    forced = _debt_constraint(state, horizon_months)
    if forced is not None:
        return forced
    scored, unscored = _scored(state, horizon_months)
    fair = [(e, v) for e, v in scored if e.customer_benefit_gbp_per_year >= 0.0]
    if not fair:
        why = "no scored action leaves the customer no worse off" if scored else "no action could be scored"
        return Decision(state.account_id, Action.NOTHING, 0.0, 0.0, why, unscored)
    est, v = max(fair, key=lambda ev: (ev[1], ev[0].customer_benefit_gbp_per_year))
    if v <= 0.0:
        return Decision(state.account_id, Action.NOTHING, 0.0, 0.0,
                        "no action the customer gains from raises forward value", unscored)
    return Decision(state.account_id, est.action, v, est.customer_benefit_gbp_per_year,
                    "largest rise in forward value among actions the customer gains from", unscored)


def flat_action(book: Sequence[AccountState], horizon_months: int) -> Action:
    """The one action with the best mean estimated value change across the book, or nothing.

    An account with no scored estimate for an action counts as zero for it: the flat rule would
    still send it, and with no estimate the company cannot claim it does anything.
    """
    totals: dict[Action, float] = {}
    for state in book:
        for est, v in _scored(state, horizon_months)[0]:
            totals[est.action] = totals.get(est.action, 0.0) + v
    if not totals:
        return Action.NOTHING
    best = max(totals, key=lambda a: (totals[a], a.value))
    return best if totals[best] > 0.0 else Action.NOTHING


def decide_flat(state: AccountState, action: Action, horizon_months: int) -> Decision:
    """The flat rule: the same action for every account; the licence constraint still applies."""
    forced = _debt_constraint(state, horizon_months)
    if forced is not None:
        return forced
    est = next((e for e in state.estimates if e.action is action and not e.missing()), None)
    if est is None:
        return Decision(state.account_id, action, 0.0, 0.0, f"flat rule: {action.value} for every account")
    return Decision(state.account_id, action, value_change(state, est, horizon_months),
                    est.customer_benefit_gbp_per_year, f"flat rule: {action.value} for every account")


@dataclass(frozen=True)
class Grade:
    flat_action: Action
    forgone_value: PairedComparison  # per-customer minus flat; negative favours per-customer
    customer_benefit_per_customer_rule: float
    customer_benefit_flat_rule: float
    chosen: Mapping[Action, int]


def grade(
    book: Sequence[AccountState],
    truth: Mapping[str, Mapping[Action, ActionEstimate]],
    horizon_months: int,
) -> Grade:
    """Both rules choose on the company's estimates; each choice is scored on its TRUE effect.

    ``truth`` is a harness instrument (the counterfactual no supplier sees). An action absent from
    an account's truth did nothing. Scored as value FORGONE (the negative of the true change) so
    the paired comparison reads as B11's does: negative favours per-customer.
    """
    flat = flat_action(book, horizon_months)
    pc_loss, fl_loss, pc_cb, fl_cb = [], [], [], []
    chosen: dict[Action, int] = {}
    for state in book:
        real = truth.get(state.account_id, {})
        mine = decide(state, horizon_months)
        chosen[mine.action] = chosen.get(mine.action, 0) + 1
        for decision, loss, cb in (
            (mine, pc_loss, pc_cb),
            (decide_flat(state, flat, horizon_months), fl_loss, fl_cb),
        ):
            t = real.get(decision.action)
            loss.append(-value_change(state, t, horizon_months) if t else 0.0)
            cb.append(t.customer_benefit_gbp_per_year if t else 0.0)
    n = len(book)
    return Grade(
        flat,
        _paired("value forgone against the true counterfactual, GBP", pc_loss, fl_loss),
        sum(pc_cb) / n if n else float("nan"),
        sum(fl_cb) / n if n else float("nan"),
        chosen,
    )
