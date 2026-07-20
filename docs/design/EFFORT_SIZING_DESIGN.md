# Effort Sizing Design (G5_effort_sizing_discipline)

**Status (2026-07-16):** CALIBRATION half built (`tools/effort_calibration.py`,
L0->L1 evidence below). This doc specifies the remaining SIZING half — the
`size` field, its FRAME-time basis rule, and the XL soft-gate — as a schema
proposal for the orchestrator to apply to `docs/design/maturity_map.yaml`
(this fork's `file_scope` does not include the map; see
`docs/staging/done/EFFORT_SIZING_DISCIPLINE.md` for the original brief).

## 1. The gap

Maturity levels (L0-L5) describe MATURITY, not EFFORT — an L0->L2 atom could
take 20 minutes or 3 days and the map cannot tell you which before the fact.
Nothing estimates effort before work starts; the loop/timer/deadman machinery
is runtime TOLERANCE for unknown duration (coping), not PLANNING. This project
has an unusual advantage most backlogs sizing by guesswork lack: every level
transition is already git-timestamped, so sizing can be CALIBRATED against
real actuals rather than argued from priors. See
`docs/staging/done/EFFORT_SIZING_DISCIPLINE.md` for the full original brief
(director-raised, disposition QUEUE).

## 2. The `size` field

**Where it lives:** a new optional top-level scalar on each atom entry in
`docs/design/maturity_map.yaml`, alongside `dial_inherited`/`level_target`:

```yaml
- id: G5_effort_sizing_discipline
  ...
  level_target: 2
  size: M                       # NEW -- S | M | L | XL
  size_basis: "calibration tool + design doc; no runtime/site changes"   # NEW
  ...
```

- `size`: one of `S`, `M`, `L`, `XL`. Set at **FRAME time** (when an atom is
  decomposed/scoped for BUILD), not at registration — a proposal atom with no
  scope decided yet has no size, same as it has no committed `level_target`
  approach.
- `size_basis`: **one line**, free text, stating *why* this size was chosen
  (touched files/lanes, novelty vs. precedent, whether it crosses the SIM/
  company wall, whether it depends on an unresolved upstream atom). This is
  the "one-line-basis rule" the brief requires — sizing without a stated
  reason is a guess, not an estimate, and cannot be checked or corrected.
- Both fields are **optional and additive** — omitting `size` changes nothing
  about how an atom draws today (`dial_inherited` remains the sole draw-order
  input); `calibration_by_size()` in `tools/effort_calibration.py` already
  degrades gracefully (`status: "no_size_data_yet"`) when no atom has the
  field, and activates automatically, unchanged, the day the first atom gets
  one.

**Band definitions (informed by real observed durations, not invented in a
vacuum — see the calibration evidence in §4):**

| Band | Rough scope | Anchor from actuals (2026-07-16 run) |
|------|-------------|----------------------------------------|
| S    | one file / narrow fix, disjoint scope | sub-hour to ~2h transitions observed (e.g. W2_customer_generator lane median 0.27h) |
| M    | a few files, one lane, one clear DoD | few-hour to ~1-day transitions (e.g. A_strategy_governance lane, 2-22h observed) |
| L    | multi-file, crosses a seam or couples two atoms | ~1-2 day transitions (e.g. H_harness lane median ~28h observed) |
| XL   | multi-file AND multi-seam AND/OR undecomposed scope | anything materially past the L band for its lane, or scope not yet reducible to a one-line basis |

These bands are a **starting calibration**, not a fixed target — as more
transitions land with a real `size` recorded, `tools/effort_calibration.py`'s
`by_size` distributions become the live source of truth and this table should
be refreshed from that output, not the reverse.

## 3. The XL -> decompose soft gate

If FRAME sizes an atom `XL`, that is a **signal to decompose before BUILD
starts**, not a blocker on its own:

