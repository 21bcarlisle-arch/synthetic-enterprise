<!-- SUPERVISOR_DRAW: blocked -->
<!-- DONE 2026-07-29T02:40Z (RUNG-7 tick, executed as build-worker): the minimal-form dependency-narrowing PROCEEDED. maturity_map.yaml DD_seasonal_cashflow_physics depends_on narrowed [W2_12_change_of_tenancy_debt_physics] -> [] with an inline rationale comment (split-on-build-draw re-attaches W2_12 to DD2). R1 CONSUMER-VERIFIED: background.supervisor._maturity_map_draw_concurrent() now returns [DD_seasonal_cashflow_physics] (was [] this same tick pre-edit) -- the false-empty BUILD draw is resolved and the HARNESS_INVESTMENT ruling's Acceptance ("a draw can no longer honestly report 'no un-minted work' and fall to HARNESS/planner") is RESTORED. level_current unchanged at 0 (no self-bump, R16); DD2 waits honestly behind W2_12 at split-time. No wall touched (R13 baseline dependency-modelling, git-reversible). Marker flipped self-drawable->blocked and archived to done/ -- work consumed, not resting on a false proof. -->
<!-- RELEASED 2026-07-29T02:07Z (RUNG-7 planner tick): propose-then-proceed window (to 2026-07-29 00:16Z) has ELAPSED with NO director revision (git log of this doc shows only the 07-28 mechanical block-hygiene backfill 65ad9d83c, no content change; no new from_rich/DIRECTOR_RULING staged). Per the doc's own PROCEED clause the split/dependency-narrowing now proceeds at build-draw. Flipped blocked->self-drawable so the next build-draw tick's selfdrawable_mint_in_progress surfaces it (no-orphan-transition, R11) -- the actual gated maturity_map.yaml map-write is the orchestrator/build-worker's job, NOT this planner tick. Level moves stay blocked_on director_level_up (R16); the front-reconciler/level gate is the backstop. -->
# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — DD_seasonal_cashflow_physics is director-ratified DRAWABLE NOW but transitively BUILD-blocked by an over-broad whole-atom dependency; split it so the sub-parts that do NOT need W2_12 draw (2026-07-28)

> **PARKED IN `in_progress/` — BLOCKING SUB-ITEM: the propose-then-proceed window is still OPEN (until 2026-07-29 00:16Z).** The FRAME + fix design below (the "propose" artefact) is complete and the core defect is empirically re-verified (2026-07-28 tick: `_maturity_map_draw_concurrent()` → `[]`; DD dropped on unmet `W2_12` dep; W1_10 coupled-triad-excluded). **UNBLOCKS:** first build-draw tick after 2026-07-29 00:16Z with no director revision → an orchestrator/build worker performs the dependency-narrowing (carry `W2_12` on DD2 only, or minimal-form whole-atom `depends_on: []`) as a gated `maturity_map.yaml` map-write under the full pre-commit level/facets/fronts gate. Parked (not proceeded) now to honour the doc's own 24h director-revision window — proceeding early would defeat the propose pause; no urgency (the tick has other drawable work, the empty BUILD draw fell to RUNG-7 by design, not a blackout).

**Provenance:** RUNG-7 planner refill (director ruling `WORK_IS_THE_DEFAULT_2026-07-23`), tick 2026-07-28 00:16Z. Minted from a ratified goal, not a doorbell — and it is a NEW un-minted next-step (grep-confirmed: no existing staging doc names the DD↔W2_12 over-block). This tick drew RUNG-7 because the BUILD draw returned an **empty candidate set**, yet the director explicitly wants DD surfaced as drawable content work. The gap between those two facts is this mint.

**Serves:**
- **`DIRECTOR_RULING_HARNESS_INVESTMENT_AND_ITS_EVIDENCE_2026-07-27` (Problem One).** The ruling registered `DD_seasonal_cashflow_physics` into `maturity_map.yaml` and stated verbatim: *"DD_seasonal_cashflow_physics (meter_to_cash, SUPPLIER front): window CLOSED 2026-07-27 → DRAWABLE NOW (blocked_on: null, verified a live BUILD candidate)… THIS is the atom that satisfies the ruling's Acceptance — find_work now surfaces real content work, so a draw can no longer honestly report 'no un-minted work' and fall to HARDEN."* **That acceptance is currently NOT met** — see the defect below.
- **`DIRECTOR_AXES` axis 3 (Believability)** — the level-DD seasonal credit cycle and the cash-rich-but-insolvent trap are the fidelity the atom delivers; this mint is the mechanical unblock that lets that fidelity get built.
- **`DIRECTOR_STEER_DD_SEASONAL_CASHFLOW_2026-07-25`** — the originating domain steer.

**Fidelity gained (one sentence):** none directly — this is a **draw-gap / dependency-modelling fix** that lets the *already-ratified* level-DD seasonal-cashflow physics (DD1/DD3/DD4/DD-H) actually reach the BUILD lane instead of sitting silently blocked behind a dependency only ONE of its six sub-parts needs.

---

## FRAME — the defect, evidence-cited (established this tick)

`DD_seasonal_cashflow_physics` (`docs/design/maturity_map.yaml:2398`) is:
`lane: D_billing_metering`, `loop_stage: build`, `blocked_on: null`, `level_current: 0 → level_target: 3`, `epoch: 3`, in the **OPEN** `SUPPLIER` front (`background/fronts.yaml`, `opened_by: director console 2026-07-18`; `epoch_ceiling: 3`, so epoch-3 members are in-scope). By every atom-local field it should be a live BUILD candidate — exactly as the director's ruling asserts.

