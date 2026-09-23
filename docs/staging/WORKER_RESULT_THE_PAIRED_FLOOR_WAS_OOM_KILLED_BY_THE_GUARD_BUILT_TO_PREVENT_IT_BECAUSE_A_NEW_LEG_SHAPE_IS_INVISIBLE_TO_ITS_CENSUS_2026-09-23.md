**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the paired floor was OOM-killed by the guard built to prevent exactly that, because a new leg shape is invisible to its census

*Lane 0 delivery, 2026-09-23. Drawn item:
`the-arms-delta-needs-a-noise-floor-before-634-pounds-means-anything`. The instrument and its
pre-registration landed at 12:08 in `7cb432d36`; this is what happened to the run.*

## What the drawn item asked for, and what was actually owed

The item asks for `tools/run_value_cycle_ab --noise-floor-seeds` against the size-term contrast, so
the £634 net-margin move between the blind and seeing churn beliefs can be read against what the
instrument resolves. `7cb432d36` had already decided — correctly — that the flag named in the item
is the **wrong ruler**: it measures the marginal spread of one configuration, while the £634 is a
*paired* difference at a shared seed. It built `tools/size_term_paired_floor.py` instead, filed the
pre-registration, and launched the family, closing with *"the run is in flight in its own cgroup;
the artefact and the grading against these predictions follow."*

**No artefact follows. The run is dead and it wrote nothing.**

## The reading

`systemctl --user show longjob-size-term-paired-floor-20260923.service`:

| | |
|---|---|
| Result | **`oom-kill`**, `code=killed, signal=KILL` |
| Duration | **1h 26min 0.944s** wall, 1h 25min 41.672s CPU |
| `MemoryPeak` | 8,261,423,104 B = **7,878 MB** |
| `MemorySwapPeak` | 2,472,112,128 B = **2,358 MB** |
| ExecStart | `python3 -m tools.size_term_paired_floor --seeds 5101,5102,5103,5104,5105,5106` |

`docs/observability/value_cycle_size_term_paired_floor.json` does not exist, on this tree or on
either scratch worktree. `run()` writes the artefact after **every pair** and prints a
`[size_term_paired_floor] i/n ...` line each time — deliberately, and its docstring names this very
failure mode. **The log carries zero such lines.** So the kill landed before the first pair closed.

**How far it actually got, and why "three passes" is not "three legs".** The log holds three
`SURVIVED full window` markers. One *leg* is **two** full passes, because `run_value_cycle_ab` runs
the value arm and the flat rule over the same book. So the run completed 1.5 legs of the 14 it
needed (7 pairs × 2 legs) — pair 1's blind leg, pair 1's seeing leg, and half of the next. At
~29 min per pass the whole family was heading for **~13.5 hours**.

## The cause, and it is the guard's own population filter

`floor_run_headroom_refusal` exists precisely to stop this. Its docstring is about the 2026-09-03
kill: *"OOM-killed after 1h 09m and wrote no artefact at all… an absent artefact reads exactly like
a run still in progress, which is why the next session repeats it."* The run on 2026-09-23 called
that guard, was **admitted**, and died the same death 17 minutes longer.

It was admitted because the guard could not see the leg it was being asked about. `running_floor_legs`
identified a floor leg by two conditions:

```python
if "--noise-floor-seeds" not in argv:   continue
if not any("run_value_cycle_ab" in tok for tok in argv):  continue
```

`python3 -m tools.size_term_paired_floor --seeds 5101,…` carries **neither token**. The subject was
scoped in two dimensions at once and each hid the other:

1. **The leg cannot count itself.** `size_term_paired_floor` called
   `floor_run_headroom_refusal()` with no argument, so it was priced at `FLOOR_RUN_PEAK_MB`
   = 6,400 MB — a *noise-floor* leg's measured peak. It needed 7,878 MB. The guard under-priced
   the caller by **1,478 MB of RSS, in the flattering direction**.
2. **No other leg can count it either.** A noise-floor run launched beside a live paired floor
   computes `required = 6400 × (0 + 1)` and is waved through while 7.9 GB is already committed.
   The 2026-09-03 defect is fully re-opened for any pair involving the new leg shape.

And the arithmetic itself could not have expressed the answer even with a correct census:
`required = FLOOR_RUN_PEAK_MB * (len(legs) + 1)` prices *n* legs at **one** peak. Two leg shapes
that genuinely differ by 1,400 MB collapse to whichever constant the multiplication uses.

**Why a paired leg is genuinely bigger, which is why this is a second constant and not a bug in the
first.** A noise-floor leg runs one configuration per process. A paired leg runs *both* — blind and
seeing — in one process, because sharing a seed across the two is the entire point of the
instrument. It carries two worlds' retained state where its sibling carries one.

