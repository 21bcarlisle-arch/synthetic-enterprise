**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publish verdict was taken before its delivery had finished, and the item's second remedy was already in force

*Worker, 2026-09-17, scheduled tick, lane-0 delivery claim
`the-publisher-cannot-push-and-the-cause-has-moved-to-push-never-landed`. The item directed:
establish which of two things is true by running the push and reading its stderr; fix the one
that is true; and "make the publisher's own cycle re-read `git ls-remote` after the reconcile and
before it records a verdict". One of those three was already done. What follows is what I
measured, kept beside the premise rather than replacing it.*

## 1. The premise's INSTANCE is spent; its subject is not

The draw's own premise check said both cited commits were already ancestors of `origin/main`, and
that is confirmed first-hand:

```
84c8bdee7 ancestor-of-origin: YES
cef62f22e ancestor-of-origin: YES
HEAD c10ee531b · origin/main 7e4f6523d · 2 ahead, 16 behind
```

So `HEAD 84c8bdee7 / origin cef62f22e, 1 ahead and 4 behind` is a state that no longer exists.
The mechanism is live, though: the same fork, two commits wider, at a new pair of shas.

## 2. The item's fork in the road, settled by running it

The item named two possibilities and told me to read stderr rather than the return code. Done,
with `--dry-run` so the measurement costs nothing:

```
$ git push --dry-run origin HEAD:main
 ! [rejected]            HEAD -> main (non-fast-forward)
error: failed to push some refs
hint: Updates were rejected because the tip of your current branch is behind its remote counterpart.
```

**The push IS being issued, and the remote rejects it non-fast-forward.** `origin_reconcile
._classify_push_failure` reads those exact words as `REFUSED_RACE`. The other possibility — "the
push is not being issued at all" — is refuted. This agrees with the prior turn's measurement of
the same race (556 s of gated merge against a ~600 s sibling push interval,
`WORKER_RESULT_THE_FIFTY_EIGHT_FAILURE_PUBLISH_EPISODE_HAS_NO_RED_TEST_AND_THE_WEDGE_IS_A_MERGE_TO_PUSH_RACE_2026-09-17.md`),
and it is now established from two independent readings rather than one.

## 3. The item's second remedy was ALREADY IN FORCE, and I did not build it again

> "make the publisher's own cycle re-read `git ls-remote` after the reconcile and before it
> records a verdict"

`process_run_complete._reconcile_then_reread_origin` does exactly this and has since 2026-09-16.
It runs `origin_reconcile.reconcile()`, fetches, re-reads the ref through `_origin_main_sha`
(`git ls-remote`, never the tracking ref), and hands the answer to the SAME predicate the pre-push
verdict used. It is wired at `git_commit_push` outside the tree lock and has its own control
(`tests/background/test_the_publish_verdict_asks_reachability_and_not_equality.py::
test_the_recovery_is_called_from_the_publish_path_and_OUTSIDE_the_tree_lock`).

**Implementing it would have been a second copy of a live mechanism.** Recording it here because
the item's phrasing reads as though it were missing, and a later draw will read the same words.

## 4. So what WAS wrong: the verdict is due later than the cycle can wait

