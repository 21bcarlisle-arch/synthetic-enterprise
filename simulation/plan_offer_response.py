"""How a household answers a payment-arrangement offer (atom EP4) -- the world side.

The company makes the offer on its SLC 27.8 step (`company/billing/collections_journey.py`). Whether
the household agrees, what it can afford, and whether it then pays each instalment are the
household's, so they are decided here and only the OBSERVABLE answer crosses
`company/interfaces/sim_interface.py`: accepted or not, the agreed instalment, and each instalment
paid or missed once its date has passed.

A HOUSEHOLD ANSWERS THE OFFER IT IS SENT, NOT THE SUPPLIER WHO SENDS IT. Knowledge first:
`docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md`, section "The world's
answer to an offer" (2026-10-12). The household is told one of three shapes, and the shape and its
own finances are all it answers to:

  * a REPAYMENT PLAN (the SLC 27.8 offer the live company makes). With no amount named, the
    household names one: the arrears spread over the weeks a GB credit arrangement took to recover
    them (Ofgem social-obligations data annexes, 46-96 weeks). A supplier-named amount above that
    is less affordable to it, and the household agrees anyway as often (the PFRC/StepChange 16%
    who agreed a plan they felt unaffordable) -- but breaks it more often, in proportion to the
    payment (HAMP: a one percent payment change moves default about one percent).
  * a LOWER MONTHLY PAYMENT for a period. A token cut changes nothing (MMI: a cut of 0.14pp of the
    balance on a 2.38% payment -- 5.9% of the payment -- had no detectable effect); a material cut
    lowers the household's failed collections by the cut times an elasticity (HAMP, about 1).
  * a PAUSE (breathing space). While paused the supplier presents nothing, which is the supplier's
    act, not the household's. When it ends a household still in difficulty (not LOW stress) fails
    its first collection with a share from the FCA's Covid deferral figures; one whose difficulty
    has passed resumes.

KEEP, BREAK AND CURE. An agreed plan is kept or broken as a whole. It breaks with the household's
break share (the analogue prior: 45-65% of plans end in breach) times the offer's affordability
ratio, in one of its first six instalments (the analogues put most of the hazard in the first 3-6
months), or at the first instalment after an income shock moves the household into HIGH stress
from a lower tier at agreement. A plan kept to its last instalment has cleared the debt: that is
a cure, and it is an OUTCOME of the break share, not a second number.

THE SHIPPED WORLD STILL ANSWERS None. Take-up, break and the effect sizes are unpublished for GB
energy, so each is a labelled toggle (`plan_*` in `docs/market_research/assumption_toggles.yaml`)
whose `default` is off. `BASIS` is the published basis -- every slot None with its reason -- until
a harness sets `BASIS = basis_at("low"|"high")`. Tests inject a basis to prove every branch.

THE PLAN IS HOW THE HOUSEHOLD REPAYS, SO THE WORLD REMEMBERS IT. An agreement is recorded on the
world's `HouseholdPlanBook` when the household says yes, and the world's other route for repaying
arrears -- a later lump settlement of an unpaid bill (`payment_behaviour_source.later_settlement_date`)
-- asks it first. The same book holds what the household's money looked like each month (its
stress tier, noted by the run as it bills), which is how an income shock reaches a plan.

NAMED SIMPLIFICATIONS:
  1. A plan is kept or broken as a whole: no isolated missed instalment in a kept plan, and a
     broken plan pays nothing more. Real households miss and recover; the company's own default
     rule (`payment_plan._DEFAULT_THRESHOLD`) sees a broken plan the same way either way.
  2. A broken plan does not hand the debt back to the lump route: a settlement withdrawn by a plan
     stays withdrawn. Understates what a household that breaks a plan later pays.
  3. The instalment crosses as paid or missed with no amount; the world does not end the plan
     itself, and only the supplier's plan book knows to stop reading instalments.
  4. Take-up does not vary with the household's means or the offer's shape: nothing published
     splits it, and the analogue (16% agreeing plans they felt unaffordable) says an unaffordable
     offer is still agreed. Means act on keeping, where the evidence puts them.
  5. The household's pay-or-heat state (`self_rationing.py`) is not read: it is not wired into
     the run, so no household carries it. A self-rationing household keeps paying by definition,
     so its plans would be kept; the error runs toward too few kept plans among the squeezed.
"""
from __future__ import annotations

