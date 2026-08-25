"""SIM-side market switching propensity: savings-elasticity churn model (Phase NS).

Encodes the empirical relationship between annual savings available from switching
and the market-level switching propensity multiplier.

Key empirical finding (Ofgem/DESNZ data; see docs/market_research/churn_price_elasticity.md):
- PRIMARY driver of switching: SAVINGS AVAILABLE from switching to a competitor.
- Absolute price level does NOT independently increase switching (2022 disconfirms it:
  bills hit 3,549 GBP/yr yet switching collapsed to 3-4% because competitor fixed deals
  were 1,000+ GBP more expensive than SVT -- the "nowhere cheaper to go" effect).
- Post-2023 fairer-pricing rule permanently removed new-customer-exclusive discounts;
  structural switching equilibrium reduced ~25-30% from pre-2021 levels.

Piecewise elasticity (calibrated from DESNZ switching series 2015-2025):
    savings < 0:         3%   (crisis floor: home movers / SoLR only)
    0 <= S < 100:        5% + 2% * (S / 100)
    100 <= S < 250:      7% + 6% * ((S - 100) / 150)
    250 <= S < 400:      13% + 5% * ((S - 250) / 150)
    S >= 400:            22% (saturation -- maximum engaged segment)

Market multiplier: normalised so that 2024 new-normal (150 GBP savings, post-ban) = 1.0.
Applied in simulation/customer_events.py before income_stress and satisfaction modifiers.
"""
from __future__ import annotations

# Annual savings (GBP/yr, dual-fuel) available to a typical household by switching to
# the best available competitor deal. Midpoints from DESNZ/Ofgem engagement survey series.
# Negative values (crisis period) indicate fixed alternatives were MORE expensive than SVT.
MARKET_SAVINGS_BY_YEAR: dict[int, float] = {
    2016: 300.0,   # Peak challenger era; cheapest fix ~18% below SVT
    2017: 200.0,   # Some consolidation; still competitive
    2018: 200.0,   # Pre-cap surge; median saving ~160-240 GBP
    2019: 175.0,   # Default Tariff Cap (Jan 2019) compressed new-customer offers
    2020: 125.0,   # COVID + fewer products; cap falls; peak switching volumes despite lower savings
    2021: 0.0,     # H2 collapse: suppliers withdrew fixed products; averaged over year
    2022: -200.0,  # Crisis: no competitive alternative below SVT; fixed deals 1,000+ GBP more expensive
    2023: 100.0,   # Recovery; acquisition tariff ban + fairer-pricing rule moderating savings
    2024: 150.0,   # New normal (calibration year)
    2025: 175.0,   # Gradual normalisation continues
}

# Post-2023 "fairer for existing customers" rule eliminates new-customer-exclusive discounts.
# Permanently reduces the savings differential vs. the pre-2022 era.
_POST_BAN_STRUCTURAL_FACTOR: dict[int, float] = {
    2023: 0.85,
    2024: 0.75,
    2025: 0.75,
}

# Calibration reference: 2024 new-normal
_CALIBRATION_SAVINGS = MARKET_SAVINGS_BY_YEAR[2024]   # 150 GBP
_CALIBRATION_POST_BAN = _POST_BAN_STRUCTURAL_FACTOR[2024]   # 0.75

_CRISIS_FLOOR_RATE = 0.03   # 3% -- structural minimum (home movers, SoLR regardless of savings)
_MAX_RATE = 0.22             # 22% -- saturation (maximum engaged segment)


def _savings_to_rate(savings_gbp: float) -> float:
    """Piecewise linear annual switching rate from savings available (GBP/yr dual-fuel).

    Calibrated from DESNZ electricity switching series 2015-2025 cross-referenced
    with Ofgem engagement surveys and savings-available estimates.
    """
    if savings_gbp < 0:
        return _CRISIS_FLOOR_RATE
    if savings_gbp < 100:
        return 0.05 + 0.02 * (savings_gbp / 100.0)
    if savings_gbp < 250:
        return 0.07 + 0.06 * ((savings_gbp - 100.0) / 150.0)
    if savings_gbp < 400:
        return 0.13 + 0.05 * ((savings_gbp - 250.0) / 150.0)
    return _MAX_RATE


