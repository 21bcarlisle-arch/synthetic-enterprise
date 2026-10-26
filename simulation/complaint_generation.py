"""W2_37: complaints arise from the failures that cause them, and the silent unhappy are a population.

REUSE: simulation/complaint_generation.py
CLASS: CUSTOM
INDEX: searched "complaint generation", "complaint cause", "dissatisfied". The live complaint roll is
       `simulation/feedback_survey.dispatch_complaint_and_resolution`: one probability per renewal
       term, 3% + 35pp if the unit rate rose more than 20%. It keys every complaint to a price rise,
       the one cause that is a commercial choice, and its rates carry no source
       (`docs/market_research/communications_sentiment_and_nps.md` §6.1). Its RESOLUTION model is
       not replaced here; only where a complaint comes from is.

Two populations, kept apart on purpose (that page, §1 and §3.4):

* **A complaint is an act.** It is drawn per household per quarter, once for each trigger the
  household actually experienced. A household that met no trigger cannot complain, and a household
  that met only a billing failure can. The per-trigger probability is not published anywhere. It is
  derived, not picked: the published market rate times the cause's published share of complaints,
  divided by how often the world produced that trigger. So the world's complaint count and cause
  mix match the published record whatever the world's trigger rates are, and when the world
  produces a trigger too rarely to carry its share the derivation refuses and names the cause.
* **Dissatisfaction is a state.** Most dissatisfied households never complain. The silent unhappy
  are drawn only from households that met a trigger and did NOT complain, sized so that they plus
  the badly handled complainants make up the published dissatisfied share. So complaints are a
  floor on dissatisfaction by construction. If the world's badly handled complainants already
  exceed the published dissatisfied share, the derivation refuses rather than draw a negative
  population.

Nothing here moves a departure yet (L1). The two edges with opposite signs (§3.4: complainants
leave faster when handled badly; the dissatisfied switch LESS) are L2's, read from that page.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class ComplaintCause(str, Enum):
    CATCH_UP_BILL = "catch_up_bill"          # back-billing, a true-up after estimates (W2_36)
    DISPUTED_USAGE = "disputed_usage"
    DISPUTED_BALANCE = "disputed_balance"    # includes a DD review the household cannot explain
    OTHER_BILLING = "other_billing"
    PRICE_RISE = "price_rise"
    METER = "meter"
    TRANSFER = "transfer"
    CUSTOMER_SERVICE = "customer_service"
    DEBT_CONTACT = "debt_contact"


# Ofgem/GfK, *Complaints to energy companies* (2014), domestic complaint subjects, multi-coded (they
# sum to 118): billing 38, prices 27, meters 21, transfer 15, customer service 11, debt 6.
# communications_sentiment_and_nps.md §2.
_SUBJECT_SHARE_2014 = {
    "billing": 0.38, "prices": 0.27, "meters": 0.21, "transfer": 0.15,
    "customer_service": 0.11, "debt": 0.06,
}

# Within billing, the Energy Ombudsman's 2024 billing disputes (53,607): disputed usage 22%, disputed
# balances 8%, back-billing 3,218 cases. Same page, §2.
_BILLING_SUBSHARE_2024 = {
    "disputed_usage": 0.22,
    "disputed_balance": 0.08,
    "catch_up_bill": 3_218 / 53_607,
}

# SIMPLIFICATION, two of them, both named. (1) The multi-coding is collapsed to one cause per complaint
# by normalising the subject shares to sum to 1; this understates causes that co-occur (a catch-up
# bill that is also a price shock). Doing it properly needs the survey's co-coding table, which is
# not published. (2) The supplier-level billing share is split by the Ombudsman's billing sub-mix,
# which describes escalated disputes, not complaints; the direction of that error is unknown.
def _cause_shares() -> dict[ComplaintCause, float]:
    total = sum(_SUBJECT_SHARE_2014.values())
    billing = _SUBJECT_SHARE_2014["billing"] / total
    other_billing = 1.0 - sum(_BILLING_SUBSHARE_2024.values())
    return {
        ComplaintCause.CATCH_UP_BILL: billing * _BILLING_SUBSHARE_2024["catch_up_bill"],
        ComplaintCause.DISPUTED_USAGE: billing * _BILLING_SUBSHARE_2024["disputed_usage"],
        ComplaintCause.DISPUTED_BALANCE: billing * _BILLING_SUBSHARE_2024["disputed_balance"],
        ComplaintCause.OTHER_BILLING: billing * other_billing,
        ComplaintCause.PRICE_RISE: _SUBJECT_SHARE_2014["prices"] / total,
        ComplaintCause.METER: _SUBJECT_SHARE_2014["meters"] / total,
        ComplaintCause.TRANSFER: _SUBJECT_SHARE_2014["transfer"] / total,
        ComplaintCause.CUSTOMER_SERVICE: _SUBJECT_SHARE_2014["customer_service"] / total,
        ComplaintCause.DEBT_CONTACT: _SUBJECT_SHARE_2014["debt"] / total,
    }


CAUSE_SHARE = _cause_shares()

# Ofgem customer service data portal, supplier-recorded domestic complaints per 100,000 accounts per
# quarter, whole market: Q4 2025 1,011, Q1 2026 1,038 (same page, §3.3).
_PUBLISHED_COMPLAINTS_PER_100K_QUARTER = {"2025Q4": 1_011, "2026Q1": 1_038}

# Ofgem/CA Energy Consumer Satisfaction Survey, dissatisfied overall: 6% across the Jan 2025, Jul-Aug
# 2025 and Jan 2026 waves (same page, §3.1).
_PUBLISHED_DISSATISFIED_SHARE = {"2025Q1": 0.06, "2025Q3": 0.06, "2026Q1": 0.06}

NEAREST_ANCHOR_GAP = (
    "GAP (communications_sentiment_and_nps.md §7.4): the 2016-2025 quarterly series is on the Ofgem "
    "portal and not captured; the nearest published quarter stands in, so the crisis years carry "
    "no rise in complaints or dissatisfaction they really had (satisfaction fell 78% to 69%, §3.1)"
)


@dataclass(frozen=True)
class Anchor:
    value: float
    period: str          # the published quarter the value is from
    basis: str           # "published", or NEAREST_ANCHOR_GAP


def _quarter(period: str) -> str:
    """'2019-05-01' or '2019Q2' -> '2019Q2'."""
    if "Q" in period:
        return period
    year, month = int(period[:4]), int(period[5:7])
    return f"{year}Q{(month - 1) // 3 + 1}"


def _nearest(series: dict, period: str) -> Anchor:
    q = _quarter(period)
    if q in series:
        return Anchor(float(series[q]), q, "published")
    def index(k: str) -> int:
        return int(k[:4]) * 4 + int(k[5])
    nearest = min(series, key=lambda k: abs(index(k) - index(q)))
    return Anchor(float(series[nearest]), nearest, NEAREST_ANCHOR_GAP)


def complaints_per_account_quarter(period: str) -> Anchor:
    a = _nearest(_PUBLISHED_COMPLAINTS_PER_100K_QUARTER, period)
    return Anchor(a.value / 100_000, a.period, a.basis)


def dissatisfied_share(period: str) -> Anchor:
    return _nearest(_PUBLISHED_DISSATISFIED_SHARE, period)


class CalibrationRefused(ValueError):
    """The world cannot carry the published record at its own trigger rates; the reason says which part."""


def complaint_probability_given_trigger(
    period: str, trigger_prevalence: dict[ComplaintCause, float],
) -> dict[ComplaintCause, float]:
    """P(complaint about cause | the household met that trigger this quarter), per cause.

    `trigger_prevalence[cause]` is the share of accounts the WORLD put through that trigger in the
    quarter, measured by the caller. A cause the world never produces is refused, not zeroed: its
    published share of complaints would silently vanish (K2).
    """
    rate = complaints_per_account_quarter(period).value
    out = {}
    for cause, share in CAUSE_SHARE.items():
        prevalence = trigger_prevalence.get(cause, 0.0)
        need = rate * share
        if prevalence <= 0.0:
            raise CalibrationRefused(
                f"{cause.value}: the world produced no {cause.value} trigger in {period}, so its "
                f"{share:.1%} of complaints has nowhere to come from")
        p = need / prevalence
        if p > 1.0:
            raise CalibrationRefused(
                f"{cause.value}: {need:.4%} of accounts must complain about it in {period}, but the "
                f"world put only {prevalence:.4%} through it")
        out[cause] = p
    return out


def draw_complaints(household_id: str, period: str, triggers_met: set[ComplaintCause],
                    probability: dict[ComplaintCause, float]) -> list[ComplaintCause]:
    """The causes this household complains about this quarter. Only a trigger it met can fire."""
    q = _quarter(period)
    return [c for c in sorted(triggers_met, key=lambda c: c.value)
            if random.Random(f"w2_37_complaint_{household_id}_{q}_{c.value}").random()
            < probability[c]]


def silent_unhappy_probability(period: str, badly_handled_complainant_share: float,
                               uncomplained_trigger_share: float) -> float:
    """P(a household becomes silently unhappy | it met a trigger in the trailing year and did not complain).

    The published dissatisfied share is the whole dissatisfied population. The badly handled
    complainants are part of it; the rest are silent. Both shares are measured by the caller on the
    world's own book.
    """
    d = dissatisfied_share(period).value
    silent = d - badly_handled_complainant_share
    if silent < 0.0:
        raise CalibrationRefused(
            f"{period}: badly handled complainants are {badly_handled_complainant_share:.2%} of "
            f"accounts, above the published dissatisfied share {d:.0%}; complaints would no longer "
            f"be a floor on dissatisfaction")
    if uncomplained_trigger_share <= 0.0 or silent > uncomplained_trigger_share:
        raise CalibrationRefused(
            f"{period}: {silent:.2%} of accounts must be silently unhappy, but only "
            f"{uncomplained_trigger_share:.2%} met a trigger and did not complain")
    return silent / uncomplained_trigger_share


def draw_silent_unhappy(household_id: str, period: str, met_trigger: bool, complained: bool,
                        probability: float) -> bool:
    if complained or not met_trigger:
        return False
    q = _quarter(period)
    return random.Random(f"w2_37_silent_{household_id}_{q}").random() < probability
