<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- RELEASED 2026-07-28: director console BUILD_OPEN (ruling_consumption_authority_seam_signoff, terms unchanged from 0ac3e1b5e); recorded in docs/observability/gate_authorizations.jsonl (channel=console, authorized_by=director). The R13 ACTIVATION (SE_DRAW_POPULATION on + entrypoint wiring) is the director-authored curriculum act now authorised. The LEVEL move stays director-reserved: the build fork re-applies blocked_on/director_level_up on completion (R16). -->
<!-- draw-visibility marker (2026-07-28 UPDATE): SELF-DRAWABLE stays — the ledger BUILD_OPENed this atom (gate_authorizations.jsonl, director console 2026-07-28) so the R13 activation is NO LONGER walled. Remaining next step is a NON-walled dedicated BUILD (SYN property modelling for the ~4 property/HH generators + the director-authorised flag flip & re-baseline), so it must be DRAWN, not parked. Fail-closed structured token parsed by background/staging_disposition.selfdrawable_mint_in_progress. -->

# [PLANNER-MINTED] Ship the population-generator DRAW-WIRING (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, origin commit 4b31c60d6, PRODUCT-FIRST item 2). **Scope step 1 (FRAME) DONE — see the FRAME section below. Scope step 2 REVERSIBLE HALF (the default-OFF seam) + step 3 (R15 both-ways) DONE this tick — see "BUILD (reversible half)" below.**
> **BLOCKING SUB-ITEM (open):** The R13 **ACTIVATION** — flipping `SE_DRAW_POPULATION=1` on AND wiring the ~19 `run_phase*` entrypoints to consume the seam — changes which world the company faces every run, reserved to the director (W2_2's own ruling + the 2026-07-24 waiver's "curriculum values remain director-reserved"). The reversible mechanism is now BUILT and tested default-OFF; **UNBLOCKS ON:** a director word authorising live activation. Escalated via NTFY (prior tick + this one). Per ESCALATION_IS_NTFY the reversible half shipped; only the irreducible activation core is held.

---

## BUILD-FRAME + coverage-gate landed — 2026-07-28 worker tick

The 2026-07-28 director console **BUILD_OPEN** (`gate_authorizations.jsonl`, `authorized_by=director`)
un-walled the R13 activation, and **POOL_VS_BOOK_LAMBDA_STANDS 2026-07-27** resolved the escalated
N/λ call. This tick landed one verified sub-step and mapped the rest into tested ground truth.

**λ RECONCILED (no contradiction):** `live_population()` appends `draw_population(...)` at the
director-signed **λ=1.0 "Profile B trickle"** (Poisson(1.0)/yr × 2021-25 ≈ 5 SYN acquisitions) — the
company's **earned** book, NOT the N=200 **pool** (a separate coverage-draw concept). Appending is
therefore *consistent* with the 2026-07-27 ruling ("book is earned, never granted"); the earlier
"activation grants a 200-book" worry was WRONG.

**Blast radius — TESTED, not asserted (scopes down the doc's "~19 entrypoints" fog):**
- **SYN-SAFE (needs nothing):** the settlement path — `customer_to_settlement_input` reads only
  `customer_id`+`acquisition_date`, both present in `to_customer_dict()`. The primary published-figure
  generators (`generate_customer_sample`, `generate_hh_data`, `generate_dashboard_data`) key mostly on
  `customer_id`.
- **NEEDS A SYN PROPERTY MODEL (the real remaining build):** `generate_hh_data` / `saas.property_model`
  / `simulation.household_segments` helpers read static-only property fields (`home_type`, `bedrooms`,
  `epc_rating`) that SYN dicts do NOT carry (SYN carries `consumption_band`/`eac_kwh`/`payment_method`/
  region). A SYN cohort needs a property/HH-shape derivation before the flip — a genuine design+build,
  not a `.get()` patch. `run_phase3a.py`'s `c["home_type"]` diagnostic also KeyErrors (off the
  published path; QUEUED, not fixed-on-sight per SELF_INTERRUPT_DISCIPLINE).

**LANDED THIS TICK — director condition #3 (coverage-report publish gate), R15-proven both ways:**
`background/process_run_complete._cohort_coverage_gate_permits_publish()` gates `generate_dashboard_json`
BEFORE any derived-figure generator. **Inert when `SE_DRAW_POPULATION` is off** (reads the env var
directly → zero new import/exception surface → today's static-book publish is byte-identical and
un-jammable). **When on:** (re)builds+writes the realised-cohort coverage report
(`docs/observability/cohort_coverage_realised.json`) then BLOCKS publication if `coverage_gate_ok` is
False — "a thin draw stops the number reaching a surface" (ruling §3), thin cells NAMED never smoothed
(R12). **FAIL-CLOSED:** an unavailable coverage build is a FAILED gate (R15 fail-silent) → blocks.
Tests: `tests/background/test_cohort_coverage_publish_gate.py` (5, green) + explicit no-gate mutation
proof (a mutant that always permits leaks a thin draw). Existing publish-gate suites still green (26).

**REMAINING (drawable dedicated build, authorised — NOT walled):**
1. SYN property/HH-shape model so the property/HH generators tolerate SYN dicts under flag-on.
2. Wire the generators to consume `live_population()` (byte-identical while off).
3. Flip `SE_DRAW_POPULATION=1` + downstream re-baseline (fidelity cells / financials / site panels),
   coverage-gate now enforcing #3; historical straddling comparisons MARKED not silently continued.
   The flip is a director-authored curriculum act, now BUILD_OPEN — run as a dedicated build, not a
   supervisor micro-turn. Level move stays `director_level_up` (R16).

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
