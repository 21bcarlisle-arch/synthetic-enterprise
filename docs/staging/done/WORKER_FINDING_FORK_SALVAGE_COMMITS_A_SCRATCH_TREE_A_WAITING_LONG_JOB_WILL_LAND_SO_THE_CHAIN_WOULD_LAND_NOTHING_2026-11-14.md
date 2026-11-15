**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`

# Worker finding: fork_salvage commits a scratch tree that a waiting long job will land, so the chain would land nothing

**Observed 2026-11-14 ~12:00Z, worker tick.** `longjob-land-seat-executor-pair` waits on vt pid 1875257 and
then runs `/var/tmp/se-land-chain/run.sh`. That script lands the re-applied work held as **uncommitted
changes** in `/var/tmp/se-cp-ZC01` and `/var/tmp/se-cp2-fyWj`. At 11:56:46Z `background/fork_salvage.py`
(worker-tick `ExecStopPost`) committed both trees as `SALVAGE(auto)` (d4e0c772d0, 0fc4054787).
`_is_a_live_writers_worktree` saw no live process, because the only owner is a long job *waiting
elsewhere*. The chain's first step was `git checkout --detach origin/main`. On a now-clean tree that
step drops the salvage commit, and `surgical_land` would then have nothing to land. The chain would have
failed silently or confusingly at ~13:30Z.

**Instance fixed (reversible):** `run.sh` now carries any `SALVAGE(auto)` HEAD forward with
`cherry-pick --no-commit` + `reset -q` onto fresh origin/main. It refuses with a named reason (rc 92 doesn't
apply, rc 93 nothing to land). Dry-run in throwaway worktrees: 6 and 3 paths, as the pathspecs name. Backup
`run.sh.bak-*`.

**Class (open):** salvage's liveness question is "is a process IN this tree". It does not ask "is a
pending job going to act ON this tree". Candidate one-leg fix: `launch_long_job` records the worktrees its
command names, and `worktree_is_live` treats them as live while the unit is active. Alternative: salvage
leaves `/var/tmp/se-*` scratch trees that a longjob unit references. Not built: commit gates are refused
until the vt run ends (WORKER_FINDING_A_LONG_JOB_WAITING_ON_ANOTHER_PID_..._2026-11-14.md).

## Class fixed: the first candidate, built (worker tick, 15 Nov 2026)

The one-leg fix landed, as written above. `launch_long_job --holds WORKTREE` (repeatable) writes `holds` on the
launch record. `seat_executor.worktree_is_live` now has a leg 3, `_held_by_a_live_long_job`. It reads a tree as live
while a `live` record names it in `holds` **and that record's unit is still held**. The claim is keyed to the unit,
not to the record, because records still read `live` weeks after their unit ended (the October rows). Salvage and the
reaper both come through this door, so both now respect the claim.

**Not automatic.** A job's command does not reveal the trees it touches: here they were named inside `run.sh`. So the
launcher has to declare them. A chain that forgets `--holds` is exposed exactly as before. Its own
cherry-pick carry-forward (the instance fix) is still its backstop.

Test: `tests/background/test_a_tree_a_waiting_long_job_will_land_is_not_salvaged.py`, covering both sides of the
partition on one tree. Two mutations were run: dropping the unit-held clause and removing the leg. Each one turns the
tests red.
