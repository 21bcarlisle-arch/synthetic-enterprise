**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the remaining long-job launches go through the one launcher)

# RESULT — the last two hand-rolled long-job launches are retired, and one of them never launched anything

Discharges the Lane 0 item `the-remaining-long-job-launches-go-through-the-one-launcher`, which
followed `SEAT_RESULT_THE_LAUNCH_AND_ITS_RECORD_ARE_NOW_ONE_CALL_...2026-09-08.md`: the launcher
landed with one real caller, and the two sites that taught the lesson were still hand-rolling it.

**Falsifiers:**
`tests/tools/test_run_arms_rerun.py::test_the_launch_goes_through_the_one_launcher_and_re_enters_this_module`,
`tests/tools/test_run_arms_rerun.py::test_a_failed_leg_skips_its_dependants_and_only_its_dependants`,
`tests/tools/test_run_arms_rerun.py::test_a_decomposed_floor_without_its_roster_is_refused_but_with_one_is_not`,
`tests/tools/test_measure_publish_gate_subject_cost.py::test_the_launch_goes_through_the_one_launcher_and_starts_the_measurement`,
`tests/tools/test_measure_publish_gate_subject_cost.py::test_the_detach_fallback_is_gone`.

## The premise, re-measured first

The item cited `0b3efd0a7` and `aa6573a19` and warned they were already ancestors of `origin/main`.
They are — but they are the LAUNCHER's own landing, not this work. Both hand-rolled sites were
still present and unchanged at draw time (`tools/run_arms_rerun_detached.sh` intact,
`_systemd_run_argv`/`_unit_is_active`/`_clear_a_failed_unit`/`_spawn_detached` all still private to
the measurement harness). The premise was live, not spent.

## What was found that the item did not say

**`tools/run_arms_rerun_detached.sh` did not detach. It did not launch at all.** The name says
`detached`; the file `cd`s to a hardcoded absolute path, runs two legs in the foreground, and
appends to a log. Every scrap of the detachment lived in a wrapper a human had to type —

    systemd-run --user --unit=arms-rerun-20260829 tools/run_arms_rerun_detached.sh

— and that line appears **in a preregistration document**, followed by the words *"with the stamp
changed"*. So the two things that decide whether an eight-hour run survives and lands where anyone
will look — the unit, and the stamp — were both instructions to the next reader. The file's own
header explains the cgroup death correctly and at length, and then cannot act on it, because a
script cannot wrap itself.

**And the stamp was a literal: `STAMP=20260829`.** Correct on exactly one day. By 2026-09-03 the
recorded procedure was to edit the script before running it.

**A defect in this turn's own first draft, caught by printing the launch argv before shipping it.**
`launch_long_job` points the unit's `StandardOutput` at the stamped log — so the draft's `record()`,
which wrote to the log *and* to stdout, put every `START`/`LEG`/`RC` line into that file twice and
put two writers on one file, losing the ordering the file exists for. It would have looked like a
cosmetic log wart and been read, eight hours later, as evidence a leg had restarted. Progress now
goes to the log only; stdout gets one line at each end naming where to look.
`::test_progress_goes_to_the_log_and_not_also_to_stdout` is mutation-proven — restoring the
`say(line)` call reds it — and asserts both directions, since printing nothing at all would pass a
one-legged version of it.

## What was built

**`tools/run_arms_rerun.py`** replaces the script. Same measurement — the default legs are the two
the script ran, at the same seeds — and three differences, each keyed to one of the above:

* `--launch` hands the whole session to `background.launch_long_job`. Transient user unit, both
  streams to one stamped log, and a liveness record `deadmans_switch` re-asks on a timer. A job
  whose record cannot be written is stopped rather than left running and invisible.
* `--stamp` is **required, with no default**. There is no value it could pick that would be right
  tomorrow, and a default would be silently stale rather than loudly absent.
* The leg set is sayable, and its dependency is a refusal. The decomposition needs four legs, and
  `floor-only`/`floor-except` cut the book along the roster the three-arm leg writes. `plan()`
  refuses before anything runs for eight hours if that roster is neither in the run nor on disk for
  this stamp — and refuses a stamp whose artefacts already exist, which is **P5 of the arms
  preregistration turned from a hope into a check**. It used to be a sentence asking the operator
  not to overwrite a leg in place.

