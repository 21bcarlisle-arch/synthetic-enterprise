**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the battery refuses a second run over one subject, and the one leg that could not fail was deleted rather than kept green

**Built and measured 2026-09-06, delivery seat, shared tree. Claim id
`contract-battery-subject-file-lock`. Subject: `tools/contract_battery.py`. Closes the item left
open by `docs/staging/done/SEAT_FINDING_THE_BATTERYS_RESULTS_LOCK_LANDED_AND_MY_OWN_PROPOSED_DESIGN_HAD_A_FAIL_OPEN_BRANCH_IN_IT_2026-09-06.md`
("What NEITHER lane closed").**

---

## The premise was live, and one part of the stated reason was not

The item's premise check said both cited commits, `5fb3bdd99` and `fc7862de7`, were already
ancestors of `origin/main`. That is expected — they are the commits that LANDED the results-file
lock, which is this work's precondition, not its repair. Re-measured directly: `grep` over
`tools/contract_battery.py` for `flock` returns the results-file claim and nothing keyed to the
subject. **Live.**

**One clause of the item's WHY is false and is corrected here.** It says *"five live specs exist
and several share subjects"*. They do not: `grid_intensity_feed`, `direction`, `ops_repo`,
`segment_vocabulary` and `company_data` name five distinct subjects. The two-specs-for-one-subject
collision is therefore **latent**, not live.

What IS live, and is the better justification, is the results refusal's own documented escape. It
ends *"Wait for it, or pass a `--out` of your own."* Take that advice in the tree the other run is
already grading, and both runs proceed — each holding an uncontested claim on a results file nobody
is contesting — and both patch one source file in place. The advice the instrument gives is the way
to build the collision.

## What was built

`claim_the_subject_file` / `release_the_subject_file`, beside `claim_the_results_file`, and a third
refusal (**exit code 4**) in `run()` naming a third remedy: a `--out` of your own does NOT help,
because the results file is not what is being shared.

**The claim is an `flock` on the subject's own inode, not on a lock file beside it.** Two reasons,
and the first is the finding that produced this work — the design it repairs had a fail-open branch
its author did not see. A lock on a DERIVED path is open to exactly that: any future caller that
derives the name a hair differently (an unresolved symlink, a relative path, a `--subject`
override) takes an uncontested claim on a name nobody else uses and proceeds. An inode cannot be
derived wrongly. The second: tree-scoping falls out for free, since two worktrees hold two inodes
for one repo path, and per-tree is exactly the scope wanted.

The cost of that choice is that there is nowhere to write an identity record — the subject is
source. The holder is named from `/proc/locks`, which cannot disagree with the lock because it IS
the lock, and which is allowed to answer "cannot tell" (`""`) and say so on the refusal rather than
guess.

`held_through_run` still stands and still voids a row whose subject did not hold. It was never the
wrong control; it was detection after the fact, costing a whole discarded run where a refusal costs
a wait.

## Graded: poison round first, then twelve mutations

**POISON ROUND FIRST**, because "survived" means two opposite things. A raise at the top of
`claim_the_subject_file` reddens **all ten legs** — the suite reaches the subject, so a survival
later means UNPROVED and not UNREACHABLE.

Eleven of twelve mutations die at a named leg:

| | mutation | killed by |
|---|---|---|
| M1 | the claim is never taken | the refusal legs, 6 of them |
| M2 | `LOCK_SH`, which two runs can both hold | the four contested legs |
| M3 | `LOCK_NB` dropped | the four contested legs, **via their deadline** |
| M4 | the refusal is unconditional | the partition leg + 3 others |
| M5 | the refusal is never returned | the four contested legs |
| M6 | the release body emptied | the crash leg |
| M7 | the release moved out of its `finally` | the crash leg |
| M8 | the kernel lookup never names anybody | the naming leg + the lookup leg |
| M9 | the kernel lookup matches any lock row | the free-inode leg |
| M10 | the claim keyed to one path for every subject | the different-subject leg |

**M3 is worth its own line.** Dropping `LOCK_NB` does not redden a contested leg — it HANGS it, and
a hang is not a red. It died here only because every contested leg runs in a subprocess with a
deadline that turns "never returns" into a verdict. That is the second time this project has
measured that shape and the first time the guard was in place before it fired.

## The twelfth: a leg that could not fail, deleted rather than kept

M12 asked whether the subject refusal — a NEW early return from inside the block holding the
results claim — can strand that claim. **It survived, twice, and the leg was withdrawn.**

* Asked from outside, the question is unanswerable: the contested run is a subprocess, so its exit
  hands every lock back whatever the code does. The assertion was re-stating the refusal in other
  words, and it was green for that reason.
* Asked from inside the refused process, it still cannot fail: `return 4` unwinds the frame, the
  handle's refcount drops, CPython closes the descriptor and the kernel drops the `flock`.

So emptying the results release changes nothing any assertion in the new file can see. Measured,
not assumed: with `finally: release_the_results_file(handle)` emptied, the only red in either suite
is `test_two_battery_runs_cannot_share_one_results_file.py::test_a_run_that_CRASHES_still_releases_its_claim`
— the sibling's leg, and the case where that release is genuinely load-bearing.

**An equivalence, established rather than left to the reader, and the leg is gone rather than
kept.** A leg that names a property it cannot test is the exact class this instrument exists to
find. It is recorded in the suite's own docstring so the next reader does not restore it.

## A contamination effect, recorded because the red it produces points at the wrong test

Under M6 and M7 the file's later legs fail in their FIXTURE, not in their body: an earlier leg runs
the battery in process, so a broken release leaves the pytest process itself holding the subject,
and every later holder subprocess is refused by us. The first red in the file is the real one. The
fixture's assertion message now says so, because a suite whose second failure is louder than its
first sends the reader to the wrong place.

## Not closed

`--pristine` still defaults to a global `/var/tmp` path shared by two specs for one subject. The
subject claim now refuses the same-tree case before a pristine copy is written, which is the path
that mattered; the cross-tree case remains, and is write-only and never read back — a debugging
artefact, not a correctness risk. Unchanged from the finding, and still not worth a lock.
