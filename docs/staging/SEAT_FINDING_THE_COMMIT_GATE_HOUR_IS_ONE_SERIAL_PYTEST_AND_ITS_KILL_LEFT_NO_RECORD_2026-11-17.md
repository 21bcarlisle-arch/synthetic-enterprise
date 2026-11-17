**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

*LATENT: the fix for the 42% below lands with this finding; the remaining selection still fills ~60% of the
3,600 s limit for a page-touching billing change. Drawn on `the-commit-gate-outlasts-surgical-lands-hour`.*

# The commit gate's hour is one serial pytest, 42% of it is a markdown citation, and its kill left no record

## The question

D5's page landing was refused at 23:41Z on 16 Nov:
`the gate could not be EXECUTED (Command '['sh', 'tools/git-hooks/pre-commit']' timed out after 3600 seconds)`
(`/var/tmp/d5page/land4.log`). Attempt 6 passed its gate, but only after 3,195 s (`wait6.log`). Which
gate spent the hour, and was it contention with `process_run_complete`?

## What the record could and could not say

**The killed run left no per-gate timings, and that is a defect in its own right.** `surgical_land.run_gate`
used `subprocess.run(..., capture_output=True, timeout=3600)` and quoted only the exception, so the
hook's stdout, which names each gate as it runs, was thrown away. Nothing on disk says which gate attempt 4
was in when it was killed. The box ledger fills part of the gap. `heavy_job_deferrals.jsonl` holds
**no `commit_gate` QUEUED row** for 22:41–23:41Z: the gate's pytest was admitted at once. It never waited
in `resource_headroom.queued`, so none of the hour was spent queueing. Attempt 6 shows the same pattern.

## Measurement

The pre-registration is `/var/tmp/gate-hour/PREREG.md`, written 02:15Z before the run. It predicted ≥40 min
solo, with ≤15 files carrying ≥60% of the time, and the publisher not the main cause.

I re-derived the selection the gate makes for D5's eight paths with the gate's own
`selection_paths` + `select_targets`. The result is **186 test files, 3,122 tests, one serial pytest.**
I ran that selection at this worktree's HEAD, which has no D5 change in it, with `--junitxml`:

**3,522 s (58:42), the pytest alone.** It was 1 red (`test_the_size_is_measured_on_the_TREE_THE_COMMIT_CREATES`),
which passes in isolation and was not reproduced. The rest of the hook (twenty-odd gates, the
import-derived extras capped at 180 s) comes on top. So the selection alone fills the 3,600 s limit, and
attempts 4 and 6 landing either side of it is what this predicts. Prediction held: the top 7 files
carry 92%.

| s | cum | file | why selected |
|---:|---:|---|---|
| 966 | 28% | tests/simulation/test_run_phase2b.py | **`home_moves.md` → `simulation/run_phase2b.py`** |
| 510 | 42% | tests/simulation/test_run_phase2b_event_log.py | **same** |
| 485 | 56% | tests/simulation/test_a_dual_fuel_movers_gas_follows_it.py | test docstring cites home_moves.md |
| 469 | 69% | tests/simulation/test_a_dual_fuel_household_is_one_account_across_both_fuels.py | test docstring cites home_moves.md |
| 357 | 79% | tests/background/test_weekly_rhythm.py | control tests |
| 310 | 88% | tests/company/billing/test_collections_journey.py | billing suite |
| 116 | 92% | tests/simulation/test_a_movers_final_bill_is_the_exit_draw.py | test docstring cites home_moves.md |

**The gate that spent the hour is `tools/pre_commit_test_gate.py`, and two thirds of its time was selected
by the markdown page `docs/market_research/home_moves.md`, not by any code in the change.**
`data_surface_tests` treats a module that names a `.md` page in any non-docstring string as the page's
reader. `simulation/run_phase2b.py:3156` cites it inside an error message, `"... (home_moves.md s.8.7)"`.
So every edit to the page selected the tests of `run_phase2b`, which are six files that each run the real
simulation. `sim/customer_state_layer.py`, `company/compliance/domain_invariants.py` and the move-out seam
are pulled in the same way. The 11 Nov fix (`_names_it_outside_prose`) dropped docstrings and comments
and deliberately kept error messages, on the grounds that "an error message cannot be told from a path
the code opens". It can. A path the code opens has no whitespace in it.

