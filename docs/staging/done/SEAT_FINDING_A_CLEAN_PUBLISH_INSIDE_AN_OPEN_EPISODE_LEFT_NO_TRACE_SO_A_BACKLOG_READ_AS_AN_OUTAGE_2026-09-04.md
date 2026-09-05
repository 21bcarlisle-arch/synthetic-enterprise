**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

> **THE REPAIR LANDED. "NOT LANDED" BELOW IS STALE AND IS KEPT AS WRITTEN, 2026-09-04 16:15Z,
> delivery seat.** Both halves are on `origin/main`: the module change is in
> `background/process_run_complete.py` (`episode_clean_publishes`, `last_clean_publish`,
> `PUBLISH_GATE_STREAK_FIELDS`) and its control is the TRACKED file
> `tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py`.
> **Do not go looking for the hunks in the shared working tree — they are not there, because they
> were committed.** The section headed *"WHERE THE REPAIR IS — do not rebuild it"* now sends its
> reader to an empty `git diff` and reads as if the work were lost; it is not, and the deadline red
> that blocked it is itself discharged (that finding's own header records the control repointed,
> 732s of room rather than 57). Corrected here, at the place it is READ, because this file is the
> one a future seat opens.

# FINDING: a clean publish inside an open episode left no trace, so a backlog read as an outage

Filed 2026-09-04 by the delivery seat, working the Lane 0 direction *"the figures stopped reaching
the reader and no direction ever named the path"*.

## What the doorbell said, and what was actually true

The tick that drew this work opened on:

> The path has been down about four hours with eight completed runs queued, so every figure this
> stretch established — the arm's-reach correction included — is sitting in a commit no reader has
> seen.

**The path was not down.** `docs/observability/sim-runner-log.md` records `Publish gate recovered`
at 02:22Z, 05:20Z and **10:53Z**, and `background-worker-log.md` records
`Processed run_complete_20260904T084511Z.md` … `published (rc=0)` at 10:53Z, which also
`Drain-superseded 10/10 older run_complete marker(s)`. That is forty minutes before the doorbell
fired. A publisher was mid-gate on `run_complete_20260904T104410Z.md` while the tick was reading.

The doorbell's other stated wedge was equally stale. It named
`site/test_the_site_lane_runs_no_untracked_control.py` and told me to land
`site/harness/test_the_deployment_reading_reaches_the_reader.py` and `site/harness/_render_harness.mjs`;
`git ls-files` shows both already tracked. The live blocking test had moved to
`tests/background/test_publish_failure_names_its_cause.py::test_the_worker_log_does_not_pass_off_library_noise_as_a_diagnosis`,
which is **green at HEAD** — it was red at the stamped `git_hash` `3d369242c` and was fixed two
commits later by `e78e17581`. Proven both ways in clean `git archive` extracts: red at
`3d369242c`, green at `4d1d6298c`.

## The defect

`.publish_gate_state.json` read `wedge_since: 2026-09-04T05:57Z`, `episode_failures: 8`, and
`_episode_phrase` rendered exactly this to the director's phone:

    EPISODE: wedged since 2026-09-04T05:57 UTC -- 5h37m and 8 consecutive failures in THIS
    episode (not a fresh hour).

They were **not consecutive**. A clean publish sat among them.

**Nothing here was lying, and that is the point.** `record_publish_gate_success` preserves
`wedge_since`/`episode_failures` when markers are still pending, and that is correct and
load-bearing — PW2, 2026-08-09: a success that drains nothing may not close an episode, or a
10h26m outage pages as a fresh 14 minutes. The defect is that the state carried **no field for
"the gate passed inside this episode"**, so one sentence was doing duty for two different faults:

* **THE GATE CANNOT PASS** — fix the red.
* **THE GATE PASSES AND ITS QUEUE OUTRUNS IT** — a publish cycle takes ~45 min; the sim runner
  mints a marker every ~13 min (09:11, 09:24, 09:37, 09:51, 10:04, 10:17, 10:31, 10:44Z). So at
  every success instant there are ~3+ newer markers pending, `pending == 0` is never observed, and
  **the episode can structurally never close**. Fixing reds will never close this one.

This is the shape `CLAUDE.md` names as the project's most expensive recurring failure: a concept
nobody defined, then differenced and published and treated as a driver. *Average unit rate*, *net
margin*, *bill shock* — and now *"the publish path is down"*.

The same conflation had a second voice. `record_publish_gate_success` logged
`Publish gate recovered -- cleared wedge state, re-armed alarm` **unconditionally**, including on
the branch that had just declined to clear it. Same class as this pipeline's own `last 40 lines`
header printed over a selection: a small lie in a diagnostic costs the reader the one thing the
diagnostic is for.

## The repair — AUTHORED AND MUTATION-PROVEN, **NOT LANDED**

> **SUPERSEDED 2026-09-04 16:15Z: it LANDED, both halves, and is at `origin/main`.** The heading and
> the section under it are kept exactly as written, because a prediction kept beside its outcome is
> the evidence the work was described before it was known to have survived. Everything below about
> *where to find the uncommitted hunks* is now false — see the correction at the head of this file.

