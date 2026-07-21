>**STATUS (2026-07-21 07:2x — CORRECTED after re-diagnosis; the director was right):** The overnight rest **WAS a draw bug**, not a correct hold. The previous tick's "correct hold, no drawable atom" claim (commit 6898247b8) was WRONG and is retracted (R9: re-checked against the live classifier before trusting the narrative). Root cause: `_dependencies_met` was **target-matched** — it required every dependency to sit at ITS OWN target. W1_4 is walled at its L2→L3 coupled-triad step, so that wall propagated down the whole cascade and W1_5/W1_10 — which only need W1_4 **at L2** (which it is) — read as `blocked_by_dependency`. Fix (commit **0a072a842**, supervisor restarted via systemd): **level-MATCHED dep gate** — a dependency is met when at its own target OR already at the level the downstream is trying to reach (`level_current+1`). Strictly more permissive → can never newly block a drawable atom; mirrors the coupled-triad gate, itself next-step-matched. Live proof: W1_5 & W1_10 now DRAWABLE, concurrent draw returns W1_5 (was `[]`); W1_4 correctly still walled. R15 tests added (walled-upstream/drawable-downstream incident + a dependency-too-low mutation control proving the looser rule did not fail open); 265 draw tests green, 0 regressions.
>
> **IN PROGRESS this tick:** W1_10 (director-named priority) build fork running → L1 national adoption S-curves. Then: advance idle backlog (E5/C4/C5/A DISCOVER-FRAME) + continue segmentation reframe.
>
> **SURFACED as ONE batched [ACT]** (NTFY `tl8dnpCfMMro`) — the genuine director gates:
>  1. **W1 coupling decision (root un-dam):** register a W1↔company twin (candidate `C13_weather_normalisation`, L0/idle) OR exempt the W1 physical primitives from the coupled-twin rule (consistent with W1_3/W1_6, already L3 twinless). Un-dams W1_4→L3 + the cascade tail.
>  2. **Level-ups** (`blocked_on: director_level_up`): D_cascade, W1_7, W1_9.
>  3. **SITE1→L3** (his live-site Expert-Hour); **W1_6** L3 PROPOSED (his Expert-Hour + ratify).
>  4. **W1_8 zonal** (epoch-console schema gate + R13 zonal curriculum); **generator wiring** (reserved).
>  5. **OPS1** systemd deploy + governance-refusal live run (his hands).

---

# DIRECTOR DIRECTIVE — Keep building: drawable work exists; draw it, and advance the idle backlog (2026-07-21)

**Type:** [DIRECTIVE + STEER]. Standing campaign authority already covers the builds below. This is here because the loop rested overnight (23:00→06:00, zero work commits) while drawable work existed — that is the failure to fix, and there is real work to do meanwhile.

## The finding that matters

At rest this morning the map held **three drawable atoms** (build stage, no block, open lane): `W1_4_regional_weather_field`, `W1_5_premise_demand_shape`, `W1_10_ev_heatpump_geography`. The loop drew none of them and rested for seven hours. **That is not a director-gating problem — it is a draw problem.** The durable fix addressed mis-parked work in `in_progress/`; it did not address a loop that goes idle while genuinely-drawable below-target atoms sit in an open front. Diagnose and fix that: a loop must not report "drained" while build-stage, unblocked, in-front atoms exist.

## Build now (all within standing authority — no console act needed)

1. **`W1_10_ev_heatpump_geography`** — EV, heat pump and (where derivable) PV/battery geography. This is asset ownership the director explicitly wants in the population model and it is drawable now. Prioritise it.
2. **`W1_5_premise_demand_shape`** — premise-level demand shape; downstream of the weather cascade, sharpens the whole chain.
3. **`W1_4_regional_weather_field`** — regional weather field to L3.

## Advance the idle backlog (correct-after — you own stage-advances within a ratified campaign)

Roughly fifteen below-target atoms sit `idle` — below target but not advanced to a build stage, so undrawable. Under the correct-after model, advancing an idle atom to its next stage within an authorised campaign does **not** require a console act. Work through them on their merits — e.g. `E5_carbon_three_ledger` (the carbon instrumentation the ratified purpose needs), `C4_adoption_physics` and `C5_key_moment_conversion` (customer behaviour), `A_scope_of_need_scoring_frame` (now reframed to learning-value). DISCOVER/FRAME on these is unblocked. Keep the drawable queue non-empty by your own hand; do not wait to be fed.

## The reframed segmentation (already consumed — continue it)

The learning-value reframe landed. Continue that analysis to the re-derived knee and the ranking, and report. The **generator wiring remains the director's reserved gate** — propose it, do not apply it.

## What genuinely needs the director (do NOT attempt these; surface as ONE batched [ACT])

- **SITE1 → L3**: needs his live-site Expert-Hour on poesys.net/now/. Built and waiting; his eyes only.
- **Level promotions**: `D`, `W1_7`, `W1_9` and any others that reach a level ceiling — batch them.
- **`W1_8` zonal pricing** (epoch-console) and the **generator wiring** (reserved) — his gates.
- **OPS1** items needing a live systemd run — his hands.

## The standing instruction the advisor should have given nights ago

Keep the drawable queue ahead of the worker. When below-target work is genuinely exhausted **and** the remainder is truly director-gated, THEN rest — and page one batched [ACT] naming exactly what is needed. But "I finished the last drawn atom" is not "the map is drained": advance idle atoms, run forward discovery, and only rest when there is genuinely nothing that is not reserved to the director.

**Risk & proportionality:** the builds and stage-advances are within standing authority and reversible. The draw fix touches the tick's rest logic — sequence it, prove by test that a drawable in-front atom is never left undrawn at rest, own commit. Generator wiring and level ceilings stay walls. Tag: **proceed by default; batch the genuine gates as one [ACT].**

— Advisor, carrying the director's direction, 2026-07-21.
