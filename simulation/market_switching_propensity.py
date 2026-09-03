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

Piecewise elasticity SHAPE (the level it is read at is settled below, not here):
    savings < 0:         3%   (crisis floor: home movers / SoLR only)
    0 <= S < 100:        5% + 2% * (S / 100)
    100 <= S < 250:      7% + 6% * ((S - 100) / 150)
    250 <= S < 400:      13% + 5% * ((S - 250) / 150)
    S >= 400:            22% (saturation -- maximum engaged segment)

Market multiplier: normalised so that 2024 new-normal = 1.0.
Applied in simulation/customer_events.py before income_stress and satisfaction modifiers.

THE LEVEL AND THE SHAPE ARE TWO QUANTITIES AND THIS MODULE USED TO CARRY ONLY ONE (2026-08-30).
`market_switching_multiplier` divided an absolute rate by its own 2024 value, so the absolute rate
existed for exactly one statement and was then cancelled. Nothing downstream could read it and no
control could compare it with anything -- which is how the world ran 3.15x below the published
GB domestic switching record for the whole of this project's history without a single test going
red. `market_departure_rate` below is that absolute quantity, kept rather than cancelled, and
`tools/measure_departure_level.py` is the instrument that puts it beside the record.
"""
from __future__ import annotations

import functools
import json
from pathlib import Path

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
    """Piecewise linear annual switching RESPONSE SHAPE from savings available (GBP/yr dual-fuel).

    IT IS NOT CALIBRATED TO THE DESNZ SWITCHING SERIES AND ITS DOCSTRING CLAIMED IT WAS until
    2026-08-30. Measured, at real inputs, against
    `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`: this curve at each
    year's own savings runs 2.04x below the published record on the 2017-2024 mean, and wrong in
    shape as well as level -- 2020 reads 8.0% against a published 22.5-23.0% while 2022 reads 3.0%
    against 2.9-4.3% and is right.

    AND IT CANNOT BE CALIBRATED TO IT, WHICH IS THE STRONGER RESULT AND THE REASON THIS FUNCTION
    KEPT ITS NUMBERS. A function of savings alone is not identified against the published series,
    because the series is not a function of `MARKET_SAVINGS_BY_YEAR`:

        2017 and 2018 carry the SAME 200 GBP saving and published rates of 13.5-14.0% and
        19.5-20.0%. No function of savings can return both, so at least one of those two years is
        out of band under every possible recalibration of this curve.

        2021 (0 GBP saving) published 17.9-18.4%, above 2023 (100 GBP, 8.9-12.5%) and 2016
        (300 GBP, 17.0-17.6%). Monotone in savings, the record is not.

    So the market LEVEL is no longer read off this curve for a year the record covers --
    `market_departure_rate` takes it from the record, which for 2016-2025 is historical ground
    truth rather than something to model. What this curve is FOR, and is good for, is the
    RESPONSE: how a household's departure propensity moves with the pounds on the table, which is
    what `offer_position_multiplier` and `churn_position_multiplier` read it for, and what
    generates a level for a year outside the record.

    The one thing recalibration CAN fix is the level it is read at outside the record, and
    `_CURVE_LEVEL_SCALE` below does exactly that and nothing more.
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


# ═══════════════════════════════════════════════════════════════════════════
# THE ABSOLUTE LEVEL — what fraction of GB domestic accounts actually left
#
# Opened by `docs/staging/WORKER_FINDING_THE_WORLDS_DEPARTURE_LEVEL_HAS_NEVER_BEEN_CHECKED_
# AGAINST_A_PUBLISHED_RATE_2026-08-30.md`; instrument `tools/measure_departure_level.py`.

#: The regulation commons. THE RECORD, not a reading of it -- it states GB domestic ELECTRICITY
#: changes of supplier over ALL GB domestic electricity accounts, per calendar year, with the band
#: each year's published counts bear. Read here rather than re-parsed from the underlying sources:
#: a second parse of the same publications is a second artefact that can drift from the first, and
#: the 3.15x gap was measured against THIS object.
_COMMONS = (
    Path(__file__).resolve().parent.parent
    / "docs" / "domain_artefact_library" / "regulatory" / "gb_domestic_switching_rate.json"
)


