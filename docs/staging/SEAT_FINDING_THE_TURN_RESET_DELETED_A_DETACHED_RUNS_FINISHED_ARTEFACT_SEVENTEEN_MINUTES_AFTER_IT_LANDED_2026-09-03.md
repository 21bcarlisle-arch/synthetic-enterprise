**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The turn reset deleted a detached run's finished artefact seventeen minutes after it landed

**Class:** `uncommitted_and_orphaned_work` (primary), `controls_that_cannot_fail` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`land-the-live-world-undecomposed-floor-leg`
**Subject:** `background/seat_executor.py::ensure_worktree` — the `git reset --hard` / `git clean
-qfd` pair, and the docstring sentence that licensed it.

## What was found

The Lane 0 doorbell drew this turn to "land `value_cycle_ab_s1_noise_floor_20260903.json` out of
the isolated worktree it finished in — the only thing standing between this and done is a `git
add`." The file does not exist. Not at the cited path, not anywhere: `find / -xdev` returns
nothing, and it is in no commit and no git object in either tree.

**The doorbell was not wrong when it was written.** It cites `generated 2026-09-03T14:18:37Z`,
`world_identity.digest 39a192ce04c1eda8`, and a stdev of `5,923.0446` — four decimal places. The
file existed and was read. Then it was destroyed.

> **Correction, 2026-09-03 17:12 BST, beside the claim it corrects.** As first written, the
> sentence above continued: *"The journal only ever printed `sd 5,923.04`, so the fourth decimal
> could only have been read out of the JSON."* **That inference is false and is withdrawn.**
> `5923.0446166138645` is also the stdev of `value_cycle_ab_s1_noise_floor_only_20260903.json`,
> which was never deleted and is on disk right now — so the fourth decimal could have been read
> out of the surviving `only` leg, and the precision establishes nothing about which leg was
> opened. The claim was checkable and nobody opened the other file to check it.
>
> **The conclusion survives, on better evidence that was available the whole time.** The unit
> journal for `se-noise-floor-all-20260903b.service` ends, at 15:18:37, with `redraw mode all`,
> the three seed rows, `sd 5,923.04 range 10,983.77`, `DISTINGUISHABLE FROM ZERO? NO`, and the
> producer's own last line: `wrote docs/observability/value_cycle_ab_s1_noise_floor_20260903.json`.
> `main()` writes before it prints, so the write is attested by the printout that follows it. The
> run succeeded and the artefact existed; only the argument for it was wrong.
>
> Recording this because the withdrawn sentence is the recurring shape, not a slip: a citation
> that reasons from a figure's *precision* to the *identity of the file it came from* has made a
> checkable claim about a second file, and here the second file was one directory away.

## The timeline, from the worktree's own reflog and the unit journal

| Local (BST) | Event |
|---|---|
| 12:53:25 | `se-noise-floor-all-20260903b.service` starts — a detached `systemd-run --user` unit |
| 15:14:18 | last `SALVAGE(auto)` commit `4277ed606` — artefact not yet written, so it misses it |
| **15:18:37** | run **succeeds**, prints the full result, writes the artefact. Untracked. |
| **15:35:25** | `reset: moving to 1df22e3bd` — `ensure_worktree`: `reset --hard` then `clean -qfd`. **Gone.** |
| 15:43:46 | `surgical-land` → `758520190` |

Seventeen minutes of life, between one salvage and the next turn's reset. The unit consumed
`1h 51min CPU over 2h 25min wall, 6.8G memory peak` to produce it.

## The false premise, quoted

`ensure_worktree`'s docstring justified the destruction outright:

> RESET, not merge: this worktree holds no history worth keeping between turns. […] **anything it
> did not land was not finished** — carrying that forward would hand the next turn a tree it did
> not build.

That is true of a turn's scratch and **false of a detached background job**, which is the one
thing here deliberately built to outlive the turn that launched it. `systemd-run --user` is the
*sanctioned* way to run a measurement longer than a bounded invocation — it is in the seat's own
learned practice precisely because a job launched from a bounded tick otherwise dies with the
cgroup. The two mechanisms are in direct contradiction: one exists so a long run survives its
turn, the other assumes anything untracked at turn start is abandoned. Nothing connected them.

## Why this is the THIRD cause of one absence, and the one both fixes missed

The same missing file has now had three distinct causes in a day:

1. **OOM kill** (`3ae262976`) — the leg died at 90 minutes and wrote nothing.
2. **Headroom refusal** — the fix for (1) `return 2`s without writing at `--out`, so a refusal
   looks identical to a run in progress. Filed as
   `SEAT_FINDING_THE_OOM_FIX_REMOVED_ONE_CAUSE_OF_THE_ABSENT_ARTEFACT_AND_LEFT_THE_ABSENCE`.
3. **This** — the run *succeeded*, printed its answer, and the tree ate it.

Both earlier fixes are still correct and **neither could have caught this one**, because both are
about a run that fails to produce. This one produced. That is what makes it worth a separate
finding rather than another instance of the second.

And the harm is identical in all three, which is the point: `clean -qfd` is silent, so the only
trace is an absent `--out` path — **and an absent artefact is exactly what a run still in progress
looks like.** The next session concludes the leg is still going and waits, or relaunches and loses
another 2h25m. That is not hypothetical here: it is what this turn's doorbell told this turn to do.

## The fix, and what it deliberately does not do

`ensure_worktree` now calls `fork_salvage.salvage_worktree` **before** the reset. That module
already existed for exactly this class ("make the bounded-invocation kill non-lossy"), is
fail-safe, never raises, and commits untracked work to the worktree's own HEAD — which is how the
15:14:18 salvage commit was still recoverable from the reflog after this same reset destroyed
everything around it.

It does **not** stop cleaning the working tree. Scratch discipline is right and the reset stays;
the difference is that scratch is now discarded *into an object that can be dug back out* instead
of into nothing. The control keys to that property — recoverability — not to today's
implementation, so swapping the preservation route keeps it green and deleting it turns it red.

`tests/background/test_a_detached_runs_artefact_survives_the_turn_reset.py`, two legs, real git
rather than a mock (the defect *is* git's behaviour: `clean -qfd` deletes what `reset --hard`
leaves alone, so a stubbed subprocess could not reproduce it). **Mutation-proven:** removing the
`salvage_worktree(...)` line reddens the recoverability leg and leaves the still-reset leg green,
so the two legs are not one assertion twice, and the salvage is not an equivalence.

## What is NOT done in this bounded tick

The measurement itself is **relaunched, not recovered** — the bytes are unrecoverable, so there
was no honest alternative to spending the 2h25m again. Reconstructing the JSON from the journal's
2-decimal console output would have been manufacturing an artefact to fill a slot, which is the
shape this project has a standing rule against.

`se-floor-all-20260903c.service` is running now, pinned to `1d821e12b` (the commit whose world
produced the matching `only`/`except` legs), with `--out
/var/tmp/se-floor-artefacts/value_cycle_ab_s1_noise_floor_20260903.json` — **outside every git
worktree**, so no reset or clean can reach it regardless of whether the fix above holds.

Consequently the doorbell's items (a)–(d) are **not** discharged and should be re-offered once the
leg lands: grading `P4`/`P6`/`P7` in the pre-registration, re-running `--decompose`, confirming
`_current_world_contrast`, and updating the `/capabilities/` headline all need the number this
finding explains the absence of. The pre-registered predictions are unaffected — they were filed
before the first run and the journal's `sd 5,923.04` / `DISTINGUISHABLE FROM ZERO? NO` are
consistent with them, but a console line is not the artefact and grading is deferred to the rerun
rather than done off a printout.
