"""C34 — next best action: one decision per customer, chosen by its effect on forward value.

WHAT THE DECISION IS, SAID BEFORE IT IS GRADED. For one account at one moment, choose ONE action
from the menu the company already takes — debt support, tariff advice, carbon advice — or do
nothing, which is always on the menu. What is ranked is the CHANGE an action makes against doing
nothing (its uplift), never the level of an outcome: ranking on who is likely to leave is
propensity, and targeting on risk is the rule the field trials found inferior to targeting on lift
(Ascarza 2018, `docs/market_research/next_best_action_and_cross_sell.md` §2).

JOINT VALUE, WITH A NO-LOSS FLOOR ON BOTH SIDES (canon v4 C7, ruled 2026-10-12, decision 5). An
action the company estimates leaves the customer worse off, or lowers our forward value, is not a
candidate. Among the rest, the one with the largest JOINT value is taken: the household's benefit
over the horizon plus our forward-value change, taken only if that sum is positive. Charging someone
more moves value without making any; the customer's floor is what stops this rule from choosing
that, and our floor is what keeps a gift from being called a decision.
The household's benefit over the horizon is its yearly benefit x horizon/12, undiscounted like B11.
It is not weighted by survival, because advice keeps paying the household after it leaves us.

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
`hazard_estimate_from_holdout` is the first door that fills one: it reads an action's hazard
effect from a coin-drawn holdout, and only when the holdout's interval decides.
`in_contact_holdout` is the coin a run draws to keep that holdout, and `holdout_observations`
reads the run's default-tariff decisions back into the rows the door takes.

THE FLAT BASELINE is B11's flat rule carried over: ONE action for every account, the one with the
best mean estimated effect across the book. The per-customer rule has to beat it on the TRUE
effect of what each rule chose, paired over the same accounts, with an interval; a tie or an
interval straddling zero is "cannot tell".

PRICING A SHARE OF WHAT AN ACTION CREATES (C35; director 2026-10-15: "not a ruling from me").
C34 found the joint-value rule positive-sum and negative on our side in every cell, so it chose
nothing. The supplier may ask the household for a share of the benefit as a one-off fee. The fee
is a transfer: it adds to our side what it takes from theirs and leaves the joint value of a
TAKEN action unchanged. What it moves is whether the action is taken, so the share is chosen by
the EXPECTED joint value, take-up times joint value, under both no-loss floors at that share.
With take-up falling as the share rises, the best share is the lowest one that clears our floor:
every penny above it costs households who would have said yes and buys nothing for the pair.
The fee is one-off because a share recovered by instalments is regulated consumer credit, as the
Green Deal's was (SI 2012/2798; `how_a_supplier_prices_a_share_of_value_it_creates_for_a_household_2026-10-14.md`
§1). Take-up is the household's (the world's, W2_39); the supplier knows it only at the shares it
has tried and observed, so it searches those points and no grid of its own. No points tried, and
the action stays priced as C34 prices it, which is the honest default: C35 adds nothing it
cannot see.

THE SECOND SHAPE OF SHARE: A RISE ON A FIXED RETENTION TARIFF AT RENEWAL (C35, 2026-10-17;
`a_retention_price_that_shares_the_value_an_action_creates.md` §4c). The share travels as a
monthly rise on the fix offered at renewal, paid only in the months the household stays. That is
lawful as a Fixed Retention Tariff under the SLC 22B derogation, which sets no price rule (§2). It
is the smallest rise that brings our side to at least zero, and it must do that twice: once with
the hazard held, and once with the price's own effect on staying added at the published slope. A
rise that clears zero only by driving a loss-making account away is shedding the account, not
sharing value (§4b's trap). It is capped by the headroom under the published default: a stayer
offered a fix dearer than the default goes onto the default instead (§4a). Before 2019 no
per-fuel default was published, so the headroom is unknown and the rise is refused. It is off unless
the policy names it (`DecisionPolicy.next_best_action_shares_by_retention_rise`).

EPISTEMIC WALL. Pure functions of the company's own estimates. No world state, no socket. Grading
against a true counterfactual (`grade`) is a harness instrument, as `tools/decision_probe.py` is:
the company never holds the truth argument.
"""
from __future__ import annotations

import hashlib
import math
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Mapping, Sequence

from company.analytics.forward_clv import PairedComparison, _paired

if TYPE_CHECKING:
    from company.policy.decision_policy import DecisionPolicy

