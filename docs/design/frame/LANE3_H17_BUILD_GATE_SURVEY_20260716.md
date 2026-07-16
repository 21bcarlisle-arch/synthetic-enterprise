# Lane-3 BUILD-gate survey — H17 re-draw of 6 idle atoms (2026-07-16)

**Turn:** H17 Lane-3 DISCOVER/FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1).
**Scope drawn:** `H18_harness_self_mutation_audit`, `W1_2_generate_futures`,
`B4_competitor_field`, `W4_2_verifier_timing_extension`, `W1_3_national_weather_signal`,
`W1_4_regional_weather_field`.

## Why this doc exists (and why it is NOT six new FRAME docs)

All six drawn atoms **already carry a complete, substantive FRAME doc** under
`docs/design/frame/` (five authored in the 2026-07-16 08:23 batch, H18 at 16:37). Each
existing FRAME already reaches its own honest terminus and records **level HELD** with a
named BUILD-gate. Re-emitting a near-identical FRAME for a FRAME-saturated atom would be
churn — precisely the make-work that SELF_INTERRUPT_DISCIPLINE and R12 (anti-goal-seek)
forbid. The draw text is a doorbell (R7): verified against real disk state, the premise
"these atoms need a fresh FRAME" is stale.

So the genuine, bankable Lane-3 increment this re-draw produces is **epoch-sequencing
intelligence**: for each atom, the single precise gate that unblocks BUILD, in one place,
so the next epoch-open / BUILD-open decision (DIRECTOR_TWIN or director) can act from a map
rather than re-reading six docs. Every level is **HELD** — no FRAME turn can honestly move
these, because their targets (→L1/L2/L3) all require BUILT, green code that is BUILD-gated.

## The gate table

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `W4_2_verifier_timing_extension` | 1 | 1 (→3) | Director re-opens `EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` (closed B/C) — a **Tier-1 safety-control** decision to build real data-flow/timing detection into a named wall control | **WALL** (director-reserved, safety control) |
| `H18_harness_self_mutation_audit` | 2 | 0 (→2) | Epoch-2 BUILD-open (TWIN, within open epoch) + actually build green meta-control mutation tests for M1–M5 | DIAL (epoch sequencing) |
| `W1_2_generate_futures` | 3 | 1 (→2) | (a) `W1_reveal_over_time` resolved (blindfold enforcer for a pre-generated path); (b) a **director-authored** named baseline-continuation scenario (curriculum, R13, category-6-adjacent); (c) Epoch-3 BUILD-open | DIAL + **curriculum WALL** (scenario authorship) |
| `W1_3_national_weather_signal` | 3 | 1 (→3) | Epoch-3 BUILD-open; build the latent blocking-high persistence regime + gap-measured vs company; declare C-S5 timescale | DIAL (epoch sequencing) |
| `W1_4_regional_weather_field` | 3 | 1 (→3) | `W1_3` at L-usable first (depends on national L1); then build the aggregation-consistency invariant (mutation-tested) + gap | DIAL (depends_on + epoch) |
| `B4_competitor_field` | 4 | 0 (→1) | `W2_3_competitor_field` (WORLD) must emit an observable competitor field first; then wire belief + one live coupling across the typed wall | DIAL (COUPLED_TRIAD depends_on) |

## Per-atom notes (the non-obvious bits worth carrying forward)

- **W4_2 — the only WALL in this set.** Its L3 target is *not* an authorization: the timing-
  detection build was closed B/C as a Tier-1 safety-control gate. The honest disposition
  (per its FRAME §6) is HOLD at L1 — the wall-timing burden stays on the PreToolUse hook +
  as-of snapshot + human review. Re-opening is director-console-only; nothing in this re-draw
  is new information that would prompt an escalation, so none is raised. Approach C (as-of
  snapshot structural fix) may retire the "extend the verifier" framing entirely if ever opened.