But it carries `depends_on: [W2_12_change_of_tenancy_debt_physics]`, and `W2_12` is `loop_stage: discover`, `level_current: 0 / level_target: 1`, `blocked_on: director_level_up` (itself `depends_on: [W2_5_life_event_stream]`). Running `background.supervisor._dependencies_met(DD)` (supervisor.py:608-642): W2_12 is not `idle` (not skipped), not at its own target (`0 < 1`), and not advanced enough (`0 < DD.required 1`) → **dependency UNMET → DD is dropped from `_maturity_map_draw_concurrent` candidates.** Empirically this tick:

```
BUILD concurrent candidates: []
single build draw: None
```

(the two pre-filter candidates were W1_10 — excluded by the coupled-triad L3-no-twin gate — and one off-front/gated atom; DD never even reaches that stage). **So the BUILD draw is legitimately empty AND the director's stated acceptance ("a draw can no longer report 'no un-minted work'") is violated** — the tick fell to RUNG-7, the precise failure the HARNESS_INVESTMENT ruling was written to prevent.

**Root cause — the dependency is modelled at the WRONG granularity.** DD's own registered scope (maturity_map.yaml:2411) sequences six disjoint sub-parts and states the W2_12 need is **DD2-only**: *"DD2 per-customer rolling credit/debit balance… non-zero opening balance from W2_12 (do NOT duplicate)."* DD1 (level-DD mandate + staggered payment_day), DD3 (held-credit LIABILITY in the double-entry chart), DD4 (annual DD-review event), DD5 (SITE — already BUILT/LIVE, de-scoped) and DD-H (belief-vs-truth solvency gap organ) do **not** reference W2_12. The whole-atom `depends_on: [W2_12]` therefore over-blocks the five sub-parts that have no opening-balance requirement. The atom's own note anticipates the split ("Splits into DD1-DD5+DD-H disjoint sub-atoms at build-draw") — but the split is supposed to happen *on build-draw*, and the un-split whole-atom dependency is exactly what prevents the build-draw. Chicken-and-egg deadlock.

---

## PROPOSE — the fix (forward-only, reversible, respects every wall)

At build-draw, an orchestrator/build worker (NOT this planner tick — the map is a `schema_sim_structure` gated path; a map edit runs the full pre-commit level/facets/fronts-reconciler gate):

1. **Split `DD_seasonal_cashflow_physics` into its documented disjoint sub-atoms** (DD1, DD2, DD3, DD4, DD-H; DD5 already built/live and de-scoped), per the atom's own "splits at build-draw" design and the mint-doc decomposition reference (`docs/staging/in_progress/PLANNER_MINTED_dd_seasonal_cashflow_physics_2026-07-25.md`).
2. **Carry `depends_on: [W2_12_change_of_tenancy_debt_physics]` on DD2 ONLY** (the opening-balance sub-part). DD1/DD3/DD4/DD-H carry no W2_12 dependency and become **independently BUILD-drawable NOW** in the open SUPPLIER front (epoch 3 ≤ ceiling). Sequencing preserved: DD1→DD3, DD4 parallel, DD-H needs DD2/DD3 (so DD-H's full L2 waits on DD2, but its DD3-facing half can begin).
3. **DD2 stays honestly blocked** behind W2_12 (which is itself `blocked_on: director_level_up` and depends on W2_5) — that is *correct* sequencing, not a defect; DD2 is one of six parts, not the gate on the whole atom.
4. **Alternative minimal form if the split is deferred:** narrow the *whole-atom* `depends_on` to `[]` (DD1 is the first-in-sequence sub-part and has no prerequisite), letting the whole atom draw and split-on-draw naturally; W2_12 re-attaches to DD2 at split time. Either form removes the false-empty.

**Walls untouched (director-reserved):**
- **Level moves** — every DD sub-atom keeps `blocked_on: director_level_up` at its level ratification (R16, no self-bump). This mint only restores *draw eligibility*, never a level.
- **W2_12's own advance** — DD2's dependency on W2_12 remains; W2_12→L1 is a director level-up (its `blocked_on`). **No escalation needed now:** DD2 is one of six sub-parts and waits naturally; the other five carry the ratified work forward without it.
- **Curriculum / one-way doors** — none touched; this is baseline fidelity plumbing (R13), a git-reversible map-content edit behind the epistemic wall (no real market, no real money).
- **`maturity_map.yaml` is a gated path** — the split is orchestrator map-write (atom content, the same operation that folded these atoms in on 07-27), run through the full commit gate; if adjudicated as a schema decision, `blocked_on` names the director act rather than proceeding.

## Acceptance
- After the fix, `background.supervisor._maturity_map_draw_concurrent()` returns a NON-empty candidate set containing DD1 (and DD3/DD4/DD-H as sequencing allows) — the director's HARNESS_INVESTMENT acceptance ("a draw can no longer honestly report 'no un-minted work' and fall to HARDEN") is then MET for the DD family.
- DD2 remains correctly excluded until W2_12 advances (dependency intact — the fix narrows, never deletes, the real prerequisite).
- Existing gates unchanged: fronts-reconciler green, level-gate green, no self-authored level increase.

## Propose-then-proceed window
**Open until 2026-07-29 00:16Z (24h).** The FRAME + the fix design above are the "then propose" artefact. A tick after that with no director revision → the split/dependency-narrowing proceeds at build-draw under the full commit gate. This is a small, reversible, high-leverage unblock of already-ratified work; the short window reflects that (PROCEED_BY_DEFAULT — a wrong reversible map edit costs ~1h and git reverts it).
