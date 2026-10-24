"""How a household changes the way it pays, as its own act -- the world side (2026-10-12).

Knowledge first: `docs/market_research/gb_payment_method_migration_rates.md`, section "The household's
own payment-method acts: what the world does" (2026-10-12). The supplier-authored routes (stopping a
DD that keeps failing, fitting a prepayment meter for debt, moving a meter back on the SLC 28.1A
reassessment) are company decisions and are not here. What is here is what a HOUSEHOLD does:

  * IT CANCELS ITS MANDATE AT ITS BANK, for its own reasons -- distrust, wanting control of when
    money leaves, closing or switching the account -- with no shock behind it (the shock-driven
    cancellation is DD4b, `dd_shock_response.py`). No source publishes a household-initiated
    cancellation rate ("the one nothing publishes", PB8 addendum 2026-10-03), so the share per
    DD household-year is a labelled range (`method_own_reasons_cancel_share`), shipped at 0. A
    stretched household cancels more readily (budgeting, control), by the world's own stress
    relativity, capped at 1 -- the same scaling DD4b uses, so one relativity serves both.
  * IT THEN PAYS BY HAND. A cancelled mandate is recorded on the run's one mandate-cancellation book
    (`DDShockResponseBook`), so the month it cancels its collection comes back "instruction
    cancelled" and every later bill is paid on receipt -- in the triad, the rails and the arrears
    engine alike, exactly as after a shock. "Stopping paying" is not a separate act: a household
    paying on receipt fails at its own tier's rate, which is where its money already shows.
  * ITS ANSWER TO THE PREPAYMENT ROUTE. When a supplier offers a prepayment meter to recover a debt
    the household agrees or not (`answer_prepayment_offer`; a labelled range, shipped at 0). When
    the meter is changed -- by agreement or under warrant, which is the supplier's act and the
    household's only response to it is to live with it -- the debt is recovered from its top-ups at
    the published mean weekly rate for new PPM-for-debt installs (GBP 6.01 electricity, GBP 4.40
    gas, Ofgem 2025; `company_debt_management.md` s.2): `meter_recoveries`, built 2026-10-24 now
    that the Consent route can change a meter (once take-up is switched on).
  * THE ROUTE ITSELF (W2_42, 2026-10-16). Deciding to ask for the meter change stays the supplier's
    act, but whether the meter actually changes is the world's: `move_to_prepayment_for_debt` moves
    it only by recorded Consent or through the SLC 28.7 involuntary gate, and refuses anything else
    with its reason. Nothing in the run calls it yet (`company_debt_management.md`, "The world's side
    of the route from debt to prepayment").

NAMED SIMPLIFICATIONS:
  1. One draw per household per billed month, the annual share taken as a monthly hazard, keyed
     on (household, month), before that month's collection: a dual-fuel household cancels both
     legs' mandate together.
  2. A household that cancelled never sets a new mandate up. Re-mandating is real (and DESNZ's DD
     share has risen), but no flow is published either way; the error overstates manual payers.
  3. Payment channel is still drawn once and uncoupled from income or tenure: the crosstab that
     would couple it is not reachable (the gap in the research section), so no coupling is built.
  4. Self-disconnection on a debt PPM is not drawn: the published counts are a stock over all smart
     PPM customers per quarter, not a per-household rate for one fitted for debt.
  5. Recovery is the published MEAN weekly sum for every household: not scaled to the debt or the
     means (SLC 27.8 sets a per-household figure; the 2025 range ran GBP 2.69-17.17 a week), and a
     household that has not topped up that week still pays it. Understates how slowly a stretched
     household repays and how often it goes off supply instead (simplification 4).
  6. Bills after the move are paid before use (the meter's own method) for the rest of the run; a
     meter is never moved back (SLC 28.1A reassessment is not built).

Pure world code: never imports `company.*` or `saas.*`. Each draw has its own named substream.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import asdict, dataclass
from typing import Optional

from simulation.dd_shock_response import stress_relativity
from simulation.meter_reads import assumption_toggle
from simulation.rng_substream import substream

STREAM_NAMESPACE = "PB8_household_method_acts"

TOGGLE_OWN_CANCEL = "method_own_reasons_cancel_share"
TOGGLE_PPM_TAKE_UP = "method_prepayment_offer_take_up_share"

#: Why a cancellation happened, on the book's record. A shock-driven row carries no cause.
CAUSE_OWN_REASONS = "own_reasons"

#: Mean weekly repayment for prepayment meters installed for debt, calendar 2025 (Ofgem, Debt and
#: arrears indicators; `company_debt_management.md` s.2, `debt_realism_three_world_fidelity_gaps.md`
#: s.2). A published mean, not a per-household figure (simplification 5).
PPM_DEBT_WEEKLY_GBP = {"electricity": 6.01, "gas": 4.40}


def meter_recoveries(debt_gbp: float, moved_on: "dt.date", through: "dt.date",
                     fuel: str = "electricity") -> list[dict]:
    """Each weekly deduction at top-up falling after the meter was changed and no later than
    `through`, as `{"due": iso, "amount_gbp": x}`. The sum never exceeds the debt carried onto the
    meter, so the last is the remainder. Asking cannot see the future."""
    weekly = PPM_DEBT_WEEKLY_GBP.get(fuel, PPM_DEBT_WEEKLY_GBP["electricity"])
    out, remaining, n = [], round(debt_gbp, 2), 1
    while remaining > 0 and (due := moved_on + dt.timedelta(days=7 * n)) <= through:
        paid = round(min(weekly, remaining), 2)
        out.append({"due": due.isoformat(), "amount_gbp": paid})
        remaining = round(remaining - paid, 2)
        n += 1
    return out


@dataclass(frozen=True)
class MethodStrengths:
    """The two shares. `off` -- both zero -- is the shipped world."""
    own_cancel_share: float = 0.0
    prepayment_take_up_share: float = 0.0

    @property
    def off(self) -> bool:
        return not (self.own_cancel_share or self.prepayment_take_up_share)

    @classmethod
    def at(cls, setting: str = "default") -> "MethodStrengths":
        return cls(assumption_toggle(TOGGLE_OWN_CANCEL, setting),
                   assumption_toggle(TOGGLE_PPM_TAKE_UP, setting))


#: What the run uses. A harness that measures a setting replaces this module attribute.
STRENGTHS = MethodStrengths.at("default")

#: The last run's counts, for a harness to read after it (world truth; never crosses).
LAST_SUMMARY: dict = {}


def pays_by_direct_debit(customer_id: str, fuel: str) -> bool:
    """Whether the supply point pays by DD, from the same channel draw the run's payment triad
    collects by (`payment_behaviour_source.generate_payment_method`), so a cancellation drawn here
    always lands on a mandate the triad presents."""
    from simulation.payment_behaviour_source import DIRECT_DEBIT, generate_payment_method
    return generate_payment_method(customer_id, fuel=fuel) == DIRECT_DEBIT


def monthly_hazard(annual: float) -> float:
    """The monthly probability that compounds to `annual` over twelve months."""
    return 1.0 - (1.0 - min(1.0, annual)) ** (1.0 / 12.0)


def own_reasons_cancellation(*, household: str, month: str, stress: Optional[str],
                             pays_by_direct_debit: bool, already_cancelled: bool,
                             strengths: Optional[MethodStrengths] = None) -> Optional[dict]:
    """A cancellation record for the run's mandate book, or None, for one billed month ("YYYY-MM").
    The annual share (scaled by stress, capped at 1) is taken as a monthly hazard. Only a household
    paying by DD and not already off it can cancel."""
    strengths = STRENGTHS if strengths is None else strengths
    if not strengths.own_cancel_share or not pays_by_direct_debit or already_cancelled:
        return None
    u = substream(STREAM_NAMESPACE, f"cancel::{household}::{month}", 0).random()
    if u >= monthly_hazard(strengths.own_cancel_share * stress_relativity(stress)):
        return None
    return {
        "household": household,
        "review_month": month,
        "rise_fraction": None,
        "stress": (stress or "LOW").upper(),
        "cancelled_month": month,
        "failure_multiplier": 1.0,
        "complained": False,
        "cause": CAUSE_OWN_REASONS,
    }


def answer_prepayment_offer(account_id: str, offered_on: str,
                            strengths: Optional[MethodStrengths] = None) -> Optional[bool]:
    """Whether a household offered a prepayment meter to recover its debt agrees. None while the
    share is off: the world cannot answer, as for an arrangement offer."""
    strengths = STRENGTHS if strengths is None else strengths
    if not strengths.prepayment_take_up_share:
        return None
    u = substream(STREAM_NAMESPACE, f"ppm_offer::{account_id}::{offered_on}", 0).random()
    return u < strengths.prepayment_take_up_share


#: The two routes to a prepayment meter for debt (SLC 28.21-28.22): the household's recorded explicit
#: Consent, or an involuntary move by warrant or remote switch.
ROUTE_CONSENT = "consent"
INVOLUNTARY_ROUTES = ("warrant", "remote_switch")

#: Involuntary moves stopped industry-wide in Feb 2023; the 28.7 rules came into force 8 Nov 2023 and
#: the first restarts were Jan 2024 (`company_debt_management.md`, "Involuntary prepayment since 2023").
INVOLUNTARY_PAUSED_FROM = "2023-02-01"
INVOLUNTARY_RESTART = "2024-01-01"
#: SLC 28.7 Debt Trigger and guidance 5.6, cited in `debt_and_collections.md` s.3 (SLC 28B row).
DEBT_TRIGGER_GBP = 200.0
DEBT_TRIGGER_MONTHS = 3
MIN_ENGAGEMENT_ATTEMPTS = 10


@dataclass(frozen=True)
class PrepaymentForDebtRequest:
    """What the supplier did before asking for the meter to be changed, for one fuel."""
    account_id: str
    fuel: str
    requested_on: str
    route: str
    debt_gbp: float
    months_outstanding: int
    on_payment_plan: bool = False
    engagement_attempts: int = 0
    site_welfare_visit: bool = False
    explicit_consent_recorded: bool = False


@dataclass(frozen=True)
class PrepaymentMove:
    moved: bool
    route: str
    reason: str


def move_to_prepayment_for_debt(request: PrepaymentForDebtRequest, *, psr_type_vulnerable: bool,
                                strengths: Optional[MethodStrengths] = None) -> PrepaymentMove:
    """Whether the world changes this meter to prepayment for debt. Only a lawful route moves it;
    anything else is refused with the first unmet condition, in SLC 28.7's order.

    `psr_type_vulnerable` is the household's hidden V1 state (`vulnerability_state`), world truth.
    No needs code is drawn, so every V1 household is treated as do-not-install (guidance 3.7, the
    Precautionary Principle): the world cannot tell which V1 households the list names, and the
    error can only shrink the route. Choices and gaps: `company_debt_management.md`, "The world's
    side of the route from debt to prepayment"."""
    r = request
    if r.route == ROUTE_CONSENT:
        if not r.explicit_consent_recorded:
            return PrepaymentMove(False, r.route, "no explicit Consent recorded (SLC 28.22)")
        answer = answer_prepayment_offer(r.account_id, r.requested_on, strengths)
        if answer is None:
            return PrepaymentMove(False, r.route, "the household cannot answer: take-up share is off")
        return PrepaymentMove(answer, r.route, "household agreed" if answer else "household declined")
    if r.route not in INVOLUNTARY_ROUTES:
        raise ValueError(f"unknown route to prepayment: {r.route!r}")
    if r.requested_on < INVOLUNTARY_PAUSED_FROM:
        return PrepaymentMove(False, r.route, "the pre-2023 involuntary gate is not established (GAP)")
    if r.requested_on < INVOLUNTARY_RESTART:
        return PrepaymentMove(False, r.route, "involuntary moves paused industry-wide")
    if (r.debt_gbp < DEBT_TRIGGER_GBP or r.months_outstanding < DEBT_TRIGGER_MONTHS
            or r.on_payment_plan):
        return PrepaymentMove(False, r.route, "Debt Trigger not met (SLC 28.7)")
    if r.engagement_attempts < MIN_ENGAGEMENT_ATTEMPTS:
        return PrepaymentMove(False, r.route, "fewer than 10 engagement attempts")
    if not r.site_welfare_visit:
        return PrepaymentMove(False, r.route, "no Site Welfare Visit")
    if psr_type_vulnerable:
        return PrepaymentMove(False, r.route, "household is on the do-not-install list")
    return PrepaymentMove(True, r.route, "the 28.7 gate holds")


def summarise(book, strengths: Optional[MethodStrengths] = None) -> dict:
    """The world's count of own-reasons cancellations on the run's book, stored as LAST_SUMMARY."""
    strengths = STRENGTHS if strengths is None else strengths
    rows = [r for h in book._by_household for r in book.responses_of(h)
            if r.get("cause") == CAUSE_OWN_REASONS]
    by_stress: dict[str, int] = {}
    for r in rows:
        by_stress[r["stress"]] = by_stress.get(r["stress"], 0) + 1
    out = {"strengths": asdict(strengths), "own_reasons_cancellations": len(rows),
           "by_stress": by_stress}
    LAST_SUMMARY.clear()
    LAST_SUMMARY.update(out)
    return out
