**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-level-selection-retake-died-twice-and-its-own-correction-asserts-it-live`)

**Knowledge:** none new. This lands a harness mechanism and scores a preregistration; no domain
constant moves.

# FINDING — the liveness mechanism was built, and nothing at HEAD carried it

Beside `SEAT_PREREGISTRATION_WHAT_A_LIVENESS_RE_ASK_MUST_CATCH_AND_WHAT_IT_WILL_FLOOD_ON_2026-09-08.md`
(written before any of this was measured, and unedited),
`SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME…_2026-09-08.md` and
`SEAT_RESULT_THE_CURRENT_BOOK_RETAKE_LANDED_AND_ITS_SPLIT_IS_STILL_UNREADABLE_2026-09-08.md`.
All stand; none is edited.

## Both halves of the drawn item were already answered, and one of the answers was invisible

The item asks for two things. Neither needed doing again, and finding that out was most of the work.

**Half one — the artefact.** The item says *"two launches, two silent deaths, no artefact at any
path"*. There is an artefact: `/var/tmp/value_cycle_ab_current_book_2026-09-08.json`, `rc=0`,
`Result=success`, produced by `04361d6c7`. The stall the item points at — the run ending on
*"legacy provider — no weather archive for this customer's location"* — was never a stall in that
code path at all. Those lines are the ordinary premise enumeration, and the log ends there because
the process was killed mid-enumeration by the tick's cgroup. The diagnosis was filed at 00:35 and
the fourth launch, under a transient user unit, ran 48 minutes to completion.

**Half two — the liveness re-ask.** `background/launch_liveness.py` was written at 02:04 with nine
controls. **It was never committed.** It existed only as untracked bytes in the shared tree and
inside a `SALVAGE(auto)` commit (`589f285a6`), which is not on `main` and is not reachable from it.

So the mechanism the item asks for existed for two and a half hours in a form where **no gate, no
tick, no test run and no future seat could see it**. `git ls-files` did not list it. A clean HEAD
extract does not contain it. The next `ensure_worktree` reset would have `git clean -qfd`'d it, and
the only trace would have been an absent module — which looks exactly like a module nobody wrote.

**That is the same class of defect as the one it was built to fix.** A run whose death leaves no
record reads as a run still going; a mechanism whose landing leaves no commit reads as a mechanism
nobody built. In both cases the evidence of the thing and the thing itself were the same object, so
losing one lost both.

**What was done: it is landed here**, with its tests, unchanged except for the repair below. Not
rewritten under a new name — that is the failure this project has logged twice, where a second seat
on one Lane 0 claim rebuilds the same module because it could not see the first.

## The preregistration, graded — two of four predictions refuted

Written before the census. The two refutations are the useful ones.

| # | predicted | measured | |
|---|---|---|---|
| 1 | a prose scan for in-flight assertions returns **3–25** documents | **453 of 7,610** | ❌ REFUTED |
| 2 | the 09-07 correction is **in** the returned set | it is **in no set — the file does not exist anywhere** | ❌ REFUTED |
| 3 | most hits are honest historical narration, not live claims | of the 43 that also name a concrete launch subject, the large majority sit in `done/` and narrate the past | ✅ holds |
| 4 | exactly one value-cycle `--user` unit is active: `value-cycle-floor-current-book` | exactly that one; `value-cycle-ab-current-book` inactive, `Result=success` | ✅ holds |

**Prediction 1's refutation killed a design.** I intended a second leg: a document asserting
in-flight must carry a launch-record block, enforced as a gate. At 453 documents that leg floods,
and the only way to make it small is to tune the pattern until the number pleases — a filter fitted
to its own conclusion. It is not built, and this is why.

**Prediction 2's refutation is the finding above, arrived at from the other side.**
`SEAT_CORRECTION_THE_FIRST_RETAKE_LEFT_NO_EVIDENCE_IT_SURVIVED_ITS_OWN_LAUNCH…_2026-09-07.md` is
named by the drawn item, cited by two landed records, and listed inside `.launch_records.json` as a
document to contradict. It is **not in this worktree, not in `git log --all`, not in the shared
tree, and not in `/var/tmp/se-valuearms-20260907`.** It was written into a store nothing reads and
is gone.

So the stale claim the item was drawn to catch **cannot be caught by any scan of `docs/`, because it
was never in `docs/`**. A prose gate would have been not merely floody but aimed at empty space.
This is the strongest argument for the design that landed: the record is keyed to the **job**, held
in a committed file, and names the documents it contradicts — so it survives the disappearance of
every one of them.

## The mechanism, proven reachable before it was trusted

The prereg fixed the poison round in advance: *take the currently-live floor unit, assert it reads
IN_FLIGHT, then re-ask a fabricated unit and assert it reads UNVERIFIABLE.* Run against real
subjects, not fixtures:

| subject | verdict |
|---|---|
| `value-cycle-floor-current-book.service` (live now) | **RUNNING** |
| `a-unit-that-was-never-launched-xyz.service` | **UNKNOWN** — not DIED, not FINISHED |
| `value-cycle-ab-current-book.service` (finished 01:20) | **FINISHED** |
| probe forced to fail | **UNREADABLE** — and it settles nothing |

All four reachable from one module against the real user manager. The verdict comes from systemd,
which sits outside the cgroup that did the killing — not from a pid, which is what all three dead
launches had at every moment anyone looked.

## The vacuity gap, which is what a live mechanism looks like when nobody feeds it

`--check` at the moment it was landed printed **`PASS (no stale liveness claim)`** — and that pass
was empty. The store held one record, already settled. **The one job actually in flight on this box
was not in it**, although it was launched at 02:39, thirty-five minutes *after* the module was
written, by the same lane, whose own record names `launch_liveness --record` as the route.

A control that passes because it has no subjects is the failure mode this project has catalogued
most often, and it appeared here within the hour, in the gap between building the mechanism and
using it. The floor leg is now recorded, and `--check` re-asks it for real.

## The repair the first real use forced

`--record` had no way to say when a job actually started, so `launched_at` became the moment of
recording. Retrofitting the floor leg — launched 01:39:56Z, recorded 04:41Z — would have written a
record claiming the run had been going for zero minutes. **How long a claim has stood is exactly
what a later reader judges it by**, so a record whose age is the record's age and not the run's
understates every stale claim it will ever hold. `--launched-at` added; the floor record carries
`2026-09-08T01:39:56Z`.

**The control for it was wrong first, in the way this project keeps finding.** The first draft
called `record(launched_at=…)` directly and stayed **green** when the CLI was mutated to pass
`None` — it graded the function and was blind to the wiring, and the wiring was the only thing that
changed. Re-aimed through `main(argv)`. Both mutants now die:

| mutation | before | after |
|---|---|---|
| CLI drops the flag (`launched_at=None`) | 10 passed — survived | **1 failed** |
| `record()` ignores the argument | 1 failed | **1 failed** |

## The orphan ratchet refused the landing, and it was right

The first landing attempt was refused: *"THIS COMMIT ADDS WORK THAT NOTHING RUNS —
`background.launch_liveness`."* Freezing it as deliberately dormant was available and would have
been wrong. **Nothing ran `--check`, so a person still had to type it** — and the drawn item asks
for a contradiction that arrives *without* a person checking. A `--check` nobody runs is the same
defect one indirection along.

Wired to the deadman's switch, beside `_check_status_honesty`, which is its exact analogue: there a
document describes a daemon that is not running, here a record describes a detached run that has
since died or finished. Same cadence, same transition-keyed alarm, same report-only stance.

**It pages once per stale claim, not every cycle.** `check()` writes the verdict and the evidence
back, so the claim stops being stale the moment it is settled and the next cycle is silent. The
alarm is keyed to the settled *count* — an event — because there is no standing condition to
re-escalate.

Three controls, each mutation-proven rather than asserted:

| mutation | result |
|---|---|
| `_check_launch_liveness()` removed from `run_cycle` | **1 failed** — the daemon-loop class guard derives the call set from `run_cycle`'s own source |
| the page downgraded from `real_alarm` | **1 failed** |
| a check that raised left the alarm *cleared* | refused by the silence control — "we did not look" must not render as "nothing is wrong" |

It is also classified `NEUTRALISED_BY_DMS_ISOLATED` in the same commit that wired it, by reading
that guard's rule rather than waiting for it to fire. That is not tidiness: `check()` **writes** the
store, and settling is deliberately one-way, so twelve live mutation cycles could have permanently
marked a running job dead from inside a unit test.

## A death and a completion are not the same event, and the first wiring paged both

Caught before it ever fired, with minutes to spare: the floor leg was on its final pass when the
wiring landed, and on finishing **successfully** it would have sent the director a `real_alarm`
reading *"a launch record claimed a run was in flight and it is not"* — indistinguishable from the
page for a job that died.

Both genuinely contradict a document saying "in flight", so both are stale. But one is an incident
and the other is the good news the run was launched for, and **a channel that pages him for success
is how this project has buried its own signal before.** This is the *"before measuring a thing, say
what it is"* rule applied to an alarm: one word, `stale`, covering two populations with different
triggers and different remedies.

`check()` now returns the settled records, not just a count — the split has to exist where the
verdict is known, because a caller handed only a number is forced to choose one severity for both.
A **DIED** record pages `real_alarm`; a **FINISHED** record goes to the batched digest as
`work_done`/`routine_landing`, still naming the documents it makes wrong. The alarm key is cleared
only when no death stands.

| mutation | result |
|---|---|
| completion paged as `real_alarm` | **2 failed** |
| completion swallowed when a death is present in the same pass | **1 failed** |

The second is the partition asserted over the whole set rather than one leg at a time — a branch
handling only whichever verdict came first would pass both single-verdict controls.

## What is still owed, unchanged and not done here

1. **A shared launcher.** Still untouched, and now five bespoke shell scripts in `/var/tmp`.
   `launch_liveness` records a launch; it does not perform one. This is the one-leg fix that would
   make the cgroup mistake unrepeatable rather than merely diagnosed.
2. **Checkpointing.** The value-cycle tool writes its artefact once, at the end, so each death
   re-buys the whole run.
3. **The floor leg has not finished.** At the close of this turn it is on pass 8 of 9, `ActiveState=active`,
   ~2h05m in. Until it lands, `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH`
   must move **together** — moving either alone republishes a 7.6x-larger headline with no error bar.

## What this does not claim

Nothing about level versus selection. The split is 98.5% in one draw and `readable: false`, for
reasons two landed records already set out; this turn did not touch that question and does not
reopen it. Nor does it claim the cgroup diagnosis is proven — it is one clean observation, four
launches, one launcher change.

## Reversal

Every part is a file. Revert the commit: `background/launch_liveness.py` and its tests leave the
tree, and `.launch_records.json` returns to its one settled entry.