import bisect
import datetime as dt
from dataclasses import dataclass, replace
from typing import Optional

from simulation.rng_substream import substream

STREAM_NAMESPACE = "EP4_plan_offer_response"

_RESEARCH = "docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md"

#: The offer shapes a household can be sent.
REPAYMENT_PLAN = "repayment_plan"
LOWER_PAYMENT = "lower_payment"
PAUSE = "pause"
OFFER_KINDS = (REPAYMENT_PLAN, LOWER_PAYMENT, PAUSE)

#: MMI (Dobbie & Song): a minimum-payment cut of 0.14pp of the balance against a 2.38% payment had
#: no detectable effect on completion. A cut smaller than this share of the payment is a token one.
TOKEN_CUT_SHARE = 0.14 / 2.38

#: The analogues put most of the break hazard in the first 3-6 months of a plan (IVA terminations
#: front-loaded; Victorian programmes under a year). A break falls uniformly in the first six
#: instalments: the upper end of that reading, a design choice from it and not a measured shape.
BREAK_WINDOW_INSTALMENTS = 6

#: The five toggles a switched-on world reads, in `assumption_toggles.yaml`.
TOGGLE_TAKE_UP = "plan_take_up_share"
TOGGLE_BREAK = "plan_break_share"
TOGGLE_WEEKS = "plan_weeks_to_recover"
TOGGLE_LOWER_ELASTICITY = "plan_lower_payment_failure_elasticity"
TOGGLE_PAUSE_RESUME = "plan_pause_resume_failure_share"


@dataclass(frozen=True)
class PlanResponseBasis:
    """The world facts an answer needs. Each None carries why, in the matching `*_gap`.

    Two ways to keep an agreed plan are supported: the original per-instalment keep rate
    (`instalment_keep_rate`, independent draws -- what an injected test basis uses), or the
    household-state model (`plan_break_share`, a plan kept or broken as a whole). The instalment is
    either a fixed sum (`monthly_instalment_gbp`) or the household's own, from
    `weeks_to_recover`."""

    take_up_rate: Optional[float]
    take_up_gap: Optional[str]
    instalment_keep_rate: Optional[float]
    instalment_keep_gap: Optional[str]
    monthly_instalment_gbp: Optional[float]
    monthly_instalment_gap: Optional[str]
    plan_break_share: Optional[float] = None
    weeks_to_recover: Optional[float] = None
    lower_payment_elasticity: float = 0.0
    pause_resume_failure_share: float = 0.0

    def first_gap(self) -> Optional[str]:
        if self.take_up_rate is None:
            return self.take_up_gap or "unnamed gap"
        if self.instalment_keep_rate is None and self.plan_break_share is None:
            return self.instalment_keep_gap or "unnamed gap"
        if self.monthly_instalment_gbp is None and self.weeks_to_recover is None:
            return self.monthly_instalment_gap or "unnamed gap"
        return None


PUBLISHED_BASIS = PlanResponseBasis(
    take_up_rate=None,
    take_up_gap=(
        "no published rate of plan take-up among domestic debtors offered one: no published source "
        "counts offers, and Ofgem's quarter-end stocks of accounts in arrears and in debt do not "
        f"bound it ({_RESEARCH})"),
    instalment_keep_rate=None,
    instalment_keep_gap=(
        "no published per-instalment keep rate: Ofgem's last published break figure (2015 social "
        "obligations report, Fig. 13: about 40% of large-supplier credit plans had at least one "
        "failed repayment in the year) counts customer-years, and the payments each was exposed to "
        f"are unpublished; the quarterly failure counts since 2019 are not published ({_RESEARCH})"),
    monthly_instalment_gbp=None,
    monthly_instalment_gap=(
        "the published average weekly repayment is over prepayment meters installed for debt, not "
        "over credit-account plans, and is not wired while take-up is unknown "
        f"({_RESEARCH})"),
)


