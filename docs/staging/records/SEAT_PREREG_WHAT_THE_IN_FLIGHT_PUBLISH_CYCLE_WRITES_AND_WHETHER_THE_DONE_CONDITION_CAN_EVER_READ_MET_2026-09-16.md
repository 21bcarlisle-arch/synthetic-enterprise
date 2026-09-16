**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — confirm the first clean publish after the split pair landed)

# PRE-REGISTRATION — what the in-flight publish cycle writes, and whether this item's done-condition can ever read MET

**Written:** 2026-09-16 ~09:40Z, BEFORE the in-flight cycle resolved and BEFORE any state file was
re-read after it.
**Seat:** Lane 0 delivery, claim
`publish-wedge-confirm-the-first-clean-publish-after-the-split-pair-landed`

## The situation this is written into

The previous turn on this claim established, and I am not re-deriving it: `d9f9ef69b` cured the
named cause, and `site/knowledge/test_index_reflects_the_record.py` is green in a clean
`origin/main` extract and in the publisher's own construction
(`PREREG_IS_THE_COPY_TEST_STILL_RED_AT_HEAD_AFTER_THE_SPLIT_PAIR_LANDED_2026-09-16.md`). That turn
released nothing, correctly, because a green test is not a clean publish.

What is new at 09:40Z and was not true when that turn ran:

- A **fresh marker exists**: `docs/staging/run_complete_20260916T085959Z.md`, and
  `pending_run_complete_markers()` is 1.
- The publisher is **live on it right now**: PID 2618284,
  `process_run_complete.py .../run_complete_20260916T085959Z.md`, ~25 minutes in.
- The last recorded failure is `ts=1789536634` (~05:31Z), against `run_complete_20260916T044947Z.md`
  at `git=dbd92cedc`. Nothing has failed since.
- A **liveness heartbeat did publish** at `ts=1789549693` (~09:08Z) at `git=141213ad4`, and
  `origin/main` is `141213ad4`. So a commit from this pipeline reached origin 30 minutes ago.

So the in-flight cycle is the event this claim was released on. Its outcome is not yet known and
this is written first.

## The structural claim, established from code and needing no measurement

`record_publish_gate_success` writes
`"last_clean_publish": None if episode_closed else stamp` and proposes `"episode_failures": 0` on
both branches. `_write_publish_gate_state` carries a prior `last_clean_publish` forward only
`if not episode_closed`. `guard_episode` returns the proposal untouched when `episode_closed` and
otherwise takes `max(old, proposed)` over `streak_fields = ("episode_failures",
"episode_clean_publishes")`.

Compose those three and the success path has exactly two exits:

| exit | `episode_failures` | `last_clean_publish` |
|---|---|---|
| episode **closed** (`pending == 0`) | `0` ✓ | `None` ✗ |
| episode **open** (`pending > 0`) | `max(34, 0) = 34` ✗ | `stamp` ✓ |

**The drawn item's done-condition is `last_clean_publish != null` AND `episode_failures == 0`. No
success path can satisfy both.** It is unsatisfiable by construction, not merely unmet. That is a
property of the code, so it is asserted here rather than predicted — and it is the reason this
claim could have been re-drawn indefinitely against a publisher that was working.

## The prediction

**If the in-flight cycle publishes cleanly** — which I predict it does, because the only named
blocking test is green at HEAD and HEAD is `origin/main`:

1. It drains the one pending marker, so `pending == 0` and the episode **CLOSES**. **PREDICT**
   `episode_failures: 0`, `failures: []`, `alerted_at: null`, `wedge_since: null`.
2. **PREDICT `last_clean_publish` stays `null`** and `episode_clean_publishes` stays `0` — set to
   `None`/`0` by the close, not carried. This is the counter-intuitive leg and the one worth
   being wrong about.
3. Therefore **PREDICT the item's done-condition reads UNMET on the very cycle that ends the
   146-hour wedge.**

