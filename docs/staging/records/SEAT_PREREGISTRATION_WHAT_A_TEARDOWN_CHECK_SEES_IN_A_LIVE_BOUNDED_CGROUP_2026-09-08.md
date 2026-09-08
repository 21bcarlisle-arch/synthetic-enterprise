**Severity:** INFO · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what a teardown check sees in a live bounded cgroup

**Filed:** 2026-09-08, delivery seat (isolated worktree), **BEFORE the detector was run against
anything.** The design choice below turns on the answer, so the answer is written down before it
is known.

---

## The question

The drawn item asks whether a LAUNCH-TIME check is worth building for long jobs started from files
that are never committed — the half `tools/launch_shape_census.py` (landed 9af8c855e) structurally
cannot see, and the half that caused **4 of 4** deaths.

Two shapes are available and only one can be right:

* **SWEEP** — a periodic check in `deadmans_switch`, next to `_check_launch_liveness`, that
  enumerates the cgroups of the bounded units and reports strays. Catches a stray *while it is
  still alive*, so it could in principle warn before the kill.
* **IN-PATH** — a check at the last moment of the bounded unit's own process, in the `finally`
  that already exists in `worker_tick.run_tick()` and `seat_executor.run_once()`. Cannot warn
  early; it reports at the instant of death.

SWEEP is strictly more useful **if and only if** a bounded unit's cgroup is quiet enough between
teardowns for a stray to stand out. If a live bounded cgroup normally holds several legitimate
processes, SWEEP needs an allowlist or an age threshold — a tuned number about the subject — and
IN-PATH needs neither, because at the exit point everything legitimate has already exited *by
construction* (both units block on their child before returning).

## Predictions

**P1.** `worker-tick.service`'s `cgroup.procs` right now holds either **0** processes (unit
inactive between ticks) or **2+** (the tick plus the `claude -p` it blocks on). It will not hold
exactly 1 for long, because a tick with no work exits in under a second.

**P2 — the one that decides the design.** Reading `seat-executor.service`'s `cgroup.procs` right
now, mid-turn, reports **at least 2** live non-zombie processes that are not the reader
(the `background.seat_executor` python3, and the `claude` it is waiting on).

**If P2 holds, SWEEP is refused**: a sweep over a live bounded cgroup sees legitimate work in every
sample and would need an allowlist or an age cutoff to say anything, and both are tuned numbers
that get silenced. IN-PATH is then the only shape whose discriminator is free — *"I am about to
return and something else is still here"* needs no threshold at all.

**If P2 is refuted** (a live bounded cgroup is normally quiet), SWEEP is the better build, because
it can warn while the job can still be saved, and this pre-registration says so in advance.

**P3.** The check, wired into the `finally` of a tick that ran normally, reports **0** doomed
processes — i.e. it does not fire on the ordinary path. A control that fired every tick would be
silenced within a day.

## What would refute the whole build

If a bounded unit's cgroup at exit *routinely* holds a legitimate straggler — a child mid-exit not
yet reaped — then the check is a false-positive generator and the honest outcome is the recorded
refusal the drawn item explicitly permits. The double-sample settle described in the module exists
for exactly this race; if it does not suppress it, the refusal is the answer.
