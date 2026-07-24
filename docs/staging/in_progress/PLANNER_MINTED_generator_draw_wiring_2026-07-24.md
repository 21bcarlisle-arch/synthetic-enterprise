# [PLANNER-MINTED] Ship the population-generator DRAW-WIRING (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, origin commit 4b31c60d6, PRODUCT-FIRST item 2). **Scope step 1 (FRAME) DONE — see the FRAME section below. Scope step 2 REVERSIBLE HALF (the default-OFF seam) + step 3 (R15 both-ways) DONE this tick — see "BUILD (reversible half)" below.**
> **BLOCKING SUB-ITEM (open):** The R13 **ACTIVATION** — flipping `SE_DRAW_POPULATION=1` on AND wiring the ~19 `run_phase*` entrypoints to consume the seam — changes which world the company faces every run, reserved to the director (W2_2's own ruling + the 2026-07-24 waiver's "curriculum values remain director-reserved"). The reversible mechanism is now BUILT and tested default-OFF; **UNBLOCKS ON:** a director word authorising live activation. Escalated via NTFY (prior tick + this one). Per ESCALATION_IS_NTFY the reversible half shipped; only the irreducible activation core is held.

---

## BUILD (reversible half) — DONE 2026-07-24 worker tick

Section D's proposed next step, shipped:
- **`simulation/live_population.py`** — the single population accessor seam. Default-OFF it returns the static `CUSTOMERS` book (byte-identical); with the director-reserved `SE_DRAW_POPULATION=1` flag it ADDITIVELY appends the synthetic SYN-* 2021-2025 acquisition cohort via `SyntheticCustomer.to_customer_dict()` (ground-truth `cohort` excluded by construction). Does NOT wire itself into any entrypoint — that wiring + the flag flip are the held activation.
- **`tests/simulation/test_live_population_seam.py`** — R15 BOTH-WAYS (8 tests, all green): flag-on adds SYN-* (wire is load-bearing) / flag-off reverts EXACTLY to the static book (mutation proves the SYN entries come from the flag, not an unconditional path); + determinism/replay (C-S2), + the epistemic-wall guard (no returned dict ever carries `cohort`), + the seam imports no `company` logic.
- **Gates:** `tools/epistemic_verifier` PASS (491 files, no barrier violations); the pre-existing `test_cohort_draw_default_off_is_byte_identical` still green (seam did not perturb the generator).
- **Honest activation-time follow-on (not silent):** SYN-* dicts and static `CUSTOMERS` dicts do not share an identical key set — entrypoints must be hardened to the SYN shape BEFORE the flag flips on. That hardening is part of the held activation, documented in the module docstring.

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Rungs 1–6 drew empty this tick; minted from a ratified goal. **Propose-then-proceed.**

## Ratified goal served
- **DIRECTOR_AXES v1 — Axis 2 (Segmentation), "Sophistication":** *real coupled structure, discoverable through the wall (ground truth behind the epistemic seam; the company starts from EPC/census priors and discovers via interaction).*
- **PRIORITIES.md PRODUCT-FIRST item 2 (verbatim):** *"Generator draw-wiring — its blocking input (the segments verdicts) landed; ship the draw so the richer population exists."*

## Why this is drawable now (not a wall)
The **generator design / ground truth is director-reserved** (segmentation memory) — that wall is untouched. What is authorized and *un-shipped* is the **DRAW-WIRING**: the blocking input (the segments verdicts, W2_2 / the segmentation taxonomy fold) has landed, so wiring the generator's draw into the live population path is a reversible build under standing PRODUCT-FIRST authority, not a values call.

## Real-world fidelity gained
Today the live book is a thin population (the front-door "14 homes" / "1,588 bills" figures rest on a small synthetic book). Wiring the richer segment-coupled generator into the run makes the population it prices, bills, and discovers-through-the-wall actually *have* the coupled EPC/census structure the axis demands — the difference between asserting segmentation sophistication and the run exhibiting it. This is the substrate every Axis-2 "efficiency" (value-per-segment) claim later rests on.

