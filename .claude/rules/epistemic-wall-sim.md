---
paths:
  - "sim/**/*.py"
  - "simulation/**/*.py"
---

# You are editing the SIM/WORLD side of the epistemic wall

This code is the WORLD — real historical settlement data (Elexon/NESO), synthetic curriculum/future
generation, weather, churn parameters, VaR internals. It knows things the company must NOT be able to
see directly.

- **Never import `company.*` or `saas.*` modules from here** in a way that leaks internal SIM state
  back to the company layer through a side channel — the only sanctioned crossing point is
  `company/interfaces/sim_interface.py`, and it is the interface-steward role's job to guard it, not
  a call this layer should ever make unilaterally.
- **Baseline vs curriculum (R13):** the BASELINE world (real 2016-25 history + externally-calibrated
  generators) may only change for fidelity-to-reality reasons, decided blind to company P&L — never
  tuned because company results look wrong. The CURRICULUM (scenario batteries, population draws,
  stress regimes, generated futures) is the DIRECTOR'S instrument: difficulty changes are named,
  versioned, director-authored artefacts, never silent parameter drift, and never adjusted by the
  agent in response to company outcomes.
- **`data_regime` field:** every record should carry `"historical"` or `"synthetic"` — the boundary
  marker between real data and generated data. Do not drop this field when adding new record types.
- If a change here could plausibly let the company observe something it shouldn't (a shared cache, a
  global keyed by a value the company also reads, timing that reveals future information), treat it
  as Tier-1 (the epistemic law) — flag explicitly rather than assuming it's fine because it's "just
  the sim side."
- Run `python3 -m tools.epistemic_verifier` before committing — it checks data-flow direction, not
  just which file the code lives in.
