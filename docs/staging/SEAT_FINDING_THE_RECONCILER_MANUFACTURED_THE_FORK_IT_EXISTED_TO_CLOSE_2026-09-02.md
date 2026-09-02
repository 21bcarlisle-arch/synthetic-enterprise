# [SEAT FINDING] The reconciler manufactured the fork it existed to close, and every liveness surface read 29 empty commits as health

**Severity:** BLOCKING (the loop is stopped and the mechanism is fixed; publishing is still wedged behind a second, separate cause named in §5)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02 by the director, from the commit list: *"Twelve commits in the last hour, every
one 'merge origin/main: automatic reconciliation', one every six minutes, no real work among them."*

## Class registration

`controls_that_cannot_fail` — a control that reported success 29 times on a subject it never
re-read. Also `publish_gate_and_wedge`: what it manufactured is what wedged publishing.

## 1. His reading, checked rather than taken

He asked me to check it rather than accept it. It is right in effect and wrong in mechanism, and
the difference matters for the fix.

**Right:** *"The reconcile you built to stop the behind-origin refusal is now manufacturing [a]
refusal on a loop."* Exactly so, and in the machine's own words — the gate log at 18:02:

> Provenance banner commit REFUSED before staging: origin/main is 30 commit(s) AHEAD of HEAD, so a
> commit created here could only be rejected non-fast-forward and would widen the fork by one more.

Every one of those 30 commits was written by this module.

**Wrong in mechanism:** it is not that HEAD moves faster than a gate completes. **Local HEAD never
moved at all** — it sat at `83c63ac58` from 18:30 onward. What moved was *origin*, away from a
shared tree that could not follow. The refusal produced is `behind_origin`, not HEAD-moved.

**And the count was 29, not 12** — 15:47 to 19:01, three hours and fourteen minutes, with exactly
one non-machine commit among them (his own staging push).

## 2. The mechanism, from the repository

| step | what happened |
|---|---|
| 1 | another lane held `tools/head_green_census.py` and its test **staged**, and origin had landed its own version of both (`30adb2b66`, 15:43) |
| 2 | so `git merge --ff-only origin/main` refused — correctly; git will not overwrite 554 modified files — and the shared tree stayed at its old HEAD |
| 3 | reconcile merged origin into that **stale** HEAD inside a worktree and pushed |
| 4 | origin advanced by one; the shared tree did not; the next cadence read BEHIND, one deeper |

Every merge has `p1 = 83c63ac58` and a tree **byte-identical to `p2`**:

```
== f2b773569 parents: 83c63ac58 d9704d6de
   diff vs p1:  3 files changed, 274 insertions(+), 2 deletions(-)
   diff vs p2:                                    <- empty. it changed nothing.
```

**There was no terminating condition.** Not "it looped because the cadence was too fast" — it
looped because the state it acted on was one it could never leave.

## 3. Three rules, each a branch rather than a comment

* **A MERGE REQUIRES SOMETHING OF OURS.** `ahead == 0` means nothing to contribute, so the only
  honest action is to *advance* — fast-forward, or report `NOT_ADVANCED` — and never to commit.
  This one branch prevents all 29.
* **NEVER WHILE A GATE IS RUNNING.** Moving origin under a live gate spends the run and refuses it
  at the last step.
* **RE-READ THE SUBJECT AFTER ACTING.** `RECONCILED` is claimed only when the shared tree is
  *observed* level afterwards. The old code put "shared tree NOT advanced" in a detail string
  nothing read and returned success beside it.

Mutation-proven: restoring the `ahead == 0` fall-through fails three tests; deleting the re-read
fails a fourth.

## 4. THE REASON I DID NOT SEE IT, WHICH MATTERS MORE THAN THE LOOP

Director: *"nothing asks whether a commit carries any work — so a daemon producing empty merges lit
up every liveness surface you have."* Three surfaces, and the shape is the same one three times:

* **`deadmans_switch._is_non_progress_commit`** — a **denylist of subject prefixes** (`chore(`,
  auto-process, HARDEN). The loop's subject matched none, so 29 no-op commits refreshed the
  liveness clock and the STALL alarm stayed clear through the entire outage. *A denylist is
  fail-open on the next name* — the identical argument I wrote into `raw_account_export` at 08:49
  this morning, six hours before this went unnoticed by it.