**If it fails**, `episode_failures` goes to 35 and `failures` names a new `git_hash`. Then the
repair is incomplete and the finding is about the cause it names, not about this file's schema.

## What outcome 2 would mean, if it holds

At the instant `last_clean_publish` is most true, it is set to `None`. The field's own comment
calls it "a LATEST-wins timestamp"; the close makes it episode-scoped, which `episode_clean_publishes`
already is and which this field's name says it is not.

The consequence is not cosmetic. **A recovered publisher and a never-run one become
indistinguishable in this file**: a clean close leaves `failures: []`, `alerted_at: null`,
`last_clean_publish: null` — byte-for-byte the reading a fresh worktree gets from the two-month-old
tracked placeholder
(`SEAT_FINDING_A_LIVE_RECORD_IS_TRACKED_SO_EVERY_WORKTREE_READS_A_TWO_MONTH_OLD_PLACEHOLDER_AS_LIVE_STATE_2026-09-16.md`).
A closed episode has **no positive record that any publish ever succeeded**, only the absence of
failures — and absence is exactly what the placeholder also asserts.

If that holds, the repair is one line with a named reason: an episode close clears the EPISODE, not
the evidence that a publish happened. `last_clean_publish` should take `stamp` on both exits.

## SECOND PRE-REGISTRATION, ~09:50Z — is the NEW red a production defect or a stale fixture?

*Written after the first result below was known, and BEFORE the measurement in this section. The
first prediction's antecedent did not hold, so this is a new question and gets its own prediction
rather than being folded into the old one.*

The cycle failed and the blocking test CHANGED to
`tests/background/test_an_exit_code_is_not_a_landing.py::test_the_channel_reads_the_SHARED_trees_log_not_the_importing_trees`.
It is **red in a clean `origin/main` (`4e0551b0e`) extract** — hermetic, builds its own git repo in
`tmp_path`, 13 siblings green. So it is red AT HEAD and no lane's pollution is involved.

Reading the code, the candidate explanation is that `_shared_tree_log`'s body **moved today** to
`live_ledger_guard.shared_tree_live_record` (its own docstring says so, 2026-09-16). That module
binds `PROJECT_DIR` and `LIVE_RECORD_DIR` from ITS OWN `__file__`. The test monkeypatches only
`seat_executor.PROJECT_DIR` and `seat_executor.LOG_FILE`, so `is_live_record_path()` measures the
fixture's `tmp_path` against the REAL repo's `docs/observability`, returns False, and the resolver
returns `path` unchanged before it ever asks git.

**If that is the whole story, the production behaviour is UNBROKEN**: in a real linked worktree both
modules are imported from the same tree, so both `PROJECT_DIR`s agree and the redirect works. The
fixture would have stopped standing where the defect is, which is a stale control, not an outage.

**PREDICT:** importing `background.seat_executor` from this linked worktree
(`/var/tmp/se-seat-executor`, whose own `docs/observability/seat-executor-log.md` is git's checkout,
not the live file) and calling `ids_run_since` returns **a non-empty list of ids read from the
SHARED tree's log** — i.e. the production path still works and the red is fixture-staleness.

**If instead it returns `[]`**, the refactor really did break the channel in production, the test is
right, and the repair is in `live_ledger_guard`, not in the fixture. That is the outcome that would
make me wrong, and it is the one worth being wrong about: "fix the test" is the fail-open move here
and it must not be reached by assumption.

## RESULT — appended after measuring, beside the prediction and not instead of it

### Result 1 — the in-flight cycle (measured ~09:38Z)

**The cycle FAILED.** PID 2618284 exited; `episode_failures` went 34 → **35**; the new failure is
`kind=test_regression`, `rc=1`, `git_hash=edded3973`, `cause=unattributed`.