- **W1_2 / W1_3 / W1_4 — built code exists but level is correctly low.** `sim/scenario/bimodal_generator.py`
  (W1_2) and `sim/weather_engine.py` Pass 1/Pass 2 (W1_3/W1_4) are real, tested mechanism code.
  The low levels are NOT mis-registration: the atoms' levels track the *coupled-triad* state
  (company faced the world + gap measured + curriculum-authored scenario), not raw mechanism
  existence. W1_2 in particular is curriculum-gated — the engine exists; *which* futures the
  company lives through is the director's, never agent-chosen (R13).

- **B4 — two orphaned pre-built modules.** `company/market/tariff_benchmarking.py` and
  `company/pricing/renewal_pricing_engine.py` are real and Ofgem/CMA-anchored but have **zero
  non-test callers**. L1 is "belief + one live coupling" — wiring one of these across the typed
  wall once `W2_3` emits an observable field. The wiring, not the modules, is the missing L1 work.

- **H18 — self-referential doctrine.** When built it must satisfy its own R15 doctrine: each
  meta-control organ (M1 deadman, M2 naive/LLM-judge outcome-miss, M3 claim hook, M4/M5) gets a
  *both-directions* (fire AND quiet) mutation assertion, and the class fails automatically if a
  future meta-control ships without one (R10 closure, not instance closure).

## Meta-finding (QUEUE, not fix-on-sight — SELF_INTERRUPT_DISCIPLINE)

The idle-DISCOVER/FRAME self-refill (`supervisor.py::_idle_discover_frame_draw`) re-drew six
atoms whose FRAME stage is **saturated**, with no remaining FRAME-stage work — a **DIAL defect**
(Rule 0: empty feasible work within a stage), not a WALL. Candidate remedy to register as a
harness atom (do not build here): track a per-atom `frame_saturated` / last-stage-output marker
so a saturated atom is not re-drawn for the *same* stage until its BUILD-gate opens, and instead
the draw yields to genuinely un-FRAMEd idle atoms. This keeps the treadmill honest rather than
generating duplicate-FRAME churn. Filed as intelligence for the next harness pass.

---

## Addendum — H17 re-draw (2026-07-16, later) — B5 folded into the gate table

