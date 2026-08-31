"""Company-observable market switching conditions -- Phase QB.

A real UK supplier tracks published switching statistics every year -- DESNZ Quarterly Domestic
Energy Switching Statistics, Energy UK, Ofgem Retail Market Indicators -- to gauge how much of
its book is genuinely at risk of leaving for a competitor, independent of its own rate decisions.
In a year where no fixed deal undercuts the default tariff (2022: wholesale costs exceeded the
price cap, suppliers withdrew fixed products), even large rate rises don't drive switching --
there's nowhere cheaper to go.

WHAT THIS MODULE GOT WRONG FOR THIS PROJECT'S WHOLE HISTORY, AND HOW.
------------------------------------------------------------------
`MARKET_SWITCHING_MULTIPLIER_BY_YEAR` was ten hand-authored numbers -- 2016: 2.17, 2020: 0.95,
2022: 0.44 -- under a docstring that said they were "derived from the same public switching-rate
series". They were not. Read back against the record they asserted 31.0% switching for 2016
(published 17.0-17.6%) and 13.6% for 2020 (published 22.5-23.0%). They correlated with the
published record at 0.40 across 2016-2025 and at MINUS 0.47 across 2016-2021: the table fell
monotonically from 2016 to 2022 while the record ROSE to its high-water mark in 2020. The
company's belief about competitive pressure had the wrong shape, not just the wrong size.

It survived because of its SHAPE, and that is the transferable part. The register that holds
every lane's reading of this series to the published band
(`tests/architecture/test_switching_rate_commons.py`) could only see RATE-shaped constants. A
number that looks like `0.95` rather than `22.8` passes every eye that knows to check percentages
against a published band -- so a live, wrong reading of a published series sat beside the control
written for exactly that defect, invisible to it, for six weeks. Found 2026-08-30 by following
the thread from the world's own multiplier; held open as a strict xfail; closed here.

THE REPAIR IS STRUCTURAL, NOT TEN CORRECTED NUMBERS. The normalisation is what destroyed the
level: a ratio has no units, so nothing could compare it with a publication. So the module now
carries the ABSOLUTE rate as its primary form, read from the regulation commons at import, and
DERIVES the multiplier from it. A hand-authored ratio cannot come back without the derivation
test firing, and the absolute table is held to the published band by name.

WHY READING THE COMMONS IS NOT A WALL CROSSING. `docs/domain_artefact_library/` is the regulation
commons: the published record, readable by every lane, because it is published in reality. What
stays owned per lane is the READING. `simulation/market_switching_propensity` holds the world's
and is allowed to differ from this; what is not allowed is the two lanes holding a different
RECORD, which is what a hand-authored copy amounted to. Same doctrine, same shape, and the same
repair as `company/regulatory/ro_commons.py`.

THE COMPANY'S READING, stated so it can be disagreed with:
  * the BAND MIDPOINT for each year. The commons publishes a range, not a scalar, and a supplier
    reading it has to read one number out. Where the record also states a point count -- 4.82m
    for 2016, 6.39m for 2020 -- the midpoint sits within 0.09pp of it, so nothing turns on the
    choice in the six years that have one, and in the four that do not the midpoint is the only
    non-arbitrary point. It is NOT the high end: §6's high-end tie-break is a CURRICULUM value
    governing where the WORLD is aimed, and the company's belief about the market is not the
    director's dial.
  * GB domestic ELECTRICITY external changes of supplier over all GB domestic electricity
    accounts. The commons' `basis` is the denominator, and the company inherits it whole rather
    than narrowing it to accounts at a renewal point, which reads about a third high.

NO FAIL-OPEN PATH (R15). A missing, empty or malformed artefact RAISES at import. Falling back to
the old literals, or to a plausible default, is the shape that let a wrong figure run for months:
an unavailable record is not a licence to invent one.

WHAT MOVED DOWNSTREAM, measured before landing rather than asserted (2026-08-31). The multiplier
is normalised to 2024, so correcting it is almost entirely a SHAPE change and barely a LEVEL one:
the geometric mean over the run window 2017-2024 moves 0.983 -> 0.963, under 2%. Individual years
move a lot -- 2021 by 2.23x, 2020 by 1.67x, 2017 by 0.51x -- and `competitive_pressure`'s
`PRIOR_LOG_VARIANCE`, computed from this table's own dispersion, moves 0.2442 -> 0.2563 (+4.9%),
which raises the weight the company puts on its own realised experience by about a point
(w = 0.812 -> 0.819 at n=100, p_expected=0.15). None of that is skill: the belief is now less
wrong about a published series it should never have been wrong about, which is an ordinary defect
corrected, and the independence-plus-inaccuracy reading of the old gap was never a credit.
"""
from __future__ import annotations

import json
from pathlib import Path

_SWITCHING_COMMONS = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "gb_domestic_switching_rate.json"
)

#: Provenances this module will read. A figure nobody fetched must not be served as the published
#: record; if one ever appears, loading raises rather than quietly narrowing the series.
_ACCEPTED_PROVENANCE = ("primary", "secondary")


