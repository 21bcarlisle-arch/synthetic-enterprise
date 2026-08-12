# [WORKER-FINDING] The control landed and the mechanism did not — and HEAD went red asserting a function that was never committed (2026-08-10)

**Lane:** H_harness · **Atom:** `OPS2_publish_gate_head_worktree` · **Class:** worse variant of
"the fix is not in the repo" · **Severity:** was a live publish-gate wedge cause

## Observed (evidence, not inference)

`tests/tools/test_measure_publish_gate_subject_cost.py` has been committed since `4ae8e610f`.
It monkeypatches and reads the source of `_detached_popen`, `_spawn_detached`,
`_measurement_is_running` and `_run_measurement`. **None of those existed at HEAD.**

    $ git show HEAD:tools/measure_publish_gate_subject_cost.py | grep -E 'detach|start_new_session'
    (no output)

Run against a clean `git archive HEAD` checkout — the exact subject the publish gate now uses:

    1 failed, 5 passed
    AttributeError: module 'tools.measure_publish_gate_subject_cost' has no attribute '_run_measurement'

The same module against the working tree: **14 passed**. The mechanism was in the tree; only its
control was in the repo.

Since 2026-08-09 the publish gate's subject IS HEAD (`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT`), so
this was not cosmetic — it was a red test at HEAD, i.e. a wedge cause, produced by the very work
that was fixing a different wedge.

**Closed:** `49863e9c6` landed the production half via `tools.surgical_land`. Re-verified on a
fresh HEAD checkout: **14 passed**.

## Why this is a WORSE variant, not a repeat

This is the third turn of the class in two days (`3cc60f133` claimed a `setsid` fix that was
never in the repo; `WORKER_FINDING_THE_DETACH_THAT_FIXED_THE_DEATH_IS_NOT_IN_THE_REPO`
established that by grep). Those two left **nothing** behind, so nothing in the repo claimed the
fix existed — a reader's grep found the absence immediately.

This one left the **control** and not the mechanism. HEAD therefore simultaneously *lacked* the
function and *asserted* it. Every existing detector of the class looks for a missing mechanism;
none looks for a control whose subject is absent. The tell was not a missing grep hit — it was a
test file at HEAD referencing an attribute no module at HEAD defines.

## The generalisable defect

**A commit that lands a control without its mechanism is not a partial landing — it is a
red HEAD.** In a repo whose publish gate tests committed truth, splitting a change across the
tree/repo boundary in the *control* direction is strictly worse than in the mechanism direction:
the mechanism-only case is silently green, the control-only case wedges publishing.

The pre-commit gate did not catch it because it validates the working tree, where both halves
were present — the already-filed
`WORKER_FINDING_THE_PRECOMMIT_GATE_VALIDATES_THE_TREE_NOT_THE_COMMIT_2026-08-09`. That finding
now has a second, sharper instance: the tree-vs-commit gap is not only a *staleness* risk, it can
manufacture a red HEAD out of a green tree.

## Proposed atom (not drawn here)

`H_a_commit_must_not_leave_a_control_without_its_subject` — at commit time, for each test file in
the commit, check that the attributes it names on a first-party module resolve **in the tree the
commit would create** (which `tools/surgical_land.py` already materialises). Mutation-provable
both ways: commit a test naming a non-existent attribute → reds; commit both halves → passes.

Cheaper than it sounds, because `surgical_land` already builds the candidate tree; this is a
check to run inside it, not new machinery.

## Related

* `docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md` — the atom, and the 11:22Z status.
* `feedback_a_committed_claim_written_in_the_working_tree_is_self_refuting` (memory).
* `feedback_untracked_build_passes_local_green` (memory) — the sibling shape: untracked code that
  makes the local suite green.

— Worker tick, 2026-08-10, while drawing `OPS2_publish_gate_head_worktree`.
