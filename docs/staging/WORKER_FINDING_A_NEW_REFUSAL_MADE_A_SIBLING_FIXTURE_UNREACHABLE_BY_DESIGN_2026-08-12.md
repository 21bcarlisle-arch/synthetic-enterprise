# WORKER FINDING — a new refusal made a sibling's fixture unreachable-by-design, and that fixture wedged publishing for ~60h

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-12
**Status:** FIXED — `2b8a7f0c5`, pushed
**Class:** R15 / control-interaction. Sibling of `feedback_a_control_committed_without_its_mechanism_reds_head`,
distinct from it: here the mechanism DID land, complete and correct, with its own tests.

## The observation (observed-with-evidence, reproduced at HEAD)

The publish gate was red for ~3611 min / **190 consecutive episode failures**, blocking all
publishing. `.publish_gate_state.json` named one blocking test and named it correctly:

```
FAILED tests/background/test_publish_gate_scope.py::test_run_fast_tests_emits_the_marker_deselection
assert (False, False) == (True, False)
```

Reproduced at HEAD `b0b3a1a80` in 0.06s. The captured stdout is the whole diagnosis:

```
Publish gate scope: ROOT UNAVAILABLE: 6 of 6 declared publish-path source(s) are absent
  under /tmp/pytest-.../head, and so is `tests/` -- the root exists but is not a checkout
  of this repo.
Publish gate: could NOT materialise a clean HEAD checkout -- not committing.
```

## The mechanism

`9fbb4dd33` (the sixteenth wedge's fix) taught `resolve_scope` to distinguish a root that is
not this repo from a declaration that has rotted, and — correctly — made the first a
**refusal**: `_run_gate_in` returns `_checkout_unavailable_verdict()` *before* `subprocess.run`
is ever reached.

That commit is good work. It shipped with its own tests (`tests/background/test_publish_scope.py`,
both directions) and it fixed a real 28-of-92-cycles defect.

What it could not see is that a **sibling** test in a **different file** stubs `_head_checkout`
with an empty `tmp_path / "head"` — which is *precisely* the condition the new refusal names.
So:

- the gate did exactly the right thing and declined to run;
- `argv` was therefore never built and never captured;
- and the assertion `run_fast_tests(...) == (True, False)` became **unreachable by any
  behaviour of the code it is about**.

The test was not testing a broken gate. It had stopped being able to test anything.

## Why this shape is worth a name

The two R15 shapes already on file are *a control that cannot fail* and *a control landed
without its mechanism*. This is a third: **a new fail-closed refusal upstream of an existing
assertion can silently relocate that assertion behind the refusal.** The new control's own
tests all pass — they exercise the refusal deliberately. The damage lands in a file the
author had no reason to open, on a fixture whose emptiness was harmless the day it was
written and became the refused condition the day the refusal shipped.

An empty stub root was *fine* while an unresolvable scope merely widened to the full suite.
It stopped being fine the moment "unresolvable" grew a second, refusing branch.

## The fix

The stub root is now repo-shaped: `ROOT_REPO_MARKER` plus every entry of
`PUBLISH_PATH_SOURCES` — materialised **from the declaration** rather than hand-typed, so a
source added to or moved within that list cannot silently return this test to the
absent-root branch. (Hand-typing it would have reproduced
`feedback_a_render_harness_that_hand_types_its_call_list_supplies_the_defect`.)

**R15, both directions:**
- with the marker present: 9 passed in `test_publish_gate_scope.py`; 45 passed across it plus
  `test_publish_scope.py` and `test_publish_gate_head_checkout_is_a_repo.py`.
- mutation — drop the `"-m", PUBLISH_GATE_MARKER_EXPR` pair from `publish_gate_pytest_argv`:
  the test fails on its own named defect. Restored; `git diff` clean on that module.

**Verified on the gate's actual subject, not the working tree** (`feedback_a_bare_head_extract_is_not_the_gates_subject`):
`git archive HEAD` at `2b8a7f0c5` into a clean tmp root → **35 passed, 1 skipped, rc=0**.

## What I did NOT do, and why

- **Did not force past the run lock.** A publisher (PID 635464) was mid-gate with a correctly
  *narrowed* 134-file scope when I finished. My launch was lock-skipped by design and the
  34-marker queue flushes via `background_worker`'s `process_leftover_run_markers()` sweep.
- **Did not R11-verify the folded live site.** That follows the first green publish, which had
  not landed when this tick ended. Not claimed.

## The residual worth an atom

`9fbb4dd33`'s own finding already flagged it: the publish gate runs against a HEAD checkout so
it never sees working-tree dirt, but **every worker running tests locally does**, and will
misattribute daemon-written tree dirt to its own change — as that tick's A/B did, for 10 tests.
Class: `feedback_ab_baseline_in_a_clean_checkout_blames_your_change_for_tree_dirt`.

## Related

- `WORKER_FINDING_AN_ABSENT_CHECKOUT_WAS_REPORTED_AS_A_ROTTED_DECLARATION_2026-08-12.md` — the
  finding whose fix is the upstream half of this one. Archived to `done/` by this tick: its
  mechanism landed and its consequence is now closed.
- `WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN_2026-08-12.md` — same episode.
  Note the contrast worth keeping: that alarm's failure was naming tests the gate never ran;
  **this** time the alarm named the blocking test exactly right, and the name was the fix.
- `feedback_a_control_committed_without_its_mechanism_reds_head`
- `feedback_a_new_layer_above_a_control_must_inherit_its_subject`