@functools.lru_cache(maxsize=1)
def _published_departure_rates() -> dict[int, float]:
    """`{year: rate}` as a FRACTION, from the commons. THE HIGH END of each year's band.

    WHERE INSIDE THE BAND IS NOT THIS MODULE'S CHOICE AND IT IS NOT A PREFERENCE. The band is
    evidence; where in it the world sits is a curriculum value, settled in
    `docs/market_research/gb_switching_rate_denominators.md` §6 under the director's brief of
    2026-08-30 §7: *"where the evidence is ambiguous, choose the option that makes the company's
    advantage harder to demonstrate."* More departures is more book to re-win, more revenue at
    risk and a harder book to hold, so the tie-break points at the HIGH end. The midpoint would
    have been the tidier default and it is the flattering one.

    It is read from the artefact rather than written down, so a correction to the record moves it.
    Nothing downstream is keyed to the value: the control in
    `tests/architecture/test_switching_rate_commons.py` asserts CONTAINMENT, so refining a year
    within its band passes and moving one outside it fails.
    """
    raw = json.loads(_COMMONS.read_text())
    return {int(r["year"]): float(r["rate_pct_hi"]) / 100.0 for r in raw["rates"]}


@functools.lru_cache(maxsize=1)
def published_departure_band() -> dict[int, tuple[float, float]]:
    """`{year: (lo_pct, hi_pct)}` — BOTH endpoints of each year's published band, as percentages.

    `_published_departure_rates` above returns the HIGH end because a world that must sit on one
    number has to choose one, and the director's anti-flattering tie-break chose that one. But a
    CHECK does not need a point and must not be given one: rung 1 of
    `DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31` asks whether the world's level is inside
    the band, and a check written against the high end alone would call a world sitting happily in
    the middle of the record a failure.

    That distinction is not hypothetical here. The whole-book fit solves onto the high endpoint in
    all eight years, so every fitted year lands on the ceiling to four decimals and the band it is
    checked against cannot fail. Any measurement of where an UNFITTED level would land needs the
    two endpoints, and reaching for `market_departure_rate` instead would quietly re-import the
    point target.

    Parsed from the same commons object as the rates above, deliberately: a second parse of the
    same publication is a second artefact that can drift from the first.
    """
    raw = json.loads(_COMMONS.read_text())
    return {
        int(r["year"]): (float(r["rate_pct_lo"]), float(r["rate_pct_hi"]))
        for r in raw["rates"]
        if r.get("rate_pct_lo") is not None and r.get("rate_pct_hi") is not None
    }


def _curve_rate(year: int) -> float:
    """The savings curve's own answer for a year, before any level correction."""
    savings = MARKET_SAVINGS_BY_YEAR.get(year, 150.0)
    return _savings_to_rate(savings) * _POST_BAN_STRUCTURAL_FACTOR.get(year, 1.0)


@functools.lru_cache(maxsize=1)
def _curve_level_scale() -> float:
    """How far the savings curve sits below the published record, over the years both cover.

    DERIVED, NEVER WRITTEN DOWN. It is the ratio of the two means over the overlap, so a
    recalibration of `_savings_to_rate` or a correction to the commons moves it without anyone
    remembering to. Today it is 2.04.

    IT IS APPLIED ONLY OUTSIDE THE RECORD, and that restriction is the pre-registered prediction
    in `docs/market_research/gb_switching_rate_denominators.md` §8.2 coming back confirmed. A pure
    multiplicative level scale takes 2022 -- the one year the curve already had right -- from 3.0%
    to 6.1%, outside its published band of 2.9-4.3%. The curve's error is not a flat scale, so a
    flat scale may not be used where the record can contradict it. Where the record is silent
    (a synthetic future) a scaled curve is the only thing on offer, and a curve known to be 2x low
    is worse than one corrected by the only factor the evidence supports.
    """
    overlap = sorted(_published_departure_rates())
    published_mean = sum(_published_departure_rates()[y] for y in overlap) / len(overlap)
    curve_mean = sum(_curve_rate(y) for y in overlap) / len(overlap)
    return published_mean / curve_mean