def basis_at(setting: str = "default") -> PlanResponseBasis:
    """The register's `default`, `low` or `high` row for every plan toggle. A take-up of 0 -- the
    shipped `default` -- is the published basis itself: the world answers None and names why."""
    from simulation.meter_reads import assumption_toggle
    take_up = assumption_toggle(TOGGLE_TAKE_UP, setting)
    if not take_up:
        return PUBLISHED_BASIS
    return replace(
        PUBLISHED_BASIS,
        take_up_rate=take_up,
        plan_break_share=assumption_toggle(TOGGLE_BREAK, setting),
        weeks_to_recover=assumption_toggle(TOGGLE_WEEKS, setting),
        lower_payment_elasticity=assumption_toggle(TOGGLE_LOWER_ELASTICITY, setting),
        pause_resume_failure_share=assumption_toggle(TOGGLE_PAUSE_RESUME, setting),
    )


#: What the run and the seam use. A harness that measures a setting replaces this attribute.
BASIS = PUBLISHED_BASIS


def _months_to_recover(weeks: float) -> float:
    return weeks * 12.0 / 52.0


def _norm_stress(stress: Optional[str]) -> str:
    return (stress or "LOW").upper()


@dataclass(frozen=True)
class OfferTerms:
    """What the household agreed, as the world remembers it."""

    kind: str
    agreed_on: dt.date
    instalment: Optional[float] = None
    debt: Optional[float] = None
    affordability_ratio: float = 1.0
    stress_at_agreement: str = "LOW"
    months: int = 0
    cut_share: float = 0.0


