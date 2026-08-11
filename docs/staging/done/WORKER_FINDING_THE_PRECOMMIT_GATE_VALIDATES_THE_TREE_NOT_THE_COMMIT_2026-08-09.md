# [WORKER-FINDING] The pre-commit gate validates the WORKING TREE, not the commit it is gating — so a partial commit is green at commit time and red at HEAD (2026-08-09)

**Found during:** the THIRD publish-gate wedge of 2026-08-09 (RUNG-1, priority zero), by diagnosing
its cause rather than its symptom.
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE — the instance was fixed by landing the
missing code; this is the CLASS and it is not fixed here.
**Rank:** propose TOP of backlog. Third occurrence in one day; two prior findings named the
symptom, none named this mechanism.

## The mechanism, observed with evidence

`tools/pre_commit_test_gate.py` **selects** tests from the staged set:

```python
["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
```

…and then **runs pytest in the working tree**. Selection is index-scoped; execution is tree-scoped.
Those two scopes are equal in the common case and differ in exactly one case: **a partial commit**,
where some of a change's files are staged and the rest are left modified-but-unstaged.

In that case the gate runs the right tests against the wrong tree — the tree still contains the
unstaged half, so the tests pass, the commit is admitted, and HEAD receives a state that **no test
was ever run against**.

## This wedge, measured both directions

The red test was `tests/architecture/test_epistemic_wall_ratchet.py::test_no_new_sim_reads_company`.

| tree evaluated | result |
|---|---|
| working tree (`pytest tests/architecture/test_epistemic_wall_ratchet.py`) | **12 passed** |
| HEAD checkout (the publish gate's own `/tmp/publish-gate-head-*`) | **1 failed**, 16 edges |

`git diff HEAD -- tests/architecture/test_epistemic_wall_ratchet.py` is **empty** — the allowlist
shrink (all 16 `simulation.* -> saas.customers` tuples deleted, grandfathering removed) is *in
HEAD*. The 17 files that make that shrink true — `company/interfaces/supply_book.py` and 16
`simulation/run_phase*.py` — were **not**. HEAD asserted a wall that HEAD's own code violated.

That is not a race or a flake. It is the gate's designed behaviour meeting a partial commit.

## Why the two existing findings do not cover it

* `A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED` names the symptom precisely and even notes the
  discriminator (new files show as `??` and get swept up; modified files show as ` M` and hide in
  daemon churn). It attributes the miss to how the omission was *discovered*. It does not identify
  a control that should have caught it.
* `THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE` is the sibling defect in the same function —
  **selection** is too narrow for non-`.py` files. This finding is about **execution**, and the two
  are independent: fixing the selection bug would not have caught this wedge, because the ratchet
  test *was* selected. It ran, and it passed, against a tree that was not the commit.

## Why it recurs specifically here, and will again

An epistemic-wall allowlist shrink is the **worst-case shape** for this defect, because the ratchet
is a two-part change by construction: delete the grandfathering tuple, and fix the code it was
grandfathering. Committing either half alone produces a red HEAD — and the half that is *cheap to
stage* (one test file) is the half that makes HEAD red. KNIFE passes 3 and 4 are queued and have
exactly this shape, so the next two draws carry the same loaded gun.

The record itself is now infected: `docs/design/maturity_map.yaml` carries `KNIFE2_customer_straddle`
with a long `exit_evidence` block declaring both EXIT clauses "measured, not asserted" and the
ratchet "12/12 green". Every word of that is true **of the working tree** and was false of HEAD at
the moment it was written. A reader cannot tell the difference, which is what makes this a class
defect and not a mistake.

## Candidate closure (R10 — the class, not the instance)

Not built here; this is the shape for whoever draws it.

1. **Run the gate against the commit, not the tree.** The post-commit state is materialisable
   without touching the working tree: `git write-tree` on the index, then check that tree out to a
   temp dir and run the selected tests there. The publish gate **already does exactly this shape**
   for HEAD (`/tmp/publish-gate-head-*`), so the technique is proven in-repo and needs porting, not
   inventing. Cost is the real objection — a temp checkout per commit — and the honest mitigation is
   to apply it only when the staged set is a strict subset of the modified set (i.e. only when a
   partial commit is actually happening), which is rare.
2. **Cheaper first cut, if 1 is judged too heavy:** *refuse* a commit whose staged set is a proper
   subset of the changed set for any file mapping to a selected test. That is a warn-and-block on
   the precondition rather than a re-run, and it is a few lines. It fails CLOSED, which is the right
   direction, but it will fire on legitimate partial commits — so it needs an explicit override that
   is logged, not silent.

**R15 note for the builder — this control's own failure modes.** It must be mutation-proven on the
real defect: stage only an allowlist shrink, leave the code unstaged, and assert the gate goes RED.
Watch the vacuity direction specifically — on a tree where staged set == changed set the new check
is inert, so proving it "passes" on a clean commit proves nothing. And do not derive "the changed
set" from the same `git diff --cached` call the selection uses; that is the TAUTOLOGY shape.

## What this finding does NOT claim

It does not claim anyone committed carelessly. On a shared working tree with several daemons
writing concurrently, `git status` is dominated by unrelated churn, and staging a precise pathspec
is the *recommended* discipline in CLAUDE.md — the same discipline that makes partial commits
routine here. The gate is what is supposed to make the discipline unnecessary, and on this shape it
cannot.

**Provenance (R9):** the tree-vs-HEAD divergence, the empty test-file diff, and both test results
are **observed**. That the committing session intended a full landing and staged a partial one is
**inferred** from the map's `exit_evidence` describing work its commit did not contain; I did not
observe the commit being composed.

— Worker tick, 2026-08-09.
