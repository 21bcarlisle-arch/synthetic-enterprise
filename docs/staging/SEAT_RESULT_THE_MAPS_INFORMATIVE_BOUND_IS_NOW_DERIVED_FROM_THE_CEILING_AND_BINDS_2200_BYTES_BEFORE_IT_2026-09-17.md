**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# RESULT: the map's informative bound is derived from the ceiling now, and it binds 2,200 bytes before it

Delivery seat (lane 0), 2026-09-17. Claim
`map-size-bound-derive-and-name-the-fattest-rows`. Discharges
`SEAT_FINDING_THE_MAPS_INFORMATIVE_SIZE_BOUND_HAS_BEEN_DEAD_SLACK_FOR_297_COMMITS_AND_ONLY_THE_UNINFORMATIVE_ONE_CAN_FIRE_2026-09-17.md`,
both of its remedies. The fork that stranded the drain is closed in the same turn.

## The two numbers, before and after

| | authorised by the per-atom bound | ceiling | can it bind first? |
|---|---|---|---|
| fixed `MAP_MEAN_BYTES_PER_ATOM = 1400`, 350 atoms | 490,000 B | 409,600 B | **no — 80,400 B of guaranteed silence** |
| derived from the ceiling, 350 atoms | 407,400 B | 409,600 B | **yes, by 2,200 B** |

The old number grew its own slack by 1,400 bytes with every atom minted. The new one is
`(MAP_SIZE_CEILING - MAP_PER_ATOM_RESERVE) // atom_count`, so the slack is a constant 2,048 bytes
whatever the population does.

Live verdict at the merged tree: 400,209 B over 350 atoms, mean 1,143 B/atom against a budget of
1,164. Green, with 7,191 bytes of room to the informative bound and 9,391 to the ceiling.

## The part the finding did not ask for, and why it had to land too

A derived bound refuses at 2,048 bytes of headroom — **inside** the band where
`map_store.size_warning` said *"This commit fits"*. One limit, two surfaces, opposite advice: the
VAT shape. So the warning has three bands now, not two, and
`test_the_reserve_band_says_the_commit_does_NOT_fit_and_the_band_above_says_it_does` asserts the
edge from both sides. The reader's path is: silent above 8 KB → *this commit fits, and the next
line down is the reserve, N bytes from here* → *this commit does not fit, and here are the rows* →
the ceiling, which can now only be reached by a single commit adding more than 2 KB, and which no
longer arrives alone.

## Where 2,048 comes from

The same distribution `MAP_SIZE_WARN_HEADROOM` was derived from, re-measured on this tree: over
the 200 most recent commits touching either map half, 126 grew it — median **+695 B**, p75
**+2,008**, p90 +4,451, p95 +6,404, max +19,406. Every percentile reproduces the recorded
derivation exactly; the grew-count is 126 against the 127 recorded there because the 200-commit
window has since slid by one, which is the kind of drift that makes a figure worth re-taking
rather than citing.

2 KB is p75. Below that much headroom more than one ordinary map commit in four would breach the
ceiling outright, so *"there is still room to act"* has stopped being true and a refusal that names
rows is worth more than a warning that says the commit fits. 8 KB is above p95, which is why the
warning band sits outside it. Neither number is picked.

## What the refusal says now

`atom_byte_sizes` measured every row and both bounds threw the ranking away before refusing. Both
carry it now:

```
mean 1142 B/atom over 350 atoms, above the 1000 B/atom this population can afford under the
409600-byte ceiling (399701 B used of the 350000 B authorised). This is the ceiling arriving
early, on purpose, so it can say WHERE:
  SITE1_expert_doors: 10757 B
  W1_14_weather_cells_for_household_heat_load: 9216 B
  PB3_book_growth_as_earned_outcome: 6457 B
  W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over: 5796 B
  D27_belief_window_saturates_on_this_book: 5444 B
```

## A prediction of this control's own is corrected, in place

