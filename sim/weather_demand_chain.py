"""W1_5 weather -> DEMAND ground truth for the coupled-triad demand facet.

WHAT THIS IS. The SIM-side ground truth the company's weather-normalisation
belief (`company/pricing/weather_normalisation_belief.py`, C13) is measured
against. W1_5 (`simulation/premise_demand.py`) is the premise-level demand
physics: each premise responds to its OWN LOCAL weather (national + W1_4 regional
deviation) through a non-linear HDD/CDD kink, and the demand-weighted aggregate
reconciles to national demand by construction. That national aggregate IS the
observable demand outturn a supplier's settlement/forecasting desk sees. This
module exposes that ground-truth demand outturn -- the REAL 2016-2025 national
demand record (Elexon INDO) aligned to the real published weather -- as the
theta the harness measures the company belief against.

Why the REAL national demand record is the honest truth (R10 named simplification,
DISCOVER section 4). W1_5's own invariant is that premise demand reconciles TO
national demand; the real national demand outturn is therefore the W1_5-consistent
aggregate truth, and using it introduces ZERO fabricated constants (R10: no faked
calibration -- it is the real record). It stands in for a per-book demand series
pending the statistical power to fit one (DISCOVER section 4 confirms real weather
CSVs back only 4 locations across the ~31-account cast) -- a registered L1->L2
refinement, not a hidden approximation. The real record carries all the structure
a temperature-only degree-day belief cannot capture -- wind-driven heat loss
(CWV), working-day/daylight load, and the regional-dispersion convexity of the
W1_5 field -- so the belief-vs-truth GAP is a genuine form-inadequacy measurement,
not a tautology (R15 independence: the truth comes from the Elexon demand record,
the belief from an OLS degree-day fit -- different machinery).

THE WALL (CLAUDE.md Architectural Laws -- LOAD-BEARING). Demand formation is
SIM/world-side physics. NOTHING in `company/`/`saas/` imports this module. The
company observes ONLY its own confounded meter reads + published weather (as a
real supplier does); how the demand was physically formed is NOT observable. The
company's approximation of this lives on the far side of the wall in
`company/pricing/weather_normalisation_belief.py`, measured against this ground
truth by `background/weather_demand_triad.py` (the HARNESS, the only layer that
holds both). The belief-vs-truth GAP is the score.

R12/R13. Nothing here is tuned to a target gap. The demand record is the real
R13 baseline (published Elexon INDO), never adjusted because company results look
a certain way. The cold-windy tail is a MEASURED cell of the real record, not a
tuned output. Determinism (C-S2): pure reads of the cached real record, no clock,
no unseeded randomness.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

# The real aligned daily record (temperature, wind speed, month, dates, INDO
# demand, ...) is already assembled + cached by the price chain's loader. Reusing
# it keeps a SINGLE real-record substrate for both weather facets (price + demand)
# -- no second parse, no divergent alignment window.
from sim.weather_price_chain import load_daily_record

_WINTER_MONTHS = (12, 1, 2)


def demand_truth_on_record() -> Dict[str, np.ndarray]:
    """The ground-truth demand series (real national INDO demand, MW) aligned to
    the real published weather, plus the weather the company observes. `demand_mw`
    is the theta the company's weather-normalisation belief is measured against."""
    rec = load_daily_record()
    return {
        "dates": rec["dates"],
        "month": rec["month"],
        "temperature_c": rec["temperature_c"],
        "wind_speed_ms": rec["wind_speed_ms"],
        "demand_mw": rec["demand_mw"],      # the ground-truth actual demand (theta)
    }


def cold_windy_tail_mask(rec: Dict[str, np.ndarray]) -> np.ndarray:
    """The winter colder-AND-windier-than-median corner: winter days below the
    winter MEDIAN temperature AND above the winter MEDIAN wind speed -- the
    wind-chill cell a temperature-only degree-day belief cannot see (real heat loss
    rises with wind on cold days, the industry's CWV term). This is the demand-facet
    analogue of the price chain's cold-and-still tail, but with an EMPIRICAL twist
    worth stating: in the real GB record cold spells are typically anticyclonic and
    STILL, so the deep cold-AND-windy corner (20th temp pct / 80th wind pct) has only
    ~3 days -- too few to score. Using MEDIAN splits within winter yields a
    ~200-day cell that still isolates the wind-elevated-heat-loss days from the
    calm cold ones, so the wind-blindness of the belief is measurable rather than
    lost to sample size. A co-occurrence, not two marginals."""
    winter = np.isin(rec["month"], _WINTER_MONTHS)
    if not winter.any():
        raise ValueError("no winter days in the record")
    t_med = float(np.median(rec["temperature_c"][winter]))
    w_med = float(np.median(rec["wind_speed_ms"][winter]))
    return winter & (rec["temperature_c"] <= t_med) & (rec["wind_speed_ms"] >= w_med)
