# [WORKER-FINDING] The ruff I001 baseline is now +6 below committed HEAD, and it drifted there quietly

**Found:** 2026-08-11, during KNIFE3 step 17 (commit `83c5d54ed`), when the static-quality
ratchet reddened on a commit that *improved* the very rule it reddened on.
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight — the machine is
**not** blocked: `test_static_quality_ratchet.py` is absent from the pre-commit gate's
`CONTROL_TESTS` and `tests_for()` maps it to no path, so it gates no landing today. It does
sit on the publish suite.
**Rank:** backlog, but promote the moment a publish wedge is attributed to lint.
**Does NOT supersede** `WORKER_FINDING_RUFF_BASELINE_IS_CALIBRATED_TO_UNCOMMITTED_WORK_2026-08-09.md`
— that finding owns the **E402** half and its cause (a baseline shrunk to match one writer's
uncommitted fix). This is a **different rule with the opposite sign**, and filing it separately is
deliberate: the E402 case is a baseline held UP by unlanded work; this is a baseline left BEHIND by
landed work.

## Observed, with evidence

Two census tests fail — `test_ruff_baseline_matches_frozen_census` and
`test_ruff_no_rule_exceeds_baseline`. They fail identically on a clean export of committed HEAD,
so no working-tree state is involved:

```
$ git archive HEAD | tar -x -C /tmp/headexp
$ cd /tmp/headexp && python3 -m pytest tests/architecture/test_static_quality_ratchet.py -q
  changed : {'E402': (193, 194), 'I001': (1384, 1390)}
    E402: baseline 193, now 194
    I001: baseline 1384, now 1390
```

**I001 is +6 above its frozen baseline on committed HEAD.** The 2026-08-09 finding recorded
`I001 1386` at HEAD that day against the same `1384` baseline, so **+2 was already there and a
further +4 has landed in the two days since**, in commits nobody attributed to lint.

## Why this is a class and not two numbers

The ratchet's own docstring states the contract: a count that rises above baseline "fails as a
regression", a count that falls "fails as STALE until the baseline is shrunk to match". Both
directions are meant to be *impossible to reach silently*. Both were reached silently anyway,
because **the control that would have caught the rise is not on the path that produces the rise.**
Landing code runs the pre-commit gate; the pre-commit gate does not run this ratchet. Only the
publish suite does, hours later and pooled with everything else — which is precisely the
"a crossing could LAND and be found hours later" shape that `CONTROL_TESTS` grew an epistemic-wall
entry to close on 2026-08-10 (see `tools/pre_commit_test_gate.py`, the KNIFE-step-12 comment).

So this is the **already-recorded lag class applied to a second wall-shaped control**, not a new
mechanism. The wall got a commit-time seat; the lint ratchet did not, and drifted +4 in two days.

## Attribution for this step, so it is not mistakenly read as the cause

Measured per file against the same HEAD export:

| rule | HEAD | working tree | delta | attributable to |
|---|---|---|---|---|
| I001 | 1390 | 1387 | **-3** | `simulation/run_phase2b.py` 7 → 4 — step 17 deleted three function-local import blocks with the code it moved |
| E402 | 194 | 194 | 0 | — |
| F841 | 130 | 131 | +1 | `tools/scale_probe_10k.py`, **another lane's uncommitted file** |

Step 17 is a net improvement on the red control (under the repo's own `ruff.toml`,
`run_phase2b.py` goes 13 → 10 findings). Stated because "the ratchet went red on the commit that
touched it" is the wrong reading and the cheap one.

## What a fix looks like — two candidates, and a recommendation

1. **Seat it at commit time** (`CONTROL_TESTS` += `test_static_quality_ratchet.py`) so a rise
   cannot land. Cost: the census is a full-tree `ruff check` on every code commit. It runs in
   ~10s here, against the ~4.8s already paid for the wall walk.
2. **Find and fix the six I001s**, then re-freeze. Cost: they are spread across other lanes'
   committed files, and re-freezing without (1) buys a baseline that drifts again next week.

**Recommendation: (1) then (2), in that order** — seating the control first is what stops the
next drift, and it is the same repair the wall already received for the same reason. Doing (2)
alone treats an instance of a class R10 says may not be closed with an instance fix.

**Reversible:** both are single-line/config changes; `git revert` undoes either.