# SLC 27.5B: proactive contact is required after two consecutive missed monthly payments. Quoted
# in docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md C1-C2 and
# docs/market_research/next_best_action_and_cross_sell.md §4.4.
SLC_27_5B_CONSECUTIVE_MISSED_MONTHLY_PAYMENTS = 2

# The fall in P(stay at renewal) per GBP a year of price gap, within one household: Deller et al.
# (2021), Energy Journal 42(3), average marginal effect 0.0013-0.0016, read at its midpoint
# (docs/market_research/retention_slope_per_pound_of_renewal_cut.md §1). Measured on opted-in
# switchers, so it overstates an inactive book's response; the world's own is 0.00065 at the
# median (a_retention_price_that_shares_the_value_an_action_creates.md §4a). A rise of GBP d a
# month adds this times d to the monthly hazard.
PUBLISHED_RENEWAL_STAYING_SLOPE_PER_GBP_YEAR = 0.0015

# A rise is priced to the penny, the unit a tariff is quoted in.
_RISE_STEP_GBP_PER_MONTH = 0.01


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
class SharePoint:
    """One share of the household's benefit the company has offered, and what it observed.

    ``hazard_change_per_month`` is the departure-hazard change among households offered the action
    at this share; None means the price did not move it from the action's own estimate.
    """

    share: float
    take_up: float
    hazard_change_per_month: float | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.share <= 1.0:
            raise ValueError(f"a share of the household's benefit lies in [0, 1], got {self.share}")
        if not 0.0 <= self.take_up <= 1.0:
            raise ValueError(f"take-up is a probability, got {self.take_up}")


@dataclass(frozen=True)
class ShareResponse:
    """The company's observed household response to the share it asks for one action."""

    action: Action
    points: tuple[SharePoint, ...]


@dataclass(frozen=True)
class SharePrice:
    share: float
    fee_gbp: float
    take_up: float
    expected_value_change_gbp: float
    expected_customer_benefit_gbp: float
    expected_joint_value_gbp: float


@dataclass(frozen=True)
class RenewalTerms:
    """What the company holds about one account at its renewal, to price a rise on its fix.

    Rates are GBP/MWh ex VAT. ``published_default_gbp_per_mwh`` is the published default for the
    account's fuel on the renewal date (`company.crm.save_offer.published_default_rate_ex_vat`);
    None means none was published, as before 2019.
    """

    fixed_offer_gbp_per_mwh: float
    published_default_gbp_per_mwh: float | None
    annual_mwh: float | None

    def headroom_gbp_per_month(self) -> float | None:
        if self.published_default_gbp_per_mwh is None or not self.annual_mwh:
            return None
        return (self.published_default_gbp_per_mwh - self.fixed_offer_gbp_per_mwh) * self.annual_mwh / 12.0


@dataclass(frozen=True)
class RetentionRise:
    rise_gbp_per_month: float
    headroom_gbp_per_month: float
    value_change_gbp: float
    customer_benefit_kept_gbp: float
    expected_joint_value_gbp: float


@dataclass(frozen=True)
class AccountState:
    account_id: str
    monthly_margin_gbp: float
    monthly_departure_hazard: float
    consecutive_missed_monthly_payments: int
    estimates: tuple[ActionEstimate, ...]
    share_responses: tuple[ShareResponse, ...] = ()
    renewal: RenewalTerms | None = None


@dataclass(frozen=True)
class Decision:
    account_id: str
    action: Action
    value_change_gbp: float
    customer_benefit_gbp_per_year: float
    reason: str
    unscored: tuple[tuple[Action, str], ...] = ()
    share: SharePrice | RetentionRise | None = None


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


def joint_value(value_change_gbp: float, customer_benefit_gbp_per_year: float,
                horizon_months: int) -> float:
    """C7's ranking key: the household's benefit over the horizon plus our forward-value change."""
    return value_change_gbp + customer_benefit_gbp_per_year * horizon_months / 12.0


