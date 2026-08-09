"""C10_self_rationing_detection -- company-side SILENT-HARDSHIP detection twin.

THE HARD CASE. The company cannot see the SIM self-rationing state
(`simulation.self_rationing`, W2_8). It never reads it. The hidden "pay-but-
don't-heat" household KEEPS PAYING (a perfect payment record -- the arrears /
collections channel shows NOTHING) but cuts its energy use below plausible
living levels to keep the bill affordable. Arrears vulnerability announces
itself; this does not. The ONLY observable signature is a CONSUMPTION ANOMALY:
a DROP from the household's own established baseline down below the Ofgem TDCV
Low-band floor, with a CLEAN payment record. This detector infers likely self-
rationing from OBSERVABLES ONLY and raises the orphaned
`VulnerabilityFlag.PPM_SELF_DISCONNECTED`, which had no detector today.

THE CONFOUND IT MUST NOT FAIL. A genuinely LOW-NEED household -- a small,
efficient, one-person home -- ALSO sits below the TDCV Low floor with a perfect
payment record. In a single snapshot the two are identical. They differ in one
OBSERVABLE respect: the self-rationer DROPPED to that level from a normal
baseline (a visible change over two meter reads), while the low-need home was
ALWAYS there (no drop). A detector that flags EVERYONE below the floor is naive
-- it would flag every efficient home (a flood of false positives) and, in
spirit, would be reading the floor as if it were the hidden label. So the
signature is the DROP-BELOW-FLOOR, not below-floor alone. This is what separates
rationing from low-need without ever reading the hidden budget or true label.

THE HONEST BLIND SPOT (why this is allowed to be wrong, and where the gap comes
from). The drop signal REQUIRES a trustworthy prior baseline -- a meter read
history. A real UK supplier does not have one for every account: traditional
(non-smart / non-AMR) meters send no regular reads, and a recently-switched
customer brings no history. For those accounts the company sees only "below
floor, no baseline" -- which is EXACTLY what a low-need home looks like too --
so it CANNOT safely raise the flag (doing so on below-floor-alone is the naive
leak above). The silent hardship among the no-baseline population is therefore
structurally invisible. That is a real, externally-anchored detection gap (it
tracks smart-meter coverage), not a modelling shortcut -- and it is the point of
the coupled triad: the harness measures the belief-vs-truth gap this blind spot
produces.

THE SUPPLIER'S OWN RECORDS -- WHY A DROP IS NOT ALWAYS A MYSTERY (atom D18).
Until D18 this detector saw two meter reads and nothing else, so EVERY drop
looked the same: a household that moved out mid-year, a property standing empty
between occupiers and a home the company itself insulated under its own ECO
scheme were all indistinguishable from silent hardship. That is not how a real
supplier works -- it HOLDS several of those records: a change-of-tenancy
registration on the account, a void notification from a landlord or agent, its
own install file. `SelfRationingObservation.account_records` is that channel.

Three things keep it a supplier record rather than the world's answer key:

  * COVERAGE -- only some events leave a record at all. Nobody registers a
    decision to use less energy, so a VOLUNTARY cut is structurally
    unexplainable; a move is registered only if the occupier tells someone; a
    void only if the landlord does; an install file exists only for the
    company's OWN scheme customers.
  * LATENCY -- a record that exists is not a record the company HAS. CoT is
    supplier-internal and industry-wide nobody is told (advisor scope brief
    `ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md`): the occupier tells
    us in week one or in month six. A record whose `received_date` is after the
    detection `as_of` DOES NOT COUNT -- point-in-time discipline, and the
    detector must still decide without it.
  * IT NEVER SAYS "NO HARDSHIP HERE". A CoT or void record does not clear the
    account; it INVALIDATES THE BASELINE, because the history belongs to the
    previous occupier and the drop is therefore not this household's drop. The
    account lands in the SAME honest blind spot as an unmetered one (a
    different reason, named separately in `not_flagged_reason`), never in a
    "cleared" state -- the incoming occupier could be self-rationing too. An
    install record adjusts EXPECTED consumption by the scheme's DEEMED saving
    (the figure on the company's own file, not the home's realised saving --
    the deemed-vs-actual performance gap is real and stays), so a household
    that cut FURTHER than its retrofit explains is still flagged.

So the channel lowers false flags without ever scoring the detector perfect,
and it has a COST the harness measures rather than hides: a genuine rationer
who also moved house is now explained away and MISSED. `tools/couple_w2_8_c10.py`
publishes both directions with and without the channel, plus the distance
between what a supplier COULD explain away and what it actually does.

EPISTEMIC WALL (.claude/rules/epistemic-wall-company.md). This module imports
NOTHING from `simulation.*`. Every input is an observable a real supplier holds
in its own systems: two annual meter reads (prior baseline + current), whether a
usable baseline exists at all, the public TDCV floor, the payment/arrears record,
an observable regional weather-normalisation factor. The TDCV Low floor is the
regulation-commons figure sourced DIRECTLY from
`company.compliance.domain_invariants` (the company-side source of truth), not a
re-derived threshold. Thresholds are domain-reasoned, set blind to the SIM's
budget->severity physics (W2_8's `_SEVERITY_RANGE` etc); that independence (R15)
is what makes the measured gap a real measurement and not a tautology.

R12/R13. The drop threshold and floor are affordability/regulation reasoning,
NOT fitted to move any gap number. A near-zero gap would be a red flag to
diagnose (a leak or a coverage assumption that erased the blind spot), never a
success to bank.

C-S1 event-arrival tolerance: `detect` works on whatever observation it is
given -- a missing baseline is simply absent (no opinion on the drop, not a
zero). C-S2: no wall-clock, no unseeded randomness; the same observation always
yields the same result.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence, Tuple

from company.compliance.domain_invariants import TDCV_ELEC_LOW, TDCV_GAS_LOW
from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRegister


# ---------------------------------------------------------------------------
# The plausible-living floor -- the Ofgem TDCV Low-band FLOOR (regulation
# commons). SOURCE OF TRUTH: company.compliance.domain_invariants. Consumption
# BELOW this floor is inconsistent with adequately heating a home of that band.
# (W2_8 DUPLICATES these on the SIM side of the wall and drift-guards against
# THIS same source; the company side imports the source directly.)
# ---------------------------------------------------------------------------
TDCV_LOW_FLOOR_KWH: dict[str, float] = {
    "electricity": TDCV_ELEC_LOW.low,   # 1400 kWh/yr
    "gas": TDCV_GAS_LOW.low,            # 5500 kWh/yr
}


# ---------------------------------------------------------------------------
# Detection thresholds -- domain-reasoned, NOT fitted to any SIM parameter.
# ---------------------------------------------------------------------------
# The company's own reading of "what a rationing signature looks like", set by
# supplier-side reasoning and blind to W2_8's hidden severity band. A drop of
# >=20% BEYOND what weather explains is treated as a material, non-seasonal cut.
# (W2_8's true severities sit in ~0.30-0.90; this 0.20 was chosen independently
# -- it is deliberately NOT the SIM's number, preserving R15 independence.)
_MATERIAL_DROP_FRACTION = 0.20


class AccountRecordType(str, Enum):
    """A SUPPLIER-SIDE record that bears on why an account's meter reads lower
    (atom D18). These are records the company holds in its own systems -- not
    causes it is told about by the world. There is deliberately NO member for a
    household that simply chose to use less: nobody registers that, so a
    voluntary cut stays unexplainable and the detector must still decide."""

    CHANGE_OF_TENANCY = "change_of_tenancy"    # occupier changed; CoT registered
    VOID_NOTIFICATION = "void_notification"    # landlord/agent: premises empty
    OWN_SCHEME_INSTALL = "own_scheme_install"  # our OWN ECO/GBIS install file


# A CoT or a void means the account's consumption history belongs to somebody
# else (or to nobody) -- so the DROP is not this household's drop. These records
# INVALIDATE THE BASELINE; they never certify that no hardship exists.
_BASELINE_INVALIDATING: frozenset = frozenset(
    {AccountRecordType.CHANGE_OF_TENANCY, AccountRecordType.VOID_NOTIFICATION}
)


@dataclass(frozen=True)
class AccountRecord:
    """One supplier-held record, with the two dates that make it a record rather
    than an oracle: when the event took EFFECT, and when it REACHED us.

    `expected_saving_fraction` applies to an install record only: it is the
    SCHEME'S DEEMED saving from the company's own file, never the home's
    realised saving (the deemed-vs-actual performance gap is real and is not
    modelled away). An install record without one adjusts nothing -- the
    detector keeps looking at the account rather than assume a saving it has no
    figure for (fail-SAFE for a vulnerability control: the failure direction is
    an extra look, never a silent clearance).
    """

    record_type: AccountRecordType
    effective_date: dt.date
    received_date: dt.date
    expected_saving_fraction: Optional[float] = None

    def has_arrived(self, as_of: Optional[dt.date]) -> bool:
        """Point-in-time: has this record reached the company by `as_of`?

        With no `as_of` the company cannot say a record had arrived, so it has
        NOT -- an unknown clock never suppresses a vulnerability flag.
        """
        if as_of is None:
            return False
        return self.received_date <= as_of


@dataclass(frozen=True)
class SelfRationingObservation:
    """Everything the company can OBSERVE about one account's consumption and
    payment posture over a detection window. Every field is a real supplier-side
    record; none is SIM ground truth.

    `baseline_annual_kwh` is the household's OWN established prior baseline (an
    earlier annual meter read). It is ``None`` when the company has no usable
    history -- a traditional/unread meter or a recently-switched account -- which
    is the real blind spot: without it the drop cannot be seen and the account is
    indistinguishable from a genuinely-low-need home (C-S1: a missing signal is
    absent, never a zero)."""

    customer_id: str
    commodity: str = "electricity"          # "electricity" | "gas"
    # Current metered annual consumption (kWh). The one always-present read.
    observed_annual_kwh: float = 0.0
    # The household's OWN prior baseline (kWh/yr); None if no usable history.
    baseline_annual_kwh: Optional[float] = None
    # Public TDCV Low-band floor; defaults from `commodity` when omitted.
    floor_kwh: Optional[float] = None
    # Payment posture -- the SILENT channel. A self-rationer keeps paying, so a
    # clean record here is EXPECTED, not reassuring. Any arrears means the
    # collections channel (C7 / PAYMENT_DIFFICULTY) already owns the case.
    missed_payments: int = 0
    arrears_open: bool = False
    # Observable regional weather-normalisation factor = expected consumption
    # this period vs baseline purely from weather (HDD ratio recent/baseline).
    # <1 = a milder period (some fall is weather, not rationing); >1 = colder.
    # 1.0 = no adjustment. Lets the detector avoid mistaking a warm year for a
    # cut. It is an OBSERVABLE (the supplier knows regional degree-days).
    weather_normalisation_factor: float = 1.0
    inbound_hardship_contacts: int = 0
    # -- The supplier's own records (atom D18) -------------------------------
    # Records the company HOLDS that bear on the drop. Empty is the honest
    # default: most drops have no record behind them.
    account_records: Tuple[AccountRecord, ...] = ()
    # The detection date. A record received AFTER it has not arrived yet.
    # None = the caller stated no clock, so no record counts (see has_arrived).
    as_of: Optional[dt.date] = None
    # Start of the period the baseline describes. A record whose event predates
    # it explains an OLDER consumption level, not this drop -- so it does not
    # count. None = no window stated (registered simplification: any arrived
    # record then counts, which is why the coupler always states one).
    baseline_period_start: Optional[dt.date] = None


@dataclass(frozen=True)
class SelfRationingDetection:
    """The company's BELIEF about one account. `self_rationing_suspected` is the
    binary the detection-gap scores; the rest is audit + support-response
    shaping."""

    customer_id: str
    self_rationing_suspected: bool
    confidence: float                       # 0..1, monotone in signal strength
    signals: dict = field(default_factory=dict)
    vulnerability_flags: tuple = ()

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "self_rationing_suspected": self.self_rationing_suspected,
            "confidence": round(self.confidence, 4),
            "signals": self.signals,
            "vulnerability_flags": [f.value for f in self.vulnerability_flags],
        }


def _floor_for(obs: SelfRationingObservation) -> float:
    if obs.floor_kwh is not None:
        return obs.floor_kwh
    if obs.commodity not in TDCV_LOW_FLOOR_KWH:
        raise ValueError(
            f"commodity {obs.commodity!r} not one of {tuple(TDCV_LOW_FLOOR_KWH)}"
        )
    return TDCV_LOW_FLOOR_KWH[obs.commodity]


class SelfRationingDetector:
    """Infers likely PAY-BUT-DON'T-HEAT self-rationing from observables, and
    (optionally) writes the resulting support response into the vulnerability
    register (raising PPM_SELF_DISCONNECTED)."""

    def __init__(self, material_drop_fraction: float = _MATERIAL_DROP_FRACTION):
        # Exposed so a reviewer / test can vary it; the default is the
        # domain-reasoned constant, never fitted to a gap.
        self.material_drop_fraction = material_drop_fraction

    def detect(self, obs: SelfRationingObservation) -> SelfRationingDetection:
        floor = _floor_for(obs)
        observed = obs.observed_annual_kwh
        below_floor = observed < floor

        # A clean payment channel is the SILENT-hardship precondition: this flag
        # is for the case the arrears channel cannot see. If arrears are open the
        # collections path owns it -- this detector defers rather than double-flag.
        clean_payment = obs.missed_payments == 0 and not obs.arrears_open

        # -- The drop signal -- the ONE thing that separates a rationer (dropped
        # below floor) from a genuinely-low-need home (always below floor). It
        # needs a usable baseline; without one the drop is unobservable and we do
        # NOT fall back to below-floor-alone (that would flag every efficient
        # home -- the naive leak). Weather-normalise the baseline first so a
        # milder period is not mistaken for a cut.
        has_baseline = obs.baseline_annual_kwh is not None and obs.baseline_annual_kwh > 0

        # -- The supplier's own records (D18). Only records that have ARRIVED by
        # `as_of` and that post-date the baseline period can bear on this drop.
        arrived, pending = self._partition_records(obs)
        invalidating = [r for r in arrived if r.record_type in _BASELINE_INVALIDATING]
        baseline_invalidated_by = (
            invalidating[0].record_type.value if invalidating else None
        )
        if baseline_invalidated_by:
            # The history is the PREVIOUS occupier's (or nobody's): the drop is
            # not this household's drop, so it is not observable here. This is a
            # blind spot, NOT a clearance -- the incoming occupier may be
            # rationing and the company simply cannot see it from the meter.
            has_baseline = False
        deemed_saving = self._deemed_saving(arrived)

        residual_drop: Optional[float] = None
        material_drop = False
        if has_baseline:
            factor = obs.weather_normalisation_factor
            if factor is None or factor <= 0:
                factor = 1.0
            # Expected consumption = the account's own baseline, weather-adjusted
            # and then reduced by any saving the company's OWN install file says
            # it paid for. A cut BEYOND that is still a cut.
            weather_expected = obs.baseline_annual_kwh * factor * (1.0 - deemed_saving)
            if weather_expected > 0:
                residual_drop = 1.0 - observed / weather_expected
                material_drop = residual_drop >= self.material_drop_fraction

        suspected = below_floor and material_drop and clean_payment

        signals = {
            "commodity": obs.commodity,
            "observed_annual_kwh": observed,
            "baseline_annual_kwh": obs.baseline_annual_kwh,
            "has_usable_baseline": has_baseline,
            "floor_kwh": floor,
            "below_floor": below_floor,
            "weather_normalisation_factor": obs.weather_normalisation_factor,
            "residual_drop_fraction": (
                None if residual_drop is None else round(residual_drop, 4)
            ),
            "material_drop": material_drop,
            "clean_payment_channel": clean_payment,
            "inbound_hardship_contacts": obs.inbound_hardship_contacts,
            # -- The record channel (D18). Both sides travel: what the company
            # HAS, and what exists but has not reached it yet -- the latency the
            # harness measures the cost of.
            "records_arrived": tuple(r.record_type.value for r in arrived),
            "records_not_yet_arrived": tuple(r.record_type.value for r in pending),
            "baseline_invalidated_by": baseline_invalidated_by,
            "deemed_saving_fraction": round(deemed_saving, 4),
            # Why an account BELOW the floor was NOT flagged -- the audit trail
            # that proves the detector is not naive (and names the blind spot).
            "not_flagged_reason": self._not_flagged_reason(
                suspected, below_floor, has_baseline, material_drop, clean_payment,
                baseline_invalidated_by=baseline_invalidated_by,
                deemed_saving=deemed_saving,
            ),
        }

        # Confidence grows with how deep the residual drop is and how far below
        # the floor -- both observable, both monotone in likely harm. An inbound
        # hardship contact corroborates.
        confidence = 0.0
        if suspected:
            confidence = 0.55
            if residual_drop is not None:
                confidence += min(0.25, max(0.0, residual_drop - self.material_drop_fraction))
            shortfall = (floor - observed) / floor if floor > 0 else 0.0
            confidence += min(0.15, max(0.0, shortfall) * 0.5)
            if obs.inbound_hardship_contacts > 0:
                confidence += 0.10
            confidence = min(confidence, 1.0)

        flags = (VulnerabilityFlag.PPM_SELF_DISCONNECTED,) if suspected else ()
        return SelfRationingDetection(
            customer_id=obs.customer_id,
            self_rationing_suspected=suspected,
            confidence=round(confidence, 4),
            signals=signals,
            vulnerability_flags=flags,
        )

    @staticmethod
    def _partition_records(
        obs: "SelfRationingObservation",
    ) -> Tuple[Tuple[AccountRecord, ...], Tuple[AccountRecord, ...]]:
        """Split the account's records into (bears on this drop, does not yet).

        A record bears on the drop only if it has ARRIVED by `as_of` AND its
        event falls inside the window the baseline describes -- a tenancy change
        from four years ago explains the baseline itself, not a fall away from
        it. Everything else is `pending`: it exists, the company does not have
        it, and the detector must decide without it.
        """
        arrived: List[AccountRecord] = []
        pending: List[AccountRecord] = []
        for rec in obs.account_records:
            in_window = (
                obs.baseline_period_start is None
                or rec.effective_date >= obs.baseline_period_start
            )
            if in_window and rec.has_arrived(obs.as_of):
                arrived.append(rec)
            else:
                pending.append(rec)
        return tuple(arrived), tuple(pending)

    @staticmethod
    def _deemed_saving(arrived: Sequence[AccountRecord]) -> float:
        """The saving the company's OWN install files say it paid for.

        Deemed, never realised. Multiple measures compound. A record carrying no
        figure adjusts NOTHING (a missing number must not become a free pass),
        and the total is clamped below 1.0 so no record can make the expected
        consumption zero and swallow any drop whatsoever.
        """
        remaining = 1.0
        for rec in arrived:
            if rec.record_type is not AccountRecordType.OWN_SCHEME_INSTALL:
                continue
            frac = rec.expected_saving_fraction
            if frac is None or frac <= 0.0:
                continue
            remaining *= 1.0 - min(float(frac), 0.9)
        return min(0.9, 1.0 - remaining)

    @staticmethod
    def _not_flagged_reason(
        suspected: bool, below_floor: bool, has_baseline: bool,
        material_drop: bool, clean_payment: bool,
        baseline_invalidated_by: Optional[str] = None,
        deemed_saving: float = 0.0,
    ) -> Optional[str]:
        if suspected:
            return None
        if not below_floor:
            return "consumption above the plausible-living floor"
        if baseline_invalidated_by:
            # The D18 channel's own blind spot, named separately from the
            # coverage one: we know WHY the history stopped describing this
            # account, and that is exactly why we cannot read a drop from it.
            return (
                f"below floor but a {baseline_invalidated_by} record means the prior "
                "baseline is not this occupier's -- no drop is observable (NOT a "
                "finding of no hardship)"
            )
        if not has_baseline:
            # The honest blind spot: below floor but no history to see a drop.
            return "below floor but NO usable baseline -- indistinguishable from a low-need home"
        if not material_drop:
            if deemed_saving > 0.0:
                return (
                    "below floor but no material drop beyond the deemed saving on our "
                    "own scheme install record (the retrofit explains the fall)"
                )
            return "below floor but no material drop vs own weather-adjusted baseline (low-need home)"
        if not clean_payment:
            return "arrears open -- owned by the collections channel, not the silent-hardship flag"
        return "not suspected"

    def detect_many(
        self, observations: Sequence[SelfRationingObservation]
    ) -> List[SelfRationingDetection]:
        return [self.detect(o) for o in observations]

    def apply_to_register(
        self,
        register: VulnerabilityRegister,
        result: SelfRationingDetection,
        as_of: dt.date,
    ) -> None:
        """Wire a believed self-rationing case into the real support response:
        register PPM_SELF_DISCONNECTED so the account picks up the required
        actions (offer_emergency_credit, debt_referral) defined in the register.
        A no-detection is a no-op -- an absent signal never clears an existing
        flag (a real supplier does not stand a vulnerability down just because a
        later read looked normal)."""
        if not result.self_rationing_suspected or not result.vulnerability_flags:
            return
        register.register(
            customer_id=result.customer_id,
            flags=list(result.vulnerability_flags),
            recorded_date=as_of,
            notes=(
                "auto-flagged by C10 self-rationing detector "
                f"(confidence={result.confidence:.2f}; consumption drop below "
                "TDCV Low floor with a clean payment record)"
            ),
        )