## Scope (propose)
1. FRAME: confirm the generator's current callable surface + the exact seam it must feed (sim→company population path), and which segment fields are now verdict-backed vs still priors-only. Name any field that would cross the wall as ground-truth (must NOT) vs be a discoverable observable (allowed).
2. BUILD the draw-wiring behind the existing typed seam (no new billing/pricing engine — portability constraint; product as first-class).
3. R15 both ways: a test that the live run's population now carries the coupled segment structure (fires on the wiring present), and that removing the wiring reverts to priors-only (mutation proves the wire is load-bearing, not decorative).
4. Verify no wall regression: run the epistemic-verifier on the diff (no segment ground-truth field reads into company logic).

## Walls untouched
Generator ground-truth / curriculum values (director-reserved); no L3 level move (leave `blocked_on: director_level_up` if the wiring reaches L3 quality); one-way doors N/A.

## Propose-then-proceed window
Proceeds under standing PRODUCT-FIRST reversible-build authority. If a genuine wall (a field that can only be sourced from generator ground truth) is hit, decompose per ESCALATION_IS_NTFY: build the reversible part, NTFY the irreducible core, keep drawing. Default: proceed.

---

## FRAME (Scope step 1) — DONE 2026-07-24 worker tick (doc-only, epistemically safe)

**A. The generator's current callable surface** (`simulation/population_draw.py`, atom `W2_2_population_draw`, L1 mechanism built + tested, NOT live):
- `draw_population(...)` / `iter_acquisition_events(...)` / `_draw_one(...)` — an **additive** per-run stochastic draw producing a synthetic `SYN-*` cohort on top of the 24 hand-authored core customers (the additive-not-replacive FRAME decision already on the atom, so all ~370 downstream `customer_id` references survive). Own SHA-256-named substream (`W2_2_cohort_draw`), deterministic replay, C-S1/C-S2 honoured.
- Cohort enrichment (`assign_cohort(...)`, `assign_cohorts` param) is **DEFAULT OFF** across `_draw_one`/`iter_acquisition_events`/`draw_population` — output is proven byte-identical when off (`test_cohort_draw_default_off_is_byte_identical`).

**B. The exact live seam it must feed** (decisive finding): the live run entrypoints (`simulation/run_phase*.py`) import the **fixed `CUSTOMERS` literal from `saas/customers.py`** and iterate it directly (`for c in CUSTOMERS`). **`draw_population` has ZERO live callers** (grep: no non-def/non-test caller anywhere; `company/analytics/cohort_discovery.py` deliberately does *not* import it — that import would breach the wall). So "draw-wiring" = making those entrypoints consume `draw_population(...)` output (additive SYN-* acquisitions 2021-2025, filling the FRAME-found "book stops acquiring at 2020" gap) instead of only the static literal.

**C. Verdict-backed vs priors-only fields** (which may cross the wall as *observable*, which must NOT as ground truth):
- **Verdict-backed** (read live from `segmentation_curriculum_v1.json` marginals, W2_2 steps 1-2): `green_stance`, `price_sensitivity`, `channel_pref`; `heating_fuel` pinned to region; cohort tenure a strict *refinement* of existing `tenure_for_customer()` (round-trips exactly).
- **Priors-only (honest gap, R10)**: `accommodation`/`cars`/`nssec` sit at the flat national census prior — no discovery mechanism, correctly gap=1.0 in the coupling ledger.
- **Wall**: NONE of these cohort fields may be read into company logic as ground truth. The company discovers via EPC/census priors + interaction observables (`cohort_discovery.py`), never reads the drawn `cohort`. Any wiring must keep the drawn ground-truth cohort strictly sim-side; `epistemic_verifier` (already extended with the seam symbol-scan, W2_2 step 5) gates the diff.

**D. Governance decomposition (ESCALATION_IS_NTFY) — the irreducible core:**
The *mechanical* wiring can be built + tested behind the existing default-OFF flag (reversible, byte-identical when off). But per W2_2's own recorded ruling ("the agent may STAGE the integration but must not flip it on") and R13/§5, **flipping it on so live runs actually draw the synthetic population is a CURRICULUM act (which world the company faces every run) reserved to the director** — and the 2026-07-24 waiver explicitly preserved "curriculum values remain director-reserved". This tick therefore FRAMEs and escalates rather than activating. Next: (a) director word on activation authority; (b) if the answer is "STAGED-only for now", a build fork wires `draw_population` behind a default-OFF run flag with R15 both-ways (present→population carries SYN-* acquisitions; removed→reverts to static 24) + epistemic-verifier on the diff — activation held for the director.
