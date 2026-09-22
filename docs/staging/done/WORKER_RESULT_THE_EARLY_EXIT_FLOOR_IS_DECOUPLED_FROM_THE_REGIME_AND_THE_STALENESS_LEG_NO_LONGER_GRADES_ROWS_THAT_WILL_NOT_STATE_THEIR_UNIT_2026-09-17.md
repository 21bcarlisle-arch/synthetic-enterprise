**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The early-exit floor is decoupled from the regime, and the staleness leg no longer grades rows that will not state their unit

**Filed** 2026-09-17 · worker · lane 0 delivery
**Item** `decouple-the-early-exit-floor-from-the-regime-constant-then-re-date-the-stale-hook-chain-measurement`

> **Both pieces landed, the constant is re-measured 134 → 333, and a live two-control wedge that
> was refusing every commit in the tree is cleared — honestly, by fixing the unit rather than by
> moving the bar.** Five mutations verified to fire; a sixth turned out to be an equivalence on
> today's data and a new control was written until it fired.

---

## The premise held

The draw's premise check flagged that `8cb9a6b96` is already an ancestor of `origin/main`. That is
the item's **precondition**, not its work: `8cb9a6b96` is where the row-level `chains` field
landed, and the item's second piece is to *consume* it. Re-measured before starting —
`origin/main` still carried `floor_of_a_real_chain = MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04
/ 4.0`. Nothing was done twice.

## What was found first: the tree was wedged, and four working copies were stale

`test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today` and
`test_the_headroom_control_ACTUALLY_REDS_at_a_deadline_below_the_measured_chain` were **RED at
HEAD** — the staleness leg missing `0.75 × 880 = 660` by **seven seconds** on a worst of 666.95s.

Separately, four files in the shared working tree were **stale copies**, identical to a local HEAD
that is forked from `origin/main`, each silently reverting a landed repair:

| file | what the stale copy reverted |
|---|---|
| `background/process_run_complete.py` | the `chains=` producer repair (`8cb9a6b96`) |
| `tests/background/test_process_run_complete.py` | the same |
| `background/suite_duration_watch.py` | `PUBLISH_CADENCE_SECONDS` 5400 → 1500, dropping its whole re-measurement comment |
| `tests/background/test_suite_duration_watch.py` | the paired derived-not-pinned cadence legs |

None were holder work — each was byte-identical to local HEAD with no local edit. All four were
refreshed to `origin/main`'s bytes before anything was written. **The tell was the direction:** a
working copy that *deletes* a dated 2026-09-17 provenance comment is behind, not ahead.

## Piece 1 — the floor is decoupled, and this is why it could not be re-dated blind

`MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04 = 134` served two uses pulling in **opposite
directions**:

- it is the **representative per-chain cost** — must RISE with the regime;
- it set **`floor_of_a_real_chain = MEASURED / 4`**, the discriminator between an early exit and a
  real chain — must stay BELOW the smallest real chain, which **has not risen and cannot**: it is
  the cost of running the gate once.

Measured over all 195 rows of `commit_hook_duration.jsonl`: nine early exits spanning
**0.93–1.58s**, then **nothing** until **67.44s**. A 42× empty gap. An honest regime figure of 333
puts the derived floor at **83.25s — above 67.44s**, so a genuine chain would read as a
short-circuit and the live control would skip itself green. *A growing regime was silently walking
a fail-open boundary up through the population it exists to exclude.*

`EARLY_EXIT_CEILING_SECONDS_2026_09_17 = 10` is keyed to the **emptiness** instead: the geometric
centre of the gap (`√(1.58 × 67.44) = 10.3`), 6.3× above every early exit ever recorded and 6.7×
below every real chain. It is the middle of a hole, and it moves only if the hole does.

## Piece 2 — the constant is re-measured, 134 → 333

Worst of the last twenty gradeable rows: **333.22s** (`770497ddd`). **One row is excluded and the
exclusion is the point** — `b55667741`'s 666.95s, which the publisher's own log names as two chains
of ~333s and which predates the `chains=` repair. Reading it as one chain is the inference that
wedged the tree, so it is not read as one here either.

The regime is monotone across three slices, not one bad day: `90–100s` → `126–218s` → `253–333s`.
The derived floor moves 168s → **417s**, and the room under the 900s ceiling narrows 732s → **483s**.
Both derived figures were recomputed in place rather than left reading the old number.

## Piece 3 — the two legs now read the window differently, and that IS the repair

The two legs pull opposite ways on the same number, which is what made one window wrong:

- **HEADROOM** (`deadline ≥ 1.25 × worst`) reads **every gradeable row, silence at face value**. A
  silent row holds *n ≥ 1* chains, so its duration is an **upper bound** on the per-chain cost —
  over-reporting can only demand more headroom. Safe. Teeth retained.
- **STALENESS** (`worst ≤ 0.75 × deadline`) reads **only rows carrying a positive int `chains`**.
  That leg demands a **RE-MEASUREMENT**, and a re-measurement names a per-chain figure — you cannot
  name one from a row that will not say how many chains it holds.

That asymmetry is exactly the live defect: 666.95s **passed** the headroom leg (834 < 880) and
**red** the staleness leg by seven seconds, refusing every commit in the tree — the liveness
heartbeat included — with a message demanding a re-measurement no honest number could satisfy.

**The transition rule: a mixed window does not narrow AT ALL.** `chains` landed today with 195
silent rows behind it, so on the first commit after it the stated sub-window is **one row**, and
`max()` of one row is not a regime — a single fast chain would have certified it. So the staleness
leg simply cannot tell yet, and **says so on its surface** rather than in a footnote:

