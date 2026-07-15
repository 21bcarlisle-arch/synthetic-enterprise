# ARCH1 step 1 — RSS profile: exogenous (replayable) vs endogenous (live) split

**Status:** measurement only. **No production code changed; no level moved (ARCH1 stays `level_current: 0`); no migration started.** This is the R4 smallest-closed-loop gate the `ARCH1_BUILD_SCOPING.md` "real path" step 1 called for: *bound the achievable memory win before migrating.*
**Author:** interactive session, 2026-07-15. **Window profiled:** 2016 truncated life (`report_end=2016-12-31`, `SIM_FAST_MODE=1`), the same window `tournament_runner` measured at 0.77 GB.
**Method:** no `memray`/`psutil` in-env → RSS attribution via `/proc/self/status` (VmRSS/VmHWM). Single-process boundary checkpoint: monkeypatched `sim.risk_committee.RiskCommitteeMonitor.__init__` (constructed in `run_phase2b.main()` immediately **after** all up-front exogenous-world construction and immediately **before** the settlement loop) to read RSS at the exogenous→endogenous boundary in the same process that then runs the loop to peak. Cross-checked against a separate exogenous-only process (per-item ledger). Scripts: `scratchpad/arch1_profile.py`, `arch1_profile_v2.py`.

## Headline (first-hand, reproduces the prior 674 MB and tournament_runner's 0.77 GB @ 2016)
- **Peak RSS 737.7 MB**; freeing the run output released **62.0 MB** → **non-output peak 675.7 MB** (matches `ARCH1_BUILD_SCOPING.md`'s ~674 MB exactly).

## Decomposition of the 737.7 MB peak (2016 window)
| Component | MB | % peak | % non-output | Replayable by ARCH1's mock? |
|---|---:|---:|---:|---|
| **Interpreter + libraries** (pymc ~208, pytensor ~111, numpy/pandas/code) | **~375** | 51% | 55% | **No** — fixed runtime floor, window-invariant |
| **Up-front EXOGENOUS world DATA** (SSP price history 134, HH smart-meter consumption 48, weather/cloud 11, misc) | **~197** | 27% | 29% | **Yes** — this is the recorded-trace target |
| **Loop working set** (transient exogenous shapes/curves + endogenous logs + output-build) | ~156 | 21% | 23% | Partly (the exogenous transient) |
| &nbsp;&nbsp;of which output payload | 62 | 8% | — | No (it's the output) |

The two-process ledger attributes the up-front exogenous data: **elec SSP records 134 MB** (20,207 rows incl. a 1yr lookback) and **half-hourly smart-meter consumption 48 MB** are the two big replayable items; weather/cloud ~11 MB; the price bitemporal log, `elec_price_lookup`, triad set, properties and household register are each <1 MB.

## The decisive fact — the exogenous world is what SCALES; the floor is fixed
`tournament_runner`'s own two measurements: **0.77 GB @ 2016 → 5.67 GB @ full 9.5-yr window** (we independently reproduced the 2016 end at 0.74 GB).
- The **~375 MB library floor is window-invariant** — it is **7% of the full-window RSS** but **51% of the 1-yr RSS**.
- The **~5.3 GB of growth (93% of the full-window RSS) is almost entirely the exogenous world scaling with the window** — SSP (~134 MB/yr), HH consumption (~48 MB/yr), weather all grow ~linearly with years; the endogenous book stays kilobytes-scale (customers accrete but the book is tiny regardless of window length).

## Verdict on the ARCH1 gate
The scoping doc posed the gate as: *"if most is endogenous machinery, the mock helps little and ARCH1 needs re-framing; if most is exogenous, the migration is justified."*

- **At the fidelity window that matters (full 9.5 yr), the exogenous world dominates (~93% of RSS is window-scaling exogenous data). → the migration IS justified; the FRAME's premise holds.**
- **But a truncated-window profile understates the win.** At 2016 the fixed pymc/pytensor library floor (51% of peak) masks the exogenous fraction (only 27% at 1 yr). Per-life RSS reduction from the mock is **window-dependent** — small at 1 yr, large at full window. Any future L1 evidence must be measured at (or extrapolated toward) the **full window**, not a truncated one, or it will look like the mock barely helps.
- **The mock's achievable floor is NOT near-zero.** A full-window mock life ≈ library floor (~375 MB) + a small recorded observable trace + the live endogenous book + output ≈ **sub-GB** (the FRAME's L1 target range, enough to lift `memory_safe_worker_cap()` off 1). The mock collapses the ~5.3 GB exogenous scaling, **not** the fixed floor.

## Secondary lever — noted, NOT actioned (scope discipline, register as candidate)
~319 MB of the fixed floor is **pymc + pytensor imported eagerly** somewhere in the `run_phase4c_on_phase2b` import chain (importing `sim.risk_committee` alone costs only 0.4 MB — it is a transitive import). If `SIM_FAST_MODE` skips the Bayesian risk model, **lazy-importing pymc/pytensor would shave ~300 MB off every life's floor** — a cheap memory win **orthogonal to ARCH1** (analogous to the tournament-truncation lever the scoping doc already noted). Candidate atom, director/twin to rank; do not action opportunistically.

## Open items for step 2 (the migration — NOT started this turn)
1. Confirm the SSP retention scales with the truncation window vs. always loading the full cache (the two `tournament_runner` measurements imply it scales, and we reproduced the 2016 end; a 2-yr vs 1-yr exo delta would nail it).
2. The observable **trace size** (what the company actually queries through the seam) is the real replacement cost — expected to be far below the 197 MB raw data, since the company reads derived observables (a forward price, a consumption baseline), not the full SSP dict. Measure it when the capture tool exists.
3. Finding-1 from the scoping doc still stands: the run path constructs **no `SimInterface`** today, so the migration is a real re-wire of the core run, incremental and behind the full suite — not a one-turn change. Step 1 does not change that; it justifies paying for it.