def price_share(state: AccountState, est: ActionEstimate, response: ShareResponse,
                horizon_months: int) -> tuple[SharePrice | None, str]:
    """The tried share with the largest expected joint value under both floors, or None and why.

    The fee is ``share`` x the household's benefit over the horizon, taken once. Ties go to the
    lower share: the customer's side first.
    """
    benefit = est.customer_benefit_gbp_per_year * horizon_months / 12.0
    if not response.points:
        return None, "no share has been tried, so take-up at any share is unknown"
    best: SharePrice | None = None
    for p in sorted(response.points, key=lambda p: p.share):
        hazard = est.hazard_change_per_month if p.hazard_change_per_month is None else p.hazard_change_per_month
        fee = p.share * benefit
        ours = value_change(state, ActionEstimate(est.action, est.customer_benefit_gbp_per_year,
                                                  est.margin_change_gbp_per_month, hazard),
                            horizon_months) + fee
        theirs = benefit - fee
        if ours < 0.0 or theirs < 0.0:
            continue
        cand = SharePrice(p.share, fee, p.take_up, p.take_up * ours, p.take_up * theirs,
                          p.take_up * (ours + theirs))
        if best is None or cand.expected_joint_value_gbp > best.expected_joint_value_gbp:
            best = cand
    if best is None:
        return None, "no tried share leaves both the customer and us no worse off"
    return best, ""


def price_retention_rise(state: AccountState, est: ActionEstimate, terms: RenewalTerms,
                         horizon_months: int,
                         slope_per_gbp_year: float = PUBLISHED_RENEWAL_STAYING_SLOPE_PER_GBP_YEAR,
                         ) -> tuple[RetentionRise | None, str]:
    """The smallest monthly rise on the renewal fix that brings our side to at least zero, or None and why.

    Our side is held to zero twice: with the hazard held, and with ``slope_per_gbp_year`` x rise
    added to it. The rise must sit within the headroom under the published default, and the
    household must keep at least nothing: its benefit over the horizon, less the rise paid over
    its expected supplied months.
    """
    headroom = terms.headroom_gbp_per_month()
    if headroom is None:
        why = ("no published default for this fuel on the renewal date" if terms.annual_mwh
               else "the account's annual volume is unknown")
        return None, f"{why}, so the headroom under the default is unknown and no rise is offered"
    benefit = est.customer_benefit_gbp_per_year * horizon_months / 12.0

    def ours(rise: float, slope: float) -> float:
        hazard = min(1.0 - state.monthly_departure_hazard,
                     est.hazard_change_per_month + slope * rise)
        return value_change(state, ActionEstimate(est.action, est.customer_benefit_gbp_per_year,
                                                  est.margin_change_gbp_per_month + rise, hazard),
                            horizon_months)

    # With the hazard held, our side rises one-for-one with the rise over the supplied months.
    held = ours(0.0, 0.0)
    supplied = forward_value(1.0, state.monthly_departure_hazard + est.hazard_change_per_month,
                             horizon_months)
    rise = 0.0 if held >= 0.0 else round(
        math.ceil(-held / supplied / _RISE_STEP_GBP_PER_MONTH - 1e-9) * _RISE_STEP_GBP_PER_MONTH, 2)
    if rise > headroom:
        return None, (f"the rise our side needs ({rise:.2f} GBP/month) is above the headroom under "
                      f"the default ({headroom:.2f} GBP/month): a stayer would decline it onto the default")
    while ours(rise, 0.0) < 0.0 or ours(rise, slope_per_gbp_year) < 0.0:
        rise = round(rise + _RISE_STEP_GBP_PER_MONTH, 2)
        if rise > headroom:
            return None, ("no rise within the headroom under the default "
                          f"({headroom:.2f} GBP/month) brings our side to zero once the price's own "
                          "effect on staying is counted")
    hazard = min(1.0 - state.monthly_departure_hazard,
                 est.hazard_change_per_month + slope_per_gbp_year * rise)
    paid = rise * forward_value(1.0, state.monthly_departure_hazard + hazard, horizon_months)
    kept = benefit - paid
    if kept < 0.0:
        return None, (f"a {rise:.2f} GBP/month rise takes {paid:.2f} GBP, more than the advice gives "
                      f"the household ({benefit:.2f} GBP over the horizon)")
    v = ours(rise, slope_per_gbp_year)
    return RetentionRise(rise, headroom, v, kept, v + kept), ""


