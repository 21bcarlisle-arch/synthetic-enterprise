"""W2_7_willingness_classification -- hidden ABILITY x WILLINGNESS 2x2 (world-side).

WHAT THIS IS
------------
The WORLD-side HIDDEN 2x2 answer key for the can't-pay / won't-pay archetype -- the
COUPLED_TRIAD design's HIGHEST-PRIORITY archetype pair. Each (arrears-eligible)
customer carries a hidden state on two orthogonal axes:

  ABILITY     -- CAN_PAY  vs CANNOT_PAY   (structural: can the household afford it?)
  WILLINGNESS -- WILL_PAY vs WONT_PAY     (attitudinal: does it CHOOSE to pay?)

The four cells (the whole point -- one identical observable, four different truths):

  CAN_WILL     -- pays. Not in arrears.
  CAN_WONT     -- the STRATEGIC non-payer (the "won't-pay"): could pay, chooses not to.
  CANNOT_WILL  -- the "can't-pay": wants to pay, genuinely cannot afford it.
  CANNOT_WONT  -- both: cannot afford it AND would not pay even if able.

Three of the four cells emit the SAME observable -- the customer is in arrears /
missing payments. A real collections team (and the company-side twin
``C9_cantpay_wontpay_classifier``) must CLASSIFY the hidden quadrant through the
wall from payment behaviour, engagement and disclosure -- and is ALLOWED to be
wrong. The GAP between that classification and this answer key is the coupled-triad
score. Getting it wrong is lethal BOTH ways (R13 curriculum, C9/A6): treating a
genuine can't-pay as a won't-pay is a Consumer-Duty / ability-to-pay breach and a
vulnerability harm (the 8:1-weighted expensive error on the ABILITY axis); treating
a won't-pay as a can't-pay is bad debt + moral hazard.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
-----------------------------------------------------
WORLD/sim code. It MUST NOT import ``company.*`` or ``saas.*``. It never reaches
across the seam. ``ability`` / ``willingness`` / ``quadrant`` are the ANSWER KEY
(harness only, via tools/couple_w2_7_c9.py once C9 exists); ``is_in_arrears`` is
the single sanctioned OBSERVABLE (identical for the three non-paying cells -- that
IS the confound). Every record carries ``data_regime="synthetic"``.

ABILITY COUPLES TO W2_4 (non-negotiable -- the two atoms must be consistent)
---------------------------------------------------------------------------
Genuine cannot-pay is NOT an independent draw. It is derived from the SAME hidden
household budget W2_4 generates: a customer whose W2_4 discretionary margin is
structurally negative (or, with the overridable near-zero threshold, thin enough
to be below a minimum-payment buffer) genuinely CANNOT pay. So this module draws
(or is handed) the customer's ``HouseholdBudget`` and reads ABILITY off its
``discretionary_margin_monthly`` arithmetically -- never a second, inconsistent
random ability draw. Drawn with the SAME base_seed derivation W2_4 uses, so the
budget here is byte-identical to a standalone ``draw_household_budget(customer_id)``
for that customer (proven in the tests).

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md -- non-negotiable; the 01:09Z incident)
--------------------------------------------------------------------------------
WILLINGNESS is the ONE genuinely new stochastic element here (ABILITY is not
stochastic at all -- it is arithmetic off the coupled budget). It is drawn from
THIS subsystem's OWN named, seeded substream ``W2_7_willingness::willingness::
<base_seed>`` -- an isolated ``random.Random`` seeded from a STABLE sha256 (never
Python's per-process-salted ``hash()``), so the same (customer_id, seed) yields
the same willingness across processes (deterministic replay), and advancing it can
NEVER shift any sibling subsystem's sequence -- population_draw, life_events,
household_budget and sme_distress stay byte-identical no matter how far this stream
is drawn. A future stochastic attribute is added by APPENDING a name to
``_SUBSTREAMS``, never by threading a draw into an existing stream. Proven by
``tests/sim/test_w2_7_willingness_classification.py``.

WON'T-PAY PREVALENCE -- BASELINE vs CURRICULUM (R13, dated 2026-07-13)
---------------------------------------------------------------------
The willingness incidence is a DIRECTOR-CURRICULUM DIAGNOSTIC (R13/R12/Law A),
never tuned toward a gap number. Its provenance, honestly:

- A precise, quotable UK "genuine won't-pay incidence" percentage was NOT found
  after TWO independent targeted searches (recorded un-anchorable, not merely
  unsearched -- docs/market_research/willingness_classification_incidence.md).
- What IS anchored [L] is the DIRECTION: real UK fuel-poverty advocacy and
  regulatory framing both hold that the WON'T-PAY quadrant is a comparative
  MINORITY -- the End Fuel Poverty Coalition's explicit position is "it's a
  can't-pay crisis, not a won't-pay one", and Ofgem's interim CEO was publicly
  criticised (Utility Week, 2026) for a "reductive" can't-pay/won't-pay framing.
- Therefore ``_WONT_PAY_INCIDENCE`` is set DELIBERATELY LOW (a minority trait) as
  an explicit director-set curriculum PLACEHOLDER (R13), pending a director-signed
  figure -- NOT a naive 50/50 or an inflated won't-pay rate, which would
  misrepresent the real population in exactly the way the real regulator is being
  challenged on. It is overridable and must never be adjusted because company P&L
  or the measured gap looked wrong.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional, Tuple

from simulation.household_budget import HouseholdBudget, draw_household_budget

STREAM_NAMESPACE = "W2_7_willingness"

# Named RNG substreams -- one per stochastic mechanism (C-S2). ABILITY is NOT
# here: it is a deterministic arithmetic consequence of the coupled W2_4 budget,
# not a draw. A future stochastic attribute APPENDS a name; it can never shift an
# existing substream's sequence.
_SUBSTREAMS: Tuple[str, ...] = ("willingness",)

# CURRICULUM (R13, un-anchorable by search -- R10) director-set PLACEHOLDER: the
# incidence of the strategic-non-payer WILLINGNESS trait (won't-pay DESPITE
# ability). Deliberately a MINORITY, per the can't-pay-dominant advocacy/regulatory
# framing above. Pending a director-signed figure; NEVER tuned toward the gap.
_WONT_PAY_INCIDENCE = 0.10

# The ABILITY threshold on W2_4's monthly discretionary margin. At 0.0, ABILITY is
# CANNOT_PAY exactly when the household is structurally negative (essentials exceed
# income) -- the purest coupling to W2_4. Raise it to a small positive buffer to
# also treat a NEAR-ZERO margin (too thin to cover a minimum energy payment) as
# cannot-pay -- an overridable R10 refinement, not a fabricated figure.
_CANNOT_PAY_MARGIN_THRESHOLD_MONTHLY = 0.0


# ---------------------------------------------------------------------------
# Substream construction -- the C-S2 heart of this module (matches W2_4/W2_6).
# ---------------------------------------------------------------------------
def _substream(base_seed: int, name: str) -> random.Random:
    """Return an ISOLATED ``random.Random`` for a named mechanism substream.

    Seed is a STABLE sha256 of ``W2_7_willingness::<name>::<base_seed>`` (never
    Python's per-process-salted ``hash()``), so the same (base_seed, name) yields
    the same stream across processes (C-S2 deterministic replay). Each name seeds
    an independent generator, so a draw here can never consume from, or shift, any
    other substream -- of this or any other subsystem.
    """
    key = f"{STREAM_NAMESPACE}::{name}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _base_seed_for(customer_id: str, seed: Optional[int]) -> int:
    """Resolve the base seed for a customer's willingness/ability draw.

    Uses a STABLE md5 of the customer_id when no explicit seed is given -- the
    IDENTICAL derivation ``household_budget._base_seed_for`` uses, so passing this
    base_seed to ``draw_household_budget`` reproduces that customer's standalone
    W2_4 budget byte-for-byte (the coupling-consistency guarantee). The built-in
    ``hash()`` is salted per process and would break C-S2 replay.
    """
    if seed is not None:
        return seed
    return int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)


# ---------------------------------------------------------------------------
# Domain enums -- the two hidden axes and the 2x2 quadrant they define.
# ---------------------------------------------------------------------------
class Ability(str, Enum):
    """Hidden ABILITY axis -- can the household actually afford to pay?"""
    CAN_PAY = "can_pay"
    CANNOT_PAY = "cannot_pay"


class Willingness(str, Enum):
    """Hidden WILLINGNESS axis -- an attitudinal trait, independent of ability."""
    WILL_PAY = "will_pay"
    WONT_PAY = "wont_pay"


class Quadrant(str, Enum):
    """The hidden 2x2 -- the answer key the company (C9) must classify blind."""
    CAN_WILL = "can_will"        # pays
    CAN_WONT = "can_wont"        # STRATEGIC non-payer (the won't-pay)
    CANNOT_WILL = "cannot_will"  # the can't-pay (wants to, can't afford it)
    CANNOT_WONT = "cannot_wont"  # both


def quadrant_of(ability: Ability, willingness: Willingness) -> Quadrant:
    """Map the two hidden axes onto the 2x2 quadrant (total, exhaustive)."""
    if ability == Ability.CAN_PAY:
        return Quadrant.CAN_WILL if willingness == Willingness.WILL_PAY else Quadrant.CAN_WONT
    return Quadrant.CANNOT_WILL if willingness == Willingness.WILL_PAY else Quadrant.CANNOT_WONT


@dataclass(frozen=True)
class WillingnessProfile:
    """A customer's full hidden ability x willingness truth (SIM ground truth).

    ``ability`` / ``willingness`` / ``quadrant`` are the ANSWER KEY -- harness
    only, NEVER read by the company. ``is_in_arrears`` is the single sanctioned
    OBSERVABLE (identical across the three non-paying cells -- THE confound the
    company must resolve). ``discretionary_margin_monthly`` is carried through
    from the coupled W2_4 budget so the ability derivation is fully auditable
    (harness/answer-key context, not a company-readable field).
    """
    customer_id: str
    ability: Ability
    willingness: Willingness
    discretionary_margin_monthly: float
    data_regime: str = "synthetic"

    # -- ANSWER KEY (harness only) -------------------------------------------
    @property
    def quadrant(self) -> Quadrant:
        return quadrant_of(self.ability, self.willingness)

    @property
    def is_strategic_nonpayer(self) -> bool:
        """CAN_WONT -- could pay, chooses not to (the pure won't-pay)."""
        return self.quadrant == Quadrant.CAN_WONT

    @property
    def is_genuine_cantpay(self) -> bool:
        """Cannot afford it (either willingness) -- the ability-constrained cases
        where wrongful enforcement is a Consumer-Duty breach + vulnerability harm."""
        return self.ability == Ability.CANNOT_PAY

    # -- OBSERVABLE (what a real supplier could see) -------------------------
    def is_in_arrears(self) -> bool:
        """The single OBSERVABLE: is this customer failing to pay?

        A customer pays iff they BOTH can and will; any other cell misses. This
        is IDENTICAL for CAN_WONT, CANNOT_WILL and CANNOT_WONT -- the company sees
        a missed payment and must classify the hidden cause, never reading it.
        """
        return not (self.ability == Ability.CAN_PAY and self.willingness == Willingness.WILL_PAY)


def ability_from_budget(
    budget: HouseholdBudget,
    cannot_pay_margin_threshold: float = _CANNOT_PAY_MARGIN_THRESHOLD_MONTHLY,
) -> Ability:
    """Derive the hidden ABILITY axis ARITHMETICALLY from the W2_4 budget.

    CANNOT_PAY exactly when the household's discretionary margin is at/below the
    threshold (structurally negative at the default 0.0; a thin near-zero margin
    if the threshold is raised). No independent random ability draw -- so W2_4 and
    W2_7 can never disagree about who can afford to pay.
    """
    return (
        Ability.CANNOT_PAY
        if budget.discretionary_margin_monthly <= cannot_pay_margin_threshold
        else Ability.CAN_PAY
    )


def draw_willingness_profile(
    customer_id: str,
    base_seed: Optional[int] = None,
    wont_pay_incidence: float = _WONT_PAY_INCIDENCE,
    cannot_pay_margin_threshold: float = _CANNOT_PAY_MARGIN_THRESHOLD_MONTHLY,
    household_budget: Optional[HouseholdBudget] = None,
    composition_weights: Optional[Mapping[str, float]] = None,
) -> WillingnessProfile:
    """Draw one customer's hidden ability x willingness truth deterministically.

    Deterministic in (customer_id, base_seed) (C-S2): same inputs -> byte-identical
    profile, every run, across processes.

    ABILITY is derived arithmetically from the coupled W2_4 household budget (drawn
    here with the SAME base_seed derivation W2_4 uses, unless one is supplied), so
    the two atoms are consistent. WILLINGNESS is the only stochastic element, drawn
    from this subsystem's own named ``willingness`` substream -- isolated from every
    sibling subsystem's RNG.
    """
    seed = _base_seed_for(customer_id, base_seed)

    # -- ABILITY: arithmetic off the coupled W2_4 budget (NOT a random draw) --
    budget = household_budget or draw_household_budget(
        customer_id, base_seed=seed, composition_weights=composition_weights
    )
    ability = ability_from_budget(budget, cannot_pay_margin_threshold)

    # -- WILLINGNESS: the one new stochastic trait, own named substream (C-S2) --
    r_will = _substream(seed, "willingness")
    willingness = (
        Willingness.WONT_PAY if r_will.random() < wont_pay_incidence else Willingness.WILL_PAY
    )

    return WillingnessProfile(
        customer_id=customer_id,
        ability=ability,
        willingness=willingness,
        discretionary_margin_monthly=budget.discretionary_margin_monthly,
    )