> `STALENESS LEG NOT GRADED: 19 of the last 19 gradeable hook-chain rows do not state their unit
> (chains, added 2026-09-17 at 8cb9a6b96) … The headroom leg above is graded and green. Clears once
> 19 more commits land.`

Self-clearing in twenty commits, and
`test_the_staleness_leg_fires_again_once_the_window_states_its_unit`'s arm 1 is what stops that
being a quiet disarm.

## Mutation evidence — five fire, and the sixth is the interesting one

Applied in a `git archive` extract under `~/.cache`, never the shared tree. Each verified to alter
the bytes, then verified to fire.

| # | mutation | fires |
|---|---|---|
| A | `EARLY_EXIT_CEILING = 83` (what re-dating under the old coupling would have forced) | `…floor_sits_in_the_EMPTY_GAP…` |
| B | delete the `len(stated) < len(recent)` guard | `…staleness_leg_CANNOT_FIRE…` arm 2b |
| C | `stated` = every gradeable row | `…never_narrows_to_a_degenerate_sample` |
| D | accept a bool as a chain count | same, bool leg |
| E | revert the reader's floor to `MEASURED / 4` | `…floor_sits_in_the_EMPTY_GAP…` — **after a new leg was written** |

**Two draft claims of mine were wrong and were corrected rather than kept:**

1. I wrote that mutation B would fire arm 2. **It did not.** With the guard gone the leg grades
   `max(stated)`, which in that fixture is the *fast* row, and passes. What it actually fired was
   the live control — on a series that stops being mixed in twenty commits, which would have left
   the claim false and unnoticed. Arm **2b** was added with the stated row *over* the bar, which
   catches it independent of the live data.
2. **Mutation E was an equivalence on today's series** — all six controls stayed green, because
   every row in today's window is far above 83.25s. The repair's use-site was graded by nothing.
   Handed a window holding the smallest real chain, the coupled floor **skips it**
   (*"worst 67.4s against a real chain's 83s floor … UNOBSERVED in this window"*). That leg is now
   asserted — and its first form made the mutation report **`5 passed, 1 skipped`**, green, because
   the reader refuses via `pytest.skip` and **a skip is the same colour as a pass**. The skip is
   now converted into a failure.

The gap control derives both populations from the **largest ratio gap** in the sorted series rather
than pinning 1.58 and 67.44, and refuses outright if that gap ever falls below 10× — a boundary
drawn through a continuum is not a boundary.

## One tension with standing direction, recorded rather than resolved quietly

`docs/direction/DIRECTION.yaml` carries
`the-commit-hook-chain-has-grown-five-fold-and-that-is-what-the-publisher-keeps-losing-to`, which
says re-dating the committed measurement **to 667** "would silence the one control now telling the
truth."

**I re-dated to 333, not 667**, and the staleness leg compares against the *deadline*, not against
this constant — so raising it silences nothing. The 667 figure is two chains; the per-chain truth
is 333, and the constant's docstring records the 2.5× climb as *a finding about this machine*
rather than answering it. But the direction is right that the chain has genuinely grown and every
lane pays it, and **that item is not discharged by this work** — it asks for the chain to be made
*cheaper*, which is untouched here.

Two further notes for whoever takes it:

- That item's third ask — *"the filter drops any row whose duration exceeds its ceiling, which is
  why the 1381s overrun is invisible to the assert with teeth"* — is **partly closed as a side
  effect**. 1381.52s is itself a two-chain row (`2c89bd534`, "lost the race on all 2 attempts");
  per-chain it is ~690s, which is under 880 and therefore **no longer dropped** once rows state
  their unit. The ceiling filter existed only because the reader could not tell a multi-chain total
  from a slow chain. It is not fully closed: the nine days of silent rows behind the repair are
  still filtered that way, and nothing can fix that retroactively.
- **DIRECTION.yaml still names `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04`,** which no longer
  exists. Left untouched — it is the director's file and another lane has it staged.

## Also cleared while in the tree

`background/finding_classes --check` was **FAIL** on a TWO ROOMS collision —
`PREREG_THE_PUBLISH_WEDGE_IS_ONE_FILE_2026-09-17.md` present in both the root and `records/`. The
two copies were **byte-identical**; `staging_two_rooms_repair.classify` graded it `redundant` and
the sanctioned repairer cleared it. Not this item's work, but it blocked every commit in the tree.

## Found in passing, not fixed: a twelve-day-old orphan that reds the ruff ratchet

`tests/architecture/test_static_quality_ratchet.py::test_ruff_baseline_matches_frozen_census` is
**RED in the shared working tree** — `{'I001': 1307} != {'I001': 1308}`. Attributed by one-variable
census rather than guessed: green in a `git archive` extract of `origin/main`, green in one of local
`HEAD`, so it is uncommitted content. The single differing file is
**`tests/tools/test_generate_maturity_map_data.py`** — *not* mine, mtime **2026-09-05**, 37
uncommitted insertions carrying a finished and documented control
(`test_an_unreadable_tracker_refuses_rather_than_publishing_every_atom_unstalled`). It sorted an
import, which lowered `I001` by one without the frozen baseline being lowered to match.

Twelve days stranded, and it reds the working-tree ratchet for **every** lane. Not swept into this
commit and not reverted — it is another lane's finished work and the fix is to land it *with* a
lowered baseline, which is its author's call. It does not block this landing because
`surgical_land` gates the tree the commit *would* create rather than the working tree. Existing
class: `uncommitted_and_orphaned_work`.

## Evidence

- `tests/background/test_process_run_complete.py` + `tests/background/test_suite_duration_watch.py`:
  **157 passed, 0 skipped** in the shared tree (was 2 failed before this work).
- `background/finding_classes --check`: **PASS (0 failures)**.
- `ruff check`: 1 pre-existing `E402` per file, byte-identical to `origin/main`'s. Nothing added.