def _load_published_rate_pct() -> dict[int, float]:
    """`{year: GB domestic electricity switching rate %}` from the regulation commons.

    The band midpoint, for the reason given in the module docstring. Raises on absence,
    emptiness, malformation, an unordered band, or an unfetched provenance -- every one of those
    is a FAILED read and never a quiet default.
    """
    if not _SWITCHING_COMMONS.exists():
        raise FileNotFoundError(
            f"GB domestic switching commons missing: {_SWITCHING_COMMONS}. The published "
            "switching record is required; there is no invented default."
        )
    raw = json.loads(_SWITCHING_COMMONS.read_text())
    rates = raw.get("rates")
    if not rates:
        raise ValueError(f"switching commons carries no rates: {_SWITCHING_COMMONS}")
    series: dict[int, float] = {}
    for entry in rates:
        provenance = entry.get("provenance")
        if provenance not in _ACCEPTED_PROVENANCE:
            raise ValueError(
                f"switching commons entry for {entry.get('year')} has provenance {provenance!r}: "
                "the company will not serve an unfetched figure as the published record"
            )
        lo, hi = float(entry["rate_pct_lo"]), float(entry["rate_pct_hi"])
        if not 0.0 < lo <= hi < 100.0:
            raise ValueError(
                f"switching commons entry for {entry.get('year')} has band ({lo}, {hi}), which "
                "is not an ordered rate range"
            )
        series[int(entry["year"])] = round((lo + hi) / 2.0, 2)
    return series


#: THE PRIMARY FORM, and it has units. What the published record says the GB domestic electricity
#: switching rate was, per cent of domestic electricity accounts per calendar year. Held to the
#: published band by name in `tests/architecture/test_switching_rate_commons.py`; that check is
#: only possible because this is a rate rather than a ratio.
MARKET_SWITCHING_RATE_PCT_BY_YEAR: dict[int, float] = _load_published_rate_pct()

#: The year the multiplier below is normalised to. 2024 is the post-ban equilibrium the churn
#: model's own base rates were fitted at, so `multiplier == 1.0` means "an ordinary recent year".
MULTIPLIER_REFERENCE_YEAR = 2024

#: DERIVED, never authored. Each year's published rate as a fraction of the reference year's.
#: `tests/architecture/test_switching_rate_commons.py` fires if this stops being the normalisation
#: of the table above -- which is the only way the ten hand-authored numbers could come back.
MARKET_SWITCHING_MULTIPLIER_BY_YEAR: dict[int, float] = {
    year: rate / MARKET_SWITCHING_RATE_PCT_BY_YEAR[MULTIPLIER_REFERENCE_YEAR]
    for year, rate in MARKET_SWITCHING_RATE_PCT_BY_YEAR.items()
}

DEFAULT_MULTIPLIER = 1.00


def market_conditions_multiplier(renewal_year: int | None) -> float:
    """Return the published market-switching-opportunity multiplier for `renewal_year`.

    Normalised so `MULTIPLIER_REFERENCE_YEAR` (2024, post-fairer-pricing-rule) = 1.0. Below 1.0
    means the published record shows less switching than that baseline (2022 crisis: 0.25, on a
    published 2.9-4.3%); above 1.0 means more (2020 high-water mark: 1.59, on a published
    22.5-23.0%).

    Returns DEFAULT_MULTIPLIER (1.0) for `None` or a year outside the published window.
    """
    if renewal_year is None:
        return DEFAULT_MULTIPLIER
    return MARKET_SWITCHING_MULTIPLIER_BY_YEAR.get(renewal_year, DEFAULT_MULTIPLIER)


def market_rate_move_pct(renewal_year: int | None, fuel: str = "electricity") -> float:
    """How far the WHOLE MARKET's domestic price moved into `renewal_year`, as a fraction.

    ``0.667`` = the market rose 66.7% that year; ``-0.208`` = it fell 20.8%.

    WHY THE COMPANY NEEDS THIS SEPARATELY FROM ITS OWN RATE CHANGE, which is the finding
    `WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED`
    (2026-08-25) exists to fix. A customer whose bill rises 60% because THIS SUPPLIER put its
    price up, and a customer whose bill rises 60% because the market did, are facing completely
    different decisions. The first has a cheaper alternative and it is obvious: the market
    average. The second has nowhere to go -- which is precisely the 2022 collapse in switching
    (bills at £3,549/yr, switching at 2.9-4.3%) that the published series this company reads
    records. Until now the company's churn model saw only the customer's own rate change
    and could not tell the two apart, so it read a market-wide move as if the company had made
    it, and -- the half that mattered -- read its OWN move with a sensitivity fitted to
    market-wide behaviour.

    DERIVED FROM THE PUBLISHED CAP, NOT WRITTEN DOWN, and read through the company's own cap
    module (`company/pricing/ofgem_price_cap.py`) rather than the world's. The Default Tariff
    Cap is the one domestic price series a real supplier can look up without knowing anybody
    else's book, it is a shared regulatory commons both lanes may read, and each lane's READING
    of it stays independently owned -- the same discipline `value_based_renewal.
    max_supported_rate_increase_pct` already had to be corrected into.

    Returns 0.0 -- no netting, unchanged behaviour -- when the year is unknown or falls outside
    the published schedule, because "the market did not move" is the only claim the company can
    make with no observation. That is a FAIL-SOFT and it is deliberate: it degrades to the
    pre-existing model rather than to a fabricated market move.
    """
    if renewal_year is None:
        return 0.0
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh

    try:
        now = get_cap_unit_rate_gbp_per_mwh(fuel, int(renewal_year))
        before = get_cap_unit_rate_gbp_per_mwh(fuel, int(renewal_year) - 1)
    except Exception:
        return 0.0
    if not now or not before or before <= 0.0:
        return 0.0
    return (now - before) / before
