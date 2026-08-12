# [WORKER FINDING] The wedge had a SECOND cause, landed 5 min after the last alarm (2026-08-09)

**Severity:** LATENT · **Lane:** H_harness

**Found during:** `DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH` draw 1 (unwedge).
**Status:** both causes FIXED in this tick. Filed because the *shape* is the finding.
**Impact:** would have re-wedged the gate immediately after a correct fix — i.e. it would
have presented as "the unwedge didn't work".

## Observed, with evidence

The 2026-08-08 episode (10 alarms, 18:01–23:17 UTC, 44 markers queued) was caused by the ruff
static ratchet going red at HEAD — filed, bisected and fixed per
`WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD_2026-08-08`. With that fixed, the gate ran 769 tests
(up from 580) and stopped at a **different** red:

```
FAILED tests/background/test_seat_guard_daemons.py::TestStructuralLock::
       test_every_main_entrypoint_is_guarded
AssertionError: background/*.py entrypoints with no seat guard as the FIRST act of
their __main__ block: ['forward_attachment_register.py']
```

`background/forward_attachment_register.py` was added by `641a87ae2` (FUT1) at **2026-08-09
00:22:24 +0100 = 23:22 UTC** — *five minutes after the last recorded gate failure of the
episode* (23:17 UTC). So:

* it is **not** a cause of the observed 7-hour episode (inferred-free: the timestamps do not
  overlap), and
* it **was** guaranteed to keep the gate wedged after a fully correct fix to the first cause.

## Why it is a class, not an instance

1. **`-x` publishes one cause at a time.** The gate stops at the first red, so its alarm can
   only ever name the first of N causes. Ten alarms across seven hours all said "rc=1" and none
   of them could have said "and there is a second one behind it". A fix verified only against
   the alarm's stated cause is verified against a partial truth.
2. **A wedge window ACCUMULATES causes.** While publishing is stopped, ordinary commits keep
   landing, and each one is untested against the gate that is already red — so the longer the
   wedge, the more causes it collects. That is a positive feedback loop, and it is why "the
   alarm clears itself on the next clean publish" is the only honest completion test.
3. **The new cause reached HEAD at all.** A commit added an unguarded `__main__` to
   `background/` and landed. Whatever ran before that commit did not include
   `test_seat_guard_daemons.py`. Not diagnosed here — see below.

## The fix applied

`refuse_if_foreign("forward_attachment_register")` as the first act of the `__main__` block,
matching the house idiom in `background/naive_organ.py` (`background._seat` import with an
`_seat` fallback for direct-path launch). 23/23 seat-guard tests and 19/19 register tests green.

## Not asserted (the drawable half)

* **Why the seat-guard test did not fire before `641a87ae2` landed.** Either the pre-commit
  gate's scope excludes `tests/background/test_seat_guard_daemons.py`, or that commit bypassed
  it. Not diagnosed — the timestamps prove the *when*, not the *how*. This is the part worth
  drawing: a structural guard on `background/**` that a `background/**` addition can walk past
  is a control with a hole in its trigger, not in its logic.
* Whether other reds sit behind this one. The gate is `-x`; only a full green run proves the
  count is zero, which is what the completion evidence for this tick has to be.

— Worker finding, 2026-08-09, during the director-priority unwedge.
