# [SEAT FINDING] The launch register guards its door and nothing guarded the wall beside it, so the floor this lane waits on ran invisible

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, launch-register coverage
**Filed** 2026-09-10 by the delivery seat, while `longjob-noise-floor-20260910.service` is still
running and roughly four hours from its artefact.

Pre-registration, written before the control existed and before any of the measurements below:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_LIVE_UNIT_WITH_NO_LAUNCH_RECORD_IS_A_CLASS_OR_A_SINGLE_SLIP_2026-09-10.md`.

---

## 1. What happened

The Lane 0 pair-move item tells the next executor, in its own words, to establish that the
nine-seed floor is alive by running `python3 -m background.launch_liveness --check`. I ran it at
15:36Z. It printed:

```
check: PASS (no stale liveness claim)
```

That instrument cannot see the floor and never could. `check()` iterates the register
(`docs/observability/.launch_records.json`) and re-asks every record claiming `live`. There was **no
record whose unit is `longjob-noise-floor-20260910`**. A job absent from the register is not a claim
to re-ask, so it contributes nothing to the verdict and nothing to the exit code.

**The PASS was not empty. It was true about a different job.** The live register held exactly one
`live` record — `arms-rerun-20260910b`, a *second* nine-seed floor launched the same day, under a
near-identical name, still running. The check looked at that, found it healthy, and said PASS. A
green about somebody else's job does not prompt the second question an empty answer would.

## 2. The class, which is bigger than the instance

`background/launch_long_job.py` will **stop a healthy long run** rather than leave it unrecorded.
Its docstring is unambiguous — *"AND A JOB WHOSE RECORD COULD NOT BE WRITTEN IS STOPPED… The state
this module exists to abolish is 'running and unrecorded'… it is the state that let the floor leg
run unrecorded for 35 minutes."* It pays a killed job to abolish that state.

That guards the **door**. Nothing guarded the **wall beside it**. A job started with `systemd-run`
by hand gets a real transient unit, a real cgroup, a real log and a real description — this one's
unit description even names its pin, *"nine-seed undecomposed noise floor over the book of
value_cycle_ab_s1_three_arm_20260910.json at commit 4e7938f67"* — and is invisible to the register
forever. It is indistinguishable from a launch that went through the door in every respect except
the one that matters.

This was a break in an established practice, not the absence of one: the same-shaped
`noise-floor-20260908b` and `noise-floor-20260909` are both in the register.

**The launch mechanics were otherwise correct, and I record that because I expected otherwise.**
PID 1072649 is a session leader in its own transient unit under `app.slice`, parent systemd, not a
tick's cgroup. The cgroup death that killed four earlier launches of this job class does not apply
here. The hard part was done by hand correctly; the cheap part was skipped, and the cheap part is
the entire reason a later reader can ask what became of it.

## 3. What the pre-registration predicted, and what actually happened

**P1 — the PASS is positively misleading, not merely vacuous. CONFIRMED.** The 15:36Z PASS was a
true statement about `arms-rerun-20260910b`.

**P2 — the control has a real subject on both sides today. CONFIRMED, exactly.** Of the two live
`longjob-*` units, the new check fires on `longjob-noise-floor-20260910.service` and stays silent on
`longjob-arms-rerun-20260910b.service`. One real positive and one real negative on the real machine,
with nothing fabricated and no fixture tuned until it agreed.

**P3 — registering the floor does not arm a false alarm. SUBSTANCE CONFIRMED, MY NUMBER WAS WRONG,
and the error found something.** I predicted `landed_check()` would count **0** refusals. It counts
**1**. My record grades `OUTSIDE` as predicted and refuses nothing — that part holds. But the
refusal that was already there belongs to `value-cycle-ab-20260910`, and it says the run artefact
`docs/observability/value_cycle_ab_s1_three_arm_20260910.json` *"is in no commit and not even
staged"*. **That refusal is a false alarm, and its cause is §5.**

**P4 — the record must carry the ABSOLUTE artefact path. CONFIRMED and acted on.** The job's cwd is
the floorrun worktree, not the repo, so a repo-relative artefact would name a different file and a
successful run would grade `UNKNOWN`. The record I wrote carries the absolute path.

**P5 — nothing published moves. CONFIRMED.** No site byte, no figure.

## 4. What was done

**The mechanism** (`background/launch_liveness.py`): `live_units()` and
`unregistered_live_units()`, plus a `--unregistered` leg that refuses, and a `--check` that no
longer claims coverage it does not have. The rule is keyed to the property — *every running
`longjob-*` unit is covered by a record claiming it live* — not to today's answer, so it goes green
when the practice is followed and red when it is not, rather than the other way round.

It fails closed: a probe that cannot be run returns `UNREADABLE` and **refuses**, because reporting
full coverage because we could not look would make it worse than nothing. `live_units()` returns
`None` rather than `[]` for a broken probe, since "nothing is running" and "we could not look" are
opposite claims that must not share a value.

`--check` reports the gap but does **not** refuse on it: `deadmans_switch._check_launch_liveness`
calls `check()` directly, and a new refusal on that path would page the director for a state no lane
can clear mid-run — the module's own already-made "crying wolf" mistake. `--unregistered` is the leg
with teeth.

**Mutation-proven, three poisons, three precise reds:** making the coverage rule never refuse reds
the three coverage tests; making the broken probe return `[]` reds the fail-closed test; restoring
the bare `PASS` reds the test that names this instance. Restored, all 33 green.

**The operational repair.** `noise-floor-20260910` is now registered in the live register with its
real launch time (14:50:22Z, from `ps`, not the moment I got round to it). `--check` now grades it:
`RUNNING -- the user manager reports longjob-noise-floor-20260910 ActiveState=active`. The Lane 0
item's stated instruction is now a true instruction. If the floor dies, the deadman will page, and
the two documents naming it as in flight will be contradicted by a file.

## 5. The thing I was not looking for: the shared tree has diverged

`landed_check()`'s refusal against `value-cycle-ab-20260910` sent me to check the run artefact.

- In **origin/main** (`7c85967cf`), `docs/observability/value_cycle_ab_s1_three_arm_20260910.json`
  **is in HEAD**, landed by `4e7938f67`.
- In the **shared tree** (`/home/rich/synthetic-enterprise`, HEAD `4b3d531bc`) it is **not in HEAD**
  — it sits untracked on disk.
- The two have **diverged**: 6 commits on the shared tree that origin/main does not have, and **11
  commits on origin/main that the shared tree does not have**.

So the `UNTRACKED` refusal is a **tree divergence rendering as stranded work**. The register says
the job is done and git — *that* git — says the file does not exist, and both are right about
different trees. This is the known repeating tree-divergence condition, not a new incident, and
`se-origin-reconcile` exists for it; I did not attempt a merge.

**This matters directly to the pair move, and it is the load-bearing sentence for whoever does it.**
The floor worktree is pinned to `4e7938f67`, which is in origin/main and *not* in the shared tree's
HEAD. The pair move must therefore be done from a worktree on **origin/main** — from the shared tree
the source artefact is not even in HEAD, and `tools.generate_value_arms_data` would run a producer
11 commits behind the one that made the run.

## 6. What this does NOT settle

The pair move itself is untouched and still blocked on an artefact that does not exist. Re-measured
this turn and the premise **stands, unspent**: published floor `2026-09-09T15:17:31Z` is older than
the candidate run `2026-09-10T14:04:08Z`, so moving the run alone still empties `contrast_bounds`
(live: `available: true`, 9 seeds, `staleness_caveat: null`). The live feed still carries no
`belief_against_control_outcomes` key. `same_tree` is already `false` on the live page, as the item
says to expect.

Nothing here says the floor will finish. It is roughly four hours out at the time of writing, and
this document was filed while that was still unknown.

The floor still carries **no book-identity stamp** — owed work, unchanged, see
`SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`.
