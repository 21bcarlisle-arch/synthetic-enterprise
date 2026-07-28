<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: propose_then_proceed -- merit-order/gas-first engine reconstruction; BUILD held behind its propose-then-proceed window, then registers to the map at build-draw -->
<!-- DISPOSITION 2026-07-25: FRAME landed (scope items 1 & 3) →
     docs/design/frame/W1_6_merit_order_reconstruction_FRAME.md (live-vs-target form + exact diff,
     evidence-cited to sim/price_engine.py + the W1_6 fidelity row; acceptance test + unmoved-baseline
     invariant + R15 mutations defined). Scope item 2 DISCOVER now DISCHARGED as far as published GB
     sources allow (network available 2026-07-25 pass) →
     docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md (DUKES 5.10.C/5.14 per-type
     efficiencies + emission factors, EF_GAS 0.184 CONFIRMED, UK Carbon Price Support ~£18/tCO₂ time-
     invariant 2016–2025; 4 residual R10 gaps left explicit — ETS annual traded price, OCGT efficiency,
     coal VOM, %-marginal-hours). BLOCKED now (was self-drawable): NO drawable-now work remains — the
     DISCOVER is discharged and the only open sub-item is the engine BUILD, held behind the propose-then-
     proceed window until 2026-07-28 (R13 baseline discipline; no interim tuning). blocked_on: propose-
     then-proceed BUILD window closes 2026-07-28 (then registers to the maturity map at build-draw,
     level moves stay blocked_on: director_level_up). The daily planner re-plan re-evaluates it. -->

# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — Merit-order / gas-first price-engine reconstruction: DISCOVER + FRAME (2026-07-25)

**Provenance:** RUNG-7 planner refill (director ruling `WORK_IS_THE_DEFAULT_2026-07-23`). Minted from a ratified goal, not a doorbell: the director's ruling `DIRECTOR_RULING_SSP_BASELINE_HELD_MERIT_ORDER_FIRST_2026-07-25.md` **names** the merit-order reconstruction as the real fix but leaves it **un-drawn** — no atom, no mint. This doc makes that named next-step drawable (R16: the ledger/register is authority; a fix named only in a ruling body is invisible to the draw).

**Serves:**
- **DIRECTOR_AXES axis 3 (Believability)** — "does it feel like the real UK market to a 20-year veteran." On ordinary GB days the marginal plant is a gas CCGT and price ≈ gas-over-efficiency + carbon; a residual-demand scarcity term should earn its structure only in *tight* hours. The live single-global scarcity form does not reconstruct ordinary days from fundamentals — the veteran smell test fails on exactly the point Board Spec 004 makes central.
- **Fidelity evidence ledger row `W1_6_physics_price_signal` (`ssp_residual_demand_scarcity_calibration_2026_07_19`)** — the row's own `simplification_note` records the defect: the global form UNDER-FITS renewables-heavy low-x calm years, losing to a per-cell OLS in 6 of 10 cells (y2019 −0.79 … y2020 −3.22 … y2025 −2.28); the +1.17 aggregate lift is carried almost entirely by 2022 crisis. This is the fidelity row this work repairs.
- **The named unblock for `PLANNER_MINTED_ssp_negative_lift_cells` part (a)** — that mint's part (a) is HELD with unblock condition rewritten to *"the merit-order reconstruction has landed."* Nothing draws that condition closed until this reconstruction exists.
- **Board Spec 004 (Price Formation) reconstructibility** + **convergence with Board Spec 001 gas-first finding (F1)** — the ruling records that F1 arrives here from a second independent direction; this doc is where that convergence is designed, not just noted.
- **VALUE_CHAIN work** — the ruling sequences the reconstruction "with the VALUE_CHAIN work and the Spec 004 reconciliation"; this DISCOVER frames that seam ([[project_wholesale_value_chain_frame]]).

**Fidelity gained (one sentence):** the SSP price engine moves from a single reduced-form residual-demand scarcity curve that under-fits ordinary renewables-heavy days to a merit-order / gas-first structure where ordinary-day price is substantially reconstructible from gas + carbon + demand + wind and a scarcity term earns its keep only in tight hours — the difference between pricing that is *right* and pricing that merely *looks right now*.

---

## Scope — DISCOVER / FRAME only (doc-only; drawable NOW)

Per `EPOCH_GATING_AND_ATOM_AUTHORSHIP` and THREE_LANES L3, DISCOVER/FRAME/research is available now regardless of BUILD epoch-gating. This mint's **drawable-now** half is doc-only and touches no engine code:

1. **FRAME the live form vs the target form.** One page, evidence-cited: what `sim/` price formation does today (the fitted A0/A1/A2 residual-demand scarcity constants, `sim/gas_prices_history.py` NBP floor), and what a merit-order / gas-first form is (SRMC stack = fuel-cost/efficiency + carbon per plant type, dispatched against residual demand; scarcity as a tight-hours term, not an every-hour multiplier). Name the exact diff.
2. **DISCOVER the ground truth** (delegate to `discovery-agent`, read-only, output to `docs/market_research/`): published GB plant-stack heat rates / efficiencies, CCGT SRMC build-up (NBP gas + UK ETS/carbon), typical merit order and where gas sets the margin, from Elexon/NESO/BEIS/Ofgem public sources. **Pre-load ground-truth context before any local model touches sources** (key learning). No fabricated constants — cite or leave a named gap (R10).
3. **DEFINE the acceptance test — the reconstructibility test, before any build.** Spec 004: "power must be substantially reconstructible from gas + carbon + demand + wind on ordinary days." Write the falsifiable ordinary-day reconstruction check AND the invariant: **re-measure the SAME `W1_6` per-cell lift table against the SAME naive baseline family, unmoved** — the ruling's own test of *right vs tuned*. State the R15 mutation the test must survive.

## BUILD — HELD (behind the propose-then-proceed window + R13 discipline)

- **Propose-then-proceed window: open until 2026-07-28 (72h from mint).** The FRAME + DISCOVER + acceptance-test-design half is the "then propose" artefact; the actual engine reconstruction (BUILD) is held for director/advisor revision of the form or the acceptance bar during the window. A tick after 2026-07-28 with no director revision → the BUILD sub-atoms register to the maturity map at build-draw (level moves stay `blocked_on: director_level_up`).
- **R13 baseline discipline (binding, not a wall against building):** the baseline world changes for **fidelity-to-reality reasons only, decided blind to company P&L**. This reconstruction is motivated by reconstructibility-from-fundamentals, never by how company results look. **No interim tuning** — no per-cell fits, no regime-partition coefficient passes, no "temporary" recalibration while the structural work waits (R12 unchanged; the ruling forbids exactly this).
- **Acceptance:** landed only when the reconstructibility test passes on ordinary days AND the `W1_6` lift table, re-measured against the unchanged naive baseline, holds — that unmoved measurement is the proof pricing became right rather than tuned. Do not re-baseline the benchmark to suit the new engine.

## Walls untouched (director-reserved)

- **Curriculum values** (scenario mix, difficulty) — R13, director-reserved; this touches the **baseline** price-formation form (fidelity), never the curriculum.
- **One-way doors** — none touched; DISCOVER is doc-only and reversible; the BUILD is a git-reversible sim change behind the epistemic wall (no real market, no real money).
- **L3 level moves** — any level claim stays `blocked_on: director_level_up`.
- **Ground-truth fabrication forbidden** — DISCOVER cites published sources or registers a named gap; it never invents plant efficiencies or carbon costs.

— Planner mint, RUNG-7 refill, 2026-07-25.
