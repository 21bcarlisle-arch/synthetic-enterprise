# Pre-registration: which of the 446 bare world constants the production run reads

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Claim:** `anchor-the-446-bare-world-constants-in-impact-order`
**Written:** 2026-10-19, BEFORE the traced run below was launched.

## Definition, said before it is measured

A registered constant (`docs/design/world_constant_anchor_register.txt`) is **READ BY THE RUN** when
at least one source line that loads its name -- in its own module, or `from m import NAME` / `m.NAME`
in another `sim/` or `simulation/` module -- executes during one production run
(`python3 -m tools.run_annual_report`, the entry `background/sim_runner.py` launches, full
2016-2025 window, no `--fast`), recorded by `sys.monitoring` LINE events. Its own assignment line
does not count. A load that sits only on a `def` line (a default argument) is counted separately
as **DEFAULT-ONLY**: evaluated at import, and only binding if a caller omits the argument.

NOT READ means no published figure of that run can depend on it. It does not mean the constant is
wrong; it means anchoring it buys no published fidelity, and it ranks last.

Limits: one seed, one window, current founders setting. A constant read only by a probe, an arm or
an off-by-default switch reads as NOT READ here; that is the intended answer for ranking.

## Predictions (filed before the run)

- P1. Of 446, between 200 and 320 are READ.
- P2. `simulation/premise_trace.py` (60) is mostly READ (>40).
- P3. `simulation/fabric_physics.py` (48) is mostly READ (>30).
- P4. `simulation/feedback_survey.py` (11) and `simulation/sme_distress.py` (10) are mostly NOT READ.
- P5. `simulation/population_draw.py::DEFAULT_BAND_WEIGHTS` is READ.

## Then

Among READ constants, rank by a one-at-a-time sensitivity on the drawn book where the constant
enters the book's draw (`live_population()`, seconds per draw), and by the published-figure leg it
feeds otherwise. Anchor the top from published evidence or label each a range with a GAP.
