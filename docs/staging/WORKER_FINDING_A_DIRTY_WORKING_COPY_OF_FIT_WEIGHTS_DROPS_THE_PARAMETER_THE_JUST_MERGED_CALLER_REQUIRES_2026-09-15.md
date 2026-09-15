# A dirty working copy of `fit_weights` drops the parameter the just-merged caller requires

**Severity:** BLOCKING · **Lane:** H_harness

**Found:** 2026-09-15, immediately after pushing `9ccda0d1e` (the commit that closed the 2026-09-11
origin fork). Found by importing `tools.generate_value_arms_data` in the shared tree to verify the
pushed feed — which is the only reason it was seen at all.

## What is wrong

In the **shared working tree**:

```python
# tools/demand_vector_coverage.py:1016  (working copy, UNCOMMITTED)
def fit_weights(values, chosen, reference, seed: int = 999):
```

At **origin/main** (`9ccda0d1e`), committed:

```python
# tools/demand_vector_coverage.py:980
def fit_weights(values, chosen, reference, seed: int = 999, groups=None):
```

`simulation/settlement_choice.py:248` — which came in on the fork merge — calls it as:

```python
weights = fit_weights(values, chosen, reference, groups=candidate_years)
```

So against the working copy that call raises:

```
TypeError: fit_weights() got an unexpected keyword argument 'groups'
```

The chain that hits it is not obscure: `tools.generate_value_arms_data` → `fold_noise_floor_family`
→ `run_value_cycle_ab` → `run_phase4c_on_phase2b` → `run_phase2b` → `live_population` (at **import
time**, via the module-level `CUSTOMERS = live_population()`) → `plan_growth_campaign` →
`settle_within_budget` → `choose_settled_sample`.

## What is NOT wrong

**Nothing that is landed.** Verified in a clean checkout of `9ccda0d1e`: the committed
`fit_weights` accepts `groups`, the import chain completes, and the published feed is correct.
This is a working-tree-only condition, and `tools/demand_vector_coverage.py` shows as ` M`
(modified, unstaged) — another lane's in-place edit.

## Why it is BLOCKING anyway

The direction of the difference is the dangerous one. The uncommitted copy is **behind** the
committed one on this parameter: it is the shape a stale buffer or a reverted edit leaves, not the
shape of work in progress toward `groups`. If that copy is landed by a pathspec commit — which
stages the **working-tree** copy — it removes a parameter that a caller merged into `main` hours
earlier now requires, and the failure surfaces as a `TypeError` inside the simulation's population
build rather than anywhere near the file that changed.

That is the removed-parameter shape this project has been bitten by before: the build stays
coherent, the error message names the data path, and nothing points at the call.

## What to do

1. Whoever holds `tools/demand_vector_coverage.py` should refresh it from `origin/main` before
   landing anything in it — `git diff origin/main -- tools/demand_vector_coverage.py` shows the
   gap in one line.
2. **Do not** land that file by pathspec from the current working tree.
   `python3 -m tools.isolate_hunks tools/demand_vector_coverage.py --survey` will show whether the
   `groups` removal is a hunk of its own, in which case dropping that one hunk is the whole repair.

## The gap this exposes

The pre-commit gate runs against the tree the commit **would** create, which is exactly right and
is why nothing red was landed. But no control asks the cheaper question the other way round:
*does the shared working tree still import?* A working copy that cannot import is invisible to
every gate until someone tries to run something in it, and here that was a manual verification
step that happened to exist. Worth one cheap check; not built here, because this finding's subject
is the parameter and building the watcher for it in the same breath is the shape CLAUDE.md warns
against.
