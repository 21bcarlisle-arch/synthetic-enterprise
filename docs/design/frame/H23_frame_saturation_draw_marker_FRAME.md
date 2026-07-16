# FRAME — H23_frame_saturation_draw_marker

**Atom:** `H23_frame_saturation_draw_marker` (lane `H_harness`, provenance `proposal`, level 0→2, `loop_stage: idle`, BUILD-gated).
**Authored:** 2026-07-16, H17 Lane-3 DISCOVER/FRAME (fork, doc-only, NO BUILD code — EPOCH_GATING Rule 1).
**Why it exists:** to convert a twice-evaporated prose meta-finding into a drawable mechanism atom (MAKE_IT_STICK: prose-only decays; a rule lives as enforced code or not at all).

## 1. The defect this atom fixes (observed, with evidence — R9)

The idle-DISCOVER/FRAME self-refill (`background/supervisor.py::_idle_discover_frame_draw`) has re-drawn the **same set of FRAME-saturated, BUILD-gated atoms three times in one day**, producing zero new FRAME-stage work each time:

| Occurrence | Commit | Draw |
|-----------|--------|------|
| 1 | `caab8d8c1` | 6 atoms (incl. H18) — all FRAME-saturated, HELD; consolidated BUILD-gate survey written instead of 6 duplicate FRAMEs |
| 2 | `3d20b846d` / fold `20d177374` | near-identical 6 (swap H18→B5) — re-confirmed HELD, B5 folded into the survey addendum, no new FRAME |
| 3 | **this turn (H17 re-draw)** | `W4_2`, `W1_2`, `B4`, `B5`, `W1_3`, `W1_4` — verified unchanged since the survey; all 6 already carry a complete FRAME doc **and** already list `LANE3_H17_BUILD_GATE_SURVEY_20260716.md` in `evidence` |

Each occurrence is honestly a **no-op** on the drawn atoms: their targets (→L1/L2/L3) all require BUILT, green, BUILD-gated code, so no FRAME turn can move them. Re-emitting FRAMEs is exactly the churn `SELF_INTERRUPT_DISCIPLINE` and R12 (anti-goal-seek) forbid.

**Class, not instance (R10 lens):** this is a **DIAL defect** (Rule 0 — an empty *feasible* set within the FRAME stage for these atoms), not a WALL. The remedy was filed as prose in the survey doc's "Meta-finding" section (occurrence 1) and reinforced in its addendum (occurrence 2) — and evaporated both times, because prose in a design doc is not a drawable unit of work and does not change the DIAL. n=3 is the trigger to elevate the disposition from prose to a registered atom.

## 2. Root cause

`_idle_discover_frame_draw` selects idle atoms for DISCOVER/FRAME with **no notion of whether an atom's FRAME stage is already saturated**. An atom is FRAME-saturated when:
- it carries a complete FRAME doc under `docs/design/frame/`, **and**
- its `level_current` is HELD strictly below `level_target` **for a BUILD-gated reason** (the only remaining path to the target is BUILT code that the epoch/curriculum/wall gate forbids now).

For such an atom there is *no honest FRAME-stage output left*. The draw should skip it in favour of a genuinely un-FRAMEd idle atom, and only re-offer it once its BUILD-gate opens.

## 3. Proposed mechanism (BUILD-gated — not built here)

Simplest construct that satisfies the SIMPLICITY GUARD (no new registry, reuse existing map fields):

