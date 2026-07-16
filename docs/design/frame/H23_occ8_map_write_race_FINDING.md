# FINDING — H23 residual frame-saturation leak: the map-write/draw-read race (occurrence 8)

**Turn:** H17 Lane-3 DISCOVER/FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map edit — F1).
**Atom home:** `H23_frame_saturation_draw_marker` (this SHARPENS its queued residual; see
`H23_frame_saturation_draw_marker_FRAME.md`). Written as a **standalone, self-owned file** — not an append to
that FRAME doc — deliberately: that doc is under active concurrent rewrite this turn (its length changed between
two reads seconds apart), so a shared read-edit-write there would be a lost-update collision. Writing only my own
disjoint file is the exact "safe by construction, not by convention" discipline `docs/design/atom_status/README.md`
mandates. **That live observation is itself a second, independent confirmation of the bug class below.**

## What occurrence 8 is

The idle DISCOVER/FRAME self-refill re-drew the FRAME-saturated set an **eighth** time (`W4_2_verifier_timing_extension`,
`W1_2_generate_futures`, `B4_competitor_field`, `B5_regional_basis_risk`, `W1_3_national_weather_signal`,
`W1_4_regional_weather_field` — identical to occurrence 7). Verified against real disk/git state (R7 — the draw is a
doorbell): all six carry complete FRAME docs, all read `_is_frame_saturated → True` against the committed map, levels
**HELD**, evidence already folded. **No new per-atom FRAME, no redundant atom_status inbox, no map edit, no BUILD
code** — an inbox re-asserting an unchanged level with nothing to append is itself the churn SELF_INTERRUPT_DISCIPLINE
+ R12 forbid. The six drawn atoms are a genuine no-op this turn.

The bankable increment is instead the **root cause** of the residual leak occurrence 7 could only call
"plausible, not verified".

## The mechanism — code-verified (R9, observed against real code, not inferred)

The current live guard is correct in the steady state: against the committed map every one of the six reads
`_is_frame_saturated → True` and `_idle_discover_frame_draw_concurrent()` excludes all six, yielding a fresh
un-framed set (`G4_unified_failure_register, W1_5_premise_demand_shape, C13_weather_normalisation, A4_sim_approver,
C4_adoption_physics, C5_key_moment_conversion`). So the leak is not a guard-logic bug — it is a **read/write race
on the map file**:

1. `background/supervisor.py:482` — the idle draw reads the **working-tree** map fresh every cycle:
   `yaml.safe_load(MATURITY_MAP_PATH.read_text(encoding="utf-8"))`. Never a committed snapshot.
2. `tools/merge_atom_status.py:276` — the integrator's fold writes the map with a **non-atomic** in-place
   `map_path.write_text(new_text)` (open-truncate-write), **not** tmp-file + `os.replace` (atomic rename).

A draw-cycle `read_text` that interleaves with a fold's `write_text` reads a **truncated/partial** map. An atom
whose `evidence` list is transiently absent or garbled makes `_atom_has_frame_doc` return `False` → the guard
**fail-opens** and hands the saturated atom. This is a textbook **R15 fail-open / fail-silent** defect: an
unavailable or partial map read is a FAILED read, but the guard treats it as "atom not saturated → offer it"
rather than failing closed.

### Time-correlation — partial, stated honestly (R9)

3 of the window's leak-draws align **to the minute** with the only 3 map-fold commits in that window:

| Leak-draw (UTC) | Coinciding fold commit |
|---|---|
| 18:57 | `5f5fefb88` (18:57 UTC) |
| 19:02 | `b4e8f8d51` (19:02 UTC) |
| 19:36 | `d3f8360bc` (19:36 UTC) |

3 other leak-draws (`19:09`, `19:23`, `19:26` UTC) do **not** coincide with a fold commit. So the fold-write race is
a **strongly-evidenced candidate**, not the sole proven cause — the mid-fold partial read itself is **inferred from
the code path plus the 3 coincidences, not directly captured**. (Capturing it is exactly the draw-path instrumentation
occurrence 7 queued; a fold's git-*commit* time also lags its map-*write*, blurring the alignment. Other concurrent
`docs/design`/tree writers — e.g. run-complete processing — may account for the non-coinciding draws; not asserted.)

## Remedy — sharpened, QUEUED not fixed (SELF_INTERRUPT_DISCIPLINE)

The fix is BUILD on `supervisor.py` / `merge_atom_status.py` — outside this Lane-3 doc-only draw — so it is
**registered, not fixed on sight**. It upgrades occurrence 7's queued "add a why-excluded log line" from a
*diagnostic* to a *root fix*:

- **(a) Atomic map write (root fix).** In the fold, `write_text` to a temp path in the same directory then
  `os.replace(tmp, map_path)` — an atomic rename, so no reader ever observes a partial map. ~2 lines + an R15
  mutation test: a reader interleaved with a fold must always see either the whole old file or the whole new file,
  never a partial one.
- **(b) Fail-closed map read (defence-in-depth).** In the daemon's draw, on a YAML parse error or an atom-count /
  shape anomaly, **skip the draw cycle** (log the reason) rather than proceed on partial data and hand a saturated
  atom. Guards against any other partial-write source.

(a) is the cleaner single-writer root fix; (b) hardens the reader independently. Both reversible (git reverts) →
**not a one-way door**; route via `director_twin.route_blocking_decision` as BUILD-within-the-open-epoch when the
H23 BUILD lane next opens. Whichever ships, the R15 mutation test above is the DoD — a control that cannot fail
is worse than none.

---
*Bankable Lane-3 increment: the H23 residual leak's mechanism moved from "unexplained / plausible" (occurrence 7)
to code-verified (line-referenced non-atomic write + working-tree read = a fail-open race), with a sharpened root
remedy (atomic map write + fail-closed read) queued for the H23 BUILD lane. Six drawn atoms HELD, no FRAME churn,
no redundant inbox, no map edit (F1), no BUILD code.*
