**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — was the named blocking test actually red at the commit stamped beside it?

**Filed:** 2026-09-04, delivery seat (isolated worktree `/var/tmp/se-seat-executor`), BEFORE running
the measurement.

RECORDED: a pre-registration and its grading, not a defect report. The finding it feeds is
filed separately.

## The observation that prompted it

`docs/observability/.publish_gate_state.json` on the shared tree, read at 2026-09-04 11:37 UTC:

```
"blocking_tests": ["FAILED tests/background/test_publish_failure_names_its_cause.py::test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis"],
"total_red": 1, "red_census": "complete",
"failures": [{"cause": "unattributed", "cause_evidence": "", "git_hash": "3d369242c",
              "kind": "test_regression", "rc": 1,
              "reason": "process_run_complete rc=1 on run_complete_20260904T104410Z.md",
              "ts": 1788520730.5458307}]
```

That test is **GREEN** — 24 passed — in two places I have already run it: this clean worktree at
HEAD `4d1d6298c`, and the shared tree as it stands.

`.last_gate_blocking_tests.json` carries `git_hash: 3d369242c`, `ts: 1788520729.18` — **1.4 seconds
before** the failure record. So this is NOT the known carried-forward-from-an-earlier-cycle shape:
the blocking record was written by *this* cycle, at *this* stamped commit.

## The question

Was `test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis` red at `3d369242c`?

## Prediction, recorded before looking

**I predict it was GREEN at `3d369242c` too**, and that the census's node id therefore describes
neither HEAD nor its own stamped commit.

Reasoning: `git diff 3d369242c..HEAD` touches exactly one module in that test's subject set
(`background/background_worker.py`, +13/-1) and does not touch the test file at all. A red that a
13-line addition fixed, in a test about whether the worker log passes off library noise as a
diagnosis, is possible but not the way to bet.

**If GREEN:** the census is wrong at its own commit, and the likely cause is that it was run
against the *shared working tree* (several lanes' uncommitted edits) while being *stamped* with a
commit hash — the "a gate can judge the working tree while its message claims the commit" shape.

**If RED:** the census was honest and the defect is only that nothing re-derives it against
current HEAD, which is the already-catalogued "subject is HEAD" shape. The stamped hash would
still be wrong in a second way: `3d369242c` was committed 10:41 UTC, and at the failure instant
(11:18:50 UTC) HEAD was already `1ed36540b` — three commits and 37 minutes further on.

## What must NOT happen for this to be a clean read

- The extract must be at `3d369242c` exactly, with **no** working-tree edits from any lane.
- `python3 -B` (a stale `.pyc` has reported SURVIVED here before).

## What I will NOT conclude either way

Nothing about whether the *publisher* was right to fail. rc=1 is not the test gate's refusal code
(77 is), so the red census and the process's exit status are two separate claims and this
measurement grades only the first.

---

**Graded below, beside the prediction, whatever it says.**

## RESULT — **THE PREDICTION IS REFUTED.** The test was genuinely RED at `3d369242c`.

```
$ git archive 3d369242c | tar -x -C /tmp/prereg_3d36 && cd /tmp/prereg_3d36
$ python3 -B -m pytest tests/background/test_publish_failure_names_its_cause.py -q
FAILED ...::test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis
1 failed, 23 passed in 0.25s

E  AssertionError: the excerpt does not label which stream it is quoting, so a reader
   cannot tell the publisher's verdict from whatever the runtime warned about last
```

I bet against a 13-line change to `background_worker.py` being the fix, and that is exactly what
it was. **The census was honest and materially right**: `3d369242c` introduced the regression, and
the very next commit to touch it — `e78e17581`, *"the sweep's new end-here branch hand-rolled its
own excerpt and silently undid three landed repairs, and only the one under a control went red"* —
is another lane fixing this same defect, 4 minutes AFTER the failure was recorded.

So the red at the failure instant (11:18:50Z, HEAD `1ed36540b`) was real at HEAD too. Both branches
of my "if GREEN / if RED" fork are therefore settled the second way, and the working-tree-vs-commit
hypothesis I favoured is **not supported by any evidence here** — I should not have led with it.

### What this refutation is worth, which is more than the confirmation would have been

It removes the interesting-looking explanation and leaves the dull correct one, and the dull one is
where the real defect turned out to live. The census was right; what was wrong sat one field to its
left. `"cause": "unattributed"` with `"cause_evidence": ""` — a verdict of *"we cannot tell"* with
nothing whatever saying why. Had the prediction been confirmed I would have spent the turn
rewriting a census that was doing its job correctly.

### The one thing it does establish about the stamp

`3d369242c` was committed 10:41:02Z; the failure was recorded at 11:18:50Z, by which time HEAD was
`1ed36540b` — **three commits and 37 minutes further on**. The stamp is the *marker's* commit, not
the commit under test. That did not mislead anyone here (the red spanned both), so it is recorded
as an observation and **not** claimed as a defect: I have not shown a case where it changes an
answer, and a finding filed on it would be filed on a hunch.

**Feeds:** `SEAT_FINDING_AN_UNATTRIBUTED_PUBLISH_FAILURE_NAMED_NO_REASON_ON_THREE_OF_ITS_FOUR_BRANCHES_2026-09-04.md`