## What landed

`tools/run_value_cycle_ab.py`, `tools/size_term_paired_floor.py`,
`tests/tools/test_value_cycle_ab_noise_floor.py`:

- `FLOOR_LEG_SHAPES` — a table of `(module substring, flag token, measured peak MB)`. The flag must
  be its own argv token and the module is a substring match, which is the discriminator the
  2026-09-03 census already learned: a sibling shell carries the whole pipeline as one argv element.
- `PAIRED_FLOOR_RUN_PEAK_MB = 7800.0`, from the kill above. Rounded **down** on the same convention
  as its sibling — the number exists to refuse, and a requirement set above the true one refuses
  runs that would have finished. Stated in RSS, not RSS+swap, because the quantity it is compared
  against is `available_mb`, which is MemAvailable and counts no swap. Like the 6,400 it is a
  **floor on the requirement, not a peak**: the run it came from was killed.
- `running_floor_legs` now returns `(pid, rss_mb, peak_mb)` — each leg carries **its own** price, so
  a caller cannot multiply one peak by a count.
- `required = sum(each leg's own peak) + own_peak_mb`, and `size_term_paired_floor` passes its own.

Mutation-proven, each mutation redding its own leg and not a neighbour's:

| mutation | red |
|---|---|
| drop the paired entry from `FLOOR_LEG_SHAPES` | `…sees_a_paired_floor_leg_and_prices_it_at_its_own_peak` (leg vanishes from census) |
| price both shapes at `FLOOR_RUN_PEAK_MB` | same test, on the price assertion |
| restore `FLOOR_RUN_PEAK_MB * (len(legs) + 1)` | `…refused_on_the_sum_not_a_multiple` |
| ignore `own_peak_mb` | `…refused_on_the_sum_not_a_multiple` |

The refuse test's margin is deliberate: a guest offering 13,500 MB with one noise-floor leg running
needs 6,400 + 7,800 = 14,200 MB, while the old arithmetic asks 12,800 and admits it. The gap is
*inside* the 1,400 MB the old arithmetic under-counted by, so only the per-shape sum reaches that
verdict. **The pass branch is asserted beside it on the same shapes** — a guard that refused every
paired run would satisfy the refusal leg and make the instrument unrunnable, which is
indistinguishable from the defect it exists to prevent.

## The landing itself carried a second trap, and it is worth recording

The working-tree copy of `tools/run_value_cycle_ab.py` was **423 lines shorter than HEAD** and last
committed 2026-09-22, while carrying another lane's live uncommitted work (`arm_population_pair`,
`arm_population_instrument`). Committing it by pathspec would have reverted `declined_renewals`,
`_denominator_reconciliation`, `_same_priced_population` and `NOISE_FLOOR_PROGRESS_MARKER` — landed
work — *and* swept a neighbour's unfinished work into my commit. The hunks were composed onto HEAD's
bytes and landed with `surgical_land --content`; the composed file was verified to differ from HEAD
only in the guard region, to retain all four landed symbols, and to contain none of the other lane's
work.

## What is still owed on the drawn item — and it is the whole measurement

**The £634 is still unfloored. Nothing about the contrast has been measured.** This turn bought the
ability to find that out in seconds rather than in 1h 26m.

With the fix in place the guard now **refuses** a paired run on this box, correctly: at the time of
writing `available_mb` is **1,605 MB** against a requirement of 7,800. That refusal is the honest
state and it is not a reason to pass `--ignore-headroom`.

The named next step, and it is a design change rather than a relaunch:

> **Run one pair per process.** The family's peak is driven by both configurations sharing a
> process. One pair per process makes the peak a single leg's, makes an OOM cost one pair instead
> of everything, and lets the artefact accumulate across processes — which `run()` is already
> written to do, since it rebuilds the whole report from `pairs` after each one. A 7-pair family
> then becomes seven ~1h units that fit, instead of one ~13.5h unit that does not.

Until that exists, **no seed budget can be spent on this box**, and the £634 stays what
`fc390b918` already called it: a one-seed move nobody should read as a change.

## Correction to the record

`7cb432d36`'s closing sentence — *"the artefact and the grading against these predictions follow"* —
is false and is corrected here rather than quietly. The five pre-registered predictions in
`docs/staging/records/SEAT_PREREG_THE_PAIRED_SIZE_TERM_FLOOR_2026-09-23.md` remain **ungraded and
unrun**, which is the state they should stay in until a seed family completes. Nothing in this
finding touches them; a prediction filed before its answer is still a prediction, and none of these
has an answer yet.