def hazard_estimate_from_holdout(action: Action, observations, window_months: int,
                                 customer_benefit_gbp_per_year: float | None,
                                 margin_change_gbp_per_month: float | None) -> ActionEstimate:
    """An action's effect on the departure hazard, from the company's own coin-drawn holdout.

    Each row is ``{"arm": "treated" | "holdout", "stayed": bool}`` over a window of
    `window_months`. B8's interval decides: an undecided or refused holdout leaves the hazard None
    with the interval as its reason, so the action stays unscored. A decided one converts both stay
    shares to a constant monthly hazard, ``1 - s ** (1 / w)``, and returns the difference
    (research §6.2).
    """
    from company.pricing.discovered_price_sensitivity import estimate_offer_effect

    if window_months < 1:
        raise ValueError(f"a holdout window must be at least one month, got {window_months}")
    eff = estimate_offer_effect(observations)
    if eff.verdict in ("refused", "undecided"):
        span = "" if eff.low is None else f" [{eff.low:+.3f}, {eff.high:+.3f}]"
        why = (f"holdout {eff.treated} contacted / {eff.held_out} held out{span}: {eff.reason}")
        return ActionEstimate(action, customer_benefit_gbp_per_year, margin_change_gbp_per_month,
                              None, why)

    def monthly(stayed: int, n: int) -> float:
        return 1.0 - (stayed / n) ** (1.0 / window_months)

    dh = monthly(eff.stayed_treated, eff.treated) - monthly(eff.stayed_held_out, eff.held_out)
    unknown = "" if None not in (customer_benefit_gbp_per_year, margin_change_gbp_per_month) else (
        "the holdout measures staying only; the customer's benefit and our margin change are not "
        "estimated from it")
    return ActionEstimate(action, customer_benefit_gbp_per_year, margin_change_gbp_per_month, dh,
                          unknown)