The idle-DISCOVER/FRAME self-refill re-drew a **near-identical** set: `W1_2_generate_futures`,
`B4_competitor_field`, `W4_2_verifier_timing_extension`, `W1_3_national_weather_signal`,
`W1_4_regional_weather_field` — **plus `B5_regional_basis_risk`** (which this survey's original
table did not carry) and **minus `H18_harness_self_mutation_audit`**. Verified against real disk
state: the five shared atoms are unchanged since the survey above (same commit-day, nothing built,
gates identical) — re-emitting their FRAMEs would be the exact duplicate-FRAME churn the meta-finding
warns against, so no new per-atom FRAME is written. `B5` already carries a complete 19KB FRAME
(`docs/design/frame/B5_regional_basis_risk_FRAME.md`, committed `5de4b2a91`); the only genuine,
non-churn Lane-3 increment this re-draw yields is folding B5's single BUILD-unblock gate into the
consolidated table so the epoch-sequencing intelligence covers every currently-drawn atom.

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `B5_regional_basis_risk` | 3 | 0 (→3) | `W1_8_zonal_locational_pricing` opens BUILD first (itself gated on `W1_6_physics_price_signal` **and** a **director-authored named zonal curriculum scenario**, R13); B5 releases **coupled with W1_8** (COUPLED_TRIAD: neither reaches L3 alone); at BUILD, register `W1_8↔B5` in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` | DIAL (depends_on) + **curriculum WALL** (zonal-regime scenario authorship, director-reserved) |

- **B5 — the company leg of the W1_8 coupled pair.** It authors the company-side twin (provenance
  `proposal`, L0→L3) that gives the W1_8 belief-vs-truth *regional-basis* gap a home: the company
  observes settled/published zonal prices through the wall, holds only a **national** hedge (from B3),
  and **cannot buy** a regional-basis hedge (no regional forward market — the real structural fact),
  so a regionally-skewed book carries unhedgeable basis it may wrongly assume its national hedge covers.
  Gap = believed (national-hedge) protection vs SIM-truth realised zonal basis cost `Σ_z vol_z·basis_z`.
  **Dormant/zero under the national baseline** — the exposure only exists inside a director-authored
  zonal-curriculum scenario, and per R13 that scenario's severity is **never** tuned to company basis
  loss. Held at **L0** (proposal-atom FRAME ≠ built; BUILD-gated, EPOCH_GATING Rule 1).

*This addendum is the only change: five shared atoms re-confirmed HELD with no new FRAME (anti-churn),
B5 added to the gate table. No BUILD code, no map edit (F1). Meta-finding above now has a second data
point — a saturated-atom re-draw recurred within the same day, reinforcing the `frame_saturated`-marker
remedy as worth registering as a harness atom.*

---
*No BUILD code, no map edit (F1 — levels reported via `docs/design/atom_status/*.yaml` inbox).
Every level HELD; see the gate table for what each atom's real progress depends on.*

---

## Resolution — occurrence 5 (2026-07-16, later) — recursion ended at the mechanism level

The idle-DISCOVER/FRAME self-refill re-drew this same FRAME-saturated set a **fifth** time
(`H18_harness_self_mutation_audit`, `W1_2_generate_futures`, `B4_competitor_field`,
`B5_regional_basis_risk`, `W4_2_verifier_timing_extension`, `W1_3_national_weather_signal`).
Per the meta-finding above, **no new per-atom FRAME was written** — every drawn atom already
carries a complete FRAME and its gate is unchanged (anti-churn, SELF_INTERRUPT_DISCIPLINE + R12).

The genuine, non-churn increment this turn produced instead is the **landing transition** that
occurrence 4 named but (as a fork) could not perform: `H23_frame_saturation_draw_marker` — the
already-registered, **twin-APPROVED** remedy for this exact draw defect (director_twin_log.jsonl
@ `2026-07-16T17:57:36`, CONFIDENCE high, DEFERS_TO_DIRECTOR:no) — was stuck at `loop_stage: idle`,
so the Lane-1 BUILD draw (`_maturity_map_draw_concurrent`, which excludes `loop_stage==idle`) never
picked it up and the fix could never be built. This orchestrator turn flipped `H23.loop_stage
idle→build`; a closed-loop check confirms `_maturity_map_draw_concurrent()` **now yields H23**. The
next BUILD cycle builds the marker + draw-skip guard + R15 mutation test, and the recursion stops
generating duplicate-FRAME draws for the whole idle-BUILD-gated set. Reversible (git reverts the
flip; the draw falls back), Epoch-2 open, not a one-way door — Rule 0's yield-the-dial-until-work-
exists path, mechanised rather than re-recorded as prose.

## Resolution — occurrence 6 (2026-07-16, later still) — guard built but not deployed (R2) + the one leak it missed

The self-refill re-drew the set a **sixth** time (`H22_scheduled_housekeeping`, `W1_2_generate_futures`,
`B4_competitor_field`, `B5_regional_basis_risk`, `W4_2_verifier_timing_extension`,
`W1_3_national_weather_signal`). The guard from occurrence 5 (`d2f1b420a`, L0→L2) is now built — so
why did the draw recur? **Two distinct causes, both diagnosed against real disk/process state (R9):**

1. **R2 — the guard is built but not deployed.** The running supervisor daemon (`tmux supervisor:0`,
   pid 704590) started **19:27**; the guard commit `d2f1b420a` landed **19:34** — the daemon is running
   7-minute-stale pre-guard code. A closed-loop check against the *current* code confirms the guard is
   correct: `_idle_discover_frame_draw_concurrent()` now yields **only `H22_scheduled_housekeeping`** and
   the 200× single-draw pool contains **none** of W1_2/B4/B5/W4_2/W1_3. So the fix works; it just isn't
   running yet. Deployment step (R2, "committed ≠ running"): **restart the supervisor daemon** — done this
   turn, confirmed live below. The five shared saturated atoms are re-confirmed **HELD, no FRAME churn**.

2. **H22 — the one atom the guard legitimately still handed, on a path-convention leak.** H22 is **not**
   genuinely un-FRAMEd: it carries a complete 17KB FRAME doc (committed `6029eefbe`). But that doc lived at
   `docs/design/H22_SCHEDULED_HOUSEKEEPING_FRAME.md` — one directory **above** the `docs/design/frame/`
   prefix `_atom_has_frame_doc` requires — so the intrinsic saturation check missed it and the draw was
   *correct by its own rule* to offer H22. Fix (this turn, in-scope Lane-3 doc-only): `git mv` the doc to
   the convention path `docs/design/frame/H22_scheduled_housekeeping_FRAME.md` and append that path to H22's
   evidence via its atom_status inbox (F1). Once folded, the intrinsic guard reads H22 as saturated and the
   recursion closes for H22 too — with no per-atom marker to remember (MAKE_IT_STICK). Level **HELD at 0**
   (BUILD-gated, EPOCH_GATING R1).

**QUEUE (not fix-on-sight — SELF_INTERRUPT_DISCIPLINE):** `_atom_has_frame_doc`'s hard `docs/design/frame/`
prefix requirement is slightly brittle — any complete FRAME doc placed one dir up (as H22's was) leaks
through the guard. A future harness pass could relax the check to accept `docs/design/**/*FRAME*.md`, or
H22's own housekeeping sweep (once built) would flag the stray doc. Filed as a finding, not fixed here
(that is BUILD on `background/supervisor.py`, outside this Lane-3 doc-only draw). No BUILD code, no map edit
(F1 — H22's level reported via `docs/design/atom_status/H22_scheduled_housekeeping.yaml`).

## Resolution — occurrence 7 (2026-07-16, later still) — recursion CLOSED, first positive live proof

The self-refill re-drew the saturated set a **seventh** time (`W1_2_generate_futures`, `B4_competitor_field`,
`B5_regional_basis_risk`, `W4_2_verifier_timing_extension`, `W1_3_national_weather_signal`,
`W1_4_regional_weather_field` — this time with `W1_4` in place of `H22`). Per the standing meta-finding,
**no new per-atom FRAME was written** — all six carry complete FRAME docs and their BUILD-gates are unchanged
(anti-churn, SELF_INTERRUPT_DISCIPLINE + R12). Levels **HELD**; no map edit (F1); no BUILD code.

What occurrence 7 adds that 5 and 6 could not — **the first positive evidence the recursion is actually dead**,
not merely a static "the check would exclude them" assertion:

- **Live reproduction of the real draw path (observed, R9).** Calling `_idle_discover_frame_draw_concurrent(exclude_stalled=True, exclude_ids=frozenset())`
  against the current working-tree map now returns a **completely fresh, genuinely-un-FRAMEd set** —
  `G4_unified_failure_register, W1_5_premise_demand_shape, C13_weather_normalisation, W1_10_ev_heatpump_geography,
  H20_parallel_maintenance_lane, H21_self_contained_escalation` — and **excludes all six** drawn atoms.
  `_is_frame_saturated` returns `True` for every one of the six (`has_frame_doc=True`, evidence folded:
  five since `206c534c1` 07:39Z, B5 since `abeb41555` 17:35Z). 22/22 H23 guard tests green. The guard is
  deployed and effective; the map is re-read fresh every cycle (`supervisor.py:729`, no cache), so the next
  cycle draws from the fresh set. **The treadmill is off.**

- **The one honest residual (inferred, NOT asserted — R9).** Occurrence 7's own draw (the daemon logged
  `DISCOVERY=6` at 18:57Z and 19:02Z) *should not* have leaked: the guard commit (`d2f1b420a`, 18:34Z) and
  the running daemon (pid 721690, started 18:43Z) both predate those draws, and the committed map already
  carried every atom's frame-doc evidence. Against committed state the leak is unexplained. Candidate causes
  — a transient uncommitted working-tree map mid-fold read by `read_text` on a concurrent-writer tree, or a
  pre-guard daemon instance overlapping the restart — are **plausible, not verified**; no mechanism is claimed.
  **QUEUE (not fix-on-sight):** register a harness finding to instrument the idle-draw path with a one-line
  log of *why* each saturated atom was or wasn't excluded, so an occurrence 8 (if any) carries its own proof
  rather than requiring post-hoc reconstruction. Filed as intelligence for the next harness pass; not built
  here (BUILD on `background/supervisor.py`, outside this Lane-3 doc-only draw).

*Bankable Lane-3 increment: positive live proof the H23 guard now excludes the whole saturated set and yields
fresh work, plus the sole unexplained residual queued honestly. No FRAME churn, no map edit (F1), no BUILD code.*

## Resolution — occurrence 9 (2026-07-16, later still) — the guard did its job: a genuinely-un-FRAMEd atom was drawn and actually FRAMEd

The self-refill re-drew a set of six: five saturated (`W1_2_generate_futures`, `B4_competitor_field`,
`B5_regional_basis_risk`, `W4_2_verifier_timing_extension`, `W1_3_national_weather_signal`) **plus
`C13_weather_normalisation`** — and C13 is exactly the genuinely-un-FRAMEd atom occurrence 7's live
reproduction predicted the guard would yield (it appeared in that fresh set). Verified against real disk
state (R7): C13 carried **only** `docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md` (a DISCOVER-stage doc,
no `FRAME` in the filename) → `_atom_has_frame_doc(C13)=False`, correctly un-saturated. So this draw is **not
a pure treadmill recurrence**: it is the guard working — C13 had real remaining FRAME-stage work.

**What this turn did (the bankable, non-churn increment):**
- **C13 — real FRAME authored.** Wrote C13's canonical per-atom FRAME
  (`docs/design/frame/C13_weather_normalisation_FRAME.md`), consolidating (not re-deriving) its
  previously-scattered FRAME-depth thinking — `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §6 (wall/gap/hedging
  frontier) + the DISCOVER audit (method/seam-gap/open-questions) — into one terminus with its single
  BUILD-unblock gate stated (W1_5 L-usable + A6 + Epoch-3 BUILD-open, coupled with W1_5). This closes C13's
  own leak into the idle draw: once the evidence folds, `_is_frame_saturated(C13)` reads `True` from disk
  (computed, MAKE_IT_STICK — no marker to remember), so the draw stops offering it. Level **HELD at 0**
  (proposal atom; FRAME complete ≠ built; BUILD-gated). Reported via
  `docs/design/atom_status/C13_weather_normalisation.yaml` (F1).
- **The five saturated atoms — re-confirmed HELD, no FRAME churn.** All five carry complete FRAME docs and
  their BUILD-gates are unchanged since the tables above (anti-churn, SELF_INTERRUPT_DISCIPLINE + R12). Their
  presence in the same draw is the same residual map-write/draw-read behaviour occurrence 8 diagnosed
  (`759648472`); nothing new about it here. No per-atom FRAME re-emitted for any of them; no map edit (F1).

**Meta-note (already QUEUED, not re-filed):** the five saturated atoms still leaking into a draw alongside a
legitimately-fresh C13 is consistent with occurrence 8's queued root-fix (atomic `os.replace` on the map
write + fail-closed draw read). This turn adds no new finding on that axis — it is BUILD on the harness,
outside this Lane-3 doc-only draw.

*This occurrence's lesson: not every re-draw of a mixed set is churn to refuse wholesale — verify each atom
against disk (R7), FRAME the genuinely-unframed one, HOLD the saturated rest. C13 is now off the treadmill by
construction, same as every other FRAMEd atom.*