def _calibration_rate() -> float:
    """Rate at the calibration year (2024) -- multiplier denominator."""
    return _savings_to_rate(_CALIBRATION_SAVINGS) * _CALIBRATION_POST_BAN


def market_switching_multiplier(renewal_year: int) -> float:
    """Return the market-conditions switching propensity multiplier for a given year.

    Normalised: 2024 new-normal = 1.0.
    Below 1.0 suppresses churn relative to model baseline; above 1.0 amplifies it.

    Typical values:
      2016 (peak competition):  ~2.2
      2020 (pre-crisis normal): ~1.0
      2021 (crisis emerging):   ~0.7
      2022 (crisis peak):       ~0.4
      2023 (recovery):          ~0.85
      2024 (new normal):        1.00
      2025 (continuing):        ~1.1

    Applied to SIM ground-truth churn probability BEFORE income_stress and satisfaction
    modifiers -- it sets the market opportunity ceiling, not the customer-level probability.
    """
    savings = MARKET_SAVINGS_BY_YEAR.get(renewal_year, 150.0)
    structural = _POST_BAN_STRUCTURAL_FACTOR.get(renewal_year, 1.0)
    adjusted_rate = _savings_to_rate(savings) * structural
    cal = _calibration_rate()
    return max(adjusted_rate / cal, _CRISIS_FLOOR_RATE / cal)


# ═══════════════════════════════════════════════════════════════════════════
# THE OTHER SIDE OF THE SAME CURVE — what OUR price position does to switching
#
# Atom `PB3_book_growth_as_earned_outcome`, exit criterion (b1), 2026-08-25.
#
# Everything above answers "how many households moved supplier this year", and the
# loss leg has read it since Phase NS. It is a MARKET-level fact: it says how big the
# switching flow was, and nothing about which supplier won it. `MARKET_SAVINGS_BY_YEAR`
# is keyed on the year alone, so no decision this company makes can move it, and that
# is correct — one small supplier does not set the national switching rate.
#
# What was missing is the half that IS the company's: a household deciding between the
# market average and OUR offer. The driver is the same one the module already argues for
# and the same one 2022 disconfirmed the alternative of — SAVINGS AVAILABLE, not the
# absolute price level. So this reads `_savings_to_rate`, the identical piecewise curve,
# at the savings OUR position offers rather than at the savings the market offers.
#
# WHY THAT SHARING IS LOAD-BEARING AND NOT TIDINESS (R12, and the director's
# anti-goal-seek guard of 2026-08-17, registered in this atom's simplifications file
# before the build). Book size is wins minus losses. Both are now functions of the same
# `price_differential_pct` through the same elasticity, with opposite signs: pricing
# down wins prospects AND holds the existing book, pricing up loses both. There is no
# constant here that can be moved to grow the book without paying for it on the other
# leg, so goal-seeking on book size is structurally unavailable rather than forbidden by
# a rule someone has to remember.

#: Reference annual dual-fuel bill at the calibration year, GBP. This exists ONLY to put
#: `price_differential_pct` — a fraction — onto the GBP scale `_savings_to_rate` is
#: calibrated in. Anchored on the Ofgem Default Tariff Cap typical dual-fuel
#: direct-debit level through 2024, which sat at £1,690 (Apr-Jun) and £1,717 (Oct-Dec).
#:
#: IT IS A SCALE, NOT A MODELLED BILL, and the distinction matters because no customer's
#: bill is computed from it anywhere — `simulation/price_cap_enforcement.py` owns what a
#: bill may be and is untouched by this. Getting it wrong stretches or compresses how
#: sharply the win side responds to a given price position; it cannot move anybody's money.
#:
#: SANITY CHECK, and it is the reason to trust the pairing rather than the figure: the
#: calibration year's market saving is £150 against this bill, i.e. the best deal in the
#: market sat ~8.8% below the average. That is a plausible best-vs-average spread for
#: 2024 and it is the consistency test this constant actually has to pass.
CALIBRATION_ANNUAL_BILL_GBP = 1700.0

