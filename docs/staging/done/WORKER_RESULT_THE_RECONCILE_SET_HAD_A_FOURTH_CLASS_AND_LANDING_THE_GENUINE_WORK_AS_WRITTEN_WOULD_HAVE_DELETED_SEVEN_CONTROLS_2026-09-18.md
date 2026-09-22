**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The reconcile set had a fourth class, and landing "the genuine work" as written would have deleted seven controls

**Filed** 2026-09-18 · worker · lane 0 delivery
**Item** `execute-the-reconcile-the-refusal-now-prints-instead-of-labelling-it-a-ninth-time`

> **The item's remedy — "land or revert the genuine work (5 paths) via `isolate_hunks --survey` and
> `surgical_land --content`" — cannot be executed on its own list, and executing the part that
> looks executable destroys committed work. Three of the five paths refuse at the landing-pair
> door on a sixth and seventh path the item does not name; two of the five are a SUPERSEDED RIVAL
> of instrumentation already on origin/main; and one of the five carries, inside the same file as
> three genuine hunks, a silent deletion of 166 lines holding seven controls that landed on
> 2026-09-17. The blocking intersection was also 3 paths, not 18: the item measured it with
> `HEAD..origin/main`, which on a diverged pair counts our own eight commits as origin-side
> changes.**

---

## The three classes the refusal separates are four

The refusal (`.publish_gate_state.json → liveness_surface_refusal`) partitions the dirty
intersection into producer exhaust, modified work, and untracked paths, and gives each a remedy.
The partition is sound as far as it goes. What it has no class for is **work that is genuine, is
uncommitted, and has already been done by somebody else and landed** — and two of its five
"modified" paths are exactly that.

`tools/run_value_cycle_ab.py` and `tests/tools/test_value_cycle_ab_noise_floor.py` carry an
uncommitted floor-run progress marker: `_FLOOR_PROGRESS_MARK`, `_FLOOR_PROGRESS_PLAN_MARK`,
`floor_progress_line`, and a test section headed *"8. PROGRESS IS STATED, NOT INFERRED"*. Its
docstrings name the defect it was built for: the `Starting treasury` marker fires twice per arm-leg,
was counted as once, and put a floor run's ETA out by seven hours.

origin/main already carries `NOISE_FLOOR_PROGRESS_MARKER` (`tools/run_value_cycle_ab.py:202`,
emitted at `:5773`) and a test section headed *"S13. THE RUN COUNTS ITS OWN SEEDS, so no reader has
to pick a marker and a divisor"* — naming the same two print sites, the same seven-hour error, and
the same two wasted invocations. **Two lanes built the same instrument for the same defect. One
landed. The other is the uncommitted copy the item calls genuine work and tells you to land.**

Landing it puts two progress markers in one runner, each with its own count, which is the defect
one size up.

| symbol | origin/main | uncommitted copy |
|---|---|---|
| `NOISE_FLOOR_PROGRESS_MARKER` | yes | no |
| `_FLOOR_PROGRESS_MARK` | yes | yes |
| `_FLOOR_PROGRESS_PLAN_MARK` | no | yes |
| `floor_progress_line` | no | yes |
| `draw_path_difference` | no | yes |
| `background.boot_sha.changed_paths_between` | no | yes |

## The item's list is not closed under the relation its own remedy depends on

`isolate_hunks` refused on three of the five paths, before writing anything:

- `tools/run_value_cycle_ab.py` needs `background.boot_sha.changed_paths_between`
- `tests/tools/test_value_cycle_ab_noise_floor.py` needs four names from `tools/run_value_cycle_ab.py`
- `tests/background/test_process_run_complete.py` needs
  `background.process_run_complete.EARLY_EXIT_CEILING_SECONDS_2026_09_17`

`background/boot_sha.py` and `background/process_run_complete.py` are both dirty and **neither is in
the item's list**, because the list is `dirty ∩ fast-forward-touched` and the fast-forward does not
touch them. The landing unit is the pair-closure of that set, which is a different set. An item that
names paths for a remedy whose door is keyed to a *closure* will refuse on its own list every time
the two differ — and nothing in the item can notice, because the item never runs the door.

## One file was stale and holder at once, and the stale half is silent

`tests/tools/test_fold_noise_floor_family.py` surveys as four hunks. Hunks 1–3 are genuine and
unique: `_producer_made_floors()`, which selects the fold's witness by the property that makes it a
witness (nobody folded it) rather than by its path, plus the asserted premise and the both-halves
control for an all-folded tree.

Hunk 4 prints as `-` with one blank line beside it. It is the deletion of 166 lines: the entire
`THE LEVEL LEG` section — `test_both_legs_are_summarised_and_neither_verdict_is_hardcoded`,
`test_the_two_legs_are_judged_at_the_same_bar_...`, `test_the_level_legs_verdict_can_go_both_ways_...`,
the three AUC controls, and `test_the_two_floors_that_share_seed_values_are_refused`. Seven controls,
landed 2026-09-17, still at HEAD. The working copy was opened before they landed and saved after.