def in_contact_holdout(account_id: str, share: float, salt: str) -> bool:
    """The company's own coin: is this account kept out of a contact programme?

    One draw per account, held for the whole run, as a real holdout group is. A hash and not a
    random stream, so the coin consumes none of the world's draws and an account's arm does not
    depend on the order accounts are met. `salt` names the run, so seeds hold out different
    accounts.
    """
    if not 0.0 <= share <= 1.0:
        raise ValueError(f"a holdout share is a fraction of accounts, got {share}")
    digest = hashlib.sha256(f"{salt}|{account_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2 ** 64 < share


def holdout_observations(svt_decisions, window_months: int, observed_until: str) -> list[dict]:
    """A run's default-tariff decisions as rows for `hazard_estimate_from_holdout`.

    Pass the door the same `window_months`: an account ``stayed`` if no departure is dated within
    that many months of its FIRST assigned segment. The arm is held per account, so its later
    segments are one draw, not fresh ones. An account whose window ends after `observed_until`
    (ISO date) is dropped, since the company cannot yet see whether it stayed. Grading the first
    segment alone gave each account its own window (a median 43 days on the published run) and
    understated the hazard about eightfold at 12 months (research §6.2).
    """
    if window_months < 1:
        raise ValueError(f"a holdout window must be at least one month, got {window_months}")
    until = date.fromisoformat(observed_until)
    starts, arms, lost = {}, {}, {}
    for r in sorted(svt_decisions, key=lambda r: r["event_date"]):
        if r.get("contact_arm") is None:
            continue
        cid = r["customer_id"]
        if cid not in starts:
            starts[cid], arms[cid] = date.fromisoformat(r["event_date"]), r["contact_arm"]
        if r["event_type"] == "churned":
            lost.setdefault(cid, date.fromisoformat(r["event_date"]))
    rows = []
    for cid, t0 in starts.items():
        months = t0.year * 12 + t0.month - 1 + window_months
        y, m = divmod(months, 12)
        end = date(y, m + 1, min(t0.day, monthrange(y, m + 1)[1]))
        if end > until:
            continue
        rows.append({"arm": arms[cid], "stayed": not (cid in lost and lost[cid] < end)})
    return rows


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


def decide(state: AccountState, horizon_months: int,
           policy: "DecisionPolicy | None" = None) -> Decision:
    """The per-customer rule. ``policy`` is the run's; only its retention-rise switch is read."""
    forced = _debt_constraint(state, horizon_months)
    if forced is not None:
        return forced
    scored, unscored = _scored(state, horizon_months)
    responses = {r.action: r for r in state.share_responses}
    priced = []
    for est, _ in scored:
        if est.action in responses:
            price, why = price_share(state, est, responses[est.action], horizon_months)
            if price is None:
                unscored += ((est.action, f"share: {why}"),)
            else:
                priced.append((est, price))
    if (policy is not None and policy.next_best_action_shares_by_retention_rise
            and state.renewal is not None):
        for est, v in scored:
            if v >= 0.0 or est.customer_benefit_gbp_per_year < 0.0 or est.action is Action.DEBT_SUPPORT:
                continue
            rise, why = price_retention_rise(state, est, state.renewal, horizon_months)
            if rise is None:
                unscored += ((est.action, f"retention rise: {why}"),)
            else:
                priced.append((est, rise))
    if priced:
        unpriced = [(e, v) for e, v in scored if e.action not in responses]
        return _decide_with_shares(state, unpriced, priced, unscored, horizon_months)
    fair = [(e, v) for e, v in scored if e.customer_benefit_gbp_per_year >= 0.0 and v >= 0.0]
    if not fair:
        why = ("no scored action leaves both the customer and us no worse off" if scored
               else "no action could be scored")
        return Decision(state.account_id, Action.NOTHING, 0.0, 0.0, why, unscored)
    est, v = max(fair, key=lambda ev: (joint_value(ev[1], ev[0].customer_benefit_gbp_per_year,
                                                   horizon_months), ev[1]))
    if joint_value(v, est.customer_benefit_gbp_per_year, horizon_months) <= 0.0:
        return Decision(state.account_id, Action.NOTHING, 0.0, 0.0,
                        "no action that leaves both sides no worse off creates any value", unscored)
    return Decision(state.account_id, est.action, v, est.customer_benefit_gbp_per_year,
                    "largest joint value among actions that leave both sides no worse off", unscored)


def _decide_with_shares(state, unpriced, priced, unscored, horizon_months) -> Decision:
    """C34's candidates plus priced ones, ranked on one key: expected joint value.

    An unpriced action is taken for certain, as C34 assumes, so its expected joint value is its
    joint value.
    """
    cands = [(joint_value(v, e.customer_benefit_gbp_per_year, horizon_months), v,
              e.customer_benefit_gbp_per_year, e.action, None)
             for e, v in unpriced if e.customer_benefit_gbp_per_year >= 0.0 and v >= 0.0]
    cands += [(p.expected_joint_value_gbp, p.expected_value_change_gbp,
               p.expected_customer_benefit_gbp * 12.0 / horizon_months, e.action, p)
              if isinstance(p, SharePrice) else
              (p.expected_joint_value_gbp, p.value_change_gbp,
               p.customer_benefit_kept_gbp * 12.0 / horizon_months, e.action, p)
              for e, p in priced]
    joint, v, cb, action, price = max(cands, key=lambda c: (c[0], c[1]))
    if joint <= 0.0:
        return Decision(state.account_id, Action.NOTHING, 0.0, 0.0,
                        "no action that leaves both sides no worse off creates any value", unscored)
    if isinstance(price, RetentionRise):
        why = (f"largest expected joint value, offered with a {price.rise_gbp_per_month:.2f} GBP/month "
               f"rise on the renewal fix (headroom {price.headroom_gbp_per_month:.2f} GBP/month)")
    elif price:
        why = (f"largest expected joint value, offered at a {price.share:.0%} share of the household's "
               f"benefit (fee {price.fee_gbp:.2f} GBP, take-up {price.take_up:.0%})")
    else:
        why = "largest joint value among actions that leave both sides no worse off"
    return Decision(state.account_id, action, v, cb, why, unscored, price)


def flat_action(book: Sequence[AccountState], horizon_months: int) -> Action:
    """The one action with the best mean estimated JOINT value across the book, or nothing.

    An account with no scored estimate for an action counts as zero for it: the flat rule would
    still send it, and with no estimate the company cannot claim it does anything.

    The same two floors as the per-customer rule, on the book's means: an action whose mean
    forward-value change or mean customer benefit is negative is not a candidate.
    """
    ours: dict[Action, float] = {}
    theirs: dict[Action, float] = {}
    for state in book:
        for est, v in _scored(state, horizon_months)[0]:
            ours[est.action] = ours.get(est.action, 0.0) + v
            theirs[est.action] = theirs.get(est.action, 0.0) + est.customer_benefit_gbp_per_year
    totals = {a: joint_value(ours[a], theirs[a], horizon_months)
              for a in ours if ours[a] >= 0.0 and theirs[a] >= 0.0}
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
    an account's truth did nothing. Scored as JOINT value FORGONE (the negative of the true joint
    change, C7's own key) so the paired comparison reads as B11's does: negative favours
    per-customer. The customer's side is also reported on its own.
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
            loss.append(-joint_value(value_change(state, t, horizon_months),
                                     t.customer_benefit_gbp_per_year, horizon_months) if t else 0.0)
            cb.append(t.customer_benefit_gbp_per_year if t else 0.0)
    n = len(book)
    return Grade(
        flat,
        _paired("joint value forgone against the true counterfactual, GBP", pc_loss, fl_loss),
        sum(pc_cb) / n if n else float("nan"),
        sum(fl_cb) / n if n else float("nan"),
        chosen,
    )