#: Parity denominator. `_savings_to_rate(0.0)` is the propensity of a household offered
#: exactly the market average — the shipped run's position (`PRICE_DIFFERENTIAL_PCT = 0.0`).
#: Normalising by it makes the multiplier EXACTLY 1.0 at parity, so wiring this in changes
#: no shipped outcome by a single roll, and every movement below is attributable to a price
#: position the company chose.
_PARITY_RATE = _savings_to_rate(0.0)


def offer_position_multiplier(price_differential_pct: float) -> float:
    """The world's response to OUR price against the market average. 1.0 at parity.

    `price_differential_pct` is our price relative to the market average as a fraction:
    ``0.05`` = 5% above (dearer), ``-0.05`` = 5% below (cheaper). It is the SAME run
    parameter the loss leg already reads — `simulation.customer_events` passes it to
    `saas.home_move_win_rate.build_home_move_win_rates`, where being dearer lowers the
    probability of holding a property through a move.

    Above 1.0 means a household is more willing to take our offer than the market's;
    below 1.0, less. Multiplies a WIN-side conversion rate; it never touches the size of
    the market (`net_new_acquisition.homes_in_market` owns that, off the year-keyed
    series), because how many homes are in play is the world's fact and how many of them
    take our quote is ours.

    THE CURVE IS READ ON ITS POSITIVE SIDE ONLY, AND ITS NEGATIVE BRANCH IS DELIBERATELY
    NOT REUSED. This is the one place where the market-level curve does not transfer, and
    reading it straight was the first draft's defect — measured, not reasoned about: every
    dearer position collapsed onto a single value, so being 1% above the market cost
    exactly what being 20% above cost. The cause is that `_savings_to_rate` returns the
    flat `_CRISIS_FLOOR_RATE` for negative savings, and that floor encodes the 2022
    "nowhere cheaper to go" effect — a statement about THE MARKET having no cheaper
    alternative. For one supplier priced above the average the premise is false by
    construction: a cheaper alternative exists, it is the average. Transferring the floor
    would have modelled a supplier who can raise prices indefinitely at no cost to its win
    rate, which is the precise shape of the defect this atom exists to remove.

    SO THE DEARER SIDE IS THE MIRROR OF THE CHEAPER SIDE, and this is a NAMED SIMPLIFICATION
    (registered in this atom's simplifications file, 2026-08-25): pricing 10% above the
    market is assumed to cost exactly what pricing 10% below it gains, reciprocally. Real
    retail is not symmetric — loss aversion and incumbency inertia both say a dearer offer
    is punished harder than a cheaper one is rewarded — and nothing in the DESNZ series can
    settle the asymmetry, because a market-level switching count never observed this
    supplier's own quote book. Symmetry is the assumption that invents least, and it is
    monotone, which is the property the model actually needs.

    It also makes the anti-goal-seek guarantee exact rather than approximate:
    ``m(d) * m(-d) == 1`` for every d, so the win side's gain from a price cut is precisely
    the reciprocal of what the same cut costs elsewhere. There is no d at which both legs
    improve.

    Bounded by the curve itself, not by a clamp bolted on: `_savings_to_rate` saturates at
    0.22, so this returns [1/4.4, 4.4] across every finite input.
    """
    our_saving_gbp = -float(price_differential_pct) * CALIBRATION_ANNUAL_BILL_GBP
    if our_saving_gbp >= 0.0:
        return _savings_to_rate(our_saving_gbp) / _PARITY_RATE
    return _PARITY_RATE / _savings_to_rate(-our_saving_gbp)


#: Where the DESNZ series stops informing the curve: `_savings_to_rate` is flat at `_MAX_RATE`
#: above this, so beyond it every input maps to the same output.
_CALIBRATED_SAVINGS_CEILING_GBP = 400.0

