"""The company's reading of the published Renewables Obligation series.

WHAT THIS CLOSES (2026-08-19,
WORKER_FINDING_THE_REPORTS_RO_OBSERVATORY_PUBLISHES_TEN_YEARS_OF_RATES_THAT_MATCH_NO_PUBLICATION).
Three RO rate tables were carried as literals in this package — `roc_ledger`'s
`_ROC_OBLIGATION_LEVEL`/`_ROC_BUY_OUT_PRICE_GBP` and `renewable_obligation`'s
`_OBLIGATION_LEVEL_ROC_PER_MWH`/`_BUYOUT_PRICE_GBP_PER_ROC` — carrying THREE
different sets of values for TWO published series, none of which matched the
publications. `roc_ledger`'s pair reached `docs/reports/ANNUAL_REPORT.md`'s "RO Cost
Observatory" and understated the RO line by GBP486,458.88 (27.74%), while its own
docstring claimed the figures were the published ones and named a buy-out price
(GBP54.35 for 2023-24) that Ofgem published as GBP59.01. A citation is not an agreement.

THE SHAPE OF THE ERROR, which is why this module exists rather than twenty corrected
literals: `_ROC_OBLIGATION_LEVEL` rose by +0.006/yr for ten years without exception, and
`_ROC_BUY_OUT_PRICE_GBP` by ~3.4%/yr. The published series does neither — the level
plateaus, DIPS to 0.469 in 2023/24 and returns; the price went 52.88 -> 59.01 -> 64.73 ->
67.06. Smooth invented physics where the publication has a plateau, a dip and a spike.
Literal tables invite that shape; a load from the commons cannot express it.

WHY READING THE COMMONS IS NOT A WALL CROSSING. `docs/domain_artefact_library/` is the
regulation commons: the published regulatory TEXT, readable by every lane, because law is
published in reality (CLAUDE.md, regulation-commons doctrine; `.claude/hooks/lane_wall_hook.py`
SHARED_READABLE). What stays owned per lane is the READING — the segment filter, the
Apr-Mar bucketing of the company's own volumes, whether to price at buy-out or at the ROC
market, and what to do about the buy-out fund recycle. This module holds the company's
reading; `simulation/policy_costs.py` holds the world's, and they are allowed to differ.
What is NOT allowed is the two lanes holding different LAW, which is what three tables of
made-up numbers amounted to.

THE COMPANY'S READING, stated so it can be disagreed with:
  * price at the buy-out price, i.e. the compliance cost ceiling. The buy-out fund recycle
    (~GBP3.87/ROC in 2020-21) is redistributed pro rata to ROCs presented, so both routes
    arbitrage to obligation x buy-out; netting it off would double-count.
  * Great Britain only. The company supplies GB; the NI obligation is a different series.
  * the level as FINALLY SET for the year, including EII revisions, because that is the
    level the supplier was actually obligated at.

NO FAIL-OPEN PATH (R15). A missing, empty or malformed artefact RAISES at import. The
tempting alternative — fall back to the old literals, or to a plausible default — is the
fail-open shape that let a wrong figure publish for months: an unavailable check is a
failed check, and an unavailable LAW is not a licence to invent one.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

_RO_COMMONS_ARTEFACT = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "ro_obligation_and_buyout.json"
)

# Provenances this module will read. `recalled` is deliberately absent: a figure nobody
# fetched must not be served as the published law. If one ever appears, loading raises.
_ACCEPTED_PROVENANCE = ("primary", "secondary")


def _load_series(key: str, value_field: str) -> Dict[int, float]:
    """Read one published series from the regulation commons, keyed by obligation year.

    Raises on absence, emptiness, malformation, or an entry whose provenance says nobody
    fetched it. Every one of those is a FAILED read, never a quiet default.
    """
    if not _RO_COMMONS_ARTEFACT.exists():
        raise FileNotFoundError(
            f"RO commons artefact missing: {_RO_COMMONS_ARTEFACT}. The published "
            "obligation level and buy-out price are required; there is no invented default."
        )
    raw = json.loads(_RO_COMMONS_ARTEFACT.read_text())
    entries = raw.get(key)
    if not entries:
        raise ValueError(f"RO commons artefact has no {key}: {_RO_COMMONS_ARTEFACT}")
    series: Dict[int, float] = {}
    for entry in entries:
        provenance = entry.get("provenance")
        if provenance not in _ACCEPTED_PROVENANCE:
            raise ValueError(
                f"RO commons {key} entry for {entry.get('obligation_year')} has provenance "
                f"{provenance!r}: the company will not serve an unfetched figure as the law"
            )
        series[int(entry["obligation_year"])] = float(entry[value_field])
    return series


# ROCs per MWh supplied, Great Britain, by the year the obligation year COMMENCES
# (obligation year 2023 = OY 2023-24, 1 April 2023 to 31 March 2024).
OBLIGATION_LEVEL_ROC_PER_MWH: Dict[int, float] = _load_series(
    "obligation_levels", "roc_per_mwh"
)

# GBP per ROC, by the same obligation-year key.
BUY_OUT_PRICE_GBP_PER_ROC: Dict[int, float] = _load_series(
    "buy_out_prices", "gbp_per_roc"
)

# The DERIVED effective cost ceiling, GBP/MWh. Deliberately computed here and NOT carried
# in the commons: holding the two publishers' own series separately is what forces the
# multiplication to be performed rather than assumed, so a wrong level cannot be cancelled
# by a wrong price and still land on a plausible product.
EFFECTIVE_RO_COST_GBP_PER_MWH: Dict[int, float] = {
    year: OBLIGATION_LEVEL_ROC_PER_MWH[year] * BUY_OUT_PRICE_GBP_PER_ROC[year]
    for year in sorted(set(OBLIGATION_LEVEL_ROC_PER_MWH) & set(BUY_OUT_PRICE_GBP_PER_ROC))
}