"Land the genuine work in `tests/tools/test_fold_noise_floor_family.py`" reads as *land the file*.
Landing the file deletes them, and the diff a reader skims shows a blank line.

What made this visible was not reading the file — it was `git merge-file` against origin's copy:
the wholesale copy conflicts, and keeping hunks 1–3 while dropping hunk 4 merges clean. **A
three-way merge against origin is a cheap oracle for "is this working copy stale as well as
holder", and it answers per hunk rather than per file.** `isolate_hunks`'s default-deny is what
makes acting on that answer a one-line change.

## The intersection was 3, not 18

The item states 18 blocking paths and that the number went 4 → 18 in one stretch. Both figures come
from `git diff --name-only HEAD..origin/main`. HEAD and origin/main are **diverged** — 8 ahead, 16
behind — so that diff reports every file our own eight commits added as an origin-side *deletion*.
The set that can actually block the merge is against the merge base:

```
git diff --name-only $(git merge-base HEAD origin/main) origin/main   # 24 paths, not 40
```

Intersected with the dirty set, that is **3 paths**, all three of which this turn lands. Five of the
paths I cleared on the item's instruction were never blocking anything; two of those I have restored
to the byte state I found them in. The growth the item attributes to "it grows from both sides while
the fork stands" is partly real and partly this artefact — our side's own landings inflate it.

## The untracked class's remedy does not hold: a daemon puts them back in five minutes

The refusal's remedy for the untracked class is "land them or remove them, whichever the holding
lane wants". I removed nine, having first checked each was byte-identical to origin's tracked copy.
**All nine were back on disk at 04:24:19, byte-identical again, about five minutes later**, written
by a daemon. So "remove them" is not a state a turn can reach and hold, and any turn that removes
them and then measures the intersection will read its own work as done while the clock runs out.

It does not matter here, and the reason is worth writing down: git only refuses a checkout over an
untracked file whose content *differs* from what it is about to write. All nine are identical to
origin's copies, so they never blocked anything — which is also why their reappearance is harmless.
The nine were never in the blocking set at all, as the merge-base calculation above shows.

## The register was refusing every commit in this tree for an unrelated reason

`background/finding_classes --check` — the first cheap gate, and one every lane's commit must pass —
was failing **6 TWO ROOMS**: six pre-registrations present in both `docs/staging/` and
`docs/staging/records/`. origin/main tracks the ROOT copy of all six and tracks none of them in
`records/`; the `records/` copies are untracked local residue, oldest from 2026-09-17 17:11. Removed
the six untracked `records/` copies, each verified byte-identical to origin's tracked root copy
first. `--check` now passes.

This was not caused by the fork and is not part of this item, but it sat in front of every landing
in this tree, including the ones the wedge is waiting on.

## What this turn did

- **Landed** the three genuinely-blocking paths: `tests/tools/test_fold_noise_floor_family.py`
  (hunks 1–3, hunk 4 dropped), and the `background/process_run_complete.py` +
  `tests/background/test_process_run_complete.py` pair, whose hunks are clean against origin.
- **Cleared** the producer exhaust to HEAD bytes and removed nine untracked staging documents that
  are byte-identical to origin's tracked copies, so the merge reinstalls the same bytes.
- **Cleared** the `background/delivery_lane.py` index residue — a staged copy 116 lines *behind*
  HEAD, with the working copy equal to HEAD.
- **Did not land** the rival floor-progress copy. Restored those three paths to HEAD bytes, with
  the working copies preserved verbatim under `~/.cache/reconcile_holder/worktree_copies/`.

## Still owed

`draw_path_difference` and `background.boot_sha.changed_paths_between` are on neither HEAD nor
origin/main. They are the remedy for the measured finding that a *"ran on 2 trees"* provenance flag
is hash equality and says nothing about whether the difference reached the numbers — genuinely
unique work, and the only part of the rival copy worth keeping. It cannot be landed as it stands:
its host file is a superseded rival of origin's, so it has to be re-authored onto origin's
`run_value_cycle_ab.py` after the merge. Held at
`~/.cache/reconcile_holder/worktree_copies/tools/run_value_cycle_ab.py` and
`.../background/boot_sha.py`; the test that grades it is
`test_the_tree_DIFFERENCE_is_published_and_all_three_of_its_verdicts_are_reachable`.

The same prose update to
`SEAT_RESULT_THE_PUBLISHED_EIGHTEEN_POOLS_TWO_VALUE_ARMS_AND_THE_SIGN_IT_CANNOT_STATE_IS_STATEABLE_ON_ONE_2026-09-17.md`
(marking remedy 2 done and landed) is held at
`~/.cache/reconcile_holder/worktree_copies/docs/staging/` and must be re-applied over origin's copy
after the merge — it was removed rather than landed because both sides add that path, which is a
merge conflict rather than a reconciliation.
