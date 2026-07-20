"""COUPLED-TRIAD runner for the W1_9 DSR/flexibility markets atom (L1).

The third loop of the flex coupled triad (COUPLED_TRIAD: SIM adds depth ->
COMPANY copes through the wall -> HARNESS measures the belief-vs-truth GAP;
the gap is the score). This is HARNESS code: it sits OUTSIDE the epistemic
wall and is the ONLY layer permitted to hold the SIM ground truth AND the
company belief side by side (design 1.3). It lives in `background/` (like
`weather_price_triad`), NOT under `company/`, so it may import both sides.

  1. SIM adds depth   -- sim.flex_dispatch (W1_9): dispatches enrolled flex on
                         the TRUE (residual-driven) scarcity schedule and
                         settles at the observed outturn price. Residual demand
                         is the hidden truth; only the dispatch instruction +
                         settlement line (observables) cross the seam.
  2. COMPANY copes    -- company.market.flex_participation: predicts dispatch
                         in the top price-percentile periods (a price-derived
                         scarcity PROXY) and forecasts utilisation revenue.
                         It sees ONLY the observed price -- never residual.
  3. HARNESS measures -- prediction_gap(true_revenue, expected_revenue): the
                         company's forecast utilised-revenue vector vs the
                         SIM's true utilised-revenue vector, normalised to the
                         no-skill (blind, climatological-mean) baseline. The
                         GAP is the L1 score.

R15 INDEPENDENCE / NOT A TAUTOLOGY. The truth dispatches on RESIDUAL DEMAND
(convex composed physics); the belief dispatches on PRICE percentile
(observables-only proxy). Different machinery -- residual drives price but is
not identical to it -- so the gap is a real form-inadequacy measurement. A
belief that recovered the true schedule would mean the observables leaked
residual (a wall violation, not a triumph). The mutation test
(`tests/background/test_flex_dispatch_triad.py`) proves the harness FIRES:
a divergent (price-proxy) belief yields gap > 0, while a leaking/perfect-
foresight belief collapses the gap to ~0 -- so the metric is neither hardwired
nonzero (fail-open) nor blind to divergence.

R12/R13. Nothing here is tuned to a target gap. The scarcity percentile is a
BASELINE structural choice (how often the world is tight), not fitted to any
company outcome. `enrolled_mw`/`period_hours` are illustrative and the
normalised gap is invariant to them, so no un-sourced £/MW figure moves the
score -- this atom is L1 ONLY (every real £/kW/yr, availability price, and
baseline-window figure remains BENCHMARK REQUIRED, source: NESO/Elexon).
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from sim.flex_dispatch import (
    DEFAULT_ENROLLED_MW,
    DEFAULT_PERIOD_HOURS,
    dispatch_and_settle,
)
from company.market.flex_participation import form_participation_belief
from background.gap_metric import prediction_gap

WORLD_ATOM_ID = "W1_9_dsr_flex_markets"
# The company twin registered for this world atom (the flex-participation
# belief facet). A dedicated C-atom id is a proposed follow-on; the flex
# participation module is the real twin meanwhile.
TWIN_ATOM_ID = "flex_participation_belief"


def measure(
    out: Optional[Dict[str, np.ndarray]] = None,
    *,
    enrolled_mw: float = DEFAULT_ENROLLED_MW,
    period_hours: float = DEFAULT_PERIOD_HOURS,
) -> Dict[str, object]:
    """Run the coupled loop and compute the L1 revenue gap.

    SIM truth dispatches on residual (hidden); the company forecasts from the
    OBSERVED price only. `out` may be injected (a small synthetic record) for
    a fast, deterministic run; None loads the real W1_6 derived-price record.
    Returns the gap plus enough numbers for a caller/test to quote the real
    values (true vs expected revenue, dispatch-set overlap)."""
    truth = dispatch_and_settle(out, enrolled_mw=enrolled_mw, period_hours=period_hours)

    # -- COMPANY side: only the OBSERVED price crosses. The company never sees
    #    residual; it infers scarcity from price. --
    belief = form_participation_belief(
        truth.outturn_price, enrolled_mw=enrolled_mw, period_hours=period_hours,
    )

    # -- HARNESS: hold truth and belief side by side; gap over the per-period
    #    utilised-revenue vectors. Normalised to the blind (climatological-mean)
    #    no-skill baseline by prediction_gap. --
    gap = prediction_gap(truth.true_utilised_revenue, belief.expected_utilised_revenue)

    overlap = int((truth.dispatch_mask & belief.predicted_dispatch_mask).sum())
    union = int((truth.dispatch_mask | belief.predicted_dispatch_mask).sum())
    jaccard = float(overlap / union) if union else 0.0

    return {
        "gap": gap.gap,
        "raw_gap_gbp": gap.raw_gap,
        "g0_noskill_gbp": gap.g0,
        "true_total_revenue_gbp": truth.total_true_revenue_gbp,
        "expected_total_revenue_gbp": belief.total_expected_revenue_gbp,
        "n_true_dispatch": truth.n_dispatch,
        "n_predicted_dispatch": belief.n_predicted_dispatch,
        "dispatch_set_jaccard": jaccard,
        "n_periods": int(truth.true_utilised_revenue.size),
        "gap_result": gap,
        "truth": truth,
        "belief": belief,
    }


def build_gap_summary(measurement: Dict[str, object]) -> Dict[str, object]:
    """Shape a compact, quotable summary of the L1 flex revenue gap for a
    digest / coupled-pair report. NOTE: this deliberately does NOT write to
    `docs/observability/coupled_gap_ledger.json` -- an un-wired entry on that
    shared surface reds its consumer's tests (a known hazard). Wiring the
    ledger line is a follow-on once the ledger consumer is extended for this
    pair; the gap is computed and asserted by the triad test meanwhile."""
    return {
        "world_atom": WORLD_ATOM_ID,
        "twin_atom": TWIN_ATOM_ID,
        "level": "L1",
        "metric": "prediction (per-period utilised-revenue MAE / no-skill)",
        "gap": measurement["gap"],
        "raw_gap_gbp": measurement["raw_gap_gbp"],
        "g0_noskill_gbp": measurement["g0_noskill_gbp"],
        "true_total_revenue_gbp": measurement["true_total_revenue_gbp"],
        "expected_total_revenue_gbp": measurement["expected_total_revenue_gbp"],
        "dispatch_set_jaccard": measurement["dispatch_set_jaccard"],
        "note": (
            "company forecasts flex utilisation from OBSERVED price (scarcity "
            "proxy); SIM truth dispatches on hidden residual demand -- the gap "
            "is that forecast error. L1: perfect delivery, one venue, "
            "scale-free units; L2+ benchmark-gated."
        ),
    }