**`tools/measure_publish_gate_subject_cost.py`** loses its private launcher:
`_systemd_run_argv`, `_unit_is_active`, `_clear_a_failed_unit`, `_spawn_detached`,
`_detached_popen` and the `--detach` flag are gone; `--systemd` now calls `launch_long_job`. This
is where the remedy was banked on 2026-08-29, bound to one unit name, which is exactly why it
helped nothing else. It gains what it never had: a liveness record, so a ~50-minute measurement
that dies is noticed by the deadman rather than by someone looking at a pid.

`--detach` is **deleted, not kept as a fallback.** It was the fourth death. It survives a
process-group kill and its record proved so (`is_session_leader: true`) — and it survives neither a
descendant walk nor a cgroup teardown, and it looks identical to a good launch for as long as it is
alive. A fallback that can only lose another 50 minutes is not a fallback.

## What moved rather than being deleted, and where it went

The controls this deletes are not fewer controls — but a reader who is not told will assume the
flattering answer, so: corpse-clearing, the fixed unit name, and "an unreadable `systemctl` reads
as HELD" now live in `tests/background/test_launch_long_job.py`
(`::test_a_corpse_is_cleared_but_a_live_unit_is_never_reset`,
`::test_an_unreadable_systemctl_refuses_rather_than_starting_a_second_copy`), against the one
launcher instead of a private copy. The descendant-walk differential has **no subject left** — its
helper is deleted — and its successor is stronger:
`::test_a_launch_that_lands_in_the_launchers_own_cgroup_is_stopped_and_never_recorded` asks the
cgroup question, which is the killer that actually took the fourth run.

`_measurement_is_running` deliberately did NOT move. A unit name refuses a second UNIT and says
nothing about an inline run someone started in a terminal, and two full suites do not fit in this
box — two OOM kills proved it.

## The new module is a frozen orphan, and here is the judgement

The orphan ratchet refused the first landing: nothing imports `tools.run_arms_rerun` and no
committed unit, timer or hook runs it. **That is correct and it is deliberate.** This is an
operator-invoked harness for an ~8-hour measurement the seat starts when it decides to grade the
arms preregistration — exactly what the shell script it replaces was, except that a `.sh` is not in
the module census, so the same dormancy was invisible. Wiring it to a timer would be worse than
dormant: it would start eight hours of compute on a schedule nobody asked for. So it is frozen with
`tools/orphan_ratchet.py --freeze` in the same commit, which is the ratchet's own named remedy for
"deliberately dormant" and puts the decision on the record rather than in someone's head.

**The freeze was taken safely, and that needed two steps this project has been burned by before.**
The module was `git add`-ed FIRST, because `freeze()` censuses `git ls-files` — an untracked module
is invisible to it, so freezing before staging would have silently omitted the very row being
added. And the worktree was fast-forwarded onto `origin/main` first (it was six commits behind),
because a baseline frozen from a stale tree carries that tree's reachability and wedges every lane.
The result was checked rather than assumed: the diff is **one row added, none removed**, module
count 1126 → 1127. No disposition-register row is needed — that register is enforced for
company-side orphans, and `--dispositions` passes; every sibling `tools/run_*.py` sits the same way.

## What is left, honestly

* **`background/worker_tick.py` is untouched, on purpose.** It blocks until its child exits, so
  that child is *supposed* to live inside the tick's cgroup. Launching it out of band would be the
  defect, not the fix. This was the item's own instruction and re-reading the code agrees with it.
* **The arms re-run has not been run.** This turn retired the launch, not the measurement; the four
  legs cost ~8 hours and the 2026-09-03 preregistration's predictions are still ungraded on the
  floor legs. The launch line in that record now names the new module.
* **No control asserts the module is the ONLY way a long job is launched.** A sixth throwaway
  script in `/var/tmp` would still work and still die. That is a census, not a wiring test, and it
  is the obvious next piece — but writing the register before the two known sites were retired
  would have been building the thing that watches the work instead of doing it.
