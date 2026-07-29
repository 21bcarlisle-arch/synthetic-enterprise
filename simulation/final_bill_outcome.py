"""W2_12 — the credit-risk exit: does a move-out final bill actually get paid?

WORLD (SIM) side of the change-of-tenancy debt physics. This module answers one
question that nothing in the codebase answered before:

    when an occupant moves out, does the final bill get paid?

`company/billing/account_closure.py` already had the *status* `DEBT_REFERRED`,
but a status is a bookkeeping label, not physics — nothing ever decided whether
a given exit ended in payment or in a hole. That decision belongs on the WORLD
side of the epistemic wall, because it is a function of the departing
household's TRUE state (tenure, payment channel, fuel poverty, income stress)
which a real supplier cannot read. The company observes only the OUTCOME
(paid / paid late / partial / unpaid, and whether the customer went away) —
never the probability, never the archetype that generated it. That split is
made concrete by `FinalBillResolution.as_observable_event()`, which is the ONLY
thing that crosses.

Why the exit is its own mechanism and not just another arrears case
------------------------------------------------------------------
`simulation/arrears_engine.py` models the *recurring* billing cycle: a live
account, a live DD mandate, an ongoing relationship, a dunning cascade that can
still reach the customer. A move-out final bill is structurally different:

  * the relationship is OVER at the moment the bill is raised;
  * the bill lands 0-42 days AFTER the customer stopped being a customer
    (Ofgem SLC 21B gives the supplier six weeks), often at an address they have
    left;
  * "gone away" — no forwarding address — is a live failure mode that simply
    does not exist mid-tenure.

So the primitives are FOLDED, not duplicated: stress lookup, the fuel-poverty
multiplier, the late-days bands, the debt archetype and the post-write-off
DCA/debt-sale recovery all come from `arrears_engine` by import. What is new
here is the gone-away leg and the exit-specific probability shape.

Real-world anchoring (R13 — fidelity to reality, decided blind to company P&L)
-----------------------------------------------------------------------------
The director's frame for this atom is that a tenancy change is "ONE credit-risk
exit PLUS TWO deemed-rate entries (double jeopardy)". Ofgem's own evidence says
that exit leg is a first-order driver of UK supplier bad debt, not a rounding
error:

  * Ofgem press release, 30 October 2025 ("Ofgem to set out plan to reset and
    reform growing energy debt"): when someone moves home, energy accounts are
    switched to "occupier" and "bills build up under these anonymous accounts
    until the individual contacts a supplier to register". Ofgem puts this
    occupier debt at **£1.1bn-£1.7bn of the £4.4bn historic total** — i.e.
    **25%-39%** of all UK domestic energy debt — and notes that in the worst
    case it is written off entirely, adding **~£52 to every household's bill**
    through the price-cap debt allowance.
  * Supplier evidence submitted to the same review put the home-move cohort at
    **20%-40% of the overall debt figure** (Ofgem, "Tackling energy debt when
    moving home", call for input closed 21 January 2026).
  * Ofgem Debt and Arrears Indicators, Q1 2026: **3.8%** of electricity
    customers (1,132,348) and 3.7% of gas customers are in arrears WITHOUT a
    repayment arrangement — the ordinary, mid-tenure baseline.

The load-bearing, published fact this module must reproduce is the RATIO: exit
debt is grossly over-represented relative to the ~3.8% ordinary arrears rate.

⚠ **Named research gap (R10 honesty).** No published figure gives
p(a single move-out final bill goes unpaid). The Ofgem numbers are debt-VALUE
shares, not per-move probabilities, and cannot be inverted into one without
knowing the move rate and the mean exit balance — neither of which is published
alongside them. Rather than invent a point estimate, `GONE_AWAY_BASE_BETA`
draws the base gone-away rate PER MOVE from a Beta distribution, so the
parameter's own uncertainty is carried in the physics instead of being
laundered into a false-precision constant. Its mean (0.12) is pinned only by
two published constraints — it must sit well above the 3.8% ordinary arrears
rate, and it must be consistent with the 8-12% net-debt-at-final-bill band
already recorded in `company/billing/account_closure.py`'s calibration notes —
and its spread (~5%-25% central) is deliberately wide enough to contain both.
Every multiplier below is likewise a directionally-argued calibration CHOICE,
not an independently sourced coefficient, and is flagged as such at its own
definition (the Anchored-noise law this codebase already applies in
`arrears_engine.payment_outcome`).

Scale constraints
-----------------
* **C-S3 (asynchronous wall contract).** The outcome is a SEPARATE EVENT LATER
  IN TIME, never a same-step resolution. `open_final_bill_exposure()` returns
  an exposure carrying no outcome at all; `resolve_final_bill()` returns
  ``None`` until `as_of` reaches the resolution date (SLC 21B's 42-day final
  bill deadline plus `cot.py`'s existing 28-day overdue window = 70 days).
* **C-S2 (RNG substreams + deterministic replay).** Every draw comes from its
  own NAMED substream (`_FINAL_BILL_SUBSTREAMS`), seeded from a stable sha256
  of the exposure identity — so resolving the same exposure twice, in any
  order, at any wall-clock moment, yields the identical outcome (idempotent),
  and adding a future draw APPENDS a substream name rather than shifting any
  existing sequence.
* **C-S1 (event-arrival tolerance).** An exposure resolves purely from its own
  identity; it never reads a batch, a population, or any sibling exposure.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Optional

from simulation.arrears_engine import (
    DCA_COMMISSION_RATE,
    DCA_RECOVERY_RATE,
    DEBT_SALE_HAIRCUT_PCT,
    FUEL_POVERTY_DD_FAIL_MULTIPLIER,
    debt_archetype,
    dca_recovered_amount,
    debt_sale_proceeds,
    late_days_band,
    on_time_probability,
)
from simulation.household_segments import (
    PaymentChannel,
    TenureType,
    fuel_poverty_for_customer,
    payment_channel_for_customer,
    tenure_for_customer,
)

# --- timing: both windows already exist in the company layer, reused not reinvented
FINAL_BILL_DEADLINE_DAYS = 42   # Ofgem SLC 21B, six weeks (company/billing/account_closure.py)
FINAL_BILL_OVERDUE_DAYS = 28    # company/billing/cot.py::_OVERDUE_DAYS
RESOLUTION_DAYS = FINAL_BILL_DEADLINE_DAYS + FINAL_BILL_OVERDUE_DAYS


class FinalBillOutcome(str, Enum):
    """The company-OBSERVABLE result of a move-out final bill.

    Deliberately outcome-shaped: nothing here names a probability, an
    archetype, or a household attribute. A real supplier sees exactly these
    five states on a closed account.
    """

    CREDIT_DUE = "credit_due"          # net balance <= 0 — we owe the customer; no credit risk
    PAID_ON_TIME = "paid_on_time"
    PAID_LATE = "paid_late"
    PARTIALLY_PAID = "partially_paid"
    UNPAID = "unpaid"

    @property
    def is_shortfall(self) -> bool:
        return self in (FinalBillOutcome.PARTIALLY_PAID, FinalBillOutcome.UNPAID)


# ---------------------------------------------------------------------------
# Named RNG substreams (C-S2). Appending a name can never shift an existing
# sequence, because each substream is an independent function of (seed, name).
# ---------------------------------------------------------------------------
_FINAL_BILL_SUBSTREAMS: tuple[str, ...] = (
    "final_bill_base_rate",
    "final_bill_gone_away",
    "final_bill_payment",
    "final_bill_partial_share",
    "final_bill_late_days",
)


def _substream(base_seed: int, name: str) -> random.Random:
    """Independent RNG for a named substream, derived from a STABLE sha256 of
    ``final_bill:base_seed:name`` (never Python's per-process-salted ``hash()``,
    which would break deterministic replay across processes)."""
    digest = hashlib.sha256(f"final_bill:{base_seed}:{name}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _exposure_seed(account_id: str, supply_point_id: str, fuel: str, closure_date: date) -> int:
    """Stable per-exposure seed. Keyed on the exposure's full identity so the
    SAME exposure always resolves the same way however many times, and in
    whatever order, `resolve_final_bill()` is called (C-S2 idempotency), while
    two different exits of the same customer resolve independently."""
    key = f"{account_id}|{supply_point_id}|{fuel}|{closure_date.isoformat()}"
    return int(hashlib.sha256(key.encode()).hexdigest()[:16], 16)


# ---------------------------------------------------------------------------
# Parameters. Every constant below is a directionally-argued calibration CHOICE
# unless its comment cites a published figure. See the module docstring's named
# research gap — no published per-move non-payment probability exists.
# ---------------------------------------------------------------------------

# Base gone-away rate is SAMPLED per move, not fixed (R10: distribution, not a
# point estimate, where the parameter cannot be anchored). Beta(3, 22): mean
# 0.12, sd ~0.064, so the central mass runs ~5%-25%. Constrained above by the
# 8-12% net-debt-at-final-bill band in account_closure.py's calibration notes
# and below by Ofgem's 3.8% ordinary arrears rate (Q1 2026) — exit risk must be
# materially worse than mid-tenure risk for the Ofgem occupier-debt share
# (25%-39% of all UK domestic energy debt) to be reproducible at all.
GONE_AWAY_BASE_BETA: tuple[float, float] = (3.0, 22.0)

# Tenure multiplier. DIRECTION is real and is the mechanism Ofgem describes: a
# private tenancy ends with the occupant physically gone, frequently with no
# forwarding address, which is exactly the anonymous-"occupier" account Ofgem
# blames for £1.1-1.7bn of debt. An owner-occupier sale leaves a conveyancing
# paper trail. MAGNITUDES are a calibration choice, kept modest.
GONE_AWAY_TENURE_MULTIPLIER: dict[TenureType, float] = {
    TenureType.PRIVATE_RENTER: 1.60,
    TenureType.SOCIAL_RENTER: 1.20,
    TenureType.OWNER_OCCUPIER: 0.55,
}

# Payment-channel multiplier. DIRECTION is a hard mechanism, not a preference:
# a live Direct Debit mandate survives the closure and can still collect the
# final bill, whereas a standard-credit customer must actively choose to pay a
# bill for a property they have already left. MAGNITUDE is a choice.
GONE_AWAY_CHANNEL_MULTIPLIER: dict[PaymentChannel, float] = {
    PaymentChannel.DIRECT_DEBIT: 0.75,
    PaymentChannel.STANDARD_CREDIT: 1.40,
}

# Income-stress multiplier. Calibration choice; deliberately FLATTER than
# arrears_engine's mid-tenure DD-failure ladder (0.03/0.12/0.35, i.e. a 11.7x
# LOW->HIGH spread) because going away without a forwarding address is driven
# substantially by mobility and traceability, not by affordability alone —
# applying the affordability ladder unchanged would over-attribute exit debt to
# income stress.
GONE_AWAY_STRESS_MULTIPLIER: dict[str, float] = {"LOW": 0.85, "MODERATE": 1.35, "HIGH": 2.00}

# Fuel poverty: FOLDED from arrears_engine rather than re-chosen here, so the
# two mechanisms cannot drift apart.
GONE_AWAY_FUEL_POVERTY_MULTIPLIER = FUEL_POVERTY_DD_FAIL_MULTIPLIER

GONE_AWAY_MIN, GONE_AWAY_MAX = 0.005, 0.85

# Given the customer did NOT go away, a final bill is still paid less reliably
# than a mid-tenure bill: it arrives up to six weeks after the relationship
# ended (Ofgem's own guaranteed-standards window), and final-bill delay was the
# #1 switching complaint category in Ofgem's 2022 survey. Calibration choice.
FINAL_BILL_ON_TIME_PENALTY = 0.85

# Of the traceable customers who do not pay on time, most eventually pay
# something. Directionally consistent with Ofgem's finding that indebted
# customers "accrue more than £600 on average in unpaid bills" — a partial
# balance, not a zeroed one. Magnitudes are calibration choices.
TRACEABLE_LATE_SHARE = 0.55       # of the non-on-time residual, pay late in full
TRACEABLE_PARTIAL_SHARE = 0.60    # of what is left after that, pay part
PARTIAL_RECOVERY_BAND = (0.15, 0.75)   # fraction of the balance actually recovered

# A gone-away customer is not necessarily a zero: a held deposit is offset
# company-side, and some balances are recovered by trace-and-collect. The
# recovery FRACTION of a gone-away balance is drawn from this band.
GONE_AWAY_RECOVERY_BAND = (0.0, 0.20)


@dataclass(frozen=True)
class FinalBillExposure:
    """Opened AT the move-out. Carries NO outcome — deliberately.

    C-S3: the request (a closure) and the response (paid or not) are separate
    events in time. Anything that let this object answer "was it paid?" at
    construction would collapse a 70-day real-world process into one step and
    make the wall contract synchronous.
    """

    exposure_id: str
    account_id: str
    supply_point_id: str
    fuel: str
    closure_date: date
    net_balance_gbp: float
    customer_id: Optional[str] = None

    @property
    def final_bill_due(self) -> date:
        """Ofgem SLC 21B: the final bill must be issued within six weeks."""
        return self.closure_date + timedelta(days=FINAL_BILL_DEADLINE_DAYS)

    @property
    def resolution_date(self) -> date:
        """The earliest date the paid/unpaid question can be answered at all."""
        return self.closure_date + timedelta(days=RESOLUTION_DAYS)

    def is_resolvable(self, as_of: date) -> bool:
        return as_of >= self.resolution_date

    @property
    def at_risk_gbp(self) -> float:
        """Balance genuinely exposed to credit risk (a credit balance is not)."""
        return round(max(0.0, self.net_balance_gbp), 2)


@dataclass(frozen=True)
class FinalBillResolution:
    """The WORLD's answer. Holds both the observable outcome AND the hidden
    drivers that produced it — the hidden fields exist so the harness can
    measure the company's belief-vs-truth gap, and are stripped by
    `as_observable_event()`, which is the only thing the company may consume.
    """

    account_id: str
    supply_point_id: str
    fuel: str
    resolved_on: date
    outcome: FinalBillOutcome
    billed_gbp: float
    recovered_gbp: float
    gone_away: bool
    days_late: int = 0
    # --- SIM-ONLY below this line. Never crosses the wall. ---
    gone_away_probability: float = 0.0
    debt_archetype: Optional[str] = None

    @property
    def shortfall_gbp(self) -> float:
        return round(max(0.0, self.billed_gbp - self.recovered_gbp), 2)

    def as_observable_event(self) -> dict:
        """The typed, versioned message that crosses the wall.

        Contains ONLY what a real UK supplier observes on a closed account: the
        outcome, the money, the dates, and whether post has come back "gone
        away" (a supplier genuinely knows that — returned mail / no forwarding
        address). It must NEVER contain `gone_away_probability`,
        `debt_archetype`, tenure, payment channel or fuel-poverty state.
        `company.billing.account_closure.assert_observable_final_bill_event()`
        enforces exactly this key set from the far side, so the guard cannot be
        defeated by editing this method alone.
        """
        return {
            "schema": "final_bill_outcome.v1",
            "account_id": self.account_id,
            "supply_point_id": self.supply_point_id,
            "fuel": self.fuel,
            "resolved_on": self.resolved_on.isoformat(),
            "outcome": self.outcome.value,
            "billed_gbp": round(self.billed_gbp, 2),
            "recovered_gbp": round(self.recovered_gbp, 2),
            "gone_away": self.gone_away,
            "days_late": self.days_late,
        }


def open_final_bill_exposure(
    account_id: str,
    supply_point_id: str,
    fuel: str,
    closure_date: date,
    net_balance_gbp: float,
    customer_id: Optional[str] = None,
) -> FinalBillExposure:
    """Open the credit-risk exit leg of a tenancy change. No outcome yet (C-S3)."""
    return FinalBillExposure(
        exposure_id=f"FBX-{account_id}-{fuel}-{closure_date.isoformat()}",
        account_id=account_id,
        supply_point_id=supply_point_id,
        fuel=fuel,
        closure_date=closure_date,
        net_balance_gbp=round(net_balance_gbp, 2),
        customer_id=customer_id,
    )


def gone_away_probability(
    exposure: FinalBillExposure,
    stress: str = "LOW",
    seed: Optional[int] = None,
) -> float:
    """p(the departing occupant leaves no traceable forwarding address).

    SIM-ONLY. Reads the household's TRUE tenure / payment channel / fuel-poverty
    state — none of which the company may see. The base rate is DRAWN, not
    fixed (see the module docstring's named research gap).
    """
    base_seed = seed if seed is not None else _exposure_seed(
        exposure.account_id, exposure.supply_point_id, exposure.fuel, exposure.closure_date
    )
    alpha, beta = GONE_AWAY_BASE_BETA
    p = _substream(base_seed, "final_bill_base_rate").betavariate(alpha, beta)

    customer_id = exposure.customer_id
    if customer_id is not None:
        channel = payment_channel_for_customer(customer_id, exposure.fuel)
        p *= GONE_AWAY_CHANNEL_MULTIPLIER.get(channel, 1.0)
        p *= GONE_AWAY_TENURE_MULTIPLIER.get(tenure_for_customer(customer_id), 1.0)
        if fuel_poverty_for_customer(customer_id, channel):
            p *= GONE_AWAY_FUEL_POVERTY_MULTIPLIER
    p *= GONE_AWAY_STRESS_MULTIPLIER.get((stress or "LOW").upper(), 1.0)

    return max(GONE_AWAY_MIN, min(GONE_AWAY_MAX, p))


def resolve_final_bill(
    exposure: FinalBillExposure,
    as_of: date,
    stress: str = "LOW",
    income_stress_trajectory: Optional[list[dict]] = None,
    seed: Optional[int] = None,
) -> Optional[FinalBillResolution]:
    """Resolve the exit — or return ``None`` because it is not resolvable yet.

    **C-S3 is the point of the ``None``.** Calling this at closure time, or a
    week later, does not produce a provisional answer: the real process has not
    happened yet. The company must hold the exposure open across the SLC 21B
    window plus the overdue window and come back.

    **C-S2:** deterministic and idempotent — the same exposure resolves to the
    identical result on every call, at any later `as_of`, in any order relative
    to other exposures, because every draw derives from the exposure's own
    identity rather than from shared engine state.
    """
    if not exposure.is_resolvable(as_of):
        return None

    base_seed = seed if seed is not None else _exposure_seed(
        exposure.account_id, exposure.supply_point_id, exposure.fuel, exposure.closure_date
    )
    resolved_on = exposure.resolution_date
    billed = exposure.at_risk_gbp

    def _mk(outcome: FinalBillOutcome, recovered: float, gone: bool,
            p_gone: float, days_late: int = 0, archetype: Optional[str] = None):
        return FinalBillResolution(
            account_id=exposure.account_id,
            supply_point_id=exposure.supply_point_id,
            fuel=exposure.fuel,
            resolved_on=resolved_on,
            outcome=outcome,
            billed_gbp=round(billed, 2),
            recovered_gbp=round(recovered, 2),
            gone_away=gone,
            days_late=days_late,
            gone_away_probability=round(p_gone, 6),
            debt_archetype=archetype,
        )

    # A closure in credit carries no credit risk at all — we owe them. Roughly
    # half of UK closures land here (Ofgem runs a standing "are you owed money
    # on your energy bill?" campaign precisely because of it).
    if exposure.net_balance_gbp <= 0:
        return _mk(FinalBillOutcome.CREDIT_DUE, 0.0, False, 0.0)

    p_gone = gone_away_probability(exposure, stress=stress, seed=base_seed)
    archetype = (
        debt_archetype(income_stress_trajectory, resolved_on.year)
        if income_stress_trajectory is not None else None
    )

    if _substream(base_seed, "final_bill_gone_away").random() < p_gone:
        lo, hi = GONE_AWAY_RECOVERY_BAND
        frac = _substream(base_seed, "final_bill_partial_share").uniform(lo, hi)
        recovered = billed * frac
        outcome = FinalBillOutcome.PARTIALLY_PAID if recovered > 0.01 else FinalBillOutcome.UNPAID
        return _mk(outcome, recovered, True, p_gone, archetype=archetype)

    # Traceable: an ordinary, if degraded, payment decision.
    r = _substream(base_seed, "final_bill_payment").random()
    p_on_time = on_time_probability(stress) * FINAL_BILL_ON_TIME_PENALTY
    if r < p_on_time:
        return _mk(FinalBillOutcome.PAID_ON_TIME, billed, False, p_gone, archetype=archetype)

    residual = r - p_on_time
    span = max(1e-9, 1.0 - p_on_time)
    if residual < span * TRACEABLE_LATE_SHARE:
        lo, hi = late_days_band(stress)
        days = _substream(base_seed, "final_bill_late_days").randint(lo, hi)
        return _mk(FinalBillOutcome.PAID_LATE, billed, False, p_gone,
                   days_late=days, archetype=archetype)

    if residual < span * (TRACEABLE_LATE_SHARE
                          + (1 - TRACEABLE_LATE_SHARE) * TRACEABLE_PARTIAL_SHARE):
        lo, hi = PARTIAL_RECOVERY_BAND
        frac = _substream(base_seed, "final_bill_partial_share").uniform(lo, hi)
        return _mk(FinalBillOutcome.PARTIALLY_PAID, billed * frac, False, p_gone,
                   archetype=archetype)

    return _mk(FinalBillOutcome.UNPAID, 0.0, False, p_gone, archetype=archetype)


def exit_debt_recovery_gbp(resolution: FinalBillResolution) -> float:
    """Eventual DCA / debt-sale proceeds on an unrecovered exit balance.

    FOLDS `arrears_engine`'s existing post-write-off cascade rather than
    duplicating it: the same archetype-conditioned DCA recovery rate,
    commission and debt-sale haircut that the mid-tenure book already uses
    (AVOIDANT debt gets sold at `DEBT_SALE_HAIRCUT_PCT`; everything else is
    worked by a DCA at `DCA_RECOVERY_RATE` net of `DCA_COMMISSION_RATE`).
    Returns 0.0 when there is no shortfall or no archetype was supplied.
    """
    shortfall = resolution.shortfall_gbp
    if shortfall <= 0 or resolution.debt_archetype is None:
        return 0.0
    if resolution.debt_archetype == "AVOIDANT":
        return debt_sale_proceeds(shortfall)
    return dca_recovered_amount(shortfall, resolution.debt_archetype)


__all__ = [
    "DCA_COMMISSION_RATE",
    "DCA_RECOVERY_RATE",
    "DEBT_SALE_HAIRCUT_PCT",
    "FINAL_BILL_DEADLINE_DAYS",
    "FINAL_BILL_OVERDUE_DAYS",
    "RESOLUTION_DAYS",
    "FinalBillExposure",
    "FinalBillOutcome",
    "FinalBillResolution",
    "exit_debt_recovery_gbp",
    "gone_away_probability",
    "open_final_bill_exposure",
    "resolve_final_bill",
]
