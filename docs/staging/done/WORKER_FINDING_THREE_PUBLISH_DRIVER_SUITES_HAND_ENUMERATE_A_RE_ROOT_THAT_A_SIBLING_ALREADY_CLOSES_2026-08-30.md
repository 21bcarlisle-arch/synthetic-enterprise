**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Three publish-driver suites hand-enumerate a re-root that a sibling in the same directory already closes generically

**Born archived**: a new instance of `publish_gate_and_wedge`, which is consolidated (53
instances, ruling ~18). Filed for the record and for the next tick that touches these fixtures,
not to win a draw.

**Found:** 2026-08-30, disposing of the publish-gate wedge that ran 14 consecutive gate failures
and ~10h with nothing reaching origin. The wedge itself is fixed (`4f4e6fa62`). This is the class
behind it, still open.

## What happened, in one line

`background/process_run_complete.py` gained a new module-level path constant. Five fixtures across
three test files did not know about it, so those files drove the real publisher at the **live**
`docs/observability/.last_publish_cause.json`, `live_ledger_guard` correctly refused, and 13 tests
went red inside the publish gate's own blocking set — which is the set that decides whether
publishing happens at all.

## Why the class is still open

Every one of prc's path constants is computed **at module import** from the real `PROJECT_DIR`, so
`monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)` does not move any of them. There are **19**
such constants under the repo root:

```
PROJECT_DIR STAGING_DIR LATEST_MD LOG_FILE LAST_TESTED_HASH_FILE LAST_TESTED_GREEN_FILE
LAST_PUSH_FILE RUN_LOCK_FILE RUN_INSIGHTS_PATH RUN_HISTORY_PATH NAIVE_ORGAN_LOG
LAST_FINGERPRINT_FILE FORCE_REPUBLISH_FLAG PUBLISH_GATE_STATE_FILE
OPERATIONAL_LAYER_STATE_FILE GATE_SUBJECT_COST_RECORD GATE_BLOCKING_TESTS_FILE
PUBLISH_CAUSE_FILE WEDGE_SUSPECT_HIT_RATE_FILE
```

(`HEAD_CHECKOUT_ROOT` and `PYTEST_TEMP_ROOT_PARENT` are env-rooted outside the repo and are not
this problem.)

Six test files drive prc's publish path. They are split, and the split is the finding:

**Closed generically — a namespace walk, nothing to remember:**
- `tests/background/test_process_run_complete.py` — `_isolate_project_dir`, lines 90–131
- `tests/background/test_a_publish_failure_names_which_of_the_three_it_was.py`
- `tests/background/test_rest_ladder_isolation.py`

**Still hand-enumerated, per fixture, opt-in:**
- `tests/background/test_a_refused_publish_commit_records_its_reds.py`
- `tests/background/test_published_provenance_is_real.py`
- `tests/background/test_the_publish_commit_carries_only_its_own_work.py`

The generic fixture's own docstring already argued this case, before the instance that proved it:

> WHY A DIRECTORY-WIDE RE-ROOT AND NOT FOUR MONKEYPATCHES. Per-test wiring is what failed. It is
> opt-in, it is invisible when omitted […] A path constant added to prc tomorrow is isolated the
> day it lands, with nothing to remember (R10: close the class, not the instance).

`PUBLISH_CAUSE_FILE` landed at `prc:2931` the next day and cost 14 gate cycles.

## What the landed repair does and does not do

`4f4e6fa62` added one `monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", ...)` line to each of the
five fixtures, with the reason written beside it. That is the correct **instance** repair and the
gate needed it. Its commit message states the intent as "so the next module-level path constant is
not a sixth instance" — but **a comment cannot enforce that**. Nothing reads it. The twentieth
constant will be a sixth instance exactly as the nineteenth was a fifth.

**No control asserts the class is closed.** `grep` finds no test that enumerates prc's module-level
paths and checks the publish-driver fixtures re-root them. The only thing standing between the next
path constant and the next wedge is whoever adds it reading a comment in three other files.

## The repair, and why I did not do it this tick

Hoist the `_isolate_project_dir` namespace walk into a fixture the three hand-enumerated files
share, and key a control to the **property** — "every prc Path under the repo root is re-rooted in
any test that calls `git_commit_push`" — not to today's list of constants, which is the mistake
that would make it go green when the code becomes more honest.

**Not done here on purpose.** The three files are the publish gate's own blocking set and a gate run
was in flight. Two hours ago this same wedge got one layer deeper because a repair to the publish
path was landed without running the three suites that drive it end to end; refactoring their
fixtures mid-run, with a second full suite unable to run beside the live one on this cgroup, is the
same move. The instance is fixed and publishing is unblocked; the class repair wants a tick where
the gate is green and the suites can actually be run against it.

## How to reverse

Nothing to reverse — this document is the whole change.
