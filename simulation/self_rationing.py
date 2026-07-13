"""W2_8_self_rationing — the hidden "pay-but-don't-heat" SILENT HARDSHIP state.

WHAT THIS IS
------------
A per-household HIDDEN self-rationing state (world-side SIM ground truth). It
models the hard-to-detect vulnerability the C7 coupled run flagged: a household
under BUDGET STRESS (from ``W2_4_household_budget`` — a squeezed or negative
discretionary margin) who KEEPS PAYING (a perfect payment record — so the
payment / arrears channel shows NOTHING) but whose ENERGY CONSUMPTION COLLAPSES
below plausible living levels. The heating/eating trade-off: they stop heating to
keep the bill affordable, rather than fall into arrears.

THE OBSERVABLE SIGNATURE — WHY THIS IS THE HARD DETECTION CASE
--------------------------------------------------------------
Arrears vulnerability announces itself: a missed payment, a broken plan, a debt
balance. Self-rationing is SILENT on the payment channel — ``missed_payments``
stays ZERO, every bill is paid on time. The ONLY observable is a CONSUMPTION
anomaly: the household's usage drops sharply, from its OWN established baseline,
to below the Ofgem TDCV Low-band floor (a level inconsistent with heating a home
of that size in that weather). Detection must come from the consumption drop
ALONE — never from arrears (there are none). This directly wires the orphaned
``VulnerabilityFlag.PPM_SELF_DISCONNECTED`` taxonomy slot, which has no detector
today, and couples to the company-side twin ``C10_self_rationing_detection``
(later), which must recover this from the consumption anomaly.

THE CONFOUND (why the true label must be carried)
-------------------------------------------------
A GENUINELY LOW-NEED household — a small, efficient, one-person home — also sits
below the TDCV Low floor, with a perfect payment record. To the company the two
look identical in a single snapshot. They differ in TWO hidden respects the
generator carries as the answer key: (1) the self-rationer is under budget
stress and the low-need household is not; (2) the self-rationer DROPPED to that
level from a normal baseline (a visible, detectable change over time), while the
low-need household was ALWAYS there (no drop). The detector's whole job is to
tell these apart from observables (the drop, the weather-inconsistency) without
ever reading the hidden budget or the true label. A detector that scores 100%
would be leaking hidden state (an epistemic-wall violation in spirit).

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
-----------------------------------------------------
WORLD/sim code. MUST NOT import ``company.*`` or ``saas.*``. The only sanctioned
SIM->company seam is ``company/interfaces/sim_interface.py``, which this module
never calls and which must never surface any HIDDEN field defined here
(``is_self_rationing``, ``rationing_severity``, ``discretionary_margin_monthly``).
Every record carries ``data_regime="synthetic"``. The TDCV Low-band FLOOR is an
externally-published Ofgem figure (regulation commons); its source of truth is
``company/compliance/domain_invariants.py::TDCV_{ELEC,GAS}_LOW``, DUPLICATED here
as a module constant rather than imported (exactly as ``population_draw.py``
does), with a drift-guard test in ``tests/`` (which may import anything) asserting
the two never diverge — the wall-safe way to reuse an anchored constant.

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md — non-negotiable; the 01:09Z incident)
-------------------------------------------------------------------------------
The rationing PROPENSITY is NOT an independent draw — it is a pure function of
the W2_4 budget margin (self-rationing ARISES FROM a squeezed budget). Only the
onset Bernoulli and the severity magnitude are stochastic, and each draws from
THIS subsystem's OWN named substream (``_substream(base_seed, name)`` ->
isolated ``random.Random`` seeded from a STABLE sha256 of
``W2_8_self_rationing::<name>::<base_seed>``). It never touches the global
``random`` module and can NEVER shift another subsystem's sequence — W2_4
household_budget, population_draw and life_events stay byte-identical no matter
how far this one is advanced. A future mechanism APPENDS a name, never threads a
draw through an existing one. Proven by the substream-isolation tests. Seeds
derive from a stable sha256/md5 (never Python's per-process-salted ``hash()``),
so replay is deterministic across processes (C-S2).

BASELINE vs CURRICULUM (R13)
---------------------------
The margin->propensity map and the severity band are DIRECTOR CURRICULUM
DIAGNOSTICS (R12 / Law A) — never tuned toward a company P&L outcome, changed
only by a named, versioned, director-authored edit.

ANCHORS & HONEST SIMPLIFICATIONS (R10, dated 2026-07-13)
--------------------------------------------------------
Provenance: ``docs/design/CHARTER_W2_AFFORDABILITY.md`` §W2_8 and Ofgem,
*Self-disconnection and self-rationing: decision* (2020),
``ofgem.gov.uk/sites/default/files/docs/2020/10/self-disconnection_and_self-rationing_decision.pdf``.

- ANCHORED [named phenomenon + obligation]: self-disconnection/self-rationing is
  Ofgem's own decided licence-level policy area; suppliers must IDENTIFY such
  customers and offer emergency / friendly-hours / additional support credit. The
  failure-to-detect harm is real and enforced (Ofgem's OVO settlement). So a
  MISSED detection here is a genuine harm event, not a hypothetical.
- ANCHORED [prevalence, directional]: Ofgem's 2019 Consumer Survey found ~1 in 7
  (~14%) of the ~4 million UK PREPAYMENT-METER households had self-disconnected in
  the past 12 months. NOTE (R10): that figure is self-DISCONNECTION among PPM
  specifically; self-RATIONING (cutting usage to avoid topping up / to keep a DD
  affordable) is the BROADER behaviour and has no single clean published
  population rate. So ``_MAX_RATIONING_PROPENSITY`` is NOT a citation of a
  measured self-rationing rate — it is a CURRICULUM shape (R13, overridable) set
  so that among ACUTELY budget-stressed households (thin / negative margin) the
  onset incidence is order-of-magnitude consistent with the ~1-in-7 anchor, and
  ~0 for comfortable households. Tagged [L]; never tuned to company outcomes.
- ANCHORED [consumption floor]: the "plausible living level" floor is the Ofgem
  TDCV Low-band FLOOR (elec 1400 kWh/yr, gas 5500 kWh/yr), REUSED from
  ``domain_invariants.py`` (drift-guarded), not a second re-derived threshold.
- SIMPLIFICATION (R10): the margin->propensity ramp (``_COMFORT_RATIO``,
  ``_STRESS_RATIO``) and the severity band (``_SEVERITY_RANGE``) are documented
  curriculum shapes, overridable, not measured per-household figures.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from simulation.household_budget import HouseholdBudget, draw_household_budget

STREAM_NAMESPACE = "W2_8_self_rationing"

# Named RNG substreams — one per stochastic mechanism (C-S2). A future mechanism
# APPENDS a name here; it can never shift an existing substream's sequence.
_SUBSTREAMS: Tuple[str, ...] = ("onset", "severity")


# ---------------------------------------------------------------------------
# TDCV Low-band FLOOR — the "plausible living level" threshold (regulation
# commons). SOURCE OF TRUTH: company/compliance/domain_invariants.py::
# TDCV_{ELEC,GAS}_LOW.low. Duplicated here (wall discipline), drift-guarded in
# tests/sim/test_w2_8_self_rationing.py. Consumption BELOW this floor with a
# perfect payment record is the concrete self-rationing harm signature.
# ---------------------------------------------------------------------------
TDCV_LOW_FLOOR_KWH: dict[str, float] = {
    "electricity": 1400.0,  # TDCV_ELEC_LOW.low
    "gas": 5500.0,          # TDCV_GAS_LOW.low
}


# ---------------------------------------------------------------------------
# CURRICULUM (R13) margin->propensity ramp + severity band — documented shapes.
# ---------------------------------------------------------------------------
# Squeeze is expressed as discretionary margin as a FRACTION of the essential
# floor (slack per pound of essentials). A household with margin >= COMFORT_RATIO
# of its floor is comfortable (no budget-driven rationing); at/below STRESS_RATIO
# (a negative margin) it is at maximum propensity. Linear ramp between.
_COMFORT_RATIO = 0.50   # margin >= 50% of essentials -> comfortable, propensity 0
_STRESS_RATIO = 0.0     # margin <= 0 (essentials exceed income) -> max propensity
_MAX_RATIONING_PROPENSITY = 0.45  # onset probability at maximum squeeze (R10/[L])

# Severity = fraction by which a self-rationer cuts consumption below its healthy
# baseline. Drawn within this band, then DEEPENED by the squeeze (a more negative
# margin rations harder). Set deep enough that an acutely-stressed household
# starting near a normal band typically falls BELOW the TDCV Low floor.
_SEVERITY_RANGE: Tuple[float, float] = (0.30, 0.55)
_SEVERITY_SQUEEZE_BONUS = 0.20  # extra cut at maximum squeeze, on top of the band


class RationingLabel(str, Enum):
    """The HIDDEN true label — the answer key the C10 twin must recover."""
    NOT_RATIONING = "not_rationing"      # normal need OR genuinely-low need
    SELF_RATIONING = "self_rationing"    # cutting heat/energy under budget stress


def _substream(base_seed: int, name: str) -> random.Random:
    """Return an ISOLATED ``random.Random`` for a named mechanism substream.

    Seed is a STABLE sha256 of ``W2_8_self_rationing::<name>::<base_seed>`` (never
    Python's per-process-salted ``hash()``), so the same (base_seed, name) yields
    the same stream across processes (C-S2 replay). Each name seeds an independent
    generator, so a draw here can never consume from, or shift, any other
    substream — of this module or of any sibling subsystem.
    """
    key = f"{STREAM_NAMESPACE}::{name}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _base_seed_for(customer_id: str, seed: Optional[int]) -> int:
    """Resolve the base seed. Stable md5 of the customer_id when no explicit seed
    is given (builtin ``hash()`` is per-process salted and would break replay)."""
    if seed is not None:
        return seed
    return int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)


def rationing_propensity(margin_monthly: float, floor_monthly: float) -> float:
    """The rationing onset PROPENSITY as a pure function of the W2_4 budget.

    This is the coupling to ``W2_4_household_budget``: self-rationing ARISES FROM
    a squeezed budget, it is not an independent draw. Returns a probability in
    ``[0, _MAX_RATIONING_PROPENSITY]``. Comfortable households (margin a healthy
    fraction of essentials) return 0.0; a structurally-negative household (income
    below essentials) returns the maximum. Deterministic — no RNG here.
    """
    if floor_monthly <= 0.0:
        return 0.0
    ratio = margin_monthly / floor_monthly
    if ratio >= _COMFORT_RATIO:
        return 0.0
    frac = (_COMFORT_RATIO - ratio) / (_COMFORT_RATIO - _STRESS_RATIO)
    frac = min(1.0, max(0.0, frac))
    return round(frac * _MAX_RATIONING_PROPENSITY, 6)


@dataclass(frozen=True)
class SelfRationingState:
    """A household's hidden self-rationing truth for a consumption period.

    Splits cleanly into OBSERVABLE fields (what a real supplier sees: the meter
    reads ``healthy_annual_kwh`` [prior baseline] and ``observed_annual_kwh``
    [current], ``missed_payments``, and the public ``floor_kwh``) and the ANSWER
    KEY (``is_self_rationing``, ``rationing_severity``, ``discretionary_margin_
    monthly`` — the hidden budget). The company NEVER reads the answer key.
    """
    customer_id: str
    commodity: str                       # "electricity" | "gas"
    # -- OBSERVABLE (meter reads over time + public TDCV floor) --------------
    healthy_annual_kwh: float            # the household's normal/prior baseline
    observed_annual_kwh: float           # current consumption (rationed if state)
    floor_kwh: float                     # public TDCV Low-band floor
    missed_payments: int                 # ALWAYS 0 for self-rationers (silent!)
    # -- ANSWER KEY (harness only; the company must NOT read these) ----------
    label: RationingLabel
    rationing_severity: float            # 0.0 if not rationing
    discretionary_margin_monthly: float  # from W2_4 (may be < 0)
    data_regime: str = "synthetic"

    # -- OBSERVABLE derived signals (what the detector may condition on) -----
    @property
    def is_below_floor(self) -> bool:
        """Consumption is below the plausible-living TDCV Low floor. OBSERVABLE
        (the company sees the meter read and knows the public TDCV floor)."""
        return self.observed_annual_kwh < self.floor_kwh

    @property
    def observed_drop_fraction(self) -> float:
        """Fractional drop from the household's OWN baseline. OBSERVABLE (two
        meter reads over time) — the primary detection signal, since it separates
        a self-rationer (a real drop) from a genuinely-low-need home (no drop)."""
        if self.healthy_annual_kwh <= 0.0:
            return 0.0
        return round(1.0 - self.observed_annual_kwh / self.healthy_annual_kwh, 4)

    # -- ANSWER KEY ---------------------------------------------------------
    @property
    def is_self_rationing(self) -> bool:
        """The HIDDEN true state (answer key). NOT the same as ``is_below_floor``
        — a genuinely-low-need home is below floor but is NOT self-rationing."""
        return self.label == RationingLabel.SELF_RATIONING

    @property
    def is_silent_hardship(self) -> bool:
        """The defining hard case: genuinely self-rationing AND below the floor
        AND a PERFECT payment record — the harm the arrears channel cannot see."""
        return self.is_self_rationing and self.is_below_floor and self.missed_payments == 0


def generate_self_rationing_state(
    customer_id: str,
    healthy_annual_kwh: float,
    commodity: str = "electricity",
    budget: Optional[HouseholdBudget] = None,
    seed: Optional[int] = None,
    floor_kwh: Optional[float] = None,
) -> SelfRationingState:
    """Generate one household's hidden self-rationing state for a period.

    Coupled to ``W2_4_household_budget``: if ``budget`` is not supplied it is
    drawn via ``draw_household_budget(customer_id, seed)`` — the SAME hidden
    budget that drives arrears — so self-rationing and arrears share ONE budget
    truth (a household that rations is choosing that OVER falling into arrears).
    The onset PROPENSITY is the pure function ``rationing_propensity`` of that
    budget's margin; only the onset Bernoulli and the severity magnitude are
    stochastic, each from this module's own named substream (C-S2).

    Deterministic in ``(customer_id, seed, healthy_annual_kwh, commodity)``.

    A household with a comfortable margin returns ``NOT_RATIONING`` with
    ``observed == healthy`` (no drop) — including the confound case where its
    ``healthy_annual_kwh`` is itself already below the floor (a genuinely-low-need
    home): below floor, but no drop and not rationing.
    """
    if commodity not in TDCV_LOW_FLOOR_KWH:
        raise ValueError(
            f"commodity {commodity!r} not one of {tuple(TDCV_LOW_FLOOR_KWH)}"
        )
    base_seed = _base_seed_for(customer_id, seed)
    if budget is None:
        budget = draw_household_budget(customer_id, base_seed=seed)
    floor = floor_kwh if floor_kwh is not None else TDCV_LOW_FLOOR_KWH[commodity]

    margin = budget.discretionary_margin_monthly
    prop = rationing_propensity(margin, budget.essential_cost_floor_monthly)

    # -- onset (own substream): Bernoulli against the budget-derived propensity.
    onset = _substream(base_seed, "onset").random() < prop

    if not onset:
        return SelfRationingState(
            customer_id=customer_id,
            commodity=commodity,
            healthy_annual_kwh=round(healthy_annual_kwh, 1),
            observed_annual_kwh=round(healthy_annual_kwh, 1),  # no drop
            floor_kwh=floor,
            missed_payments=0,
            label=RationingLabel.NOT_RATIONING,
            rationing_severity=0.0,
            discretionary_margin_monthly=margin,
        )

    # -- severity (own substream): band draw, DEEPENED by the squeeze. A more
    # negative margin rations harder (squeeze_frac in [0, 1], 1 at max stress).
    prop_max = _MAX_RATIONING_PROPENSITY or 1.0
    squeeze_frac = min(1.0, prop / prop_max)
    r_sev = _substream(base_seed, "severity")
    severity = r_sev.uniform(*_SEVERITY_RANGE) + _SEVERITY_SQUEEZE_BONUS * squeeze_frac
    severity = round(min(0.90, severity), 4)  # never cut below ~10% of baseline

    observed = round(healthy_annual_kwh * (1.0 - severity), 1)

    return SelfRationingState(
        customer_id=customer_id,
        commodity=commodity,
        healthy_annual_kwh=round(healthy_annual_kwh, 1),
        observed_annual_kwh=observed,
        floor_kwh=floor,
        missed_payments=0,  # the SILENT channel — self-rationers keep paying.
        label=RationingLabel.SELF_RATIONING,
        rationing_severity=severity,
        discretionary_margin_monthly=margin,
    )