def market_departure_rate(year: int) -> float:
    """The world's ABSOLUTE annual domestic departure rate for `year`, as a FRACTION.

    UNITS: external changes of supplier on a GB domestic ELECTRICITY meter point, over ALL GB
    domestic electricity accounts, per calendar year. The same pair the commons declares. This is
    the quantity that has to survive somewhere a control can read it -- a normalised multiplier
    has no units and therefore nothing a publication can be compared against, which is precisely
    why the world sat 3.15x outside the record unnoticed.

    INSIDE THE RECORD IT IS THE RECORD. 2016-2025 domestic switching is historical ground truth in
    the same sense as 2022 prices: it happened, and CLAUDE.md's third wall says the world does not
    model what the record already states. The mechanism still decides WHICH households leave and
    for what reason -- that is the director's brief of 2026-08-30 and C2's competing-risks work --
    but HOW MANY left in 2020 is not ours to derive.

    OUTSIDE IT, the savings curve at `_curve_level_scale()`, which is the only extrapolation
    available and is named as one.
    """
    published = _published_departure_rates()
    if year in published:
        return published[year]
    return _curve_rate(year) * _curve_level_scale()


def market_departure_rate_pct(year: int) -> float:
    """`market_departure_rate` as a percentage. The form the commons and every lane reading use."""
    return 100.0 * market_departure_rate(year)


#: The year `market_switching_multiplier` is normalised at. Unchanged from Phase NS: the
#: post-ban "new normal", and every company-side consumer is written against 1.0 meaning it.
MULTIPLIER_REFERENCE_YEAR = 2024


def market_switching_multiplier(renewal_year: int) -> float:
    """The market-conditions switching propensity multiplier. DIMENSIONLESS, 2024 = 1.0.

    DELIBERATELY STILL NORMALISED, AND THIS IS THE HALF OF THE 2026-08-30 CORRECTION THAT IS
    EASIEST TO GET WRONG. This value crosses the epistemic wall as a published observable:
    `simulation/renewals.py:163` hands it to `company/pricing/renewal_desk.py`, which reads
    `pressure = max(0.0, market_switching_multiplier - 1.0)` and tightens its SVT-anchored ceiling
    by 1pp per unit of pressure. That expression is only meaningful on a quantity whose 1.0 means
    "the reference year". Pushing the ABSOLUTE rate through it (0.143 at 2024) makes `pressure`
    identically zero for every year the record covers -- the desk's competitive ceiling would go
    quiet permanently and nothing would say so. `simulation/net_new_acquisition.py:373` is on the
    same expression via `min(pool, pool * multiplier)`.

    So the fix is a SEPARATION, not a substitution: `market_departure_rate` carries the level and
    the units, this carries the ratio, and the ratio is now a ratio OF THE RECORD rather than of a
    curve nobody had checked.

    Values, and they moved because the record is not the curve:
      2016  1.09   (was 2.17 -- the curve badly overstated the challenger era's lead)
      2018  1.24   (was 1.63)
      2020  1.43   (was 1.19 -- the record's high-water mark, which the curve had near the floor)
      2021  1.14   (was 0.74 -- the curve had 2021 SUPPRESSED; the record has it above 2024)
      2022  0.27   (was 0.44 -- the crisis trough is deeper than the curve knew)
      2024  1.00
      2025  1.11

    Applied to SIM ground-truth churn probability BEFORE income_stress and satisfaction
    modifiers -- it sets the market opportunity ceiling, not the customer-level probability.
    """
    return market_departure_rate(renewal_year) / market_departure_rate(MULTIPLIER_REFERENCE_YEAR)


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