1. **Marker.** When a FRAME/DISCOVER turn on an idle atom produces **no new evidence and no level move**, it records a `frame_saturated: true` marker (a new optional atom field, or reuse `expert_hour`-style sub-map: `frame_stage: {saturated: true, since: <commit>, gate: <one-line BUILD-unblock gate>}`). The gate string is exactly the one already tabulated in `LANE3_H17_BUILD_GATE_SURVEY_20260716.md`.
2. **Draw-skip guard.** `_idle_discover_frame_draw` filters out atoms with `frame_saturated: true` **whose BUILD-gate is still closed**, preferring un-saturated idle atoms. If *every* idle atom is saturated (genuinely no FRAME work anywhere), the draw returns nothing and the turn reports idle-with-reason (Rule 0: this is now a *true* empty feasible set for the FRAME lane, not a spin) rather than re-handing a saturated atom.
3. **Auto-clear.** The marker clears automatically when the atom's BUILD-gate opens (epoch-open / TWIN BUILD-open / director curriculum scenario) or when new evidence/level actually lands — so a re-opened atom re-enters the FRAME/BUILD draw normally. The marker is a cache, never a permanent hold (no orphan transition — R11).

## 4. The R15 mutation test (the DoD — a control that cannot fail is worse than none)

Both directions, per R15 doctrine:
- **FIRES:** given three idle atoms, two FRAME-saturated (gate closed) + one un-saturated, `_idle_discover_frame_draw` returns the un-saturated one; assert the saturated pair is never handed while the third is available.
- **QUIET (no false skip):** given a saturated atom whose BUILD-gate has just *opened*, assert the marker auto-clears and the atom re-enters the draw — the guard must not permanently starve a legitimately-ready atom (fail-open on the wrong side = a stuck atom, the H1-class idle-hole this whole subsystem exists to prevent).
- **All-saturated:** given every idle atom saturated + gates closed, assert the draw returns `None` with a logged reason, and does NOT re-hand any saturated atom (the exact 3× spin this atom fixes).

## 5. Level disposition

- **level_current: 0** — nothing built (this FRAME doc is not a build; EPOCH_GATING Rule 1).
- **level_target: 2** — BUILD the marker + draw-skip guard + the 3-way mutation test (L2: real, tested mechanism code with a DISCOVER-lite/VERIFY pass). L3 would add a HARDEN/adversarial pass proving the guard can't be gamed into starving a ready atom.
- **BUILD-unblock gate:** Epoch-2 BUILD-open (this is harness/supervisor infrastructure in the currently-open epoch) — routes via `director_twin.py::route_blocking_decision` as a reversible BUILD-within-the-open-epoch decision, **not** a one-way door (reversible: git reverts the supervisor change, the draw falls back to current behaviour).
- **file_scope:** `[background, tools, tests, docs/design]` — `supervisor.py` + a mutation test + this doc; disjoint from all six drawn atoms' scopes.

## 6. The six re-drawn atoms this turn (re-confirmed, no churn)

Verified against real disk/git state (R7 — the draw text is a doorbell): all six are unchanged since `LANE3_H17_BUILD_GATE_SURVEY_20260716.md`, each carries a complete FRAME doc, each already lists the survey in `evidence`. Levels HELD: `W4_2`=1 (→3, **WALL** — Tier-1 safety-control re-open, director-reserved), `W1_2`=1 (→2, curriculum WALL + epoch), `B4`=0 (→1, W2_3 depends_on), `B5`=0 (→3, coupled W1_8 + curriculum WALL), `W1_3`=1 (→3, epoch), `W1_4`=1 (→3, W1_3 depends_on + epoch). No new per-atom FRAME written and no redundant `atom_status` inbox emitted (evidence already present — an inbox re-asserting an unchanged level with nothing to append is itself churn). Full gate table: `LANE3_H17_BUILD_GATE_SURVEY_20260716.md`.

## 7. QUEUED sub-finding (2026-07-16, H17 Lane-3) — the detector's SCOPE is too narrow: 7 already-framed atoms read un-saturated

**Not fixed on sight** (F1 bars the map/guard edit; a `supervisor.py`/map change is H23 BUILD-lane work,
BUILD-gated). Registered here so the eventual H23 BUILD widens its own scope. This SHARPENS the remedy
already designed in §3, it does not contradict it.