- The FRAME pass must either (a) split the atom into two or more sized child
  atoms (each `depends_on`-linked or independently scoped) before it is
  BUILD-eligible, or (b) record an explicit one-line reason decomposition
  was considered and rejected (e.g. genuinely atomic, cannot be split without
  breaking the exit test).
- This is a **soft gate on size, not on time** — it never blocks an atom that
  is merely taking longer than expected mid-BUILD (that is what the runtime
  tolerance machinery — timers/deadman/loop boundaries — already handles).
  It only fires once, at FRAME, before work starts.
- Enforcement mechanism (proposed, orchestrator's to wire): a DISCOVER/FRAME
  checklist item, and optionally a `tests/tools` assertion that no atom with
  `size: XL` and `loop_stage` in `{build, harden}` lacks either child atoms in
  `depends_on` of other atoms or a `size_basis` explaining the exception. Not
  built in this fork (would require editing the map / FRAME tooling, outside
  this fork's `file_scope`).

## 4. Calibration mechanism (built this fork — the evidence)

`tools/effort_calibration.py` (read-only, two `git log` calls, never mutates
`maturity_map.yaml`):

1. Reads every atom's current `lane` (and `size`, once populated) from the map.
2. Walks `git log` on `maturity_map.yaml` and parses each commit **subject**
   for this repo's own established convention, `<atom-short-code> -> L<n>`
   (e.g. `"H10 -> L3"`, `"C9->L3+W2_7->L3"`, `"Record H14 judge-validation
   L0->L2"`) — a convention already visible across ~50+ real commits in this
   repo's history, not invented for this tool.
3. For each atom, computes the elapsed **hours between consecutive recorded
   level transitions** (an atom's first recorded transition has no prior
   anchor and yields no duration — no start time is guessed).
4. Aggregates those real durations into a distribution **per lane**
   (`calibration_by_lane`) and, once any atom carries a `size`, **per S/M/L/XL
   band** (`calibration_by_size`) — mean/median/min/max/stdev, hours.

**Real run against this repo's own history (2026-07-16), evidence for L1:**

```
transitions parsed: 51, durations computed: 16
excluded ambiguous short codes: F5
by lane:
  A_strategy_governance: n=2 mean=12.02h median=12.02h min=2.12h max=21.92h
  C_customer_ops: n=1 mean=0.91h median=0.91h min=0.91h max=0.91h
  H_harness: n=6 mean=24.42h median=27.91h min=0.26h max=33.7h
  W2_customer_generator: n=6 mean=2.19h median=0.27h min=0.13h max=11.93h
  W3_industry_systems: n=1 mean=1.73h median=1.73h min=1.73h max=1.73h
by size: no_size_data_yet
```

This is a genuine computed distribution from git-timestamped actuals, not a
mock — reproducible via `python3 -m tools.effort_calibration --json`.

**Known limitation (documented, not hidden):** commit-subject parsing is
heuristic (regex over free-text prose, not a structured log). Several short
codes are ambiguous in this repo's real history (`F5`, `G1`, `G2`, `G3`,
`H23`, `H24`, `H27`, `OPS1` — each shared by two atoms) and are excluded
rather than guessed. A commit that bundles a transition mention without the
`->L<n>` arrow syntax (e.g. prose-only mentions) is not counted. This
under-counts rather than over-counts, which is the safe failure direction for
a DIAL/diagnostic tool (per §5).

**Demotion/revert exclusion (2026-07-20 HARDEN, red-team of the AT-target
atom):** the safe-failure-direction claim above was being *violated* by a real
case — `compute_durations` counted every consecutive transition pair as
positive elapsed cost, including DEMOTIONS. Two live level reverts
(`BRAND1_identity_system` L3->L2 and `SITE1_expert_doors` L2->L1, both from the
fronts_reconciler reverting self-promotions) landed at ~123h and ~121h and were
dominating the `H_harness` lane `max`/`mean`, and non-progress pairs were
dragging the `L` size-band median to an implausible ~0.6h. A demotion is time
the atom SAT at the higher level before reverting — not build effort toward a
level — so `compute_durations` now keeps only a STRICT rise
(`cur.to_level > prev.to_level`). The effort to RE-reach a level after a revert
(the demotion→re-promotion pair, genuine rework) is still counted; the revert
itself is not. This restores the honest under-count invariant, now enforced by
`test_compute_durations_excludes_demotion_reverts` /
`_counts_rework_after_revert_but_not_the_revert` /
`_drops_same_level_reaffirmation` (mechanism, not just prose — MAKE_IT_STICK).

## 5. THE GUARDRAIL — dial, not a wall (non-negotiable)

Sizing and calibration are diagnostics. They inform decomposition and
prioritisation. They are **never** a target or a completion gate:

- An estimated `size: M` becoming "must finish in M" would reintroduce the
  deadline pressure that manufactures self-certified levels — the same
  failure mode R12 (anti-goal-seek) already names for margin and cycle-time.
  Size to DECIDE and DECOMPOSE, never to JUDGE completion.
- `tools/effort_calibration.py`'s own module docstring and `build_report()`
  output both carry this guardrail as a first-class field (`"guardrail"` key
  in the JSON report) so it travels with every consumer of the tool, not just
  this document.
- Estimate-vs-actual divergence (a lane consistently running long against its
  own historical band) is a **learning signal about the lane**, never a stick
  against the atom or the fork that built it.
- This guardrail belongs in `CLAUDE.md` per the original brief's DoD
  ("the dial-not-a-gate guardrail recorded in CLAUDE.md") — not added in this
  fork because CLAUDE.md is at its 35k-char hard limit
  (~34,800/35,000 at time of writing) and edits there are explicitly this
  fork's orchestrator's follow-on, not this fork's `file_scope`.

## 6. What remains for L2

**Built (2026-07-16, second fork — the mechanism half):** `tools/effort_
calibration.py` gained four functions implementing everything in this doc
except the schema fields themselves: `expected_hours_for_atom` (the fallback
chain: real per-size actual → `SIZE_BAND_ANCHOR_HOURS` → real per-lane
actual → unknown; XL never sized, matching §3/§5), `remaining_effort_report`
(sized below-target total, §1/§6), `estimate_vs_actual_by_lane` (per-lane
delta + direction, §4/§5), and `xl_decompose_flags` (the soft gate itself,
§3 — flags only, never blocks, silent when a child atom or an explicit
`size_basis` exception is recorded). `background/effort_digest.py` (new)
renders all three as an `EFFORT SIZING` block in `LATEST.md`, wired into the
live publish cycle in `background/process_run_complete.py` next to the
existing `NAIVE ORGAN asks:` block, with the same defensive
try/except-log-and-swallow discipline — this digest can never break
publishing. CLI: `python3 -m tools.effort_calibration --remaining-effort /
--estimate-vs-actual / --xl-flags`. Tests: `tests/tools/test_effort_
calibration.py` (fallback chain, aggregation, XL gate) and `tests/
background/test_effort_digest.py` (digest render + wiring), all using
FIXTURE atoms with `size` set — the real map still carries none.

**Still open (the orchestrator's, per this fork's `file_scope`):**

- `size`/`size_basis` fields actually live on real atoms in the map (schema
  in §2 above; representative proposed sizes for ~8-10 real atoms are in
  `docs/design/atom_status/G5_effort_sizing_discipline.yaml`'s
  `append_simplification`, ready to apply).
- The XL → decompose soft gate wired into the actual FRAME workflow (the
  mechanism — `xl_decompose_flags()` — is built and tested; nothing calls it
  as part of FRAME yet).
- The dial-not-a-gate guardrail landed in `CLAUDE.md` itself (currently only
  in this doc, the tool's own output, and the digest block's own header
  line).

`level_current` for this atom is left unset by this fork (LEVEL HONESTY —
the orchestrator applies the real `size:` values and confirms the full L2
DoD before moving the level).