def offer_position_multiplier(
    price_differential_pct: float, annual_bill_gbp: float | None = None
) -> float:
    """The world's response to OUR price against the market average. 1.0 at parity.

    `annual_bill_gbp` is THE HOUSEHOLD'S OWN annual spend, and passing it is what makes this a
    response to POUNDS rather than to a percentage. Default `None` keeps the market-average scale
    (`CALIBRATION_ANNUAL_BILL_GBP`), which is right for a WIN-side quote to a prospect whose
    consumption is not yet known. See `churn_position_multiplier` for why the loss side must not
    take that default, and for the evidence that the decision is absolute rather than proportional.

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
    bill = CALIBRATION_ANNUAL_BILL_GBP if annual_bill_gbp is None else float(annual_bill_gbp)
    our_saving_gbp = -float(price_differential_pct) * bill
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


#: How strongly a household of each drawn `price_sensitivity` FEELS a given price differential.
#: Applied to the differential, never to the multiplier — see `perceived_price_differential`.
#:
#: MEAN-PRESERVING IN THE WEIGHT. Against the curriculum's own shares (high 0.30 / medium 0.45 /
#: low 0.25) the population mean weight is exactly 1.000 — by construction, since each weight is a
#: subgroup importance over the share-weighted mean importance. `medium` is 1.0149 rather than
#: exactly 1.0, because the evidence puts the median household marginally above the book average;
#: that is the data's answer, not a rounding convenience.
#:
#: BUT NOT MEAN-PRESERVING IN THE RESPONSE, AND THE FIRST DRAFT OF THIS NOTE CLAIMED IT WAS.
#: `churn_position_multiplier` is CONVEX, so by Jensen a mean-preserving spread in the argument
#: RAISES the mean response. The size of that lift scales with the SQUARE of the spread, so
#: re-deriving the weights from evidence (1.26x, from an invented 3.75x) shrank it by roughly an
#: order of magnitude — see `test_the_spread_RAISES_average_churn_and_that_is_recorded_not_tuned_away`,
#: which asserts the DIRECTION and leaves the magnitude to be measured rather than pinned to a
#: table that goes stale the moment the marginals move.
#:
#: The lift is a real consequence and it is recorded rather than tuned away: renormalising the
#: weights until aggregate churn held still would be selecting parameters to hit an output, which
#: is exactly what R12 forbids.
#:
#: IT REMAINS A FIDELITY CHANGE UNDER R13, and the direction is the reason it is safe to make
#: without the director: it moves AGAINST the company (a book that churns more, never less), it
#: follows from the curve's ALREADY-CALIBRATED convexity rather than from any new difficulty knob,
#: and it was fixed before any pricing arm was re-run against it. What stays the director's is the
#: MARGINALS — how many households are highly elastic.
#:
#: DERIVED FROM PUBLISHED EVIDENCE, NOT CHOSEN. Director, 2026-08-27: *"derive them from published
#: evidence, not from what makes the arm look good... If the honest distribution leaves little to
#: infer, that's the finding."* It does leave little, and that IS the finding — see below.
#:
#: SOURCE. Ofgem / BMG Research, *Understanding Consumers' Energy Tariff Choices* (conjoint choice
#: experiment, n=3,235 GB energy bill payers representative on 2021 census targets; fieldwork
#: 29 Mar – 9 Apr 2024; published July 2025). Overall feature importance: **annual savings 41%**,
#: customer service rating 32%, exit fees 22%, tariff type 5%.
#:
#: THE SPREAD IS THE REPORT'S OWN SUBGROUP RANGE for the savings attribute. Across EVERY subgroup
#: it reports, price importance runs **35%–44%**, mean 41%:
#:
#:      44%  consumers rating their current supplier 0–2 stars   <- most price-focused reported
#:      42%  aged 65+;  42%  highly financially vulnerable
#:      41%  overall;   41%  "doing well financially"
#:      35%  aged 18–34 (who weight customer service 37% instead) <- least price-focused reported
#:
#: Each weight is that subgroup's importance divided by the SHARE-WEIGHTED population importance
#: (40.4%), which makes the population mean exactly 1.000 by construction rather than by a fudge
#: factor. high 44/40.4, medium 41/40.4, low 35/40.4.
#:
#: WHAT THIS REPLACED, AND BY HOW MUCH IT WAS WRONG. The first version of this table was
#: 1.5 / 1.0 / 0.4 — a **3.75x** high-to-low ratio, reasoned from intuition about disengaged
#: households and labelled "asserted". The evidence gives **1.26x**. The invented spread was
#: roughly three times too wide, in the direction that makes per-customer pricing look more
#: winnable than it is. That is precisely the failure the director's instruction names.
#:
#: THE FINDING, which is a negative one and belongs here rather than in a note nobody reads.
#: GB households weight price REMARKABLY HOMOGENEOUSLY. The most and least price-focused subgroups
#: Ofgem could find differ by a quarter, and the report says so directly: *"Choices were similar
#: across demographics... feature importance scores are generally quite stable across different
#: groups"*, and on vulnerability, *"highly vulnerable consumers have scores that are close to
#: identical (42%) for price savings to those doing well financially (41%)"*. Its Table 3 puts the
#: Spearman correlation between energy SPEND and switching propensity at −0.07 to +0.05.
#:
#: So there is very little here for any supplier to infer, and that is a fact about GB households
#: rather than a gap in this model. The heterogeneity that IS large and published lies elsewhere:
#: the household's satisfaction with its CURRENT supplier (Table 4 — at a 1-star alternative,
#: 57% of 1–1.5-star raters would switch against 39% of 5-star raters, a 1.46x spread, larger than
#: anything price sensitivity shows) and a **17%** minority who "disproportionately prioritise exit
#: fees over other factors". See `docs/design/WHAT_A_HOUSEHOLD_DECIDES_ON.md`.
#:
#: WHAT WOULD DISCHARGE IT: a supplier-level churn series split by customers' own prior switching
#: history. Conjoint importance is a RELATIVE weight among four attributes, not a measured
#: elasticity, so using its subgroup ratios as elasticity ratios is a proportional proxy and is
#: named as one. A market-wide switching rate can never settle it: it never observed which
#: households did the switching.
PRICE_SENSITIVITY_WEIGHT: dict[str, float] = {
    "high": 44 / 40.4,    # 1.0891
    "medium": 41 / 40.4,  # 1.0149
    "low": 35 / 40.4,     # 0.8663
}


def price_sensitivity_weight(level: str | float | None) -> float:
    """This household's own weighting of a price differential. 1.0 when unknown.

    ACCEPTS A NUMBER AS ITSELF, AND THE FIRST VERSION DID NOT -- a bug caught by its own wiring
    test on 2026-08-27, the day it was written. When the decision moved to a CONTINUOUS
    per-household elasticity, callers began passing a float; this function looked it up with
    `PRICE_SENSITIVITY_WEIGHT.get(1.5, 1.0)`, found no such key, and returned **1.0**. Every
    household silently got the neutral weight and the whole per-household draw was discarded,
    while the module still exported everything it was supposed to.

    That is the FAIL-OPEN-ON-UNREADABLE-INPUT shape, and the "unknown is 1.0" kindness below is
    exactly what hid it: a fallback written for one kind of unknown (a level name nobody
    recognises) silently absorbed a completely different one (a value this function was never
    taught to read). A number is now read as the weight it is, and only a genuinely unrecognised
    LABEL falls back.

    UNKNOWN LABELS ARE STILL 1.0, deliberately: the pre-2026-08-27 behaviour is exactly
    `weight == 1.0` everywhere, so a caller that cannot resolve a sensitivity gets the world as it
    was rather than a crash or a silent zero. A zero would make the household immune to price,
    which is the failure this whole change exists to remove.
    """
    if level is None:
        return 1.0
    if isinstance(level, bool):  # bool is an int; a True here is a caller bug, not a weight
        raise TypeError("price sensitivity weight received a bool, which is never a weight")
    if isinstance(level, (int, float)):
        return float(level)
    return PRICE_SENSITIVITY_WEIGHT.get(level, 1.0)


def perceived_price_differential(price_differential_pct: float, sensitivity: str | None) -> float:
    """The differential as THIS household feels it.

    THE WEIGHT SCALES THE DIFFERENTIAL, NOT THE MULTIPLIER, and the difference is the whole
    argument for the shape. `churn_position_multiplier` is the reciprocal of the win leg below
    saturation, which is what makes `m(d) * m(-d) == 1` hold and guarantees there is no
    differential at which the company gains on BOTH legs. That identity holds *for any argument*,
    so feeding it `d * w` preserves the guarantee exactly, for every household, at every weight.
    Scaling the returned multiplier instead would break it: `w * m(d) * w * m(-d) == w**2`, and at
    `w < 1` that is a household the company profits from on both legs at once — precisely the
    goal-seeking hole R12 exists to close.

    It is also the semantically right place. A high-sensitivity household is more responsive to
    price in BOTH directions — it leaves sooner when dear and stays harder when keen — which is
    what elasticity means. Weighting only the loss side would model spite, not sensitivity.
    """
    return float(price_differential_pct) * price_sensitivity_weight(sensitivity)


def churn_position_multiplier(
    price_differential_pct: float, annual_bill_gbp: float | None = None
) -> float:
    """The world's LOSS-side response to our price against the market. 1.0 at parity.

    POUNDS, NOT PERCENT — and until 2026-08-27 this was wrong in a way that mattered. The
    calibrated curve `_savings_to_rate` has ALWAYS been a function of an absolute annual saving in
    GBP; what was wrong was the conversion into it, which multiplied the differential by the
    market-average `CALIBRATION_ANNUAL_BILL_GBP` for EVERY household. A 3,000 kWh flat and a
    25,000 kWh house 10% above the market were therefore modelled as facing the same GBP 170
    shortfall, when the second faces several times that and, on the evidence, responds accordingly.
    Passing the household's OWN annual spend is the whole fix; the curve needed no recalibration.

    THE EVIDENCE THAT SETTLES IT, and it was published rather than reasoned about. Ofgem/BMG,
    *Understanding Consumers' Energy Tariff Choices* (n=3,235, fieldwork Mar-Apr 2024):
    *"consumers value savings in absolute terms rather than in proportion to their bill... it may
    benefit suppliers to frame savings in cash rather than percentage terms, i.e. GBP 150 and not a
    3% saving - particularly for customers with higher energy outgoings"*, and *"Reported household
    spending on energy has a very limited impact on how consumers evaluate prospective deals."*
    Its Table 3 is the same finding from the other side: the Spearman correlation between energy
    SPEND and switching propensity runs -0.07 to +0.05, i.e. a big bill barely changes how eagerly
    a household chases a given NUMBER OF POUNDS. What it changes is how many pounds a given
    percentage is worth to them, which is exactly what this argument now carries.

    WHAT IT MEANS ECONOMICALLY, because it is not a neutral refactor: customer value now scales
    with consumption. A large home is cheaper to win and dearer to lose per point of margin,
    because the same percentage buys a more visible saving. A percentage world cannot express that
    and this one now can — and consumption is OBSERVABLE to a supplier, so unlike the hidden
    sensitivity axis it is something the company can legitimately act on.

    `annual_bill_gbp=None` retains the market-average scale. That is correct for a caller with no
    household in hand and WRONG as a silent default at a renewal, where the supplier knows exactly
    what it has billed; `simulation.customer_events` therefore derives it from the household's own
    settled records rather than letting it default.

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
    instance of that shape found today, after the company's bill-shock churn cap and the
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
    bill = CALIBRATION_ANNUAL_BILL_GBP if annual_bill_gbp is None else float(annual_bill_gbp)
    differential = float(price_differential_pct)
    if differential <= 0.0:
        # Cheaper or at parity: the reciprocal of the win leg, exactly. No extrapolation is
        # involved and none is invented -- a keener price cannot take churn below the crisis
        # floor the market series already carries.
        return 1.0 / offer_position_multiplier(differential, bill)

    our_shortfall_gbp = differential * bill
    if our_shortfall_gbp <= _CALIBRATED_SAVINGS_CEILING_GBP:
        return 1.0 / offer_position_multiplier(differential, bill)

    beyond = our_shortfall_gbp - _CALIBRATED_SAVINGS_CEILING_GBP
    extrapolated_rate = _MAX_RATE + _LAST_INFORMED_SLOPE_PER_GBP * beyond
    return extrapolated_rate / _PARITY_RATE
