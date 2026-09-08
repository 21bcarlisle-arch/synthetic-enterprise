**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the uncommitted half of the launch hazard is closed, and the sweep was refused by a measurement rather than a preference

**Filed:** 2026-09-08, delivery seat (isolated worktree).
**Drawn item:** *the-uncommitted-half-of-the-launch-hazard-is-the-half-that-killed-everything*.

---

## The premise, re-measured at draw time

The item cites `9af8c855e`. `git merge-base --is-ancestor 9af8c855e origin/main` → **yes**, already
an ancestor. That commit landed `tools/launch_shape_census.py` (floor 9 sightings / 6 rows, sixth
`pre_commit_test_gate` `CONTROL_TESTS` entry).

**The premise is NOT spent.** What landed is the census of *committed* launch shapes. The question
the item actually asks — *is a launch-time check worth building for the uncommitted half* — was
untouched, and `grep -rln launch_long_job` still named only the launcher, its callers and their
tests. That is the work, and this is the decision.

## The decision: BUILD, and the refusal the item offered is declined

The item is explicit that a recorded refusal naming *"a control that watches a control"* would be a
perfectly good outcome. **It is not the right one here, and the reason is a fact rather than a
preference:** the two controls have **disjoint populations and neither can see the other's**.

| | population | visible to |
|---|---|---|
| `tools/launch_shape_census.py` | launch shapes in `git ls-files` | the TREE |
| `background/doomed_at_teardown.py` | processes in a bounded unit's cgroup at exit | the RUNTIME |

A `/var/tmp/*.sh` that is never committed is invisible to the first **by construction**, and that
population is not a hypothetical: it is **4 of the 4 deaths** that motivated the one-launcher work.
The census would have caught none of them at the time. CLAUDE.md's warning is about a control
guarding *your own controls*; this one guards the machine, and the overlap between the two is empty.

The counter-argument in the item — that retiring the five throwaway scripts moved the work into
committed modules where the census can see it — is true and does not close it. The **generator** of
the hazard is a seat writing a shell script to `/var/tmp`, which is structurally never committed and
is still available to every session, including this one, today.

## What was built

`background/doomed_at_teardown.py`, wired into the `finally` of `worker_tick.run_tick()` and the
`--once` branch of `seat_executor.main()` — the two `Type=oneshot` units whose teardown does the
killing.

The rule is the whole rule, and it needs no tuned number:

> anything in my cgroup, when I am about to return, that is not me, is about to be SIGKILLed

That works because both units already **block** on the child they legitimately spawned, so at the
exit point everything legitimate has already gone.

## PRE-REGISTERED, and the prediction decided the design

`docs/staging/records/SEAT_PREREGISTRATION_WHAT_A_TEARDOWN_CHECK_SEES_IN_A_LIVE_BOUNDED_CGROUP_2026-09-08.md`
was filed **before the detector was run against anything**, because two shapes were available and
the choice turned on an unmeasured number. It said: if a live bounded cgroup normally holds several
legitimate processes, a periodic **SWEEP** (next to `deadmans_switch._check_launch_liveness`) needs
an allow-list or an age cutoff — a tuned number that gets silenced — and **IN-PATH** wins. If a live
bounded cgroup is normally quiet, SWEEP is the better build because it could warn while the job can
still be saved.

Measured immediately after:

| | prediction | measured | verdict |
|---|---|---|---|
| **P1** `worker-tick.service` cgroup | 0, or 2+ | **2** (tick + `claude -p`) | held |
| **P2** `seat-executor.service` mid-turn | ≥2 live non-zombie | **3** (`seat_executor`, `claude`, a bash child) | held |
| **P3** ordinary path reports nothing | 0 doomed | **0** — silent on a clean cgroup | held |

**P2 holding is what refused the sweep.** A sweep over a live bounded cgroup sees legitimate work in
every sample. The design was chosen by a reading, and the reading could have gone the other way.

## Printed at real inputs before shipping the formula

In a real fresh cgroup (`systemd-run --user --scope`), not a fixture:

```
my cgroup: 0::/user.slice/…/app.slice/doomed-demo-1393043.scope
BEFORE any stray: (silent - clean)
AFTER launching a setsid'd long job:
DOOMED-AT-TEARDOWN: 1 process(es) in this bounded unit's cgroup will be SIGKILLed when it
returns -- launch long jobs via background/launch_long_job.py: 1393065 (/bin/sleep 300)
```

`start_new_session=True` is the exact shape of all four deaths. Both verdicts reachable on the real
machine.

## THE LIMIT, on the surface and not in a footnote

**This reports; it does not rescue.** By the time the `finally` runs, the kill is milliseconds away
and nothing can adopt a process out of a doomed cgroup. It cannot refuse the launch, and no shape
available here can — the file is never in the tree and there is no import hook over `bash
/var/tmp/x.sh`.

What it buys is precisely what was missing: the launcher's own docstring says *"invisible is the
state that cost four launches"*, and each of those deaths was found hours later by a person going to
look. This turns a silent disappearance into a named line carrying the doomed job's own command
line, at the instant it happens. **That is a smaller claim than a refusal and it is the honest one.**

Second limit: it covers the two bounded oneshots. A long job launched from a unit nobody has wired
is still invisible, and `test_both_wired_units_are_oneshot_control_group_killers` is keyed to the
property — if either unit stops being a `Type=oneshot` control-group killer, the control goes red
rather than becoming decoration.

## Evidence

* `tests/background/test_doomed_at_teardown.py` — 11 controls.
* **Poison round FIRST** (`doomed()` pinned to return nothing): 3 red, so the suite reaches the
  subject. *Survived* means two opposite things and the ambiguity was removed before the battery.
* **9 mutations written, 9 killed, 0 survived** — including both unwirings (the `worker_tick`
  `finally` and the `seat_executor` `--once` call), the self-exclusion, the settle intersection,
  the zombie filter, and the unreadable-renders-as-clean fail-open.
* `test_all_three_verdicts_are_reachable` asserts the whole partition in one control — clean, found,
  and *not checked* — rather than a leg per branch, which is the shape that lets a detector refusing
  everything pass every test.

## Found on the way, and filed separately

`SEAT_FINDING_THE_ONE_CONTROL_GUARDING_THE_UNATTENDED_WRITER_WAS_FAIL_OPEN_AGAINST_ITS_OWN_DOCUMENTED_MUTATION_2026-09-08.md`
— BLOCKING. `test_the_only_thing_that_invokes_it_is_the_declared_schedule` was **red at HEAD**
(proven in a clean extract) because it read `launch_long_job.py`'s prose as an invocation, **and**
fail-open against the argv-list `subprocess.run` its own docstring offered as its mutation proof.
Both are one class — substring matching cannot tell code from prose — and both are fixed by reading
Python as an AST. 5 further mutations, 5 killed.