class HouseholdPlanBook:
    """The arrangements this world's households have agreed, and each household's money month by
    month, as the world knows them. One per run, shared by every seam that answers offers for it.
    Ground truth: the company never reads it."""

    def __init__(self) -> None:
        self._agreed: dict[str, list[dt.date]] = {}
        self._terms: dict[tuple[str, dt.date], OfferTerms] = {}
        self._stress_dates: dict[str, list[dt.date]] = {}
        self._stress_values: dict[str, list[str]] = {}
        self.answers: list[dict] = []
        #: account -> (date the meter was changed for debt, debt carried onto it). First move only.
        self._meters: dict[str, tuple[dt.date, float]] = {}
        self._fuel: dict[str, str] = {}

    def record_meter(self, account_id: str, moved_on: dt.date, debt_gbp: float) -> None:
        """The household's meter was changed to prepayment for debt (payment_method_dynamics)."""
        self._meters.setdefault(account_id, (moved_on, debt_gbp))

    def meter_of(self, account_id: str) -> Optional[tuple[dt.date, float]]:
        return self._meters.get(account_id)

    def on_meter(self, account_id: str, on: dt.date) -> bool:
        m = self._meters.get(account_id)
        return m is not None and m[0] <= on

    def note_fuel(self, account_id: str, fuel: str) -> None:
        # A dual-fuel account notes both legs; its debt meter recovers at the electricity rate.
        if self._fuel.get(account_id) != "electricity":
            self._fuel[account_id] = fuel

    def fuel_of(self, account_id: str) -> str:
        return self._fuel.get(account_id, "electricity")

    def record(self, account_id: str, agreed_on: dt.date,
               terms: Optional[OfferTerms] = None) -> None:
        self._agreed.setdefault(account_id, []).append(agreed_on)
        if terms is not None:
            self._terms[(account_id, agreed_on)] = terms

    def terms(self, account_id: str, agreed_on: dt.date) -> Optional[OfferTerms]:
        return self._terms.get((account_id, agreed_on))

    def note_stress(self, account_id: str, on: dt.date, stress: Optional[str]) -> None:
        """The household's stress tier for the month billed on `on` (the run calls this as it
        bills, in date order per account)."""
        dates = self._stress_dates.setdefault(account_id, [])
        values = self._stress_values.setdefault(account_id, [])
        i = bisect.bisect_right(dates, on)
        dates.insert(i, on)
        values.insert(i, _norm_stress(stress))

    def stress_on(self, account_id: str, on: dt.date) -> Optional[str]:
        """The latest tier noted on or before `on`, or None if none was."""
        dates = self._stress_dates.get(account_id)
        if not dates:
            return None
        i = bisect.bisect_right(dates, on)
        return self._stress_values[account_id][i - 1] if i else None

    def repays_through_plan(self, account_id: str, bill_due: dt.date, paid_on: dt.date) -> bool:
        """Whether a bill due on `bill_due`, unpaid until `paid_on`, is repaid through a plan rather
        than as a lump that day: a repayment plan was agreed after the bill fell due and before the
        day. A lower-payment or pause agreement repays nothing, so it withdraws no lump."""
        meter = self._meters.get(account_id)
        if meter is not None and bill_due < meter[0] < paid_on:
            return True  # the meter recovers it from top-ups instead
        for agreed in self._agreed.get(account_id, ()):
            terms = self._terms.get((account_id, agreed))
            if terms is not None and terms.kind != REPAYMENT_PLAN:
                continue
            if bill_due < agreed < paid_on:
                return True
        return False

    def collection_effect(self, account_id: str, due: dt.date,
                          basis: Optional[PlanResponseBasis] = None) -> tuple[float, bool]:
        """(failure multiplier, forced failure) for the household's ordinary collection due on
        `due`, from any lower-payment or pause agreement in force. (1.0, False) when none is."""
        basis = BASIS if basis is None else basis
        mult, force = 1.0, False
        for agreed in self._agreed.get(account_id, ()):
            terms = self._terms.get((account_id, agreed))
            if terms is None or terms.kind == REPAYMENT_PLAN:
                continue
            end = _add_months(agreed, terms.months)
            if terms.kind == LOWER_PAYMENT and agreed < due <= end:
                mult *= lower_payment_failure_multiplier(terms.cut_share, basis)
            elif terms.kind == PAUSE and end < due <= _add_months(end, 1):
                force = force or pause_resume_fails(
                    account_id, agreed, self.stress_on(account_id, end), basis)
        return mult, force

    def summary(self) -> dict:
        kinds: dict[str, int] = {}
        for t in self._terms.values():
            kinds[t.kind] = kinds.get(t.kind, 0) + 1
        return {"offers_answered": len(self.answers),
                "accepted": sum(1 for a in self.answers if a["accepted"]),
                "declined": sum(1 for a in self.answers if a["accepted"] is False),
                "unanswered": sum(1 for a in self.answers if a["accepted"] is None),
                "agreed_by_kind": kinds}


@dataclass(frozen=True)
class PlanOfferAnswer:
    """What the supplier learns from the conversation an offer opens: nothing more."""

    accepted: Optional[bool]
    #: Monthly, in GBP.
    instalment: Optional[float]
    reason: str


def lower_payment_failure_multiplier(cut_share: float, basis: Optional[PlanResponseBasis] = None
                                     ) -> float:
    """The multiplier on a household's failure probability while a lower payment is in force: 1
    for a token cut (below `TOKEN_CUT_SHARE`), else 1 - elasticity x cut, floored at 0."""
    basis = BASIS if basis is None else basis
    if cut_share < TOKEN_CUT_SHARE:
        return 1.0
    return max(0.0, 1.0 - basis.lower_payment_elasticity * cut_share)


