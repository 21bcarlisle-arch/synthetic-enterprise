# [SEAT PRE-REGISTRATION] Is a live `longjob-*` unit with no launch record a class worth a control, or a single slip?

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, launch-register coverage
**Filed** 2026-09-10 by the delivery seat, **while `longjob-noise-floor-20260910.service` is still
running and roughly four hours from its artefact**, and therefore before the outcome that would
make any of this look obvious. Subject: `background/launch_liveness.py`, its register
`docs/observability/.launch_records.json`, and the Lane 0 pair-move item that instructs the next
executor to consult `--check` as its evidence the floor is alive.

Related: `docs/staging/SEAT_FINDING_THE_FLOORS_PIN_NAMED_THE_COMMIT_THAT_LANDED_THE_RUN_NOT_THE_ONE_THAT_PRODUCED_IT_2026-09-10.md`,
`docs/staging/records/SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME_AND_THE_KILLER_WAS_NEVER_THE_SESSION_IT_IS_THE_TICKS_CGROUP_2026-09-08.md`,
`docs/staging/WORKER_FINDING_REPEATING_ALARM_DEADMAN_LAUNCH_LIVENESS_DONE_2026-09-09.md`.

---

## 1. What is established by reading, and is NOT in question

Plain reads taken before a word below was written.

- `systemctl --user list-units 'longjob-*' --all` returns exactly **two** units, both
  `active running`: `longjob-arms-rerun-20260910b.service` and
  `longjob-noise-floor-20260910.service`.
- The live register — the **shared tree's working copy**, which is 108 lines beyond HEAD and is
  the copy the deadman actually reads — holds **10** records. One of them,
  `arms-rerun-20260910b`, claims `live`. **There is no record whose unit is
  `longjob-noise-floor-20260910`.**
- Its same-shaped predecessors ARE registered: `noise-floor-20260908b` and `noise-floor-20260909`
  both sit in the register, settled `finished`. So this is a break in an established practice, not
  the absence of one.
- `background/launch_long_job.py:312` calls `launch_liveness.record(...)`, under a docstring that
  says **"THE RECORD IS NOT A SEPARATE STEP, AND THAT IS THE POINT."** A job with a transient unit
  but no record was therefore launched around that door, by hand.
- `launch_liveness.check()` iterates the register and skips anything not claiming `live`. A job
  absent from the register is not graded, cannot be graded, and contributes nothing to the exit
  code.
- I ran `python3 -m background.launch_liveness --check` at 15:36Z. It printed
  `check: PASS (no stale liveness claim)`.

None of the above is a prediction. What follows is.

## 2. The question

The Lane 0 item tells the next executor, in its own words, to establish that the floor is alive by
running `background.launch_liveness --check`. That instrument cannot see the floor. The question is
whether that is worth a control, or whether the honest answer is "someone forgot once, register it
and move on".

## 3. Predictions, written before the control exists

**P1 — the PASS is not merely vacuous, it is positively misleading.** I predict the PASS at 15:36Z
was a TRUE statement about `arms-rerun-20260910b` — a *different* nine-seed floor job, launched the
same day, carrying a near-identical name. If that is right, a reader who follows the item's
instruction gets a green that is about somebody else's job, which is worse than an empty answer: an
empty answer prompts a second question and a green does not.

**P2 — the control has a real subject on both sides today, so it needs nothing fabricated.** I
predict a check of the form "every live `longjob-*` unit has a `live` record" fires on exactly one
of the two units now running and stays silent on the other. If it fires on both, or neither, the
rule is wrong and I will say so here rather than tune it until it agrees.

**P3 — registering the floor does NOT arm a false unlanded alarm.** The floor writes to
`/var/tmp/se-floorrun-20260910/...`, outside the repo. I predict `landing_verdict()` returns
`OUTSIDE`, and `landed_check()` counts **0** refusals from it, because only `UNTRACKED` and
`UNREADABLE` refuse. If registering would page the director for a job that is behaving correctly,
that is the module's own already-made "crying wolf" mistake and I abandon the repair.

**P4 — the record must carry the ABSOLUTE artefact path.** `reask()` resolves a relative artefact
against the *repo*, but this job's cwd is the floorrun worktree, so `docs/observability/...` names
a different file. I predict that registering the relative path would make a successful run grade as
`UNKNOWN`/`DIED`. This is a prediction about the shape of the record I am about to write, and I am
writing it down because getting it wrong would produce a register entry that looks right and reads
false.

**P5 — what will NOT move.** I predict this changes no published figure and no site byte. The pair
move itself is blocked on an artefact that does not exist yet; nothing here advances it. If a
site-data byte moves, I have done something other than what I described.

## 4. What would refute the whole frame

If `launch_long_job` has a sanctioned path for a job that supplies its own unit, and this floor took
it, then the register gap is designed and the control I am proposing would fire on correct
behaviour. I check that before writing the control, not after.

## 5. What this does not settle

Nothing here says the floor will finish, or that the pair move is right. The floor is roughly four
hours out at the time of writing and this document is deliberately filed while its outcome is
unknown.