`test_per_atom_budget_is_invariant_to_atom_COUNT` asserted that 1,000 atoms at 1,000 B each is not
a violation. Its stated reasoning — a control that fires on honest growth arrives as a wedge
carrying no information — was right; the property was wrong. 1,000,000 B is over any ceiling this
map has ever had, so the test asserted that the bound **cannot bind**, and 297 commits then
measured exactly that. Scale-invariance and binding under a fixed total cannot both be true.

The test is kept, renamed to the property that survives
(`test_per_atom_budget_is_invariant_to_HOW_THE_SAME_BYTES_ARE_SPLIT`: the same total over 50, 350
or 1,000 rows is the same map and gets the same verdict) with the error written above it. Genuine
count-invariance moved one leg over to the MAX cap, where it was always true: one fat atom is a
violation however many lean ones surround it. The MAX leg is untouched — the finding measured it
alive, peaking at 12,221 B against a 12,288 B cap.

## Mutation-proven, both directions

`test_the_per_atom_bound_CAN_bind_before_the_whole_file_ceiling` is the control that did not exist.
It is keyed to the property at the **live** population and at 2x and 10x it, not to today's answer:

* restore the fixed 1,400 → *"at 350 atoms the per-atom budget authorises 490000 B against a
  409600 B ceiling — 80400 B of guaranteed silence"*.
* a budget that binds at today's count and not at 10x it → fires at 700 atoms. That second leg is
  the one that matters: a bound that binds only at today's population is the same defect with a
  later date on it.

`test_a_refusal_NAMES_THE_FATTEST_ROWS_and_not_only_a_total` asserts the ranking is present, in
order, and is a ranking rather than a sample — written against the message, because naming rows
changes nothing an exit code can see.

## The fork, closed in the same turn

Local HEAD was 13 ahead of `origin/main` and 12 behind, diverging at `d316e039b`; nothing at origin
carried the drain. Four paths conflicted. Three were the same authored work landed twice
(`tools/build_weather_world.py` and its validator test, and the liveness fixture where **both**
sides fixed the same `merge-base --is-ancestor` catch-all) — origin's copy strictly subsumes this
side's in each case. The fourth, `docs/design/orphan_baseline.json`, was **computed** against the
merged tree rather than chosen from a side: 540 orphans over 1,151 modules. A union would have
grandfathered `sim.weather_world`, which origin wired and this side did not.

**A fifth path deadlocked the merge outright**, and it is the `rederive_in` class one axis over.
The drain's own finding was in `done/` here (discharged) and in the root at origin (live, because
origin lacked the drain), with **identical bytes** — a room disagreement, not a content one. A
three-way merge takes an add from whichever side has it, so the merged tree held both copies and
`finding_classes` rule TWO ROOMS refused it, correctly. There is no `--resolve` route:
`build_merge_tree` rule 1 refuses a resolution for a path that did not conflict, and that rule is
the only thing stopping `--merge --content` becoming a smuggling door. Neither side could fix it
alone — this side cannot delete a path it does not have, and origin cannot archive a discharge it
cannot see. So the rooms were made to agree *before* the merge (`afd73a7a2`) and the archival
re-made after it, which is the only shape available today.

**That is a mechanism-sized gap and it is left open deliberately**: `rederive_in` exists because a
derived COUNT merged from two sides deadlocks the same way, and it was built once the class was
established. Room membership is now a second instance of the same class — a merge that cannot
settle a two-rooms collision costs three landings instead of one, and it will recur every time one
lane consumes a finding another lane still holds live. Filed rather than built, because the fork
was the thing blocking every lane and a mechanism designed under that pressure is the wrong one.

## Files

* `tools/maturity_map_store.py` — `MAP_PER_ATOM_RESERVE`, `mean_bytes_per_atom_budget`,
  `size_warning`'s third band.
* `tests/design/test_simplifications_store.py` — the derived budget, `fattest_rows`, both refusals
  naming rows, the corrected invariance test, the two new controls.
* `tests/tools/test_maturity_map_store.py` — the reserve-band edge from both sides, and the
  downward-remedy control re-keyed from a literal phrase to the property across every band.