* **`delivery_seat.commits_since`** — classifies substantive **by filename**, and `git log
  --name-only` prints **no filenames at all for a merge**. So every merge scored non-substantive,
  `substantive_count` was 0, `is_material` read the stretch as EMPTY, and the seat **skipped
  orienting**. A machine committing every six minutes and a machine asleep produced the identical
  brief.
* **the gate and publish path** counted and receipted those commits without asking what was in them.

**The rule that replaces all three is structural, not lexical:**

> a commit carries work IFF its tree differs from EVERY one of its parents' trees.

No subject line, author or path is consulted, so a new class of no-op cannot be work-by-default.
`background/commit_narrative.py` implements it and renders the stretch **as a list**, because the
director saw this from a list: "29 commits, 0 substantive" was true all afternoon and reads as a
statistic; twelve identical titles in a column reads as a fault. It is wired into the seat's brief
*above* the JSON truncation, into `is_material`, and into the liveness clock.

Run against the real history it names the loop at a glance, and would have done so by 10:25.

## 5. WHAT THIS DOES **NOT** FIX, and the wedge is not all mine

Publishing is wedged on **two** causes and only one is this. The other is a genuinely red test at
HEAD:

```
FAILED tests/tools/test_head_green_census.py::test_the_recorded_head_is_the_commit_the_SUITE_RAN...
E   KeyError: 'head'
```

**Its fix is already on origin** (`30adb2b66`) and cannot reach HEAD, because the lane that wrote
it still holds those two files staged — the same condition that jammed the fast-forward in §2. So
the two causes share a root: *the shared tree cannot advance while a lane holds the files origin
changed.*

### 5a. CORRECTED AN HOUR LATER: that lane is dead, and its copy would have reverted origin

The paragraph above said *"it is live, and the correct resolution is that it lands or reverts its
own files."* **It is not live.** Checked rather than assumed, after writing it: no `claude -p`
session remains in the process table. The work was orphaned in the shared index with nothing to
land it — the `uncommitted_and_orphaned_work` class.

And it is worse than orphaned. **The lane's working copy was based on a state before its own landed
commit.** It landed `30adb2b66` to origin; the shared tree never advanced past `83c63ac58`; so it
went on editing a copy that predates its own work. Committing that working tree as-is would have
**reverted** `30adb2b66` — the recording-seam tests and the `register:` line in the census's alarm.

> **A stale shared tree does not merely block. It silently reverts.** That is the part of this
> incident with the longest reach, and nothing on this machine was watching for it.

Salvaged in `66c4e780b` by three-way merge with git's own plumbing — base the shared tree's HEAD,
ours the lane's copy, theirs origin. `tools/head_green_census.py` merged clean; the test file's one
conflict region was not a disagreement but two **disjoint** blocks of new tests appended at the same
insertion point (the lane's six overlay tests, origin's three recording tests), resolved by keeping
both, each asserted present exactly once before writing. 43 tests pass against the merged tool:
both lanes', neither reverted.

**What I have not established:** whether the publish path should hold its own view of HEAD rather
than testing a tree that other lanes can pin. That is a real question and I am not answering it
from inside an incident.

## 6. CORRECTED 18:40 UTC: §5's stated cause is spent, and the fork re-opened from the console

§5 said the wedge's second cause was *"a genuinely red test at HEAD ... its fix is already on origin
and cannot reach HEAD, because the lane that wrote it still holds those two files staged."* **Both
halves of that are now false, and neither expired the way §5 expected.**

* The two nodes are **not red** any more: `66c4e780b` composed both lanes and `49e840ec6` is
  origin/main, which defines all five controls — the lane's six overlay tests AND `30adb2b66`'s
  three recording tests — plus `_install_fake_register`, which is the actual repair.
* The lane no longer holds the files. **The director committed them himself at 18:34:35 UTC as
  `5260c6859`**, from the shared tree, onto the stale parent `83c63ac58`.

**That commit is the armed silent revert of §5a, fired — as a commit.** Checked node by node rather
than assumed: `5260c6859` contains the two wedging tests and the six overlay tests, and does **not**
contain `test_a_completed_run_lands_a_row_the_REAL_register_accepts`,
`test_a_log_parsed_after_the_fact_records_no_sha_so_it_cannot_manufacture_a_run` or
`test_a_census_that_could_not_record_says_so_on_the_channel_he_reads`. Merged naively into origin it
deletes three landed controls. **Nothing of his is lost by preferring origin**: every test node and
every function in `5260c6859` already exists at `49e840ec6`, verified by set difference in both
directions, so origin is a strict content superset and the resolution loses nothing.

