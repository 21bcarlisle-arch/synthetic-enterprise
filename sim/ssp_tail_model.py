"""The MODEL's SSP (System Sell Price) TAIL -- step 3 (control-first) of the spike-tail attack plan
(docs/design/proposals/PROPOSE_SPIKE_TAIL_ATTACK_PLAN.md; defect SPIKE_TAIL_SSP_RESIDUAL).

WHY THIS EXISTS: sim/ssp_tail_target.py gives the REAL tail (the target, blind to P&L). To grade the
generator against it, the T1 tail-fidelity test needs the MODEL's tail computed the SAME way, from the
SAME generator that produces the ~GBP574 ceiling the defect is about. That generator is
sim/price_engine.py's residual-demand scarcity form (synthetic_price), applied across the real
gas/demand/renewable driver inputs -- exactly the series simulation/run_phase3b_recalibration.py fits
and whose distribution (max GBP574.22, 0.013% negative) is recorded in
docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md.

This module re-measures that tail from the generator directly (not by reading a stored figure -- that
would be a tautology, R15) so T1 is a genuine belief-vs-truth comparison: real target on one side, a
live generator measurement on the other, both through sim.ssp_tail_target.tail_stats (identical maths).
When the generator is later reshaped to reproduce the heavier real tail (step 3 physics change, a
supervised R13 build), THIS measurement moves and T1's strict-xfail trips -- the control retires itself.

BLIND TO COMPANY P&L (R12/R13): the model tail is a property of the BASELINE generator over real
drivers only; no company outcome participates. See test_ssp_tail_model.py::test_no_goalseek_path for
the mechanised no-write-back guard (T2).

Reproduce:  python3 -m sim.ssp_tail_model
"""
from __future__ import annotations

import json

import sim.price_engine as price_engine
from sim.ssp_tail_target import MODEL_END_DATE, MODEL_START_DATE, tail_stats


def model_ssp_series(start_date: str = MODEL_START_DATE, end_date: str = MODEL_END_DATE) -> list[float]:
    """The model SSP for every real settlement period with full driver data over [start, end]:
    price_engine.synthetic_price(gas, demand, renewable) with the calibrated module-level constants
    (carbon term 0.0, as in the recalibration fit). Reuses run_phase3b_recalibration._build_dataset so
    the drivers (incl. the AGWS latest-publish dedup) are identical to the fit that produced the
    recorded GBP574 ceiling. Raises (FAIL-CLOSED) if no rows can be built -- an uncomputable model tail
    is a failed check, never an empty pass."""
    # Local import: the recalibration script reads several large caches on import of its data helpers;
    # keep this module import-cheap and side-effect-free until the series is actually requested.
    from simulation.run_phase3b_recalibration import _build_dataset

    rows = _build_dataset()
    if not rows:
        raise ValueError(
            "no settlement periods with full driver data -- cannot compute the model SSP tail "
            "(FAIL-CLOSED: a missing model tail is a failed check, not an empty pass)"
        )
    return [
        price_engine.synthetic_price(r["gas_price"], r["demand_mw"], r["renewable_mw"])
        for r in rows
    ]


def model_ssp_tail(start_date: str = MODEL_START_DATE, end_date: str = MODEL_END_DATE) -> dict:
    """The model's SSP tail-shape block over [start, end] -- same shape as
    sim.ssp_tail_target.real_ssp_tail, computed through the shared tail_stats so T1 grades
    like-for-like."""
    series = model_ssp_series(start_date, end_date)
    return {
        "source": "sim/price_engine.py::synthetic_price over real gas/demand/renewable drivers "
                   "(via simulation.run_phase3b_recalibration._build_dataset)",
        "window": {"start": start_date, "end": end_date},
        **tail_stats(series),
    }


if __name__ == "__main__":
    print(json.dumps(model_ssp_tail(), indent=2))
