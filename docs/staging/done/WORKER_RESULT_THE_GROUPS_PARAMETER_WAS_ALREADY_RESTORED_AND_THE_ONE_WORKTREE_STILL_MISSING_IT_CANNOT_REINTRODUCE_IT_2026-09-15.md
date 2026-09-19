**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the `groups` parameter was already restored, and the one worktree still missing it cannot re-introduce it

**Filed 2026-09-15 by the autonomous worker**, against the drawn Lane 0 direction *"restore the
three `groups` hunks to the working copy of `fit_weights`"*. Closes
`WORKER_FINDING_A_DIRTY_WORKING_COPY_OF_FIT_WEIGHTS_DROPS_THE_PARAMETER_THE_JUST_MERGED_CALLER_REQUIRES_2026-09-15.md`
and `WORKER_FINDING_REPEATING_ALARM_RUN_FAILED_AFTER_S_TYPEERROR_FIT_WEIGHTS_GOT_AN_UNEXPECTED_2026-09-15.md`.

## The drawn work was already done, and the premise is refuted on real state

The direction stated that the shared working copy read
`def fit_weights(values, chosen, reference, seed: int = 999):` at line 1016. It does not. At the
time of this tick the shared tree reads, at line 1016:

```python
def fit_weights(values, chosen, reference, seed: int = 999, groups=None):
```

All three hunks the direction named are present in the working copy: the signature (1016), the
docstring paragraph beginning ``groups` IS ADDITIVE` (1025), and the `if groups is not None:` block
(1062–1071). `git diff HEAD -- tools/demand_vector_coverage.py` touches **zero** lines containing
`groups`. Something restored the file between the alarm's first sighting (11:09:11Z) and the run
that started at 11:34:35Z; no edit by this tick was required or made.

## Both legs of the stated done-condition are met

The direction defined done as *"`python3 -c "import tools.generate_value_arms_data"` completes in
the shared tree and the sim runner's next five-minute tick runs instead of dying in five seconds"*.

1. **The import completes.** Clean exit; the only output is the unrelated pytensor `g++` warning.
2. **The runner did not die in five seconds — it completed a full run.** `run_output_0142fc891_20260915T113435Z.json`,
   733s elapsed, 706,578 events, and `ANNUAL_REPORT_20260915T113435Z.md` (761,724 chars, 10 years)
   written at 11:46:48Z. The archived `docs/staging/done/run_complete_20260915T113435Z.md` is the
   artefact.

`background/alarm_repetition.py --check` now returns clean with no output for the signature
`auto:c51d26ba309513c3`.

## The only thing worth checking that was not already checked

The repair being present in the shared tree does not settle whether it can be undone. Four
worktrees exist; two still carry a parameter-less `fit_weights`:

| worktree | HEAD | `fit_weights` | commits `origin/main` lacks |
|---|---|---|---|
| `/home/rich/synthetic-enterprise` | `6d802b8fa` | **has `groups`** | 0 |
| `/var/tmp/se-forkmerge-20260915b` | `f434e28b5` | has `groups` | — |
| `/var/tmp/se-seat-executor` | `6d802b8fa` | has `groups` | — |
| `/var/tmp/se-floorrun-20260910` | `4e7938f67` | no `groups` | **0** |
| `/var/tmp/se-lane0-merge-20260915` | `c9f6df15b` | no `groups` | **3** |

`se-floorrun-20260910` is outstanding by nothing: its base simply predates the `groups` commit. It
is an old checkout, not a pending revert.

`se-lane0-merge-20260915` is the one that could in principle re-arm the regression, because it is
**not** an ancestor of `origin/main` and holds three commits that must still come home:

```
c9f6df15b SALVAGE(auto): preserve this fork's uncommitted work at 2026-09-15T08:56:32Z
afb9d7f7d failing closed is not available on a page that owes the reader a reading, ...
10a8866cd the headline composer asks the withdrawal register before it publishes, ...
```

**It cannot.** `git log origin/main..HEAD -- tools/demand_vector_coverage.py` in that worktree is
**empty** — none of the three commits touches the file. A merge resolves by change, not by endpoint
content, so that side contributes nothing to this path and `main`'s version (with `groups`) is what
survives. The parameter-less text in that worktree is an artefact of its base, not a pending
deletion.

**This is the question the endpoint diff answers wrongly.** Comparing the worktree's *file content*
against the trunk names `demand_vector_coverage.py` as a path the merge will overwrite; asking the
*merge result* — what commits actually touch the path — shows it will not be written at all. The
content comparison would have produced a confident false alarm and a pointless defensive edit.

## What was deliberately not built

The closed finding named a real gap: no control asks *"does the shared working tree still import?"*,
so a working copy that cannot import is invisible to every gate until someone runs something in it.
`tools/write_time_gate.py --explain background/working_tree_imports.py` confirms no existing row
covers it, and the nearest neighbour (`tools/symbol_landing_check.py`) asks a different question.

It is still not built here, for the reason the original finding gave and which this tick does not
overturn: the finding's subject is the parameter, and building the watcher in the same breath is
the shape CLAUDE.md warns against. Recorded as an unminted candidate for the seat to rank rather
than actioned on a bounded tick — if it is worth doing it is worth ranking.

## Correction to the record

The direction's instruction to run `isolate_hunks --survey` *first* was followed and was the right
order: the survey shows **7** hunks against HEAD, all of them the other lane's additive work
(`seasonal_swing` removal prose, `DISTRIBUTION_AXES`, `derived_from`, the gas-shape blind-list
note, the `values` stack) and **none** of them a `groups` hunk. Had the direction been acted on
without the survey — by `git checkout` or by restoring the signature by hand — it would have
written a parameter that was already there and risked the other lane's seven hunks for nothing.
