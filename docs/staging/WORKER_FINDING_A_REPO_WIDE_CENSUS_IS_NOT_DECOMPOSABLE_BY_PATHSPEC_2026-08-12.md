# [WORKER-FINDING] A repo-wide census cannot be satisfied by a pathspec commit, and the file it needs may be in another lane

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, unwedging the 18th publish wedge (landed `4bee2bd47`).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. The instance is fixed and pushed; the
CLASS is filed here, not fixed on sight — the machine is not blocked by it.
**Rank:** backlog, promote on the next partial-commit refusal that costs more than one cycle.

## Observed, with evidence

`tests/architecture/test_static_quality_ratchet.py` asserts a **whole-repo** ruff census against
a frozen baseline. The repair for the wedge touched eight files. `git status --porcelain` filtered
over the lanes a code fix normally lives in —

```
git status --porcelain -- tests/ background/ company/ tools/ simulation/
```

— showed seven of them. `python3 -m tools.surgical_land` then **refused the commit**, correctly:

```
changed  : {'I001': (1380, 1381)}
FAILED tests/architecture/test_static_quality_ratchet.py::test_ruff_baseline_matches_frozen_census
[test-gate] ❌ TESTS FAILED -- COMMIT REFUSED.
```

The eighth file was `site/proof/test_coupled_gaps_panel.py` — a two-line `import sys` /
`import tempfile` swap, in the **SITE lane**, which that path filter does not name.

It was located by set-differencing the **per-file** I001 census of the resulting tree against the
working tree, after building the resulting tree the same way `surgical_land` does
(`GIT_INDEX_FILE` + `read-tree HEAD` + `git add -A <paths>` + `git archive`):

```
diff /tmp/res_i001.txt /tmp/wt_i001.txt
203d202
< 1 site/proof/test_coupled_gaps_panel.py
```

## The property that breaks

Every other gate on this tree is **decomposable**: a test selected for `foo.py` passes or fails on
`foo.py`, so committing a coherent subset of a change set is safe and is exactly what CLAUDE.md's
pathspec discipline recommends. A repo-wide census is not. Its verdict is a function of the
*whole tree*, so a subset commit is not a smaller version of the change — it is a **different and
possibly red tree**. The recommended discipline and this control are in direct tension, and the
control wins by refusing, which is the right direction but gives no clue where the shortfall is.

The refusal message names only the delta (`1380 -> 1381`). It does not name the file. Recovering
the file took a hand-built resulting-tree extract and a per-file set-difference — about as much
work as the fix itself, and work that has now been done at least twice
(cf. `feedback_measure_blast_radius_before_choosing_a_dirt_predicate`).

## Why the two obvious diagnoses are both wrong

- **Not "the author forgot a file".** The change set was complete on disk. It was the *status
  query* that was partial, and it was partial in a way that looks thorough — filtering to code
  lanes is the normal way to read a status on a tree carrying 200+ modified observability files.
- **Not "commit everything instead".** A broad `git add` on this shared tree is the defect
  `feedback_commit_specific_paths_not_broad_add` exists to prevent, with three concurrent writers
  live at the time (`process_run_complete.py` was mid-gate in another process throughout).

## Recommendation

**Make the census name its own offenders.** When `test_ruff_baseline_matches_frozen_census` fails,
have it emit the per-file diff for the changed codes, not just the totals. The test already
computes a full JSON census; grouping the offending code's findings by filename and printing the
files whose count differs from a stored per-file census is a small addition to the failure
message, and it turns a twenty-minute forensic exercise into a readable assertion. That is the
R15-shaped fix: the control keeps failing exactly when it should, and starts saying why.

Secondary, cheaper, and complementary: any status query used to assemble a landing set for a
repo-wide control must be **unfiltered** (`git status --porcelain` over the whole tree), because
the control's subject is the whole tree. A filtered status is the wrong instrument for it.

## Related, already recorded

- `feedback_untracked_build_passes_local_green` — the same tree/HEAD split, other direction.
- `feedback_an_inherited_index_can_hold_half_a_coherent_change`
- `feedback_a_concurrent_sweeper_can_commit_one_half_of_a_two_file_atomic_write`
- `WORKER_FINDING_A_FINISHED_CUT_SAT_UNCOMMITTED_WITH_EVERY_CONTROL_GREEN_2026-08-12.md` — the
  containing class; this is its partial-landing corollary.
- `feedback_sitelane_precommit_scope_gap` — the SITE lane going unseen by a code-lane instrument,
  previously at the pre-commit gate, here at the status query.