**So prediction 1's antecedent ("if the in-flight cycle publishes cleanly") did not hold, and legs
1–3 were never graded.** They are not scored as right or wrong — they are untested, and saying so
is the point of having written them down. The second branch is what happened, and that branch was
predicted correctly: `episode_failures` went to 35 and the record named a new `git_hash`.

**The structural claim is unaffected and still stands**, because it was derived from code rather
than measured: the done-condition `last_clean_publish != null AND episode_failures == 0` remains
unsatisfiable on every success path. Nothing in this result bears on it either way.

**What DID change, and it is the substantive finding of this turn:** `blocking_tests` no longer
names `site/knowledge/test_index_reflects_the_record.py`. The copy test that wedged 34 cycles is
gone from the blocking set. **`d9f9ef69b`'s repair held.** The wedge did not persist — it MOVED,
to a red that did not exist when this item was written.

### Result 2 — the new red is a stale fixture, not a broken channel (measured ~09:55Z)

**The prediction held.** Importing `background.seat_executor` from this linked worktree
(`/var/tmp/se-seat-executor`, whose own `docs/observability/seat-executor-log.md` does not exist):

    PROJECT_DIR    : /var/tmp/se-seat-executor
    LOG_FILE exists in THIS worktree: False
    resolved log   : /home/rich/synthetic-enterprise/docs/observability/seat-executor-log.md
    ids_run_since(0.0) -> n = 193

The channel reaches the shared tree's log and answers 193 ids. **The production path is intact.**

The cause is the one predicted: `_shared_tree_log`'s body moved on 2026-09-16 to
`live_ledger_guard.shared_tree_live_record`, which asks its OWN `PROJECT_DIR` and
`LIVE_RECORD_DIR`. The fixture patched only `seat_executor`'s, so `is_live_record_path` measured
`tmp_path` against the real repo's `docs/observability`, returned False, and the resolver returned
before ever asking git.

**Attribution, one variable.** Clean `origin/main` (`4e0551b0e`) extract: **RED**. The same extract
with **only** `tests/background/test_an_exit_code_is_not_a_landing.py` replaced by the repaired
copy: **31 passed**. One file swapped into its parent tree.

**Mutation-proven both ways, in that extract, not asserted:**

| mutation | result |
|---|---|
| revert `ids_run_since`'s default to `LOG_FILE` (the docstring's named mutation) | **1 failed**, 30 passed — the control still fires |
| drop the new `live_ledger_guard` rebind (re-create the stale fixture) | **1 failed**, 30 passed — the added patch is load-bearing |
| neither | 31 passed |

The second mutation now fails on the added premise-assert, which names the gate as the cause. Before
the repair the same condition failed on the channel assertion, reporting *"a worktree-imported
channel silently lost the shared tree's log"* — **a true-sounding sentence about a channel that was
working**. That misdirection is the reason the red read as a regression rather than as a fixture.

### What this turn establishes about the claim

1. The 146-hour wedge's named cause is **cured** and is out of `blocking_tests`.
2. The wedge **moved** to an unrelated red, which was red at HEAD, and that red is now repaired
   and mutation-proven.
3. The done-condition as written **can never read MET** — filed as
   `SEAT_FINDING_LAST_CLEAN_PUBLISH_IS_CLEARED_AT_THE_INSTANT_IT_BECOMES_TRUE_SO_A_RECOVERED_PUBLISHER_IS_INDISTINGUISHABLE_FROM_A_PLACEHOLDER_2026-09-16.md`.

**So the claim is released on 1 and 2, and explicitly NOT on the done-condition as drawn**, because
that condition is unsatisfiable and waiting for it is what would burn the next invocation too. The
honest replacement, for whoever reads this next: the publisher publishes when a cycle records a
success rather than a failure — observable as `episode_clean_publishes >= 1` (episode open, gate
passing, queue outrunning it) **or** `failures: []` with `alerted_at: null` (episode closed). The
second reading is only trustworthy once the finding above is repaired.