**Observed (R7, against real disk/map state this turn):** `_atom_has_frame_doc()` recognises a FRAME only
when an `evidence` entry both (a) starts `docs/design/frame/` AND (b) has `FRAME` in the filename. A large
slice of this project's *genuine, complete* FRAME work does **not** live at that path/name, so the intrinsic
detector false-negatives and the draw keeps re-offering atoms that are substantively framed. Concretely, of
the 14 idle atoms the live guard offered as "non-saturated" this turn, **7 are already framed elsewhere**:

| Atom | dial | Where its FRAME actually lives | Why the detector misses it |
|---|---|---|---|
| `W1_5_premise_demand_shape` | 3 | `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.3 (full FRAME depth + I2 invariant + R15 mutation test) | shared multi-atom design doc, not a per-atom `frame/*FRAME*` file |
| `C13_weather_normalisation` | 3 | same design §6 (authoritative gap formula/wall) + `C13_WEATHER_NORMALISATION_DISCOVER.md` | shared design + a DISCOVER doc |
| `W1_10_ev_heatpump_geography` | 3 | `docs/design/W1_10_FRAME.md` | non-canonical path (`docs/design/`, not `docs/design/frame/`) |
| `G4_unified_failure_register` | 3 | `docs/design/UNIFIED_FAILURE_REGISTER.md` | non-canonical path + no `FRAME` in name |
| `A5_tournament_fitness_mortality` | 2 | `docs/design/A5_TOURNAMENT_FITNESS_MORTALITY_FRAME.md` | non-canonical path (uppercase, `docs/design/`) |
| `H20_parallel_maintenance_lane` | 3* | `docs/design/H20_PARALLEL_MAINTENANCE_LANE_FRAME.md` | non-canonical path |
| `H21_self_contained_escalation` | 3* | `docs/design/H21_SELF_CONTAINED_ESCALATION_FRAME.md` | non-canonical path |

(This subsumes and expands the earlier `ad8ec7eac` queue note, which named only G4 + W1_10.)

**Consequence:** the treadmill this whole atom exists to stop is only *partly* closed — the drawn set is
correctly excluded (canonical `frame/` docs), but the guard still keeps re-handing these 7. The genuinely
un-framed idle remainder is now small and mostly low-dial (`A4`, `C4`, `C5`, `D4`, `H8`, `F4` — dial 1;
this turn framed `G3`, dial 2). **All dial-3 FRAME work is in fact complete.**

**Remedy (two options, BUILD's call — the §3 design already supports the cleanest one):**
1. **Cheapest, uses the existing design:** pre-populate the explicit `frame_saturated: true` override
   (§2/§3.1 — already specified as an author-set force-mark for exactly "a FRAME doc under a non-standard
   name") on the 7 atoms above. Pure map edit, no guard-code change, immediately stops the re-offer.
2. **More durable:** broaden `_atom_has_frame_doc()` to recognise a FRAME artefact listed in `evidence`
   regardless of directory, keyed on `FRAME`-in-name OR an explicit `frame_doc:` field — plus a shared-doc
   case (an atom whose `evidence` names a multi-atom design doc that *declares* it frames this id). Higher
   surface; needs its own R15 mutation test (a mis-named FRAME must still read saturated; a shared doc that
   does NOT frame this id must still read un-saturated — TAUTOLOGY guard).

Both are reversible (git reverts) → **not a one-way door**; routes via `director_twin.route_blocking_decision`
as BUILD-within-the-open-epoch when H23 BUILD opens. Whichever is chosen, add a mutation test that plants a
FRAME doc at a non-canonical path and asserts the atom reads saturated — the current gap made executable.

---
*No BUILD code, no level move on any drawn atom. This turn's bankable Lane-3 increment: (1) a genuine
consolidated FRAME for `G3_method_ip_worktree_retro` (dial 2, epoch 2 — the highest-dial, nearest-epoch,
genuinely-un-framed idle atom), turning director-authored method IP from decaying prose into a checkable
BUILD bar; (2) this expanded QUEUE of the detector-scope sub-finding so the treadmill's residual leak stops
evaporating — the doctrinally-correct QUEUE disposition (SELF_INTERRUPT_DISCIPLINE), not a fix-on-sight.*
