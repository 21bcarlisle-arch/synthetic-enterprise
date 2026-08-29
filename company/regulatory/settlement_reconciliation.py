"""Elexon BSC settlement reconciliation cash flow exposure model.

UK electricity suppliers receive reconciliation adjustments up to 28 months
after each settlement day via the R1/R2/R3/RF run sequence. These runs
correct metering errors, re-read data, and finalise consumption volumes.

For suppliers, this creates:
  - Outstanding reconciliation pool: billed revenue still subject to adjustment
  - Direction uncertainty: adjustments can be credits or charges
  - Crisis-year bias: during price spikes, demand destruction causes
    actual < estimated consumption -> net credit in late reconciliation

Non-HH (profile class, resi/SME): ±4% variance on billed units.
HH (I&C with sub-half-hourly metering): ±0.5% variance.
Source: Elexon Settlement Performance Reports; Ofgem supplier review data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


# Reconciliation variance bands (fraction of billed kWh potentially adjusted)
_HH_RECON_VARIANCE = 0.005     # ±0.5% for HH-metered I&C customers
_NON_HH_RECON_VARIANCE = 0.040  # ±4.0% for profile-class non-HH meters

# Settlement run timeline (months after delivery date)
#
# VERIFIED 2026-08-29 against an Elexon-authored primary document read directly -- slide 2 of
# "Settlement Timetable, Electricity settlement expert group", Jonathan Priestley, Elexon,
# 16 June 2014, hosted at ofgem.gov.uk. Write-up and the full table:
# `docs/market_research/elexon_settlement_run_timetable_verified.md`.
#
# WHAT WAS WRONG, AND IT WAS THE SAME MISTAKE FOUR TIMES PLUS ONE WORSE ONE. Every scheduled
# timing was too early (1/3/5 against 2/4/7), and `_RF_MONTHS = 28  # Final Reconciliation`
# named the wrong run entirely: 28 months is **DF**, the dispute rectification run that only a
# disputed Settlement Date ever reaches (the same deck, slide 7: "90 Disputes were closed in
# 2013. 58 were upheld, and 56 used the DF run"). RF -- the LAST SCHEDULED run, the one that
# closes the normal correction window for every day -- is 14 months. So this model had every
# ordinary settlement day carrying a dispute-length tail.
#
# PROVENANCE OF THE OLD NUMBERS, because the lesson is in how they got here. This file's
# source line is a general attribution ("Elexon Settlement Performance Reports; Ofgem supplier
# review data"), not a citation for any of these values.
# `docs/market_research/settlement_rebilling_best_practice.md` (2026-07-12) had ALREADY said RF
# was "roughly 12-14 months", tagged [M], and asked explicitly that its offsets "be verified
# directly against Elexon's BSC Section T / published Settlement Calendar ... rather than
# hard-coded from this recall". Code had hard-coded a different figure than the note it was
# meant to defer to, and then `f4_international_expansion_probe.md` read 28 back OUT of here as
# the sourced GB fact and built a GB-vs-SEMO comparison on it. A constant read back out of code
# acquires a provenance it never had.
#
# VINTAGE, bounded rather than assumed: the deck is 2014 and argues the case for reform, so the
# fair question is whether it still describes 2016-2025. It does. Elexon's own MHHS material
# says "the current Settlement process takes 14 months", falling to four only under Market-wide
# Half-Hourly Settlement, whose central systems went live 24 September 2025 --  AFTER
# `run_phase2b.REPORT_END` (2025-06-07). So 14 applies to the whole modelled window with no
# time-variation to model.
_R1_MONTHS = 2
_R2_MONTHS = 4
_R3_MONTHS = 7
_RF_MONTHS = 14  # Final Reconciliation -- the LAST SCHEDULED run. DF (disputes only) is 28.

# Share of total reconciliation volume resolved at each run.
#
# FROM ELEXON'S OWN CURVE, same slide, rather than from the shape of an argument. The deck plots
# NHH energy settled on ACTUAL data cumulatively: 30% at R1, 60% at R2, 80% at R3, 97% at RF.
# The increments are 30/30/20/17 of 97, which normalise to the four values below.
#
# The old 0.60/0.25/0.12/0.03 was commented "80% of errors found in R1/R2; long tail into RF is
# small but persistent". Elexon's curve puts 62% in R1/R2, not 80%, and 17% at RF against the 3%
# claimed here.
#
# WHAT IT DOES TO THE PUBLISHED NUMBER, PRINTED BEFORE BEING ASSERTED -- and the first draft of
# this comment asserted the opposite direction from a plausible argument without computing it,
# which is the exact move CLAUDE.md's "print the numbers at real inputs" rule exists to stop.
# Weighted months outstanding at year end:
#
#     old (1/3/5/28, .60/.25/.12/.03)   4.4600 months   pool fraction 0.3717
#     new (2/4/7/14, per Elexon)        2.9899 months   pool fraction 0.2492
#
# and the two corrections pull in OPPOSITE directions, with the timings winning eight to one:
#
#     timings alone, old shares   4.4600 -> 2.7900   (-1.67)
#     shares  alone, new timings  2.7900 -> 2.9899   (+0.20)
#
# So the dominant effect is RF 28 -> 14 collapsing the R3-to-RF tail from 23 months to 7, and the
# later-weighted shares claw back only an eighth of it. The corrected model reports a THIRD LESS
# outstanding exposure than the old one -- the old figure was inflated by carrying a dispute-run
# tail on every ordinary settlement day, not by anything about the share table.
_R1_SHARE = 0.3093
_R2_SHARE = 0.3093
_R3_SHARE = 0.2062
_RF_SHARE = 0.1752  # the remainder, so the four sum to exactly 1.0

# RAG thresholds: max adverse adjustment as % of monthly revenue
_GREEN_THRESHOLD = 5.0   # < 5% of monthly revenue
_AMBER_THRESHOLD = 15.0  # < 15% of monthly revenue


@dataclass(frozen=True)
class ReconciliationExposure:
    year: int
    annual_revenue_gbp: float
    hh_fraction: float            # fraction of revenue from HH-metered customers
    outstanding_pool_gbp: float   # approx volume still subject to adjustment at year-end
    max_adverse_gbp: float        # worst-case one-sided adjustment
    expected_adjustment_gbp: float  # expected |net| adjustment (zero-mean, this is 1-sigma)
    months_outstanding: float     # weighted-avg months until final settlement
    rag: Literal["GREEN", "AMBER", "RED"]
    is_crisis_year: bool          # crisis-year bias: expect net credit in late reconciliation


def _blended_variance(hh_fraction: float) -> float:
    """Weighted average reconciliation variance across HH and non-HH meters."""
    return hh_fraction * _HH_RECON_VARIANCE + (1 - hh_fraction) * _NON_HH_RECON_VARIANCE


def _outstanding_months_at_year_end() -> float:
    """Weighted-average months of outstanding reconciliation tail at any year-end.

    At year-end, the most recent 14 months of deliveries are still partially open —
    RF is the last scheduled run and closes the window (28 was DF, the dispute run;
    corrected 2026-08-29, see the constants above):
    - Current year (12 months): in the R1/R2/R3 tail — high volume, resolving
    - Prior year (2 months): still in the R3-to-RF tail

    Returns a consumption-weighted average months outstanding.
    """
    # Weight by share outstanding × remaining months. The comments name what each run
    # LEAVES OPEN until the next one, so they are derived from the constants above and
    # move with them rather than restating a frozen arithmetic.
    r1_remaining = _R2_MONTHS - _R1_MONTHS   # open from R1 until R2
    r2_remaining = _R3_MONTHS - _R2_MONTHS   # open from R2 until R3
    r3_remaining = _RF_MONTHS - _R3_MONTHS   # open from R3 until RF
    rf_remaining = 0                          # RF is final

    weighted = (
        _R1_SHARE * r1_remaining +
        _R2_SHARE * r2_remaining +
        _R3_SHARE * r3_remaining +
        _RF_SHARE * rf_remaining
    )
    return weighted


def _rag(max_adverse_gbp: float, monthly_revenue_gbp: float) -> Literal["GREEN", "AMBER", "RED"]:
    """Rate settlement exposure against the revenue available to absorb it.

    The zero-revenue guard exists to avoid a divide-by-zero, but returning GREEN
    answered "is this exposure safe?" with "yes" when it should decline to
    reassure: open settlement exposure with NO revenue behind it is the worst
    state a supplier can be in -- the SoLR shape exactly -- and it was the one
    input on which this control could not fail (R15). A negative max-adverse is
    corrupt input, not a gain, and is likewise not evidence of safety.
    """
    if max_adverse_gbp < 0:
        return "RED"
    if monthly_revenue_gbp <= 0:
        # Nothing at risk is genuinely green; exposure with no revenue is not.
        return "GREEN" if max_adverse_gbp == 0 else "RED"
    pct = max_adverse_gbp / monthly_revenue_gbp * 100
    if pct < _GREEN_THRESHOLD:
        return "GREEN"
    if pct < _AMBER_THRESHOLD:
        return "AMBER"
    return "RED"


_CRISIS_YEARS = {2021, 2022}


def build_reconciliation_series(
    management_accounts: dict,
    hh_revenue_fraction: float = 0.90,
) -> List[ReconciliationExposure]:
    """Compute per-year settlement reconciliation exposure.

    Args:
        management_accounts: dict keyed by year string with revenue_gbp per year.
        hh_revenue_fraction: fraction of revenue from HH-metered I&C customers.
            Default 0.90 reflects an I&C-dominated portfolio (confirmed Phase NV).
    """
    by_year = management_accounts.get("by_year", {})
    if not by_year:
        return []

    variance = _blended_variance(hh_revenue_fraction)
    outstanding_months = _outstanding_months_at_year_end()
    result = []

    for yr_str in sorted(by_year.keys()):
        yr = int(yr_str)
        rev = by_year[yr_str].get("revenue_gbp", 0.0)
        if rev <= 0:
            continue

        monthly_rev = rev / 12.0
        # Outstanding pool: fraction of annual revenue still in reconciliation tail
        # Approximation: 12 months of deliveries × weighted outstanding fraction
        pool_fraction = outstanding_months / 12.0  # e.g. 2 months / 12 = 0.17
        pool = rev * pool_fraction
        max_adverse = pool * variance
        # Expected adjustment (1-sigma for zero-mean process)
        expected_adj = max_adverse * 0.5  # 1-sigma is roughly half the maximum band

        rag = _rag(max_adverse, monthly_rev)
        result.append(ReconciliationExposure(
            year=yr,
            annual_revenue_gbp=round(rev, 2),
            hh_fraction=hh_revenue_fraction,
            outstanding_pool_gbp=round(pool, 2),
            max_adverse_gbp=round(max_adverse, 2),
            expected_adjustment_gbp=round(expected_adj, 2),
            months_outstanding=round(outstanding_months, 1),
            rag=rag,
            is_crisis_year=yr in _CRISIS_YEARS,
        ))

    return result


def largest_exposure_year(
    series: List[ReconciliationExposure],
) -> Optional[ReconciliationExposure]:
    if not series:
        return None
    return max(series, key=lambda r: r.max_adverse_gbp)