def pause_resume_fails(account_id: str, agreed_on: dt.date, stress_at_end: Optional[str],
                       basis: Optional[PlanResponseBasis] = None) -> bool:
    """Whether a paused household fails its first collection when the pause ends: only one still
    in difficulty (not LOW stress) can, at the basis's share."""
    basis = BASIS if basis is None else basis
    if _norm_stress(stress_at_end) == "LOW":
        return False
    rng = substream(STREAM_NAMESPACE, f"resume::{account_id}::{agreed_on.isoformat()}", 0)
    return rng.random() < basis.pause_resume_failure_share


def _own_instalment(debt_gbp: float, basis: PlanResponseBasis) -> float:
    if basis.monthly_instalment_gbp is not None:
        return basis.monthly_instalment_gbp
    return debt_gbp / _months_to_recover(basis.weeks_to_recover)


def answer_plan_offer(account_id: str, offered_on: dt.date, debt_gbp: float, *,
                      offer: Optional[dict] = None,
                      base_seed: int = 0,
                      basis: Optional[PlanResponseBasis] = None,
                      agreements: Optional[HouseholdPlanBook] = None) -> PlanOfferAnswer:
    """The household's answer to one offer. Deterministic in (seed, account, offer date). A yes is
    recorded on `agreements`, the world's own book.

    `offer` is the shape the household is told: None (or kind `repayment_plan` with no amount) is
    the SLC 27.8 conversation, where the household names the instalment; `repayment_plan` with
    `monthly_gbp` is a supplier-named instalment; `lower_payment` carries `monthly_gbp`,
    `usual_monthly_gbp` and `months`; `pause` carries `months`."""
    basis = BASIS if basis is None else basis
    offer = dict(offer or {})
    kind = offer.get("kind", REPAYMENT_PLAN)
    if kind not in OFFER_KINDS:
        raise ValueError(f"unknown offer kind {kind!r}: one of {OFFER_KINDS}")
    gap = basis.first_gap()
    if gap is not None:
        answer = PlanOfferAnswer(None, None, gap)
        if agreements is not None:
            agreements.answers.append({"kind": kind, "accepted": None})
        return answer
    rng = substream(STREAM_NAMESPACE, f"offer::{account_id}::{offered_on.isoformat()}", base_seed)
    accepted = rng.random() < basis.take_up_rate
    if agreements is not None:
        agreements.answers.append({"kind": kind, "accepted": accepted})
    if not accepted:
        return PlanOfferAnswer(False, None, "household declined the arrangement offered")
    stress = _norm_stress(agreements.stress_on(account_id, offered_on) if agreements else None)
    if kind == REPAYMENT_PLAN:
        own = _own_instalment(debt_gbp, basis)
        named = offer.get("monthly_gbp")
        instalment = round(min(named if named is not None else own, debt_gbp), 2)
        ratio = (instalment / own) if (named is not None and own > 0) else 1.0
        months = int(-(-debt_gbp // instalment)) if instalment > 0 else 0
        terms = OfferTerms(REPAYMENT_PLAN, offered_on, instalment, debt_gbp, ratio, stress, months)
    elif kind == LOWER_PAYMENT:
        usual = float(offer["usual_monthly_gbp"])
        instalment = round(float(offer["monthly_gbp"]), 2)
        cut = max(0.0, 1.0 - instalment / usual) if usual > 0 else 0.0
        terms = OfferTerms(LOWER_PAYMENT, offered_on, instalment, None, 1.0, stress,
                           int(offer["months"]), cut)
    else:
        instalment = None
        terms = OfferTerms(PAUSE, offered_on, None, None, 1.0, stress, int(offer["months"]))
    if agreements is not None:
        agreements.record(account_id, offered_on, terms)
    return PlanOfferAnswer(True, instalment, "household agreed the arrangement offered")


def _add_months(day: dt.date, months: int) -> dt.date:
    month0 = day.month - 1 + months
    year, month = day.year + month0 // 12, month0 % 12 + 1
    # Clamp to the month's last day: a plan agreed on the 31st falls due on the 30th in April.
    for d in (day.day, 30, 29, 28):
        try:
            return dt.date(year, month, d)
        except ValueError:
            continue
    raise AssertionError("unreachable")


def plan_fate(account_id: str, agreed_on: dt.date, terms: Optional[OfferTerms], *,
              base_seed: int = 0, basis: Optional[PlanResponseBasis] = None) -> Optional[int]:
    """The instalment number (1-based) at which a plan breaks for the household's own reasons, or
    None if it would be kept. Income shocks are separate (`plan_instalments`)."""
    basis = BASIS if basis is None else basis
    ratio = terms.affordability_ratio if terms is not None else 1.0
    rng = substream(STREAM_NAMESPACE, f"fate::{account_id}::{agreed_on.isoformat()}", base_seed)
    u_break, u_when = rng.random(), rng.random()
    if u_break >= min(1.0, basis.plan_break_share * ratio):
        return None
    return 1 + int(u_when * BREAK_WINDOW_INSTALMENTS)


def plan_instalments(account_id: str, agreed_on: dt.date, through: dt.date, *,
                     base_seed: int = 0,
                     basis: Optional[PlanResponseBasis] = None,
                     agreements: Optional[HouseholdPlanBook] = None) -> list[dict]:
    """Each monthly instalment falling due after `agreed_on` and no later than `through`, paid or
    missed. Nothing dated after `through` is returned, so asking cannot see the future. Empty when
    the basis has a gap: a plan the world cannot answer was never agreed."""
    basis = BASIS if basis is None else basis
    if basis.first_gap() is not None:
        return []
    terms = agreements.terms(account_id, agreed_on) if agreements is not None else None
    whole_plan = basis.instalment_keep_rate is None
    breaks_at = (plan_fate(account_id, agreed_on, terms, base_seed=base_seed, basis=basis)
                 if whole_plan else None)
    start_stress = terms.stress_at_agreement if terms is not None else None
    broken = False
    out = []
    n = 1
    while (due := _add_months(agreed_on, n)) <= through:
        if whole_plan:
            shocked = (agreements is not None and start_stress not in (None, "HIGH")
                       and agreements.stress_on(account_id, due) == "HIGH")
            broken = broken or shocked or (breaks_at is not None and n >= breaks_at)
            paid = not broken
        else:
            rng = substream(STREAM_NAMESPACE,
                            f"instalment::{account_id}::{agreed_on.isoformat()}::{n}", base_seed)
            paid = rng.random() < basis.instalment_keep_rate
        out.append({"due": due.isoformat(), "paid": paid})
        n += 1
    return out


def plan_outcomes(book: HouseholdPlanBook, through: dt.date, *,
                  basis: Optional[PlanResponseBasis] = None) -> dict:
    """The world's own count of what its agreed repayment plans did by `through`: completed (every
    instalment to the last paid -- the cure), broken (with the cause), or still running. Ground
    truth for the freeze record; never crosses."""
    basis = BASIS if basis is None else basis
    out = {"agreed": 0, "completed": 0, "broken_own": 0, "broken_income_shock": 0, "running": 0}
    for (account, agreed), terms in book._terms.items():
        if terms.kind != REPAYMENT_PLAN:
            continue
        out["agreed"] += 1
        rows = plan_instalments(account, agreed, through, basis=basis, agreements=book)
        rows = rows[:terms.months] if terms.months else rows
        missed = next((i for i, r in enumerate(rows, 1) if not r["paid"]), None)
        if missed is None:
            out["completed" if terms.months and len(rows) >= terms.months else "running"] += 1
        elif plan_fate(account, agreed, terms, basis=basis) == missed:
            out["broken_own"] += 1
        else:
            out["broken_income_shock"] += 1
    return out
