**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The roster run would have been inert, because the working copy of the runner is behind the commit that carries it

**Claim id:** `run-a-three-arm-to-fill-the-declined-renewal-roster-that-now-exists-but-has-never-executed`
**Filed:** 2026-09-18 ~02:5x UTC. **Measured on:** local `HEAD` = `da9cf65ae`, `origin/main` = `a08752789`.

---

## The headline

The drawn item says the roster is *"code with no data"* and that the run is *"the only thing standing
in it"* — **"one run away"**. That is false, and the run it asks for would have produced nothing.

`tools/run_value_cycle_ab.py` **in the working tree — the copy `python3 -m tools.run_value_cycle_ab`
actually executes — does not contain the `declined_renewals` block at all.** It is one merge and one
run away, not one run away, and the merge is the part nobody has done.

## The measurements, in the order I took them

| question | how | answer |
|---|---|---|
| is `a08752789` an ancestor of local `HEAD`? | `git merge-base --is-ancestor` | **NO** |
| is it an ancestor of `origin/main`? | same | YES (`origin/main` **is** it) |
| how far apart are they? | `git rev-list --left-right --count HEAD...origin/main` | **7 ahead, 16 behind** |
| `declined_renewals` at local `HEAD`? | `git grep -c … HEAD --` | **no match** |
| `declined_renewals` on `origin/main`? | `git grep -c … origin/main --` | **5 occurrences** (`def` at :3926, wired at :4820) |
| `declined_renewals` in the **working copy**? | `grep -c` | **0** |
| what Python would actually load | `import tools.run_value_cycle_ab; m.__file__` | `/home/rich/synthetic-enterprise/tools/run_value_cycle_ab.py`, `declined_renewals present: False` |
| working copy vs `origin/main` | `git diff --stat origin/main --` | **142 insertions, 264 deletions** |
| working copy vs local `HEAD` | `git diff --stat HEAD --` | 140 insertions, 2 deletions |

**The working copy is stale and a holder at once.** It lacks the 264 lines `origin/main` has —
including the whole roster block — *while* carrying 140 lines of another lane's uncommitted work
(`floor_progress_line`, `draw_path_difference`; mtime **2026-09-18 00:40:40**, two hours before this
turn). So this file cannot simply be overwritten from `origin/main`: that would destroy live work.

## The reusable class, which is the part worth keeping

**A premise check that asks git about `origin/main` licenses a run that executes the working tree.**

The item's own draw-time premise check reported, correctly: *"all 1 commit id(s) this item cites —
`a08752789` — are ALREADY ancestors of origin/main."* It then reads that as *the work has landed, so
go and run it*. Ancestry of `origin/main` says **nothing** about what the tree on this disk will
execute. Here the two answers differ by 16 commits and the one field the whole turn is for.

This is the same shape as `a gate whose subject is HEAD cannot see that a daemon runs the
working-tree copy`, arriving through a new door: the *draw* is the thing that is blind, not the gate.
Every drawn item whose work is **"run X and read field Y"** carries an un-re-asked prediction that
the tree holds the code writing Y — and no premise check in this lane asks it.

## The declines are in no artefact on disk, so there was no cheaper route

I looked for one before concluding the run is required:

- `/var/tmp/longjob-floor-next12-20260917.log` (158MB, the run in flight): `grep -ac` for `declin`,
  `DECLIN`, `MarginDecisionUnavailable`, `value_arm_log`, `churn_support`, `ceiling_filter` — **0 for
  every one of the six.**
- `docs/reports/run_output_49e08b13b_20260918T011929Z.json` (30MB, a sim run that finished
  **01:44:54Z tonight**, newer than every artefact the pre-registration checked): a recursive key
  walk for any key containing `value_arm` or `declin` returns **nothing**. The ordinary sim run does
  not carry the log at all.

This **confirms** `PREREG_THE_DECLINED_RENEWALS_ARE_NAMEABLE_ONLY_FROM_A_LOG_NO_ARTEFACT_KEEPS`
against two artefacts it did not examine, one of which did not exist when it was written.
`company/pricing/renewal_rate_chain.py:411-420` builds the decline rows per renewal into
`value_arm_entries`; nothing persists them.

## Why I did not just fix it, and this is a judgement I am recording rather than hiding

**I did not run anything.** `next12` (PID 3819244) is still in flight — 8h35m elapsed, 8.4GB RSS at
measurement, no output file yet. The item forbids launching alongside it and I did not.

**I did not touch `tools/run_value_cycle_ab.py`.** It is the single most contested file in the tree
right now: 264 lines behind `origin/main` and holding another lane's two-hour-old uncommitted
functions. An edit there would either clobber live work or be clobbered by the merge that has to
happen anyway. The correct next move on that file is a **merge**, not an edit, and an edit by me
would make the merge harder.

**I did not attempt the merge either, and this is the call most open to challenge.** The tree is
**723 files dirty**, the index carries another lane's staged work mid-commit (`delivery_lane.py`
`MM`, `DIRECTION.yaml`, `decisions.jsonl` staged, seven staged `D` deletions), and
`background/process_run_complete.py` (PID 1043743) has had a pytest gate running for **17½ minutes**
against this working tree. A 16-commit merge started inside a rival's live gate, over an index
holding their staged deletions, is this project's most repeatedly-paid failure — recorded in
`WORKER_RESULT_BOTH_LOST_ATTEMPTS_BEGAN_INSIDE_A_RIVALS_GATE…` and
`…A_TWO_ROOMS_STAGING_COLLISION_DEADLOCKS_SURGICAL_LAND_MERGE_AND_COSTS_THREE_LANDINGS`. I judged
that a bounded invocation which cannot run the sim anyway should not spend itself losing that race.

## What is owed, in the order it must happen

The sequencing is the deliverable, because the item's own sequencing is wrong:

1. **Close the fork** — `python3 -m tools.surgical_land --merge`, once `process_run_complete`'s gate
   is clear, preserving the holder's 140 lines (`tools/isolate_hunks.py` is the instrument if the
   merge contests the file).
2. **Verify, do not assume** — `grep -c declined_renewals tools/run_value_cycle_ab.py` must be
   non-zero *in the working tree* before any run is launched. This is one command and it is the whole
   lesson of this finding.
3. **Then** run `--level-arm`, after `next12` settles.

**Prediction, written now so it can refute me:** step 2 is what fails next if it is skipped, and it
will fail silently — a run that completes and reports no roster reads exactly like a run whose arm
declined nothing.

## What this finding does NOT claim

- **It does not claim the roster block is wrong.** I read it on `origin/main` only; I did not grade
  it. `SEAT_RESULT_THE_DECLINED_RENEWALS_NOW_HAVE_A_ROSTER…` records seven controls with fired
  mutations and I take that at its word rather than re-deriving it.
- **It does not name a single customer.** "Name the customers" is **still owed**, and this turn moves
  it from *"one run away"* (false) to *"one merge and one run away"* (measured). That is a correction
  to the lane's own belief about its distance, not progress toward the answer.
- **It does not report `next12`'s mean, sem or sems-from-zero.** Part ONE remains blocked and
  unguessed.
