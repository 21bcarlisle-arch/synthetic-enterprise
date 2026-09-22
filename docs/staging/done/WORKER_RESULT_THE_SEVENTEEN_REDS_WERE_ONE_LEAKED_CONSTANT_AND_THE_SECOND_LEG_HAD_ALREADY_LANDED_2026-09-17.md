**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The seventeen reds were one leaked constant, and the second leg had already landed

**Filed** 2026-09-17 · worker · lane 0 delivery
**Item** `the-publish-gates-own-tests-are-red-at-head-and-the-finished-repair-is-unlanded`

> **The item named the wrong file for its second leg, and there really was an unlanded finished
> repair — eight lines, in a different file, and it is the one wedging every lane's commit.** The
> leg as written is spent; the leg as *meant* was live. Both are below.

---

## What the item asked for, and what was actually there

Two legs. **Leg (a)** — fix the single cause of 17 failures across the publish gate's own five
blocking files. **Leg (b)** — land 207 uncommitted insertions in
`background/process_run_complete.py` implementing reachability-not-equality plus the
verdict-after-reconcile, and commit the `git mv` archiving
`WORKER_FINDING_THE_PUBLISH_SUCCEEDS_BY_REACHABILITY_AND_IS_GRADED_BY_EQUALITY_2026-09-16.md`.

**Leg (b) is SPENT, both halves, and the draw's own premise check said so before I started.**
Measured rather than assumed:

- `git diff --numstat background/process_run_complete.py` → **empty**. There are no 207
  uncommitted insertions; there is no uncommitted diff at all.
- The work is commit `9c4ce323f` *"the publish verdict asks REACHABILITY, and asks it after the
  cadence that absorbs the commit"*, and `git merge-base --is-ancestor 9c4ce323f origin/main`
  passes.
- The archival is not pending either: the finding is already at
  `docs/staging/done/WORKER_FINDING_THE_PUBLISH_SUCCEEDS_BY_REACHABILITY_AND_IS_GRADED_BY_EQUALITY_2026-09-16.md`,
  tracked, and `git cat-file -e origin/main:<that path>` succeeds. It reached origin, not just HEAD.

So leg (b) discharges nothing further — the finding it was said to pay for was already discharged
by the route that wrote it. Nothing was re-done.

## Leg (a): the cause, and it is one line

Reproduced in a clean `git archive HEAD` extract: **17 failed, 53 passed**, and all 17 tracebacks
end in the same place — `background.live_ledger_guard.LiveLedgerWriteUnderTest`, raised from
`process_run_complete._landing_in_flight_marker` writing
`docs/observability/.publish_landing_in_flight.json`.

The guard is right and the tests are right. What was missing is the isolation, and the reason is
the trap this repository has now named five times:

```python
LANDING_IN_FLIGHT_FILE = PROJECT_DIR / "docs" / "observability" / ".publish_landing_in_flight.json"
```

**bound at module import.** All five suites redirect `prc.PROJECT_DIR` to a scratch tree — which
cannot move a constant that was resolved before the monkeypatch ran. So the publisher, driven by a
fixture, wrote at the *real* live path, and the guard refused it. Correctly. The marker is new:
`9c4ce323f` added it two hours before the brief, to interlock the liveness heartbeat against a
content landing.

