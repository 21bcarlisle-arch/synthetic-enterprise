**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `H15_publish_gate_failure_alert`

# The wedge was a tree-lock timeout filed as a test regression, and the front door's machine claim said the opposite of the paragraph beneath it

**Found:** 2026-08-30, on the RUNG-1 draw sent to diagnose a 438-minute publish wedge
(7 consecutive failures, no pass at HEAD `3e90ae5e1`).

Born archived: `publish_gate_and_wedge` is an existing class with 52 instances. This is the
53rd, and the fact that it is the 53rd is most of what it says.

---

## What the doorbell said, and why it was wrong

> the publish gate has been FAILING for ~438 min ... **DIAGNOSE the failing test** ... **FIX
> the red test**

There was no red test. `.publish_gate_state.json` recorded the last two failures as
`kind: "test_regression", rc: 1` with `blocking_tests: []` and `total_red: 0` — an accusation
with no accused, which this module's own source has a name for and had already paid for twice.
Three lines above the third failure, `sim-runner-log.md` reads:

```
- [2026-08-30 12:29 UTC] [process_run] Tests skipped — already passed for git=09b90343d
- [2026-08-30 12:29 UTC] [process_run] Committing and pushing (net=£148,720)
  ...
background.tree_lock.TreeLockTimeout: Could not acquire tree lock (...) within 60.0s
- [2026-08-30 12:30 UTC] [process_run] Publish-gate failure #3 (test_regression, rc=1)
```

The suite had not been run at all. **`git_commit_push` entered `tree_lock()` outside its own
`try`**, so a 60-second contention timeout propagated out of `main()` as an uncaught traceback
— rc=1, the generic code, which `_classify_gate_failure` maps to `test_regression`.

## This is the same defect on its fourth clock

The module already carries two carve-outs written for exactly this, each with an incident
behind it:

| clock | the escape | filed as | closed |
|---|---|---|---|
| the caller's deadline (`sim_runner`, `background_worker`) | rc=124 | 145 recorded test failures | before 2026-08-21 |
| the publisher's own gate clock (`GATE_SUITE_TIMEOUT_SECONDS`) | `return 1` | 3 of 46 refusals of a 32-hour wedge | 2026-08-21 |
| **the tree lock** | **uncaught `TreeLockTimeout`** | **2 of 7 failures of this episode** | **2026-08-30** |

Each was found by a draw sent hunting a red test that did not exist. The cost is not the
misfiling — it is that the alarm spends the director's attention on the wrong subject, and the
streak keeps climbing while the draw looks in the wrong place.

**The generalisable shape: any path that can fail WITHOUT the suite returning a verdict must
name itself, because the default classification is "a test is red" and that default is a
positive accusation, not an absence.** Nothing about rc=1 says "a test ran".

## The repair

`EXIT_TREE_LOCK_UNAVAILABLE = 79` and a `tree_lock_unavailable` kind, in the shape the two
prior carve-outs established. Three things changed beyond adding a constant:

1. **Acquisition is guarded separately from the body** (`ExitStack.enter_context`, not an outer
   `try` around the whole `with`). A `TreeLockTimeout` raised from INSIDE the lock is a
   different fact — the nested re-acquisition deadlock documented at `_git_add_or_refuse`, a bug
   in our own code — and must not be relabelled as contention, which would tell the reader to
   wait for a lock that will never be released.
2. **The two `kind != "gate_timeout"` comparisons became `UNJUDGED_GATE_KINDS`.** They had been
   two separate string comparisons for nine days, and this carve-out had to find both. A set
   makes a third one inherit the behaviour instead of shipping without it.
3. **Contention still keeps the streak and still fires.** A publish that did not happen is a
   failed publish (R15: an unavailable check is a failed check). What changes is only what the
   alarm SAYS: `NO TEST WAS JUDGED`, and `fuser -v docs/observability/.tree.lock` as the one
   thing worth looking at. A single occurrence is normal contention; **a streak of them is the
   real finding**, and the subject is the writer holding the lock, not any test.

Controls: `test_a_lost_tree_lock_is_a_named_outcome_and_not_an_uncaught_traceback`,
`test_the_guard_covers_acquisition_only_so_a_nested_deadlock_still_surfaces`,
`test_an_unjudged_kind_never_sends_the_reader_after_a_test` (parametrised over the set, so a
future kind inherits it), `test_a_tree_lock_timeout_is_not_recorded_as_a_test_regression`,
`test_the_tree_lock_outcome_reports_its_own_exit_code_and_never_a_silent_zero`. All five were
mutation-proven by restoring the bare `with tree_lock():` and by breaking the payload branch.

---

## The second defect, found on the way: the front door's machine claim was false for six days

Separately red, and genuinely red — this one the gate got right.

`site/index.html` carries `data-mix-claim="non_domestic_revenue_share_gt_95"`, the
machine-readable form of the segment disclosure that must precede the mission claim.
`_check_front_door_segment_claim` recomputes the real share every publish and refuses if the
sentence has stopped being true. It had been refusing since 2026-08-24.

**The prose was already correct.** The paragraph directly beneath that attribute reads *"This
book is households, as of 24 August 2026"* and *"What is published now is a domestic book"*. It
was rewritten the day the director suspended I&C supply. Its machine-readable form could not
be: **the grammar only said `gt`.** There was no way to write "this book is domestic" in a
vocabulary that only expresses "greater than", so the attribute was left asserting the exact
opposite of the sentence it was supposed to encode — 98.35% domestic, claiming >95%
non-domestic.

| | claim | actual |
|---|---|---|
| before 2026-08-24 | non-domestic > 95% | ~99% non-domestic — **true** |
| 2026-08-24 → 2026-08-30 | non-domestic > 95% | **1.65%** non-domestic — **false** |
| now | non-domestic < 5% | 1.65% non-domestic — true |

**The tempting repair is the wrong one.** Relabelling to `gt_0` passes today (1.65 > 0) and
would go on passing if the book flipped back to I&C — a control keyed to today's answer instead
of to the property, which is the failure this project keeps paying for. The gate learned the
`lt` direction instead, so a domestic claim can go red the moment the book stops being domestic.
`test_dashboard_front_door_mix_claim_gate_fires_on_a_domestic_claim_too` asserts that, and also
that `gt` did not quietly become a synonym for `lt` when the grammar widened.

**Note what this cost to find.** A hand-authored public sentence and its machine-readable form
are two artefacts, and only one of them was edited by the person who knew the book had changed.
The gate caught it — correctly, immediately, and for six days nobody read what it said, because
its refusal was interleaved with a wedge alarm that was accusing the test suite.

---

## What I got wrong in the diagnosis itself

While mutation-proving the fix I twice edited `background/process_run_complete.py` into a
deliberately broken state, in the shared tree, with another lane's publish hook chain in flight.
At 12:57 that chain refused its commit naming four tests in
`tests/background/test_process_run_complete.py` — all four green before and after, red only
inside my mutation window.

**That refusal was recorded as the episode's next failure.** The doorbell warns against running a
second full suite beside a live one for exactly this reason ("the diagnosis would MANUFACTURE the
red it went looking for"); it does not warn about mutating a live module, and the effect is the
same and cheaper to trigger. A mutation proof needs the real module on disk, so the shared tree is
the one place it cannot safely happen. **Take the tree lock for the mutation window, or do the
proof in a worktree** — the current practice is sound only when no other lane is publishing, and
this seat cannot see that without checking.

## Left undone

The episode counter still reads 7. Two of those seven were this misfiling and one was my own
mutation window; the streak clears itself on the next clean publish rather than being edited, per
the standing rule that a level move is recorded and never authorised.
