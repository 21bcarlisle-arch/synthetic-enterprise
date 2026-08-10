# WORKER FINDING — the publish scope is resolved against a different tree than the gate runs in

**Date:** 2026-08-10
**Class:** fail-CLOSED wedge / subject mismatch (R15, R9)
**Status:** FIXED + mutation-proven both ways in this tick.
**Rank proposal:** already actioned (RUNG 1, publish wedge). Filed for the CLASS, not the instance.

## The wedge, in one line

The publish gate resolved *which tests may block* against the **shared working tree**, then ran
them against a **clean HEAD checkout** — so one lane's **untracked** test file was handed to a
tree that had never seen it, and pytest's `rc=4` "file or directory not found" was read by the
publisher as a failing test.

## Evidence (observed, R9)

From `docs/observability/sim-runner-log.md`, the 17:05 cycle:

```
Publish gate scope: 6 publish-path source(s) -> 131 blocking test file(s) via the static import graph.
Publish gate RED (rc=4) -- no FAILED/ERROR summary line found
Publish gate RED output tail:
no tests ran in 0.00s
ERROR: file or directory not found: tests/background/test_publish_decoupling_exit.py
```

Reproduced live at HEAD `05a26f0c3` and again at `54141b559`:

| resolved against | scope size | paths absent from the HEAD extract |
|---|---|---|
| working tree (what the gate did) | 131 | 2 |
| HEAD extract (what the gate runs) | 129 | 0 |

The two absent paths were `?? ` **untracked**:
`tests/background/test_publish_gate_blocking_payload.py`,
`tests/background/test_wedge_suspects_from_the_red.py`.

Confirmed `rc=4` is a *usage* error, not a red test: a `--collect-only` naming one missing path
returns `ERROR: file or directory not found` with `no tests collected`.

## Why it was unbreakable

The publish path commits **only after a green gate**. So the commit that would have made those
paths exist at HEAD could never land through the gate that the paths themselves were reddening.
141 consecutive failures; the published stamp froze. This is the same shape already filed as
*a repair downstream of its own gate cannot land* — here it arrived through a brand-new layer.

## The real lesson (the class)

`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` moved the gate's **subject** to a clean HEAD
checkout precisely so that *"the working tree belongs to the lanes"*. One day later
`DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10` added a **scope** layer that re-derived its
answer from the working tree — and thereby **re-coupled every lane's uncommitted work to the
public surface through the new layer**, reinstating the exact defect the previous ruling had
removed one layer down.

> **A control has a subject. When you add a layer above a control, the new layer inherits the
> obligation to name the same subject — and nothing checks that for you.** A path is not a
> value; it is a value *relative to a tree*. Moving a control's subject is only complete when
> every layer that computes paths for it has moved too.

Note also that the whole `publish_scope` module is written against the risk of narrowing too
far (**fail-open**). This failure was fail-**closed** — it narrowed to something *unrunnable* —
so not one of its four existing guards could see it. A module hardened exclusively in one
direction is blind in the other.

## The fix (landed)

1. **Cause.** `process_run_complete._scoped_gate_argv(run_root=...)` now resolves the scope
   against the tree the suite will execute in; `_run_gate_in` passes its own `cwd`. Both halves
   of the gate — what it runs, and what it runs it against — are now the same committed truth.
2. **Seam control.** `publish_scope.scoped_pytest_argv(..., run_root=...)` verifies every scoped
   path exists under the run root and degrades to the **full suite** on a mismatch (the module's
   standing safe direction; `tests/` exists in every tree, so the fallback is always runnable).
   A wedge becomes a slower gate, never a quiet publish.

## R15 — mutation-proven both ways

`tests/background/test_publish_scope.py`, 20 passed:

| mutation | result |
|---|---|
| cause-side fix reverted (`resolve_scope()` un-rooted) | **FAILS** `test_the_publisher_resolves_the_scope_against_the_tree_it_runs_the_gate_in` |
| seam guard disabled (`absent = []`) | **FAILS** `test_a_scope_naming_a_path_absent_from_the_run_root_falls_back_to_the_full_suite` |
| neither (restored) | 20 passed |

**A guard-shadowing trap caught en route, worth its own note.** The first version of the
cause-side test asserted the *outcome* (`full_suite is True`) and **survived** reverting the fix
— because the new seam guard rescues the bad scope and produces the identical outcome. The outer
guard shadowed the inner fix. The test now asserts *which control fired* (the source-declaration
check, reachable only if the resolve was rooted at `run_root`), which discriminates. Had the
mutation not been run, a fix with a test that proved nothing would have been claimed as fixed.

## A false second cause, caught before it was reported (worth keeping)

Verifying the fix, the gate stopped on
`test_every_registered_artefact_is_currently_fresh`, and the self-healing repair announced:

```
Derived-artefact repair did NOT converge after 3 pass(es):
docs/design/BLOCKED_ATOM_VISIBILITY.md still stale.
Two projections may be invalidating each other -- this is a real defect, not slow convergence.
```

That message asserts a real defect **in its own words**, and it was wrong. The cause was my
reproduction: I had built the checkout with `git archive HEAD | tar -x` and no `.git`, while the
live gate calls `_make_checkout_a_repo` (init + object alternates + `read-tree`). The projection
walks git history, so in a repo-less extract it renders a different document every pass and can
never converge. Rebuilt faithfully, **both projections repaired on pass 1 and the message
vanished.**

> **Reproduce a gate red in the gate's own checkout, built the way the gate builds it — not in
> an approximation of it.** An extract missing `.git` fails every git-shelling oracle *as an
> artefact of the harness*, and here the harness's own alarm text would have laundered that
> artefact into a filed defect. The existing note `feedback_named_blocking_test_passes_when_you
> _run_it` says to reproduce in a `git archive HEAD` extract; this sharpens it — the extract
> alone is not the gate's subject, `_make_checkout_a_repo` is part of it.

## Related, NOT fixed here (queued)

`Provenance banner commit FAILED (rc=128): cannot lock ref 'HEAD': is at <X> but expected <Y>` —
a concurrent-writer race on the shared tree, seen twice (16:44, 17:06). Separate cause, separate
atom; it does not gate publishing.
