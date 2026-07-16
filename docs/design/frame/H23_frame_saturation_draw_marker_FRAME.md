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

---
*No BUILD code, no level move on any drawn atom. This turn's bankable Lane-3 increment is registering the DIAL-defect remedy as a drawable proposal atom (H23) so it stops evaporating — the doctrinally-correct QUEUE disposition of this draw's own thrice-observed meta-finding.*