The re-read happens. It happens **556 seconds after the absorbing cadence starts**, inside a
publish path whose whole post-gate allowance is 900 s (`PUBLISH_PATH_ALLOWANCE_SECONDS`) and whose
hook-chain commit alone may take 880 s (`GIT_COMMIT_HOOK_TIMEOUT_SECONDS`). One absorbing cadence
barely fits. The measured win rate of one cadence against a ~600 s sibling interval is roughly a
coin toss, and the obvious repair — retry it — is the one move that cannot be made here: **the
director ruled on 2026-08-21 that no gate budget grows** ("A 75-minute gate is absurd on its face
and neither of us said so"). A retry loop would be killed by the publisher's own wrapper and filed
as `deadline_kill`, which is *worse* attribution than the one it replaced.

That is why the fix is not a retry. **The verdict, not the push, is what was in the wrong place.**

The cost of taking it early is on the record: `episode_failures: 58`, `last_clean_publish: null`,
`wedge_since` 7.2 days, `total_red: 0`, `blocking_tests: []`. Fifty-eight consecutive recorded
publish failures **with no red test in any of them**, and failure #58's own evidence line names
the mechanism that then delivered its commit. `84c8bdee7` is on origin. The publish happened; the
gate recorded a failure.

## 5. What landed

| Piece | What it is |
|---|---|
| `background/publish_delivery_deferral.py` | A stdlib-only leaf holding the ONE outstanding delivery and grading it: `REACHED` / `ABSORBING` / `OVERDUE` / `NONE`. It cannot claim a publish — `reached` is threaded in from the caller's read of the remote ref. |
| `EXIT_PUBLISH_DELIVERY_DEFERRED = 80`, `COMMITTED_DELIVERY_DEFERRED` | The third answer. Not rc=0 (which routes into `record_publish_gate_success` and would stamp a clean publish for content origin does not have — the 2026-08-19 disarm-by-rc-0 defect) and not rc=77 (which is the 58-failure record). Not retryable, so no fingerprint retires the marker while a verdict is owed. |
| `grade_outstanding_delivery` | The re-measurement, called once from `record_publish_gate_outcome` — the verdict writer — for every rc it grades. `REACHED` takes the push clock, the content stamp and a clean publish the gate graded ITSELF. `OVERDUE` records a real failure. `ABSORBING` writes nothing. |
| `publish_cause.LOST_PUSH_RACE` | The seventh cause, and the distinction is the repair: `push_never_landed` is a ref standing still with nothing to explain it (a push to be MADE); this is a push that was made and lost a race (a race to be WON). |
| `DELIVERY_NOT_REACHED_KIND` | A kind whose label does not accuse a hook chain that passed, wired into the supervisor's `WEDGE_KINDS_NO_TEST_JUDGED` so no RUNG-1 draw is sent hunting a red test that was green. |
| the rc=0 leg | **The fail-open this repair would otherwise have opened.** With a predecessor's content undelivered, the next cycle finds `NOTHING_TO_COMMIT` — retryable, rc=0 — and would have bought a clean-publish stamp for figures the public never saw. It now answers `unproven` and leaves the streak. |

**Silence is bounded and not by a number of mine.** `_race_benign_seconds` borrows
`deadmans_switch.RACE_PERSISTENCE_SECONDS` (2700 s), the quantity this machine already declares
for "when a lost push race stops being benign"; a control reds if either module mints a second
one. Past that window the deferral is `OVERDUE` and a failure is recorded with a cause that was
re-measured. Unreadable record, unstamped record, sha-less record, unreadable window, unreadable
remote past the window: all `OVERDUE`. Fail-closed here means toward the alarm, because a deferral
that cannot expire is a wedge that cannot be reported.

Twelve controls in
`tests/background/test_a_lost_push_race_holds_its_verdict_and_is_graded_on_the_ref.py`, each
naming the mutation that reds it, including one over the WHOLE partition — a `verdict` that
answered `ABSORBING` for everything would pass four per-branch tests and hold every wedge open
for ever.

## 6. One existing control was widened, and it is strictly harder to pass

`test_the_publishers_kinds_and_the_supervisors_set_have_not_drifted` asked its question with
`assert f'kind="{kind}"' in src` — a string grep that can only see a literal. The fifth kind is
passed as a named constant (`kind=DELIVERY_NOT_REACHED_KIND`), deliberately, so the publisher's
label table and this reader cannot disagree about the spelling — and the grep read that as "the
producer has moved". It now asks the AST what the publisher actually passes as `kind=`, counting
both shapes and **nothing else**: a match inside a comment or docstring no longer satisfies it.

*Stated because widening a control to accommodate one's own change is the asymmetric move this
repo has a rule about. The widening's direction is recorded in the docstring beside it.*

## 7. What is NOT done, plainly

**The item's done-condition is not met and cannot be met by a landing.** It asks for
`episode_clean_publishes` non-zero with a `last_clean_publish` the gate graded itself, and
`git ls-remote origin main` equal to HEAD immediately after a publish cycle. At the moment of
writing the counter is still 0 and the stamp is still null, because **only a real publish cycle
can produce one** and none has run since this landed. What changed is that a cycle now *can*: the
path that produces a graded clean publish exists, and the path that recorded 58 failures for
races no longer does.

The honest next measurement is the next cadence's `.publish_gate_state.json`: either
`episode_clean_publishes` moves, or an `OVERDUE` grading records a failure whose cause is
`lost_push_race` — and that second outcome would be the first *attributable* one in the episode.

## 8. Method notes worth the next session's time

* **My working copy of `process_run_complete.py` was STALE against HEAD and holder at once.** HEAD
  (committed 11:04 today) defines `red_tree_fork_verdict`; the working copy I was editing does
  not. 22 tests were red in the shared tree and **zero** of them were mine: green in a pristine
  HEAD extract, green in HEAD-plus-my-hunks. The landing is `isolate_hunks` bytes, four files,
  every dropped hunk printed.
* **`isolate_hunks` refused my publisher bytes as "only HALF a landing"** — correctly: they name
  `publish_cause.LOST_PUSH_RACE`, which exists only in the uncommitted sibling. The refusal is
  per-path and its own message says the answer is "land them together", so the bytes were built
  with that module's own pure API (`head_lines`/`group_opcodes`/`reconstruct`, soundness checks
  run, every dropped hunk printed) and all four landed in one `surgical_land` call, which is the
  door that gates the tree the commit would actually create. Landing `publish_cause.py` alone
  would genuinely have redded every lane: `CAUSES` would gain a name `PUBLISH_CAUSE_OVERRIDES`
  does not have, and the closed-set control asserts equality in both directions.
* **`tests/architecture/` and `tests/design/` cannot be graded in a `git archive` extract.** 51
  failed there — and 12 of the 12 I checked fail identically in a *pristine* extract with none of
  my changes, because the extract has no `.git` and those controls' subject is the repository.
  "Green in a clean extract" is unsatisfiable for that family; the landing gate is the only valid
  subject.
