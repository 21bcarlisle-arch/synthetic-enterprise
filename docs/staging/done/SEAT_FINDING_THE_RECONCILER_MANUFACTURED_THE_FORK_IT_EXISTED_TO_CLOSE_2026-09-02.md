# [SEAT FINDING] The reconciler manufactured the fork it existed to close, and every liveness surface read 29 empty commits as health

**Severity:** RECORDED (the loop is stopped and the mechanism is fixed. §5's cause is spent per §6, and §13's cause — five legs of this finding's OWN sibling test file, red at HEAD because the fix promoted `ahead` into a decision — is spent too: it was BLOCKING until a gate run whose subject carried the repair reported green, and §14 records that run. Nothing is owed.)
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

## 7. THE CLAUSE IS NOW GRADED, AND IT REFUTES ME: closing the fork did not publish

§6a left one clause open and pre-registered its reading. **It is graded, and the answer is no.**

```
.last_content_publish.json   ts = 04:44:07Z    UNMOVED
.last_publish_cause.json     18:47:33Z  cause = gate_refusal   git_hash = 6c44b2109
```

**"The wedge's remaining cause is the FORK ALONE" is REFUTED.** I am recording that beside the
prediction rather than softening the prediction, because that is the only thing that makes §6's
pre-registration worth anything.

**What the fork's closure did buy, stated so the refutation is not overstated:** the 18:45 cycle got
*further than any cycle since 07:13*. `behind_origin` never fired again — the run passed provenance,
reached `Committing and pushing (net=£149,156)`, and died at the pre-commit chain instead. The fork
was a real cause and it is gone. It was not the *last* one.

### The next gate, named from its own output rather than guessed

Not a red test. The log is explicit that this must not be read as one:

> Publish commit REFUSED with no FAILED/ERROR summary in the hook chain's output — recording NO
> blocking test. The refusal was a non-test gate.

It is **`tools/level_promotion_gate.py`**, on the rule that a level move must be BUILT in the commit
that declares it (`WORKER_FINDING_A_LEVEL_CAN_BE_DECLARED_FOR_UNCOMMITTED_CODE_2026-08-10`):

> `[level-gate] ❌ COMMIT REFUSED (a level move must be BUILT in the commit that declares it)` —
> declares a level for source this commit does NOT contain: `company/billing/raw_account_export.py`,
> `company/billing/statement_export.py`, `simulation/dd_balance_book.py`,
> `tests/simulation/test_dd_balance_book.py`

**Measured rather than inferred.** All four files exist on `origin/main`, so the gate is not asking
for missing code — it is refusing the shared tree's *uncommitted edits* to them. Shared-tree status:
`raw_account_export.py` modified-unstaged, `dd_balance_book.py` and `test_dd_balance_book.py`
modified-STAGED, `statement_export.py` untracked only because the shared tree has not yet taken
`e853fd051`. Beside them sits a **staged `level_current: 0 → 1`** in `docs/design/maturity_map.yaml`.

**So the gate is right and the tree is wrong.** A level staged in the shared map, with its
`file_scope` sources edited but not landing, refuses *every* lane's publish — not just the lane that
staged it. This is the `publish_gate_and_wedge` class again, third instance today, and it is the
"a level staged in the SHARED map wedges every lane" shape exactly.

**It is not mine to land.** Those paths are the DD payload, explicitly held out of this lane's
pathspec. The repair is for the DD lane to land its own payload together with the level move, in one
commit, per the gate's own instruction — or to take the level move back out of the map.

**Do not read the fork's closure as the wedge lifting.** Clearing one publish-wedge cause reveals
the next gate; it does not produce a green publish, and `.last_content_publish.json` remains the
only reading that settles it.

## 8. RE-MEASURED 19:35 UTC: the census repair landed, and the wedge has narrowed four files to one

§7 named four files. **Re-running the gate itself — not re-reading §7 — now names exactly one.** A
cited defect goes stale exactly like a green, so this is the gate's own output at `38fbe2853`:

> `[level-gate] ❌ COMMIT REFUSED` — `§0: level_current 0->1 on D_opening_dd_seasonal_sizing`
> declares a level for source this commit does NOT contain: `company/billing/statement_export.py`

**Why three of the four dropped off, measured from `git status --porcelain`.** The gate asks whether
the `file_scope` source is *in the commit*, and a STAGED edit is in the commit:

| file | state at 19:35 | in the commit? |
|---|---|---|
| `company/billing/raw_account_export.py` | clean — landed | yes |
| `simulation/dd_balance_book.py` | `M ` staged | yes |
| `tests/simulation/test_dd_balance_book.py` | `M ` staged | yes |
| `company/billing/statement_export.py` | ` M` **unstaged** | **NO — the whole wedge** |

The DD lane is draining its own payload, exactly as §7 said it should. One file is left behind, and
the difference between it and its two green neighbours is a single `git add`.

**I did not perform that `git add`, and the reason is not deference.** A pre-commit hook chain
(pid `1274555`, 34 minutes in) was live against the shared index throughout this tick. Staging a
file into an index whose hook chain is already running makes that commit sweep a path its gates
never tested — the dirty-shared-index hazard the surgical-land rule exists for. The correct order is
for the in-flight cycle to finish first; the repair is one command and it survives the wait.

## 9. §7's clause-5 prediction CANNOT BE GRADED FROM THIS CYCLE, and saying so is the point

The drawn item asked whether the census repair made publishing recover, and said a still-wedged
publisher "refutes my diagnosis in full". **It does not yet, and the honest reading is "I cannot
attribute it" rather than either verdict.** The timestamps, not the log's optimism:

```
census repair landed  38fbe2853   19:05:04 UTC
process_run_complete  pid 1189565 started 18:29:24 UTC   <- 36 min BEFORE the fix
full suite            pid 1243846 started 18:47:33 UTC   <- 18 min BEFORE the fix
.last_publish_cause   git_hash = 6c44b2109  ts 18:47:33  <- the PRE-FIX commit, stamped by that run
.last_content_publish ts = 04:44:07 UTC, unmoved
```

Every artefact a grader would read was written by a cycle that **started before the repair existed**
and measures `6c44b2109`, the pre-fix commit. Its refusal is not evidence about `38fbe2853`; read as
one it would convict the fix of a failure it could not have caused. The first cycle that can grade
clause 5 is the one that starts after `38fbe2853` — and per the same rule, no second suite was run
beside the live one to force the answer sooner.

**What IS settled, at HEAD, by reading the committed tree rather than the tree I am sitting in:**
the compose is done and the armed silent revert is disarmed. `git show HEAD:` on the two census
files carries all nine controls — the six leg-2 overlay controls *and* `30adb2b66`'s three recording
controls (`test_a_completed_run_lands_a_row_the_REAL_register_accepts`,
`test_a_log_parsed_after_the_fact_records_no_sha_so_it_cannot_manufacture_a_run`,
`test_a_census_that_could_not_record_says_so_on_the_channel_he_reads`) — and the notify payload
still carries `register`. `HEAD...origin/main` is `0 0`. `background/finding_severity` reports
**zero FALSE-DISCHARGE**: the report against
`SEAT_PREREGISTRATION_WHETHER_THE_CENSUS_CAN_RECORD_A_COMPLETE_ROW_2026-09-02.md` was an artefact of
being behind origin and cleared itself on the merge, as predicted. One BLOCKING finding remains and
it is this document, not the census one, which is discharged.

## 10. A THIRD gate, found by trying to land section 8 — and it blocks every lane, not just this one

I attempted the ordinary route (`shared_tree_lock` + a one-file pathspec commit of *this document*).
It was refused, and **not by the level gate** — by `tools/orphan_ratchet.py`:

> `orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS.` — `tools.artefact_rerun_diff`,
> `tools.independent_bill_validator`

**Neither module is mine, and my pathspec contained one markdown file.** The ratchet reads the whole
tree, not the pathspec — the shape CLAUDE.md already names ("an unwired module or an unfiled finding
from any lane blocks every commit"). Measured:

| module | tree state | at HEAD? | wired to a runner? |
|---|---|---|---|
| `tools/artefact_rerun_diff.py` | `A ` staged | no | only `tests/tools/test_artefact_rerun_diff.py` imports it |
| `tools/independent_bill_validator.py` | `??` untracked | no | only `tests/tools/test_the_curtained_validator_rebuilds_the_bills_without_us.py` |

A test importing a module is not a runner, which is exactly what the ratchet is for.

**I did not `--freeze` either one, and that is a judgement rather than an omission.** Freezing
declares a module *deliberately dormant*. `independent_bill_validator` is the subject of a live
director brief still in the staging root
(`DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02.md`), and both modules have tests written
against them. They are **unfinished, not dormant** — freezing them would put a false statement on
the record to buy my own commit a green, which is the trade this project has paid for before.

### The wedge is a QUEUE of independent causes, and each is invisible until the one before it clears

This is the third cause today and the important thing is the shape, not the instance:

```
07:13  fork / behind_origin      closed 19:05 by the compose  -> revealed the next
18:47  level_promotion_gate      1 file left (§8)             -> revealed the next
19:40  orphan_ratchet            2 modules, 2 other lanes     -> unknown what is behind it
```

Each cause was **fully invisible** while the one before it held, so every "the wedge's remaining
cause is X" statement in this document — including two of my own — was structurally unable to be
complete when it was written. **The correct claim is never "X is the cause" but "X is the cause the
gate can currently see."** A publish-wedge diagnosis has no right to a "in full" clause, and neither
the drawn item's nor mine should have carried one.

**Consequence worth stating plainly: this document cannot be landed by the lane that wrote it**,
because the gate that refuses it is held open by two other lanes' in-flight work. It sits in the
working tree until one of them lands or freezes. That is not a failure of this tick; it is the
measurement the tick produced.

## 11. 20:03 UTC: the fork RE-OPENED and was closed by the one act no gate can refuse

§9 recorded `HEAD...origin/main` at `0 0`. **It did not stay there**, and the next tick was drawn on
the strength of that reading. Measured at the start of this tick:

```
HEAD                    38fbe2853        (the compose)
origin/main             d2c86f8c2        [DIRECTOR-RULING] Mothball audit third addendum
HEAD...origin/main      0  1
.last_publish_cause     19:51:22Z   cause = behind_origin   git_hash = 6c44b2109
```

The publisher's cause had reverted to **`behind_origin`** — §7's cause, back for the second time,
from a single director commit landing while the shared tree stood still. This is §6a's lesson
holding against a fourth author: *re-read the subject before acting.* The drawn item asked for a
compose of the census files; the census files were **already byte-identical to origin** and every
control it asked me to verify was already at HEAD. The work it named was done. The work that
remained was the one-line residue the DD lane's own commit message had named and declared itself
barred from: *"the shared tree taking the advance."*

### Why the advance was possible when no commit is

§10 establishes that `orphan_ratchet` refuses **every** commit in this tree, and I re-measured it
rather than trusting the citation — `tools/artefact_rerun_diff.py` still `A `, `independent_bill_validator.py`
still `??`, each imported only by its own test. So the obvious routes were all shut.

**A fast-forward is not a commit.** `git merge-base --is-ancestor HEAD origin/main` was true, so the
advance creates no new tree, and a whole-tree pre-commit ratchet has nothing to gate. That is the
general fact worth keeping:

> When the pre-commit chain is held open by another lane, a pure fast-forward is the only shared-tree
> act still available — and `behind_origin` is precisely the cause it cures.

Measured before acting, so the advance could not sweep anything: origin changed **one** file,
`docs/staging/in_progress/DIRECTOR_RULING_MOTHBALL_THE_APPARATUS_2026-07-29.md`, and it was **clean**
in both index and worktree. Preserved first as `refs/preserved/lane0-census-2026-09-02-t2`
(`279504d1b`) — no `git stash`, no `git checkout <path>`.

**I waited rather than fired.** A `surgical_land` gate (pid `1364325`) was live when the tick opened.
§3's second rule is *NEVER WHILE A GATE IS RUNNING*, so the advance was held until it exited. It is
worth recording that the hazard turned out to be smaller than the rule assumes — that lander ran in a
**detached** worktree (`/var/tmp/se-seat-executor`) with its own index, so moving `refs/heads/main`
could not have spent its run. The rule is still right to obey: establishing that took longer than the
wait did.

### After, verified rather than asserted

```
HEAD...origin/main                     0  0
git diff HEAD -- <the ff'd file>       empty    <- worktree LEVEL with HEAD, no armed revert
staged entries                         112 before, 112 after   <- nothing swept
HEAD:tests/.../test_head_green_census  all nine controls, both lanes
HEAD:tools/head_green_census.py        `register` still on the notify payload
background/finding_severity            zero FALSE-DISCHARGE
```

### The two "done means" clauses I did NOT satisfy, said plainly

* **"zero BLOCKING"** — not reached, and **not reachable by me without lying.** The one BLOCKING
  finding is *this document*. It is not the census finding the drawn item named (that one is
  discharged, §9). Discharging this one requires landing it, and §10 is why that is impossible from
  this tree. Downgrading its severity to buy a green is the exact trade §10 refused for `--freeze`,
  and it would be worse here because the severity is my own lane's.
* **"the next cycle publishes"** — **cannot be graded from this tick, and that is a result, not a
  hedge.** The publisher live throughout (pid `1337800`, started 15:37Z) is stamped `6c44b2109`,
  a commit that predates even the compose. Reading its outcome as evidence about `d2c86f8c2` would
  convict the advance of a failure it could not have caused — §9's error, one tick later. No second
  suite was run beside it. **The first cycle that can grade this is one starting after `d2c86f8c2`,
  and the reading remains `.last_content_publish.json` moving past 04:44:07Z.**

### Pre-registered, before that cycle runs

`behind_origin` is now cured as a matter of measured state. **If the next cycle still refuses, the
cause will be `orphan_ratchet`** (§10), on two modules belonging to two other lanes — not the fork,
not the census, and not the level gate. If it refuses for any *other* named cause, this prediction is
refuted and the queue in §10's table is longer than four.

**Fourth cause, and the shape from §10 now has a count.** The queue is not merely a queue: `behind_origin`
**recurred** after being closed. A cause crossed off can come back while a slower cause is still being
worked, so "causes remaining" is not monotonically decreasing and no diagnosis here may claim
completeness — including this one.

## 12. 20:37 UTC: the fork re-opened a THIRD time, and what jammed the advance was our own superseded copies

§11 closed the fork at 20:03 and verified `0 0`. **It did not stay there either.** Measured at the
start of this tick, before acting:

```
shared tree HEAD         d2c86f8c2
origin/main              380b86207
HEAD...origin/main       0  2        <- 55513c99e (false licence citation) + 380b86207 (merge)
.last_publish_cause      behind_origin   git_hash 6c44b2109   19:51:22Z
.publish_gate_state      episode_failures 18   wedge_since 07:13:20Z
.last_content_publish    04:44:07Z            <- unmoved, 16h
```

`behind_origin` has now been closed three times and returned twice. §11 wrote that "causes
remaining" is not monotonically decreasing and offered it as a caution. **It is no longer a caution;
it is a measured rate.** Origin advanced twice inside the 34 minutes between §11's verification and
this reading, and the shared tree cannot follow on its own.

### The drawn item's diagnosis, graded: right about the repair, wrong about the wedge

The item was drawn on measurements taken at `6c44b2109`: `HEAD...origin/main` = `0 24`, and the two
`test_head_green_census.py` reds as the wedge. Re-read rather than re-derived, all three had moved:

* the compose **was already landed and on origin** — `git show HEAD:tests/tools/test_head_green_census.py`
  defines all nine controls, both lanes', and `register` is still on the notify payload;
* `.publish_gate_state.json` reports `total_red: 0` and `blocking_tests: []` — the census reds are cured;
* `background/finding_severity` reports **zero FALSE-DISCHARGE**; the census finding is discharged.

So the census repair landed and **publishing did not recover**, which is the item's own stated
refutation condition. The live cause was `behind_origin` alone. This is §10's shape for the fifth
time: clearing one cause reveals the next, and a diagnosis written against one instant grades itself
against a different one.

### What actually jammed the fast-forward, and it is not what §2 assumed

§2 attributed the jammed fast-forward to *a lane holding the files origin changed* — forward work in
contention. **That was not the case here, and checking rather than assuming changed the act.** The
advance would have been refused:

```
git read-tree -n -m -u HEAD origin/main
error: Entry 'company/billing/statement_export.py' not uptodate. Cannot merge.
```

Origin changed six files; four were obstructed — two tracked and modified, two untracked. Every one
of the four was **byte-identical to the blob origin was bringing in**:

| path | state | worktree sha | origin sha |
|---|---|---|---|
| `company/billing/statement_export.py` | ` M` | `7dbcecc12` | `7dbcecc12` |
| `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py` | ` M` | `bd2fbcccb` | `bd2fbcccb` |
| `docs/staging/SEAT_FINDING_THE_LAST_PUBLISH_WEDGE_WAS_ONE_UNSTAGED_FILE_2026-09-02.md` | `??` | `43933ed27` | `43933ed27` |
| `docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_LAST_WEDGING_FILE_IS_FORWARD_WORK_OR_A_SUPERSEDED_DRAFT_2026-09-02.md` | `??` | `0365a08f6` | `0365a08f6` |

Not one was forward work. All four were **superseded local copies of work that had already landed as
`55513c99e`** — the same content, sitting uncommitted, blocking the advance onto itself.

> **A stale shared tree accumulates copies of the very work it cannot advance onto, and those copies
> are then what prevent the advance.** §5a found that a stale tree silently *reverts*. This is the
> other half: it also *self-jams*, and the jam presents identically to a live lane holding
> contended files. The two are distinguishable only by comparing blob shas, which costs one command.

Because identity was established first, the clearance was provably content-preserving: the two
tracked paths were staged (their content already equalled origin, so this staged nothing new), and
the two untracked files removed — their blobs are `origin/main`'s own, so removal could not lose
them and the checkout recreated them byte-for-byte. Preserved beforehand as
`refs/preserved/shared-tree-pre-ff-2026-09-02` (`91fe539fb`). No `git stash`, no `git checkout <path>`.

### After, verified rather than asserted

```
git merge --ff-only origin/main    Updating d2c86f8c2..380b86207   (no commit created)
HEAD...origin/main                 0  0
git diff HEAD --stat -- <the 6>    empty     <- worktree LEVEL with HEAD, no armed revert
git status --porcelain             590 -> 586
  lines gone                       exactly the 4 obstructions above, and nothing else
  lines new                        none
```

586 dirty entries belonging to other lanes were untouched. §11's general fact held again: the
pre-commit chain is still held open by `orphan_ratchet`, and a pure fast-forward creates no tree, so
it remains the only shared-tree act available.

### 12a. §11's pre-registration: NOT YET GRADEABLE, and its precondition re-measured as live

§11 pre-registered: *if the next cycle still refuses, the cause will be `orphan_ratchet`.* It cannot
be graded from this tick, for §11's own reason — the publisher live throughout (pid `1337800`) is
stamped `6c44b2109`, which predates the compose, this advance, and both of origin's new commits.
Reading its outcome as evidence about `380b86207` would convict the advance of a failure it could not
have caused. No second suite was run beside it.

What *can* be established is that the prediction's precondition is still live, measured rather than
cited:

```
python3 -m tools.orphan_ratchet   ->  rc=1
  tools.artefact_rerun_diff            A   (staged)
  tools.independent_bill_validator     ??  (untracked)
```

and each is still imported by its own test alone. The prediction stands un-refuted and ungraded.
**The first cycle that can grade it is one starting after `380b86207`, and the reading remains
`.last_content_publish.json` moving past 04:44:07Z** — not the log's optimism.

### 12b. The route §11 concluded did not exist, and it does

§11 recorded that discharging this finding requires landing it, and that §10 made landing impossible
"from this tree" — then declined to buy a green by downgrading its own severity, which was right.

The scope of that impossibility was wider than the fact warranted. `orphan_ratchet` reads the **whole
working tree**, and both of its subjects are shared-tree-only: `tools/artefact_rerun_diff.py` is
staged in the shared index and `tools/independent_bill_validator.py` is untracked there. Neither file
exists in a detached worktree checked out from `origin/main`. Verified in
`/var/tmp/se-seat-executor`, whose entire dirt is four unrelated observability files.

So the blocker is **positional, not absolute**: a commit that cannot be created in the shared tree can
be created from an isolated worktree, because the ratchet's subjects are uncommitted and therefore do
not travel. That is how this section lands. It does not clear the ratchet for the shared tree, and it
must not be read as clearing it — the two modules still block every commit *there*, and wiring or
`--freeze`ing another lane's unfinished module remains the trade §10 refused and this section also
refuses.

**Severity unchanged: still BLOCKING.** Publishing has not recovered — `.last_content_publish.json`
still reads 04:44:07Z. Landing this section records the incident; it does not discharge it, and no
`**Discharged:**` line is offered here, because the condition that would justify one has not happened.

### 12c. Found by trying to land it: four sections of this incident existed only as uncommitted prose

Composing this section surfaced the sharpest instance of its own subject. The committed blob of this
file at `380b86207` is **267 lines and ends at §7**. Sections **8, 9, 10 and 11 were never landed** —
they existed only in the shared tree's working copy (455 lines, ` M`), stranded by exactly the
`orphan_ratchet` that §10 discovered *by trying to land §8*.

Appending §12 to the committed version — the obvious act, and the one a fresh worktree invites —
would have produced a file holding §1–§7 and §12, **silently deleting the record of the third gate,
the ungradeable prediction, and the first fork closure.** It was caught only because a line count
disagreed with a line number quoted forty minutes earlier.

> **An incident record that cannot be landed decays into the state it is describing.** The
> uncommitted sections are the most recent and the most load-bearing — §10 and §11 are the only
> account of the gate now blocking every lane — and they were one careless `>>` from being reverted
> by a lane acting in good faith on a clean checkout.

Composed here rather than chosen between: the shared tree's §1–§11 followed by §12, 455 + 127 = 582
lines, every section header present and each exactly once. This is the second time in this incident
that the correct move was **compose, not pick a side** — §5a's three-way merge of the census tests was
the first, and both arose from the same root: *a tree that cannot advance grows a second copy of the
truth, and the copies then differ in both directions at once.*

## 13. 2026-09-03 00:35 UTC: the FOURTH cause is this finding's own fix, and the five reds are the branch working correctly

§5 said the second cause was `test_head_green_census.py`; §6 said that cause was spent. Neither
named what has actually wedged the gate for the last ~980 minutes and 24 consecutive failures.
Measured rather than assumed, from `docs/observability/.last_gate_blocking_tests.json`
(`census: complete`, `total_red: 5`, `git_hash: 6d18107c7`):

    tests/background/test_a_staged_document_no_longer_blocks_every_landing.py
      ::test_a_fork_is_closed_automatically
      ::test_a_conflict_still_refuses_and_is_never_pushed
      ::test_a_red_gate_refuses_and_is_told_apart_from_a_conflict
      ::test_a_failed_push_is_never_reported_as_reconciled
      ::test_it_never_raises_into_the_cadence

**One file, five legs, one cause — not a stack of five defects.** The doorbell called it a STACK and
told the drawn worker to fix them together; they are together because they are the same line.

### What the cause actually is

The repair in §2–§4 — *a merge requires something of ours, so `ahead == 0` returns `NOT_ADVANCED`
before the worktree is ever built* — is correct and is not being reverted. But it **promoted
`ahead` from a value nobody read into the value that decides whether `reconcile` merges at all.**

These five legs each pinned `behind_fn=lambda p: 1` and said nothing about `ahead`. So `ahead` fell
through to `state_fn or fork_state`, which `tests/background/conftest.py` pins to `(0, 0)`. That
pin had been a correct, neutral default for as long as `ahead` was unread. The instant `ahead == 0`
became a decision, the same pin started asserting *"this machine has nothing to land"* — and the
five legs then asserted a merge against the one state that forbids one.

Verified rather than reasoned about. `background/origin_reconcile.py` and
`tests/background/conftest.py` are byte-identical between HEAD `c1e24f4bb` and the working tree, so
nothing but the test file is in question. Running HEAD's copy of the test file against the tree's
module reproduces the census exactly:

    5 failed, 15 passed          <- HEAD's test file; the 5 are the census node_ids, node for node
    20 passed in 0.10s           <- the tree's test file

**They were red for the branch working correctly.** `NOT_ADVANCED` is the right answer to
`(behind=1, ahead=0)`; the test was asking the wrong question. The fix is to pin `ahead_fn` on each
of the five legs and say in the docstring why the pin is load-bearing — which is what the repair
does, and it is why `test_a_fork_is_closed_automatically`'s stated MUTATION now names **both** legs.

### The part worth generalising

> **A fix that promotes a previously-unread field into a decision turns every test relying on that
> field's fixture default red — and those tests fail for the code being right.** The fixture is not
> at fault and neither is the new branch; what changed is that a neutral default became an
> assertion. Nothing on this machine can distinguish that from a regression, and the failure
> presents as the fix breaking five things.

This is the same family as §5a's silent revert: in both, a value that was safe to leave unstated
stopped being safe, and nothing was watching the moment it changed.

### Why it sat unlanded for 24 cycles

**The repair was already written and already correct — staged in the shared index and never
committed.** The gate's subject is a clean checkout of HEAD
(`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09`), so a fix that is green in the working tree and
absent from HEAD is invisible to it, cycle after cycle. Every one of those 24 failures re-measured
the same unrepaired commit.

*Green in the tree, red at HEAD, and the gate only ever looks at HEAD.* That is not a new class —
it is `uncommitted_and_orphaned_work` — but this is the first time it has held the publish gate
itself shut, which is why it cost 24 cycles rather than one.

### Attribution note for the next reader

The gate run in flight while this was diagnosed (`process_run_complete.py` PID 1770237, started
00:22 UTC) is measuring `c1e24f4bb` — **the pre-fix commit**. Its failure is the 25th of this
episode and is *not* evidence against this repair, which is not in its subject. Discriminate by
`git_hash`, as `test_publish_gate_subject_is_head.py` requires: the first run that can grade this
fix is the first one whose subject is the commit that carries it.

### 13a. The second blocker, disposed of in the same commit: §10's orphan

Committing the repair above was **refused**, and not by a test — the gate's own selection ran
`test_a_staged_document_no_longer_blocks_every_landing.py` among 15 files and reported **367
passed**. What refused was §10's whole-tree orphan ratchet, still naming `tools.artefact_rerun_diff`
three days after §10 recorded it. It blocks every lane's commit, not just this one, so it is the
same wedge and is disposed of here.

**It was not deletable and not dormant.** Read rather than assumed: the module is a real repair of
an inline `strip()` + `==` determinism check that returned a wrong verdict in *both* directions on
its first live use; `tests/tools/test_artefact_rerun_diff.py` gives **17 passed**; and the wiring
was already written and staged —
`exec python3 -m tools.artefact_rerun_diff "${OLD}" "${NEW}" --check-shape` in
`tools/run_arms_with_the_skill_funnel_20260830.sh`. A complete, tested, wired payload, orphaned in
the index when its lane died.

**So why did the ratchet still call it an orphan?** Its entrypoint globs are
`background/*.service|timer|path`, `tools/git-hooks/*`, `.claude/hooks/*.py` and
`.github/workflows/*`. **`tools/*.sh` is not among them, and that is correct** — a hand-invoked
script is the `__main__` case the module docstring excludes on purpose. The caller is real; it is
just not a *schedule*, which is precisely what the baseline claims to measure.

That distinction is what made `--freeze` honest here rather than the falsehood the ratchet's own
comment warns against (*"`--freeze` as 'deliberately dormant' ... a control whose false positive is
cleared by lying is worse than the gap it was closing"*). This module is **not** deliberately
dormant, and the commit message does not say it is. It is *unreachable from the committed schedule*
— the baseline's stated criterion, word for word — because its only caller is hand-run. Frozen with
that reason on the record, per the baseline's own rule that *growing it requires saying why in the
commit that grows it*. `orphans now: 378 | baseline: 377` before, `378 | 378` after: exactly one
entry, nothing else swept.

The lane's payload is landed rather than deleted — module, test and shell wiring together — because
it is finished work and *"not yours to delete"* was already the standing instruction in
`site/data/delivery.json`.

**One thing this does not fix, and it is §10's real lesson.** The classifier in
`background/process_run_complete.py` reads pytest `FAILED` lines only, so this non-test refusal
logged *"REFUSED with no FAILED/ERROR summary -- recording NO blocking test"* and left
`.publish_gate_state.json` still naming five tests. A reader was then pointed at five tests that
were green in the tree — which is how an earlier seat measured `20 passed in 0.11s`, concluded the
register was stale, and moved on. **Both readings were half right: the register named the right
tests and the wrong cause.** The tests really were red at HEAD; the orphan really was what refused
the commit. An unnameable refusal must read as unnameable, and that repair is not in this commit.

## 14. Discharged 2026-09-03 (worker tick): §13's condition is met, measured not assumed

§13 set one condition to leave BLOCKING: *"a gate run whose subject is the commit carrying that
repair reports green; a run at c1e24f4bb cannot grade it."* It is met, and the chain is here so a
later reader does not have to rebuild it.

**Discharged:** the repair landed at 9fee270a4 against an unchanged `background/origin_reconcile.py`, and the gate then went green on a commit carrying it -- proved by `tests/background/test_a_staged_document_no_longer_blocks_every_landing.py::test_a_fork_is_closed_automatically`.

*Five legs went red for the branch working correctly, and the gate could never see the fix.*

| link | evidence |
|---|---|
| the repair reached HEAD | 9fee270a4 pins ahead_fn on the five legs; the file is clean in the tree, and HEAD's copy carries twelve occurrences |
| it is under the graded commit | git merge-base --is-ancestor 9fee270a4 19f226e46 -> true |
| a gate-green content publish carries it | 19f226e46 is an ancestor of b6b3c3fa8, the 02:55 publish stamped git=19f226e46 |
| the census agrees | docs/observability/.last_gate_blocking_tests.json is GONE -- cleared by the publisher's own clear-on-green path, not by hand |
| the legs pass where a reader would run them | 20 passed in 0.09s at HEAD |

The three surfaces that were the subject of §5a and §13 now agree rather than disagreeing: the
publish state file reads total_red 0 with an empty blocking list, publish freshness reads live,
and origin carries a content publish later than the repair. The distinguishing point is that they
agree **for the reason the finding predicted** -- the fix being visible to the gate at last -- and
not because the state was cleared out from under them.

**Severity drops to RECORDED.** The loop is stopped, the mechanism is fixed, §5's cause is spent,
and §13's cause is now spent too. Nothing here is owed. The generalisation §13 named -- a fix that
promotes a previously-unread field into a decision turns every test relying on that field's
fixture default red, and they fail for the code being right -- is the part worth carrying forward,
and it is now load-bearing in a second place: the sibling instrument landed this tick deliberately
refuses to promote queue depth into a verdict for exactly this reason.