## Contention with the publisher: not the cause

`process_run_complete` re-processes the same `run_complete_20261116T070501Z.md` every ~55 min and is busy
for ~35 min of each cycle (`sim-runner-log.md`). Attempt 4 (22:41–23:41) overlapped it for ~45 min.
Attempt 6 (~23:42–00:35) overlapped it for ~25 min and still took 3,195 s. My measurement overlapped it
from 02:33 and co-ran with D5 attempt 7's own gate (same selection, pid 3486927) for the whole hour.
Load average stayed at 3.6 on 16 cores with ~11 GB available. The pytest is single-threaded and
CPU-bound (no I/O wait observed). I had no quiet window to run a clean no-publisher control, so the
contention share cannot be bounded below about ±10%. What the evidence does show is that both runs with
heavy and light overlap took ~55 min, and so did the gate solo at HEAD. **A surgical_land that deferred
while the publisher runs would have waited ~35 min of every 55 and then taken the same hour.**

## The two changes (this landing)

1. **`tools/pre_commit_test_gate.py::_path_shaped`.** For a `.md` page, a module counts as its reader only
   if a literal holding the page's name has no whitespace in it. That covers a path, a joined basename, or
   an f-string's constant part. A sentence, including an error message, is prose. Every other suffix keeps
   the old behaviour, because shell strings (`"git show HEAD:docs/x.json"`) do read data files. Effect on
   D5's selection: 186 → 177 files, **−1,477 s (42%)**. Control:
   `tests/tools/test_pre_commit_test_gate.py::test_a_module_that_only_CITES_a_document_is_not_its_reader`,
   which now has six legs plus a non-markdown sentence leg. Each of these mutations reds it: the old rule
   (any mention), the whitespace rule applied to every suffix, and dropping everything.
2. **`tools/surgical_land.run_gate`** now gives the hook its own session and kills the **whole group** at
   the deadline. Before, `subprocess.run` killed `sh` alone, and the gate's pytest, a grandchild, lived on
   holding its reservation. The refusal also now quotes the last 12 lines of the hook's stdout, so a
   timeout names the gate it was in. The refusal's head is unchanged, so the publisher's parser still
   reads it. Control: `tests/tools/test_a_killed_gate_names_where_it_was_and_leaves_no_child.py`. These
   mutations each red it: the original `subprocess.run` (grandchild alive), `p.kill()` plus a wait (the
   refusal waits 120 s for the child), and the dropped tail (the message assert fails).

The 3,600 s limit is unchanged.

## What is left, with its number

After change 1, D5's pytest is ~2,034 s, plus ≤180 s of extras and the rest of the hook. That is inside the
limit on this measurement, but it leaves no margin to speak of. The next 954 s is two simulation tests
selected only because their **docstrings** cite `home_moves.md` (`_names_it_outside_comments` keeps test
docstrings on purpose, for `test_simplifications_store` and its README). A test that never opens the page
cannot change verdict when the page's prose changes. That rule is the next change, and it needs the
README case re-keyed to "reads the file" first.

## Prediction filed before its outcome

D5 attempt 7 (`longjob-d5-land7.service`, started 02:14Z) runs the OLD selection in its extract. Its gate
pytest was 54 min old at 03:10Z. **I predict it is refused at the 3,600 s limit (~03:15–03:20Z) and its
refusal names no gate**, because it was launched with the old `surgical_land` and its extract carries the
old selection (the hook and `pre_commit_test_gate` run from the tree being landed). The next D5 attempt, cut from a
base that holds this landing, should pass its gate inside the limit on the first attempt. That is this
item's done-test, and it is not yet observed.
