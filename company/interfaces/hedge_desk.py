"""Seam: the world asks the desk how much of a term is bought forward, and books it.

KNIFE pass 3, `A_composition_lift` step 23, 2026-08-13, disposition register
§3r. Before this, `simulation/run_phase2b.py::main()` ran the supplier's own
hedging desk itself — holding the mandate floor and deriving the naked fraction
from it, taking the VaR decision at both commodity sites, adjudicating the risk
committee's override against that decision, assembling the VaR log entry,
pricing the bid-ask spread, attributing a counterparty, constructing the forward
contract, holding the trading book, settling every period against it, and
rolling the fraction forward from the completed term's P&L. Three of that
module's wall crossings (`company.trading.forward_book`,
`company.trading.hedge_decision`, `company.risk.hedge_policy`).

Now the world hands over what it can observe — its own demand estimate, the
forward it locked, the tariff it proposes, and a PUBLIC price history it has
already put through the point-in-time blindfold — and takes back a `TermHedge`.
The VaR model, the mandate floor, the bid-ask calibration, the counterparty
bands and the roll rule are unreachable from the SIM; what crosses is this one
door, in one direction, per term.

THE READ DIRECTION IS WHY THIS IS A CUT AND NOT A FILE MOVE — the same test §3f
applied to bill assembly, §3i to the month-end close, §3l to the statutory
return, §3m to the flexibility book, §3n to the collateral desk and §3q to the
commercial pair. `company/trading/hedge_desk.py` imports nothing from
`simulation/` or `sim/`: the price history arrives as plain records through this
signature. Had the composition been moved with a `simulation.*` import intact it
would have traded class-(b) crossings for class-(a) ones, the strictly forbidden
direction, which is at zero and stays there.

WHAT THIS DID NOT DO, AS OF STEP 23. `run_phase2b` kept the pricing/regulatory
group (`tariff_engine`, `margin_feedback`, `ofgem_price_cap`, `decision_policy`)
and the `saas.*` set. Stated rather than left to be discovered from a count that
stops at 3.

ALL OF THOSE ARE NOW CUT — updated 2026-08-18, KNIFE3 step 39 (register §3ah).
The pricing three went at step 24 (§3s) and `decision_policy`, the last of them
and the last live crossing on that module, went at step 39. `run_phase2b` has
ZERO live wall crossings and `A_composition_lift` is paid off.

The last one landed HERE as well as in the growth desk, and the piece worth
knowing when reading `decide_term_hedge` below: the world used to gate both call
sites on `policy.use_var_hedge_decision`, reading the supplier's Phase-43b switch
to decide whether to consult the supplier's desk. The desk now decides, resolving
that switch from the run's active policy and returning `None` when the layer is
off. So `decide_term_hedge` is typed `TermHedge | None`, and a caller must handle
the decline — it is not an error path, it is the supplier saying it is not taking
VaR-constrained decisions this run.
"""

from __future__ import annotations

from company.trading.hedge_desk import (
    HedgeDesk,
    HedgeMandate,
    TermHedge,
    build_hedge_desk,
    hedge_mandate,
)

__all__ = [
    "HedgeDesk",
    "HedgeMandate",
    "TermHedge",
    "build_hedge_desk",
    "hedge_mandate",
]