Three of those five files already carry a hand-written comment about exactly this trap
(`LATEST_MD`, `LAST_PUSH_FILE`, `PUBLISH_CAUSE_FILE`, `tree_lock.LOCK_FILE` — *"the fourth instance
of the same trap"*). **The class fix for it already exists** and I did not write a new one:
`tests/background/conftest.py::_no_daemon_state_reaches_the_live_record` re-roots a named tuple of
leaking constants, preserving each one's repo-relative path, and its own docstring states the
remedy — *"A new leak is one line plus a re-run of this directory; do not re-derive the wide version
without reading the 43."*

The repair is that one line: `("background.process_run_complete", "LANDING_IN_FLIGHT_FILE")` added
to `_LEAKING_STATE_CONSTANTS`.

## Why this re-rooting costs no control, checked rather than assumed

That docstring is explicit that the wide version of itself was *run* and cost 43 controls, because
for a large class of these constants **the live artefact is the control's subject**. So membership
in the tuple is a claim that has to be tested, not a convenience. Both candidates were checked:

- `test_the_liveness_heartbeat_took_the_tree_from_the_content_publish` **is** a control whose
  subject is this constant — and it sets `prc.LANDING_IN_FLIGHT_FILE` in its own body, which runs
  after the fixture and therefore wins. It measures what it always did.
- `test_live_ledger_guard::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed`
  counts guard **calls in source**. A redirected destination does not move it, and the production
  write still goes through `guard_live_ledger_write` at the real path. The guard keeps its bite
  everywhere a test has *not* redirected the tree.

Both were run: 93 passed across the five blocking files plus those two controls.

## Evidence

| Measurement | Before | After |
|---|---|---|
| The five blocking files, clean `git archive HEAD` extract | 17 failed, 53 passed | **3 failed, 67 passed** |
| The same five, real repo | — | **all green** |
| Five + the two controls that could have been disarmed, real repo | — | **93 passed** |

**The 3 residual extract failures are an artefact of the extract, not a red**, and this is stated
rather than left for a reader to trip over. They are the three tests in
`test_published_provenance_is_real.py` that read the *live* repository — `meta.git_commit names no
commit in this repo: '770497ddd'`, `showing_run.run_id is not a real run id`. A bare `git archive`
extract has no `.git` and no run outputs, so those three cannot pass there by construction. In the
real repository `tests/background/test_published_provenance_is_real.py` is **30 passed**. They were
invisible before this fix only because the guard refused earlier in the same tests.

## The second repair: eight lines, and a prediction of mine that was refuted first

`background/finding_classes --check` refused the commit on
`WORKER_FINDING_THE_LIVENESS_REACHABILITY_LEG_PASSES_ALONE_AND_FAILS_IN_THE_SUITE_SO_EVERY_LANES_COMMIT_IS_WEDGED_2026-09-16.md`
— a BLOCKING finding in this same lane, about the same commit (`9c4ce323f`).

**I PREDICTED MY CONFTEST FIX WOULD CURE IT, AND IT DID NOT.** The prediction is kept here beside
the result because it was made before the answer was known. The reasoning was good: that finding
names its own class as *"test-pollution … arriving through a test that reads REAL repository
state"*, and `_landing_in_flight()` read the live marker, so rerooting it should have been the
cure. Measured: HEAD + my hunk, that test still fails. The fix does change one leg — a
`Liveness heartbeat commit FAILED (rc=1)` line appears that was not there before — so it was not
even inert, just not the cause. Refuted and dropped.

**The finding's own diagnosis of WHERE the red lives is also wrong, and that is why nobody landed
the cure.** It states: *"it is not red at HEAD in the ordinary sense and `red_at_head` will not
establish it"*, and tabulates "passes alone / fails in the suite". Measured both ways:

| | verdict |
|---|---|
| the single test, alone, in the **shared working tree** | **passes** |
| the single test, alone, in a **clean `git archive HEAD` extract** | **FAILS** |

It is a plain red at HEAD. The shared working tree is what makes it *pass* — the inverse of the
pollution story the finding tells — because **the finished repair was already sitting on disk,
uncommitted**, and every run in the shared tree picked it up. `red_at_head` measured in the shared
tree could never establish it, which is exactly the trap the finding fell into.

The repair is eight insertions in the test's own git fake:

```python
if argv[:3] == ["git", "merge-base", "--is-ancestor"]:
    return types.SimpleNamespace(returncode=0 if argv[3] == argv[4] else 1, stdout="", stderr="")
```

`9c4ce323f` moved the push verdict from equality to **reachability**, which handed this stub a new
question — and the `rc=0` fall-through under it answered *"yes, reachable"* to every question,
grading the `push_never_landed` refusal as a success. **A fake more permissive than its subject**,
which is the R15 shape that turns a fail-open into a green suite. The production change landed; its
companion fake repair did not.

Attributed by one-variable swap into the parent tree — HEAD plus *only* these eight lines, conftest
left at HEAD: **1 failed → 14 passed.** The conftest hunk is not needed for it and it is not needed
for the conftest hunk; the two repairs are independent and each was measured alone.

## What this does NOT fix, said out loud

**The done-condition has two halves and this pays one of them.** The five files are green; a
non-null `last_clean_publish` in `.publish_gate_state.json` is not something a repair can type in —
it has to be graded by the publisher on its own next cycle, which is now unblocked rather than
achieved. `wedge_since` is still set and `last_clean_publish` is still `null` as this is filed.

**The HEAD-ref-lock fault is untouched and will survive this.** The brief warned about it and the
warning holds: `.publish_gate_state.json`'s last `liveness_surface_refusal` ends `fatal: cannot lock
ref 'HEAD': is at aff4b153f but expected 56d746816` — the publisher losing the HEAD ref lock to
another lane mid-commit. That is a concurrency fault between two writers, not a red, and nothing in
this repair addresses it. If the next cycle still fails to produce a clean publish, **that** is the
cause to look at, and mistaking it for a recurrence of these 17 is the specific error this
paragraph exists to prevent.

## The generalisable shape

*A constant bound at import cannot be moved by redirecting the directory it was derived from* — and
the cost is not a confusing test failure, it is a **fixture writing the measurement of record**.
This tree has now paid for it five times on five different attributes. The fifth cost 17 reds
across the publish gate's own blocking set, which wedged every lane's commit, two hours after the
constant was introduced by an unrelated and correct repair.

The lesson is narrower than "watch out for import-time constants", because that is already known
here and written down three times in these very files. It is: **a repair that adds a live-record
write to a function tests already drive has added a leak, and the leak is invisible to the repair's
own suite.** `9c4ce323f` was correct, was tested, and its author could not have seen this — the
refusal fires in five *other* files. The cheapest place to catch it is the one-line tuple, and the
thing that makes that cheap is that the tuple already exists.