#: The last slope the data actually informs, per GBP of annual saving. Taken from the final
#: graduated segment of `_savings_to_rate` (0.13 -> 0.22 across 250..400 GBP) rather than
#: written down, so a re-calibration of that segment moves this with it.
_LAST_INFORMED_SLOPE_PER_GBP = (_MAX_RATE - 0.13) / (_CALIBRATED_SAVINGS_CEILING_GBP - 250.0)


def churn_position_multiplier(price_differential_pct: float) -> float:
    """The world's LOSS-side response to our price against the market. 1.0 at parity.

    THE RECIPROCAL OF `offer_position_multiplier` BELOW SATURATION, and deliberately NOT above
    it. Both legs share one curve so that the anti-goal-seek guarantee holds -- there is no
    differential at which the company gains on winning AND on keeping -- and that property is
    preserved here: this is monotone increasing in the differential, so a dearer position is
    never better on this leg.

    WHY THE TWO LEGS PART COMPANY ABOVE SATURATION, measured rather than reasoned about.
    `_savings_to_rate` is flat at `_MAX_RATE` above 400 GBP of annual saving, so
    `offer_position_multiplier` saturates at 4.4x. Applied to the loss side that produced this:

        +10% vs market  -> churn x1.96 -> p(leave) 0.157
        +25% vs market  -> churn x4.40 -> p(leave) 0.352
        +50% vs market  -> churn x4.40 -> p(leave) 0.352
       +200% vs market  -> churn x4.40 -> p(leave) 0.352

    A supplier 25% above the market and one 200% above it lose the SAME third of their book.
    The world could punish moderate over-pricing and could not express a supplier pricing itself
    out of existence -- so `WORLD_MAX_CHURN_PROBABILITY` was unreachable by the one mechanism
    that should reach it.

    ON THE WIN SIDE THE SATURATION IS CORRECT and is left alone: you cannot win more customers
    than the market has engaged households to give, and `_MAX_RATE` is exactly that ceiling. On
    the LOSS side the same number is a category error -- a MARKET-WIDE annual switching rate used
    to bound an INDIVIDUAL's response to their own supplier doubling their bill. It is the third
    instance of that shape found today, after the company's `MAX_CHURN_PROBABILITY` cap and the
    win leg's own crisis-floor defect (`50274434a`).

    WHAT IS ASSUMED, NAMED AS A SIMPLIFICATION. Above the calibrated ceiling the response
    continues at the LAST SLOPE THE DATA INFORMS rather than flattening. Flattening is not the
    neutral choice -- it is an extrapolation too, and it is the one that asserts "no further
    response", which is both the least defensible of the available assumptions and the one that
    flatters an over-pricing supplier. Continuing the measured slope invents no new parameter:
    it is derived from the final graduated segment of `_savings_to_rate` and moves if that
    segment is ever recalibrated.

    WHAT WOULD DISCHARGE IT: a supplier-level churn series against that supplier's own position
    versus the market -- the 2018-19 small-supplier failures and the SoLR events are the obvious
    place to look. A market-level switching count can never settle it, because it never observed
    any single supplier's own book.

    R13: baseline fidelity, decided blind to company P&L, and it moves against the company --
    it makes over-pricing more expensive and cannot make anything cheaper.
    """
    differential = float(price_differential_pct)
    if differential <= 0.0:
        # Cheaper or at parity: the reciprocal of the win leg, exactly. No extrapolation is
        # involved and none is invented -- a keener price cannot take churn below the crisis
        # floor the market series already carries.
        return 1.0 / offer_position_multiplier(differential)

    our_shortfall_gbp = differential * CALIBRATION_ANNUAL_BILL_GBP
    if our_shortfall_gbp <= _CALIBRATED_SAVINGS_CEILING_GBP:
        return 1.0 / offer_position_multiplier(differential)

    beyond = our_shortfall_gbp - _CALIBRATED_SAVINGS_CEILING_GBP
    extrapolated_rate = _MAX_RATE + _LAST_INFORMED_SLOPE_PER_GBP * beyond
    return extrapolated_rate / _PARITY_RATE
