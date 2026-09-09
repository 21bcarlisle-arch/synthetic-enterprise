**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — resolve the selection leg by seeds) · **Class:** controls_that_cannot_fail

# A stamp's refusal is keyed to the artefact, so a run that died before writing one leaves the stamp looking free

**Found 2026-09-09 by launching the nine-seed floor under stamp `20260909b` and then reading the
log it appended to.**

## What happened

`tools/run_arms_rerun.plan()` refuses a stamp that already has artefacts, and the docstring names
the defect precisely: *"a re-run under the same stamp leaves a floor from one clock beside a
contrast from another."* It fired correctly here — `value_cycle_ab_s1_noise_floor_20260909b.json`
did not exist, so the stamp was free and the launch went through.

It was not free. `docs/observability/arms_rerun_20260909b.log` already held **77,361 lines** from an
earlier run of the same stamp:

    line     2: START 2026-09-09T07:02:12Z stamp=20260909b legs=floor-all
    line 77361: ... progress: 7,518,600 settlement periods processed (latest: 2024-06-18 ...)
    line 77362: START 2026-09-09T09:04:58Z stamp=20260909b legs=floor-all seeds=11111,...,99999

No `FLOOR_ALL_RC=` line. No `DONE`. No artefact. That run reached mid-2024 in the settlement
walk — roughly two hours of compute — and then simply stopped mid-stream. There is no
`longjob-arms-rerun-20260909b` unit from 07:02Z and `background.launch_liveness --check` reports no
stale claim, so it was never handed to the one launcher: it was started inside a caller's own
cgroup and died at that caller's teardown, which is the class
`SEAT_FINDING_THE_PAIR_MOVE_PARTNER_WAS_HAND_LAUNCHED_INTO_THE_TICKS_OWN_CGROUP_AND_DIED_WITH_IT_LEAVING_NOTHING`
already names.

## Why this is a separate finding and not that one again

**The refusal that exists for exactly this hazard cannot fire in the case that produces it.** The
stamp guard reads the artefact; the failure mode it is guarding against — a run that dies — is
defined by there being no artefact. So the guard is green precisely when a stamp has already been
spent, and red only when it has been spent *successfully*. It is not fail-open by accident; it is
keyed to the wrong witness.

The evidence the stamp had been used was on disk the whole time, in the log the module itself opens
in append mode (`open(str(log), "a")`) and writes its own `START` line to.

## What it cost, and what it nearly cost

Two hours of compute, already spent, invisible. And the near-miss is worse than the loss: had the
07:02Z run still been *alive*, my launch would have been a second concurrent floor leg. The headroom
refusal in `run_value_cycle_ab.floor_run_headroom_refusal` would have caught that one (it counts
running legs by argv token and needs 6.4 GB × (legs + 1) against this guest's 13.5 GB available) —
so the machine was protected, but by a control in the other module, and only against the
*concurrent* case. Nothing anywhere protects against the *sequential* one, which is the one that
happened.

## What is next

A one-leg check inside `plan()`: if `log_path(stamp)` holds a `START` line with no matching `DONE`,
refuse and name the timestamp and the last line the dead run wrote. That is where the evidence
already is, it costs a `read_text` on a file the module already owns, and it needs no new register.

Deliberately **not** proposed: a watcher, a stamp ledger, or a second liveness store. The fact is in
the log; the guard just has to read it.

## What a reader of that log must know today

`docs/observability/arms_rerun_20260909b.log` is 8 MB and **two runs deep**. The live nine-seed run
starts at **line 77362**. Everything above it belongs to a dead run and reaches only 2024-06-18.
The two `START` lines are distinguishable only because `seeds=` was added to that line in
`c066c114b`, landed minutes before the launch — before that commit the two lines were byte-identical.