### The wedge's remaining cause is the FORK ALONE, and that is a measurement, not a reading

The 18:29 refusal is `origin/main is 31 commit(s) AHEAD of HEAD`. The obvious next question is
whether the shared tree could even accept those commits, given 564 modified files. **Measured:**

```
files origin/main changes vs the shared tree's HEAD (5260c6859) :  15
of those 15, how many are locally modified in the shared tree   :   0
```

**Zero.** The shared tree is not blocked by its own dirt at all — a fast-forward would touch fifteen
files it has not edited. It is blocked *only* because `5260c6859` made it 1-ahead, and a 1-ahead
tree cannot fast-forward. So the whole wedge now rests on one commit that contributes no content.

**The act:** merge `5260c6859` into origin/main from an isolated worktree, resolving both census
files to origin's superset, so origin becomes a DESCENDANT of his commit. His authorship stays in
history, the revert is defused permanently (it can never replay), the shared tree goes 0-ahead, and
`test_when_the_tree_CAN_advance_it_advances_without_making_a_commit` is then the branch that applies
— the fixed reconciler fast-forwards it without making a commit at all.

**Pre-registered, before running it:** if that merge lands and the shared tree still does not
publish, the fork was not the remaining cause and this correction is wrong in its turn. The
falsifiable reading is `.last_content_publish.json`, whose `ts` must move past 04:44 UTC — not the
log's optimism, and not my expectation of it.

### 6a. GRADED 18:47 UTC. The diagnosis held; the act was someone else's, and I did not perform it

**I did not run that merge, and the prediction is graded on a fork closed by another route.** Said
plainly rather than quietly rewritten: between my writing §6 and reaching for the door, origin gained
three commits — `5260c6859`, then `17e40f7b7` *"merge origin/main: the census overlay work had
already been salvaged there, so ours is superseded"*, then `6cecb32ef`. The shared tree went from
1-ahead-33-behind to **1 ahead, 0 behind**. The fork is closed and my merge would now be a no-op, so
it was never made.

**What that grades, clause by clause, because a heading must not claim more than its evidence:**

* *"origin is a strict content superset, so preferring it loses nothing of his"* — **CONFIRMED, and
  it is what actually happened.** `17e40f7b7`'s own subject is that finding in the other lane's
  words. Re-checked at `6cecb32ef` node by node: all five controls, the six overlay tests,
  `_install_fake_register` and `_record_observation` are present. **The silent revert never fired.**
* *"the wedge's remaining cause is the fork alone"* — **NOT YET GRADED.** The fork is closed and
  that is necessary, not shown to be sufficient. The reading that settles it is still
  `.last_content_publish.json` moving past 04:44 UTC, and it had not moved when this was written.
* *"the act: merge it from an isolated worktree"* — **NOT PERFORMED BY ME.** Correct as a plan,
  overtaken as an act.

**The lesson is the one this finding is already about, one turn later and against its own author.**
I measured a fork at 18:37, wrote a plan against it at 18:40, and by 18:43 the subject had moved
twice. Two director commits and a lane's merge landed inside a six-minute window while I was
composing prose about them. §3's third rule — *RE-READ THE SUBJECT AFTER ACTING* — has a twin that
this near-miss exposes: **re-read the subject before acting, too.** Had I gone straight from the
measurement to `surgical_land --merge`, I would have pushed a merge of a commit that was already
merged, and widened by one the fork I had just finished proving was the whole remaining cause.

**Note for whoever grades this next:** the director has since filed the reachability half himself —
`docs/staging/done/SEAT_FINDING_THE_PUBLISH_GATE_JUDGED_A_HEAD_31_COMMITS_BEHIND_ORIGIN_AND_NOTHING_IN_THE_WEDGE_MACHINERY_READS_ORIGIN_2026-09-02.md`,
corrected in `59d70e9a1` to *"the behind-origin check exists and is unreachable, which is worse"*.
That is a different defect from this one and is not discharged here.