**Read this before believing the section below.** The code repair is written, green, and its five
mutations are each proven to red. It is **not in the tree**, because
`python3 -m tools.surgical_land` refused it — twice, and the second refusal is the real one:

    FAILED tests/background/test_process_run_complete.py::
      test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today
    1 failed, 655 passed in 343.89s
    [test-gate] ❌ TESTS FAILED -- COMMIT REFUSED.

That red is the boxed commit deadline, it is **pre-existing at HEAD and not caused by this change**,
and it sits in the blocking scope of any edit to `background/process_run_complete.py` — so it
refuses this repair and the publisher's own commits alike. It is documented in
`SEAT_FINDING_THE_COMMIT_DEADLINE_IS_BOXED_BETWEEN_TWO_CONTROLS_AND_THE_ROOM_IS_57_SECONDS_2026-09-04.md`,
raised to BLOCKING today. **The code below therefore describes what is authored, not what is
running.** Anything reading this file as a description of live behaviour is reading it wrong, which
is precisely the failure mode this whole finding is about.

(The first refusal was mine and is worth recording: I listed the root-room prereg copy as a
positional path to express its deletion. `surgical_land` positionals only ADD, so the deletion never
entered the candidate tree and `finding_classes --check` refused TWO ROOMS on a tree where my
working copy passed. A deletion needs `--content-remove REPOPATH`, **and** that path must still
appear in the positionals — a content override is still a landed change.)

### WHERE THE REPAIR IS — do not rebuild it

**It is sitting in the shared working tree, finished.** Look before you write anything:

* `background/process_run_complete.py` — uncommitted, 8 hunks, all this seat's. Re-applied
  three-way onto `6fa525ecb` after that merge brought in the other lane's `cause_evidence` work,
  so it is already rebased on the current base and does **not** revert their 30 lines
  (verified: their `cause_evidence` parameters survive, and both lanes' suites pass together —
  52 tests across `test_an_episode_held_open_...`, `test_a_publish_failure_names_which_of_the_three_it_was`
  and `test_publish_gate_alert`).
* `tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py` —
  **untracked.** These two go together or not at all: landing the module without this file lands
  the behaviour with none of its controls, which is the half-landed shape this project keeps
  paying for.

The only thing standing between it and the tree is the deadline red. When that is resolved, land
both paths in one commit; nothing else needs writing.

## The repair as authored

* `.publish_gate_state.json` gains `episode_clean_publishes` and `last_clean_publish`.
  The counter is a `PUBLISH_GATE_STREAK_FIELD`, so the `episode_monotonic` class guard (R10)
  stops a failure write forgetting it. The timestamp is LATEST-wins, which the guard's
  earliest-wins `since_fields` cannot express, so it is carried at the single choke-point in
  `_write_publish_gate_state`. Both clear only on an evidenced episode close.
* `_episode_phrase` gains the intermittent branch, which names THROUGHPUT and says fixing a red
  will not close it. **The unbroken-outage branch is unchanged and still says "consecutive"** —
  that is the null control, so "delete the word everywhere" goes red.
* The recovery log line now names which branch it took and how many markers are still pending.

Controls: `tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py`,
7 tests, five mutations each proven to red by reverting the fix.

**Two mutations first SURVIVED and the reason is recorded rather than quietly fixed.** The failure
write also passed both fields explicitly, duplicating the two real mechanisms — so deleting either
real mechanism left all seven controls green. Not a missing test: an equivalence, and one that
made both safeguards unprovable. The duplicate is gone and each mechanism is now the only thing
holding its field, which is what makes those two mutations fire at all.

## Owed next — NOT done here, and not mine to close silently

**The throughput fault itself is untouched.** This finding makes the two states distinguishable;
it does not make the queue drain. The open question is which lever is right — a longer marker
cadence, a faster gate cycle, or a sweep that publishes the newest marker and retires the rest
without a full cycle each. That is a judgement about what the site is for, and it wants the
measurement first: gate cycle duration against marker interarrival, over a week, not over the one
morning quoted above.

**A second, separate red is live at HEAD and is NOT mine:**
`tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`
fails on `.seat_continuation.json` and `.weekly_rhythm.json` — undispositioned hits in
`docs/design/self_clearing_alarm_dispositions.json`. Proven pre-existing in a clean
`git archive HEAD` extract, byte-identical failure, before any edit of mine. `.weekly_rhythm.json`
arrived with `4d1d6298c` (today): `weekly_rhythm.tick()` bootstraps a **fresh `due_on`** whenever
`read_baton` returns `None`, and `read_baton` returns `None` for an unreadable or unrecognised
baton — so a truncated state file resets the lateness clock that the FINDING branch reads for
`days_late`. That reads as `real`, not `benign`, and a `real` row needs a guard plus a test
citation that exists on disk. I have deliberately **not** dispositioned it: marking another lane's
control `benign` to unblock my own commit is precisely the fail-open this census exists to refuse.
It belongs to the lane that landed `weekly_rhythm.py`, and it is stated here so it is not invisible.

## Class registration

Belongs to `publish_gate_and_wedge`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 12 matches for `publish_gate_and_wedge` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
