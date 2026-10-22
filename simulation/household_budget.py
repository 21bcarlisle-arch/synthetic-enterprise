"""W2_4_household_budget — per-household HIDDEN budget state (world-side SIM truth).

WHAT THIS IS
------------
A per-household hidden financial-budget sketch: an income band, an essential-cost
floor, the resulting discretionary margin, a savings buffer, and a
priority-of-debts stack (which bills get serviced first when money is short).

This is HIDDEN SIM GROUND TRUTH. The company layer can NEVER read it. In a real
UK energy supplier the company does not know a customer's income, savings, or
household budget; it INFERS affordability from OBSERVABLES only — missed
payments, broken repayment plans, arrears, consumption patterns, and what the
customer discloses. The company-side twin that recovers this through the wall is
`C6_affordability_inference`; it never reads this module. The GAP between that
inference and this truth is the coupled-triad score.

The decisive finding this atom exists to fix (adjudicated `coldwalk:
bad_debt_implausibly_low_through_2021_22_crisis`): arrears were being generated
as a customer *propensity*. In reality arrears are the OUTPUT of a household
budget meeting a price shock — a thin or already-negative discretionary margin
crossing zero when the unit rate rises. This module is that hidden budget, so a
crisis-era bad-debt step-up can EMERGE from income-minus-essentials arithmetic
rather than be coded as a probability (R12/Law A: never tune these distributions
toward a bad-debt target).

WALL DISCIPLINE (record verbatim, .claude/rules/epistemic-wall-sim.md)
----------------------------------------------------------------------
WORLD/sim code. MUST NOT import `company.*` or `saas.*`. It exposes no crossing
point; the only sanctioned SIM->company seam is
`company/interfaces/sim_interface.py`, which this module never calls and which
must never surface any field defined here. Every record carries
`data_regime="synthetic"` (this is a curriculum draw, not real history).

RNG SUBSTREAM DISCIPLINE (C-S2, CLAUDE.md — non-negotiable, the 01:09Z incident)
-------------------------------------------------------------------------------
Every budget attribute draws from this subsystem's OWN named substream
(`_substream(base_seed, salt)` derives an isolated `random.Random` from a STABLE
sha256 of the stream name + salt + base seed). Each attribute has its OWN named
salt ("income", "composition", "housing", "savings", "debts"), so introducing a
new attribute is done by APPENDING a salt, never by threading a new draw through
an existing stream — a new draw here can NEVER shift the sequence any other
attribute, or any sibling subsystem (population_draw / life_events), produces.
Proven by `tests/sim/test_w2_4_household_budget.py`. Seeds derive from a stable
sha256/md5 (never Python's per-process-salted `hash()`), so replay is
deterministic across processes (C-S2 deterministic replay).

BASELINE vs CURRICULUM (R13)
---------------------------
These distributions are the DIRECTOR'S curriculum instrument. They are
DIAGNOSTICS, never targets (R12/Law A): a difficulty change is a named,
versioned, director-authored edit of these constants, never an agent-side
adjustment made because company P&L looked wrong.

HONEST SIMPLIFICATIONS (R10, dated 2026-07-13)
----------------------------------------------
- INCOME LADDER: the ONLY externally-cited anchors are (a) the ~£3,225/month
  median household disposable income and (b) the structural fact that the bottom
  quintile's essential expenditure EXCEEDS income (a genuinely NEGATIVE margin),
  both from `docs/market_research/household_budget_w2_4.md`. The full per-decile
  ladder below is a documented SHAPE that REPRODUCES both anchors (median at the
  D5/D6 boundary; bottom deciles able to go negative once the floor is applied);
  it is NOT a fabricated citation of an ONS/HMRC decile table. The charter
  (`docs/design/CHARTER_W2_AFFORDABILITY.md`) flags resolving the HMRC-taxpayer
  vs ONS-equivalised-household unit-of-measure before wiring a real ladder — that
  is an open DISCOVER item, not silently assumed here. Overridable via argument.
- ESSENTIAL FLOOR: the core (ex-housing) essentials figure is anchored to the
  JRF/Trussell "Essentials Guarantee" (single £120/week, couple £205/week, from
  the research doc). Children and housing are R10: the children add-on and the
  housing-cost draw are documented SHAPES, not cited figures (UK housing cost
  varies enormously by tenure/region, which this model does not track). This is
  why the floor is composition-aware but housing is a broad draw.
- SAVINGS BUFFER: the low-income (≈<£15k/yr) and high-income (≈>£50k/yr) bucket
  weights are anchored to FCA Financial Lives (22% zero / >1/3 under £1k for the
  low band; majority over £10k for the high band; ~10% zero / ~21% under £1k
  population-wide). The MIDDLE-decile weights are interpolated (R10) between
  those cited endpoints.
- PRIORITY-OF-DEBTS ORDER: the PRIORITY-vs-NON-PRIORITY split is directly
  sourced (StepChange / MoneyHelper / Citizens Advice consequence-severity
  taxonomy — energy sits INSIDE the priority tier because of disconnection risk,
  NOT below rent/council-tax/food as the atom's original registration text said;
  and "food" is essential SPENDING competing for the discretionary pool, not a
  debt-stack entry, since there is no creditor relationship for future food).
  The SECONDARY ordering WITHIN the priority tier (rent vs energy vs council tax
  when all three are simultaneously in arrears) is an explicit R10 open item —
  the research found the split clearly but no strict within-tier ranking. The
  default within-tier order below is a documented default, overridable.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, replace
from enum import Enum
from typing import Dict, Mapping, Optional, Sequence, Tuple

from simulation.rng_substream import substream

STREAM_NAME = "W2_4_household_budget"

# Named substream salts — one per drawn attribute (C-S2). A new attribute is
# added by APPENDING a salt here, never by inserting a draw into an existing one.
_SALTS: Tuple[str, ...] = ("income", "composition", "housing", "savings", "debts")


# ---------------------------------------------------------------------------
# Substream construction — the C-S2 heart of this module.
# ---------------------------------------------------------------------------
def _substream(base_seed: int, salt: str = "") -> random.Random:
    """Return an ISOLATED `random.Random` seeded from a STABLE sha256 of
    (`STREAM_NAME`::`salt`::`base_seed`).

    Isolation is structural: an independent `random.Random` whose seed is a pure
    function of (name, salt, base_seed). It shares no state with the global
    `random` module, with any other salt in this module, or with any other
    subsystem's substream — so a draw here can never shift another sequence.
    Stable digest (not Python's per-process-salted `hash()`) => deterministic
    replay across processes (C-S2).
    """
    return substream(STREAM_NAME, salt, base_seed)


def _base_seed_for(customer_id: str, seed: Optional[int]) -> int:
    """Resolve the base seed for a customer's budget draw.

    Stable md5 of the customer_id when no explicit seed is given (the built-in
    `hash()` is per-process-salted and would break C-S2 replay).
    """
    if seed is not None:
        return seed
    return int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)


def _weighted_choice(rng: random.Random, weights: Mapping[str, float]) -> str:
    """Deterministic weighted categorical draw from an isolated Random."""
    keys = list(weights.keys())
    cum = []
    running = 0.0
    for k in keys:
        running += weights[k]
        cum.append(running)
    x = rng.random() * running
    for k, threshold in zip(keys, cum):
        if x <= threshold:
            return k
    return keys[-1]


# ---------------------------------------------------------------------------
# INCOME LADDER (R10 shape; anchors: median £3,225/mo, negative bottom margin)
# ---------------------------------------------------------------------------
# Monthly household disposable income by decile. Deciles are equal-population by
# construction, so a population draw is UNIFORM over 1..10. The D5/D6 boundary
# (~£3,225) reproduces the cited median; the bottom deciles are low enough that,
# once the essential floor is subtracted, discretionary margin CAN go negative,
# reproducing the cited "bottom quintile essentials exceed income" structure.
MONTHLY_DISPOSABLE_INCOME_BY_DECILE: Dict[int, float] = {
    1: 1_150.0,
    2: 1_700.0,
    3: 2_150.0,
    4: 2_600.0,
    5: 3_050.0,
    6: 3_400.0,
    7: 3_900.0,
    8: 4_600.0,
    9: 5_700.0,
    10: 8_500.0,
}

# Income-tier boundaries (annualised disposable, monthly*12) used to key the
# savings-buffer joint distribution to the FCA-cited <£15k and >£50k bands.
_LOW_INCOME_ANNUAL = 15_000.0
_HIGH_INCOME_ANNUAL = 50_000.0


# ---------------------------------------------------------------------------
# HOUSEHOLD COMPOSITION + ESSENTIAL-COST FLOOR
# ---------------------------------------------------------------------------
class Composition(str, Enum):
    SINGLE = "single"
    COUPLE = "couple"
    SINGLE_PARENT = "single_parent"
    COUPLE_PARENT = "couple_parent"


# Composition marginal (R10 shape; ~30% single-person is the one directional
# anchor from general UK household-composition knowledge, overridable).
DEFAULT_COMPOSITION_WEIGHTS: Dict[str, float] = {
    Composition.SINGLE.value: 0.30,
    Composition.COUPLE.value: 0.45,
    Composition.SINGLE_PARENT.value: 0.10,
    Composition.COUPLE_PARENT.value: 0.15,
}

# Core (EX-HOUSING) essential spend per month, anchored to the JRF/Trussell
# "Essentials Guarantee": single £120/week => £520/mo; couple £205/week => £888/mo.
# (£/week * 52 / 12.) The per-child add-on is R10 (documented shape, not cited).
_ESSENTIALS_GUARANTEE_SINGLE = round(120.0 * 52 / 12, 2)   # 520.00
_ESSENTIALS_GUARANTEE_COUPLE = round(205.0 * 52 / 12, 2)   # 888.33
_CHILD_ESSENTIALS_ADDON = 180.0  # R10: children essentials, documented shape only

_CORE_ESSENTIALS_BY_COMPOSITION: Dict[str, float] = {
    Composition.SINGLE.value: _ESSENTIALS_GUARANTEE_SINGLE,
    Composition.COUPLE.value: _ESSENTIALS_GUARANTEE_COUPLE,
    Composition.SINGLE_PARENT.value: _ESSENTIALS_GUARANTEE_SINGLE + _CHILD_ESSENTIALS_ADDON,
    Composition.COUPLE_PARENT.value: _ESSENTIALS_GUARANTEE_COUPLE + _CHILD_ESSENTIALS_ADDON,
}

# Housing cost draw (R10): UK monthly housing cost varies enormously by tenure/
# region, neither of which this model tracks. Drawn uniform over a broad plausible
# monthly range. Documented shape, overridable — NOT a cited figure.
_HOUSING_COST_RANGE = (400.0, 1_100.0)


# ---------------------------------------------------------------------------
# SAVINGS BUFFER — FCA-anchored joint distribution (income band x buffer)
# ---------------------------------------------------------------------------
# Bucket weights per income tier. LOW and HIGH endpoints are FCA-anchored; the
# MID tier is interpolated (R10). Buckets: zero / under_1k / 1k_10k / over_10k.
_SAVINGS_BUCKET_WEIGHTS: Dict[str, Dict[str, float]] = {
    # <£15k/yr: FCA — 22% no savings; >1/3 under £1k.
    "low": {"zero": 0.22, "under_1k": 0.33, "1k_10k": 0.35, "over_10k": 0.10},
    # mid deciles: interpolated to the ~10% zero / ~21% under-£1k population figure.
    "mid": {"zero": 0.10, "under_1k": 0.21, "1k_10k": 0.44, "over_10k": 0.25},
    # >£50k/yr: FCA — few lack savings; majority hold >£10k.
    "high": {"zero": 0.03, "under_1k": 0.07, "1k_10k": 0.35, "over_10k": 0.55},
}

_SAVINGS_BUCKET_BOUNDS: Dict[str, Tuple[float, float]] = {
    "zero": (0.0, 0.0),
    "under_1k": (0.0, 1_000.0),
    "1k_10k": (1_000.0, 10_000.0),
    "over_10k": (10_000.0, 40_000.0),  # R10 upper bound
}


def _income_tier(annual_disposable: float) -> str:
    if annual_disposable < _LOW_INCOME_ANNUAL:
        return "low"
    if annual_disposable >= _HIGH_INCOME_ANNUAL:
        return "high"
    return "mid"


# ---------------------------------------------------------------------------
# PRIORITY-OF-DEBTS STACK (consequence-severity; sourced split, R10 within-tier)
# ---------------------------------------------------------------------------
# PRIORITY tier — non-payment carries the most severe consequence (eviction,
# repossession, loss of essential supply, imprisonment for fines). Energy sits
# INSIDE this tier because of disconnection risk (StepChange/MoneyHelper/Citizens
# Advice), NOT below rent/council-tax as the atom's original text said. The order
# WITHIN this tuple is a documented DEFAULT (R10): the real debt-advice framework
# is a consequence-severity ranking, not a strict total order, and no within-tier
# ranking was found in the sources — overridable.
PRIORITY_DEBTS: Tuple[str, ...] = (
    "rent_mortgage_arrears",
    "council_tax_arrears",
    "court_fines",
    "child_maintenance_arrears",
    "energy_arrears",
    "tv_licence_arrears",
)

# NON-PRIORITY tier — lower-consequence unsecured credit, serviced only once
# priority debts are under control (StepChange/MoneyHelper). NOTE: "food" is NOT
# here — it is essential SPENDING inside the floor, not a debt (no creditor for
# future purchases).
NON_PRIORITY_DEBTS: Tuple[str, ...] = (
    "credit_card",
    "personal_loan",
    "overdraft",
    "catalogue_bnpl",
)

DEFAULT_DEBT_PRIORITY_ORDER: Tuple[str, ...] = PRIORITY_DEBTS + NON_PRIORITY_DEBTS


@dataclass(frozen=True)
class HouseholdBudget:
    """Hidden per-household budget state (world-side ground truth).

    The company NEVER reads this. `discretionary_margin_monthly` may be NEGATIVE
    (income below essentials) — that is the whole point of the finding this atom
    fixes, and it is an arithmetic consequence of income minus the floor, never a
    coded probability.
    """
    customer_id: str
    income_decile: int                    # 1 (lowest) .. 10 (highest)
    monthly_disposable_income: float
    composition: str                      # Composition value
    essential_cost_floor_monthly: float   # core essentials + housing
    discretionary_margin_monthly: float   # income - floor (may be < 0)
    savings_buffer: float                 # accessible cash savings, £
    debt_priority_order: Tuple[str, ...] = DEFAULT_DEBT_PRIORITY_ORDER
    data_regime: str = "synthetic"
    housing_cost_monthly: float = 0.0     # the housing part of the floor, kept for `margin_in_year`

    @property
    def annual_disposable_income(self) -> float:
        return self.monthly_disposable_income * 12.0

    @property
    def is_structurally_negative(self) -> bool:
        """True if essentials exceed income BEFORE any price shock is applied."""
        return self.discretionary_margin_monthly < 0.0


def draw_household_budget(
    customer_id: str,
    base_seed: Optional[int] = None,
    composition_weights: Optional[Mapping[str, float]] = None,
    income_ladder: Optional[Mapping[int, float]] = None,
    housing_cost_range: Tuple[float, float] = _HOUSING_COST_RANGE,
) -> HouseholdBudget:
    """Draw one household's hidden budget deterministically.

    Deterministic in (customer_id, base_seed): same inputs -> byte-identical
    budget, every run, across processes (C-S2). Each attribute is drawn from its
    OWN named substream salt, so the attributes are mutually isolated and a future
    attribute can be appended without shifting any existing draw.
    """
    seed = _base_seed_for(customer_id, base_seed)
    ladder = income_ladder or MONTHLY_DISPOSABLE_INCOME_BY_DECILE
    comp_weights = composition_weights or DEFAULT_COMPOSITION_WEIGHTS

    # -- income (own substream) -- uniform decile draw, interpolate within band.
    decile, income = _income_draw(_substream(seed, "income"), ladder)

    # -- composition (own substream) --
    r_comp = _substream(seed, "composition")
    composition = _weighted_choice(r_comp, comp_weights)

    # -- essential-cost floor: core essentials (composition) + housing (own sub) --
    core = _CORE_ESSENTIALS_BY_COMPOSITION[composition]
    r_house = _substream(seed, "housing")
    housing = round(r_house.uniform(*housing_cost_range), 2)
    floor = round(core + housing, 2)

    margin = round(income - floor, 2)

    # -- savings buffer (own substream), joint on income tier --
    r_sav = _substream(seed, "savings")
    tier = _income_tier(income * 12.0)
    bucket = _weighted_choice(r_sav, _SAVINGS_BUCKET_WEIGHTS[tier])
    b_low, b_high = _SAVINGS_BUCKET_BOUNDS[bucket]
    savings = 0.0 if b_high == 0.0 else round(r_sav.uniform(b_low, b_high), 2)

    return HouseholdBudget(
        customer_id=customer_id,
        income_decile=decile,
        monthly_disposable_income=income,
        composition=composition,
        essential_cost_floor_monthly=floor,
        discretionary_margin_monthly=margin,
        savings_buffer=savings,
        housing_cost_monthly=housing,
    )


def allocate_debt_payments(
    available: float,
    debts_due: Mapping[str, float],
    order: Optional[Sequence[str]] = None,
) -> Dict[str, float]:
    """Allocate a BINDING budget across debts in consequence-severity order.

    Priority-tier debts (rent/mortgage, council tax, court fines, child
    maintenance, energy, TV licence) are serviced — in `order` — before ANY
    non-priority debt (credit cards, loans, overdrafts, BNPL) receives a penny.
    Each debt is paid in full if funds remain, else partially, then allocation
    stops. This is the "which bills get paid first under stress" mechanism.

    Returns {debt_name: amount_paid} for every debt in `debts_due`.
    """
    order = list(order) if order is not None else list(DEFAULT_DEBT_PRIORITY_ORDER)
    remaining = max(0.0, float(available))
    paid: Dict[str, float] = {name: 0.0 for name in debts_due}

    # Service in the given order first, then any debt not named in `order`.
    ordered_names = [n for n in order if n in debts_due]
    ordered_names += [n for n in debts_due if n not in order]

    for name in ordered_names:
        due = max(0.0, float(debts_due[name]))
        pay = min(remaining, due)
        paid[name] = round(pay, 2)
        remaining = round(remaining - pay, 2)
        if remaining <= 0.0:
            break
    return paid


# ---------------------------------------------------------------------------
# THE BUDGET DECIDES HOW MUCH OF THE BILL IS PAID (2026-10-19)
# ---------------------------------------------------------------------------
# Design: `docs/market_research/household_budget_w2_4.md`, "2026-10-16: design for the next build"
# and "The price level, researched (2026-10-17)". Diagnosis and pre-registration (R1-R4):
# `docs/staging/WORKER_FINDING_THE_WORLDS_PAYMENT_DRAW_HAS_NO_PRICE_INPUT_..._2026-10-16.md`.
#
# The floor above holds JRF's whole basket, which includes £24/£33 a week of electricity and gas.
# A margin that pays the world's own energy bill must leave energy out of the floor, or energy is
# counted twice: these are the basket's other lines, summed (JRF/Trussell itemised table, 2026/27).
_CORE_EX_ENERGY_SINGLE = round((42 + 7 + 7 + 8 + 21 + 13) * 52 / 12, 2)   # 424.67
_CORE_EX_ENERGY_COUPLE = round((74 + 11 + 11 + 11 + 42 + 20) * 52 / 12, 2)  # 732.33

_CORE_EX_ENERGY_BY_COMPOSITION: Dict[str, float] = {
    Composition.SINGLE.value: _CORE_EX_ENERGY_SINGLE,
    Composition.COUPLE.value: _CORE_EX_ENERGY_COUPLE,
    Composition.SINGLE_PARENT.value: _CORE_EX_ENERGY_SINGLE + _CHILD_ESSENTIALS_ADDON,
    Composition.COUPLE_PARENT.value: _CORE_EX_ENERGY_COUPLE + _CHILD_ESSENTIALS_ADDON,
}

# Each run year's price level against 2026/27 (= 1), annual averages, transcribed from the knowledge
# page's tables (ONS MM23 and LMS, fetched 2026-10-17; harness-side, never read at runtime, W6).
# The ex-energy basket on its CPIH divisions deflates the floor.
_BASKET_EX_ENERGY_FACTOR: Dict[int, float] = {
    2016: 0.708, 2017: 0.727, 2018: 0.744, 2019: 0.755, 2020: 0.760,
    2021: 0.779, 2022: 0.856, 2023: 0.926, 2024: 0.943, 2025: 0.972,
}
# All-items CPIH carries housing. GAP: the page researched no rent or housing-cost series (ONS
# PIPR / IPHRP not fetched); the housing draw is itself an R10 shape, so CPIH is the named stand-in.
_CPIH_FACTOR: Dict[int, float] = {
    2016: 0.709, 2017: 0.727, 2018: 0.744, 2019: 0.757, 2020: 0.764,
    2021: 0.783, 2022: 0.846, 2023: 0.903, 2024: 0.933, 2025: 0.969,
}
# AWE whole-economy total pay (KAB9) carries earned income (docs/market_research/household_budget_w2_4.md,
# "The price level, researched", the AWE column).
_AWE_FACTOR: Dict[int, float] = {
    2016: 0.655, 2017: 0.670, 2018: 0.690, 2019: 0.714, 2020: 0.725,
    2021: 0.769, 2022: 0.817, 2023: 0.874, 2024: 0.920, 2025: 0.966,
}
# The April benefit-uprating path (previous September's CPI; frozen April 2016 to April 2019),
# calendar averages (docs/market_research/household_budget_w2_4.md, the benefit-path row).
_BENEFIT_PATH_FACTOR: Dict[int, float] = {
    2016: 0.765, 2017: 0.765, 2018: 0.765, 2019: 0.765, 2020: 0.775,
    2021: 0.781, 2022: 0.800, 2023: 0.867, 2024: 0.932, 2025: 0.959,
}
# Which deciles live on the uprating path rather than on earnings. GAP: HBAI income by source by
# decile is not fetched. R10: the bottom quintile, the deciles whose essentials the page cites as
# exceeding income. Named so a run can be read with the path off, never blended silently.
BENEFIT_PATH_DECILES: Tuple[int, ...] = (1, 2)

# The switch. Off: no payment path reads this module and the world is unchanged. On by default since
# 2026-10-20, when it was graded on two dice seeds of a fixed-seed paired run
# (docs/staging/records/SEAT_RESULT_THE_SHARED_SHORTFALL_HOLDS_ON_A_SECOND_DICE_SEED_2026-10-20.md).
BUDGET_DECIDES_PAYMENT = True


def _factor(table: Mapping[int, float], year: int) -> float:
    """2026/27 and later are the floor's own prices; years before the table take its first row."""
    if year >= 2026:
        return 1.0
    return table[max(year, min(table))]


# THE INCOME MOVES EACH YEAR, so a household under water can leave it (2026-10-19). Design and
# origin: `docs/market_research/household_budget_w2_4.md`, "how an under-water spell ends in the
# record". Each calendar year after the first, the household's income takes a fresh draw from the
# same ladder with this probability; otherwise it keeps last year's. A fresh draw from the same
# ladder leaves the stationary distribution, and so the under-water share, where it was.
# CALIBRATED, not cited: the value at which the drawn population's exit from under water at 2021
# prices equals DWP Income Dynamics' 36% AHC exit from low income (2022/23 to 2023/24). Range
# 0.36-0.45 spans the published 32% (BHPS 1991-2008) to 40% (BHC). Check it did not use: under
# water in 3 of 4 years over under water in a year, 0.57 drawn against the record's ~0.52.
INCOME_MOVE_PER_YEAR = 0.41
_FIRST_INCOME_YEAR = 2016


def _income_draw(r: random.Random, ladder: Mapping[int, float]) -> Tuple[int, float]:
    decile = r.randint(1, 10)
    low = ladder[decile]
    high = ladder[decile + 1] if decile < 10 else ladder[10] * 1.5
    return decile, round(r.uniform(low, high), 2)


def budget_in_year(budget: HouseholdBudget, year: int,
                   move_per_year: float = INCOME_MOVE_PER_YEAR,
                   base_seed: Optional[int] = None) -> HouseholdBudget:
    """The household's budget with `year`'s income: the latest year's fresh draw, if any, else the
    drawn one. A pure function of (household, year), so a household's two legs, posted out of date
    order, read the same income for the same year."""
    seed = _base_seed_for(budget.customer_id, base_seed)
    for y in range(year, _FIRST_INCOME_YEAR, -1):
        r = _substream(seed, f"income_move:{y}")
        if r.random() < move_per_year:
            decile, income = _income_draw(r, MONTHLY_DISPOSABLE_INCOME_BY_DECILE)
            return replace(budget, income_decile=decile, monthly_disposable_income=income,
                           discretionary_margin_monthly=round(
                               income - budget.essential_cost_floor_monthly, 2))
    return budget


def core_in_year(budget: HouseholdBudget, year: int) -> float:
    """The ex-energy, ex-housing basket in `year`'s own pounds: the part of the floor a household
    short of money can go without."""
    return _CORE_EX_ENERGY_BY_COMPOSITION[budget.composition] * _factor(_BASKET_EX_ENERGY_FACTOR, year)


def margin_in_year(budget: HouseholdBudget, year: int,
                   benefit_path_deciles: Sequence[int] = BENEFIT_PATH_DECILES) -> float:
    """Income less every essential except energy, in `year`'s own pounds. May be negative."""
    income_path = (_BENEFIT_PATH_FACTOR if budget.income_decile in benefit_path_deciles
                   else _AWE_FACTOR)
    income = budget.monthly_disposable_income * _factor(income_path, year)
    floor = core_in_year(budget, year) + budget.housing_cost_monthly * _factor(_CPIH_FACTOR, year)
    return round(income - floor, 2)


# WHAT A HOUSEHOLD SHORT OF MONEY CUTS (2026-10-20). Origin: `docs/market_research/household_budget_w2_4.md`,
# "what a household short of money cuts, and in what order". Housing is protected: ONS OPN June 2023
# has 6% of adults behind on energy and 2% on rent or mortgage, with about as many finding each hard
# to afford. Food and energy are cut together: JRF's winter 2022-23 tracker has 4.3m of the 4.7m
# low-income households in arrears also going without essentials. Off, the core basket is paid in
# full before energy and energy takes the whole shortfall. On, money left after housing is shared
# between the basket and what is owed on energy in proportion to their sizes, so each is short by
# the same fraction. No new number: the split is the two amounts themselves. GAP: no source says
# how a pound of shortfall divides between going without and arrears; pro rata is the
# no-priority stance between the two, not a measured one. On by default since 2026-10-20, on the
# same two-seed grade as BUDGET_DECIDES_PAYMENT; basket-first left a +1 to +2.7 point pre-crisis
# excess on both seeds.
ENERGY_SHARES_THE_SHORTFALL = True

# SHARED ON THE MONTH'S DEMAND, NOT THE ARREARS STOCK (2026-10-22). Origin: `household_budget_w2_4.md`,
# "2026-10-22: stock or demand". Sharing against `owed_total` lets energy's part grow with the debt,
# so a household under water stops falling behind at C/(A-B) bills (median 1.67 over the deficit
# account-years), where Ofgem's arrears are most of a year's bill. On, the basket is short by the
# fraction this month's money falls short of this month's basket and bill, `min(C, C*A/(C+B))`,
# and everything else after housing goes to energy, oldest bill first; the stock then grows while
# the margin is below the bill. Same GAP as the switch above: pro rata is a stated belief. On by
# default since 2026-10-22, after D1-D5 held on two dice seeds:
# SEAT_RESULT_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_SEED_2_2026-10-22.md (depth 2.8-6.0 months
# against 1.6-2.6, Q4 2023 £710 against £250, Ofgem £1,303).
THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND = True

# MONEY HELD TOWARD A BILL IS A PART PAYMENT, NOT MONEY TO SHARE AGAIN (2026-10-22). Origin:
# `household_budget_w2_4.md`, "2026-10-22: held money is a part payment". The demand reading's own
# arithmetic (stock grows `1 - A/(C+B)` bills a month) assumes energy's part builds up month on
# month. Off, the money held toward an unpaid bill re-enters `after_housing` and is shared with the
# basket again, so it levels off at `(m+C)*B/C`, below one bill when the margin `m` is below zero,
# and such a household pays nothing while under water (26 of 257 deficit account-years, seed 2).
# On, only this month's money is shared; what is held stays energy's. Read only on the demand
# reading. On by default since 2026-10-22, after H1-H5 held on two dice seeds:
# SEAT_RESULT_HELD_MONEY_IS_A_PART_PAYMENT_SEED_2_2026-10-22.md (no-payment account-years 26 to 0,
# arrears engagement 25-60% to 90-100% against DRS's ~90%; Q4 2023 £710 to £452, Ofgem £1,303).
HELD_MONEY_IS_A_PART_PAYMENT = True


class BudgetPaymentBook:
    """Per supply point: what the household's money pays of each month's energy bill, and which
    earlier unpaid bills it clears.

    Keyed per LEG, never per household, because the run posts a leg's whole term at a time, so a
    household's two legs do not arrive in date order. A dual household's margin and savings are
    split evenly across its legs. Design choice, unsourced: the two cap bills were of a similar size
    in 2021-23, and a split by bill would need the other leg's bill before it is posted.

    Bills are paid whole, oldest first. Ofgem's arrears age by the oldest unpaid bill, and a
    payment allocated to the oldest debt is the ledger's own fallback; money short of a whole bill
    is held toward it. Savings are drawn while the margin is short and, once no bill is unpaid,
    refill out of surplus only up to the buffer the household was drawn with (design choice).
    """

    def __init__(self, benefit_path_deciles: Sequence[int] = BENEFIT_PATH_DECILES,
                 income_move_per_year: float = INCOME_MOVE_PER_YEAR,
                 energy_shares_the_shortfall: Optional[bool] = None,
                 shared_on_demand: Optional[bool] = None,
                 held_is_paid: Optional[bool] = None):
        self._benefit_path_deciles = tuple(benefit_path_deciles)
        self._income_move_per_year = income_move_per_year
        self._shares = (ENERGY_SHARES_THE_SHORTFALL if energy_shares_the_shortfall is None
                        else energy_shares_the_shortfall)
        self._on_demand = (THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND if shared_on_demand is None
                           else shared_on_demand)
        self._held_is_paid = HELD_MONEY_IS_A_PART_PAYMENT if held_is_paid is None else held_is_paid
        self._legs: Dict[str, dict] = {}

    def settle_month(self, *, supply_point: str, household: str, year: int, amount_gbp: float,
                     legs: int, ref) -> Tuple[bool, Tuple]:
        """(this bill paid, refs of earlier unpaid bills paid this month, oldest first)."""
        share = 1.0 / max(1, legs)
        st = self._legs.get(supply_point)
        if st is None:
            budget = draw_household_budget(household)
            st = self._legs[supply_point] = {
                "budget": budget, "savings": budget.savings_buffer * share,
                "cap": budget.savings_buffer * share, "unpaid": []}
        budget = budget_in_year(st["budget"], year, self._income_move_per_year)
        cash = st["savings"] + margin_in_year(budget, year, self._benefit_path_deciles) * share
        # A bill is in pence, and `allocate_debt_payments` pays in pence. An unrounded amount left a
        # GBP 17.441972 bill unpaid against GBP 17.44 paid out of GBP 15k, about half of all bills.
        owed = st["unpaid"] + [(ref, round(float(amount_gbp), 2))]
        owed_total = sum(a for _, a in owed)
        if self._shares and cash < owed_total:
            # Short: what is left after housing is shared with the basket, pro rata. The basket's
            # part is spent (gone without, not saved), so `cash` becomes energy's part alone.
            core = core_in_year(budget, year) * share
            # With a bill unpaid, `savings` is what was held toward it last month.
            held = st["savings"] if (self._on_demand and self._held_is_paid and st["unpaid"]) else 0.0
            after_housing = max(0.0, cash - held + core)
            if self._on_demand:
                # A household that can meet this month's basket and bill keeps its basket whole and
                # repays the backlog out of the rest; only this month's shortfall is shared.
                bill = owed[-1][1]
                cash = held + after_housing - min(core, core * after_housing / (core + bill))
            else:
                cash = after_housing * owed_total / (core + owed_total)
        paid = allocate_debt_payments(cash, {"energy_arrears": owed_total})["energy_arrears"]
        cleared, spent = [], 0.0
        for bill_ref, amount in owed:
            if round(spent + amount, 2) > paid:
                break
            cleared.append(bill_ref)
            spent += amount
        st["unpaid"] = owed[len(cleared):]
        # Money left while a bill is still unpaid is held toward it, which is what a part payment
        # does; only a household clear of arrears stops refilling at its buffer.
        left = max(0.0, cash - spent)
        st["savings"] = left if st["unpaid"] else min(st["cap"], left)
        this_paid = bool(cleared) and cleared[-1] == ref
        earlier = tuple(cleared[:-1] if this_paid else cleared)
        return this_paid, earlier

    def unpaid_of(self, supply_point: str) -> Tuple:
        st = self._legs.get(supply_point)
        return tuple(st["unpaid"]) if st else ()
