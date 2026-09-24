**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared checkout cannot advance because a producer's output living in an authored tree is invisible to the generated-path oracle — and the producer's own repair is stuck behind that same gap

Claim id: `the-shared-checkout-is-the-second-gap-between-a-landed-commit-and-a-running-daemon`.
Measured 2026-09-24, after landing `5eba17198` (which made the gap measurable —
`records/SEAT_RESULT_THE_CHECKOUT_GAP_IS_MEASURED_AND_A_RESTART_WOULD_HAVE_HIDDEN_IT_2026-09-24.md`).

## The state

`deploy_restart.checkout_drift()` on the shared tree, after the landing above:

```
{'behind': 12, 'ahead': 3, 'contains_origin': False, 'gap_paths': 32}
MISSING 12 commit(s) from origin/main (32 path(s) the daemons cannot load whatever their stamp says)
```

It is DIVERGED, so no fast-forward is possible until the tree's own 3 commits reach origin.

## Why the reconciler never closes it — two causes, both measured

**Cause 1: the refusal names producer output that nothing recognises as producer output.**

`origin_reconcile`'s `NOT_ADVANCED` refusals name 11 paths, and 9 of them are the
`docs/staging/WORKER_FINDING_REPEATING_ALARM_*.md` family — *"modified here, and origin changes it
too"*. These are rewritten every tick by `background/alarm_repetition.py`. `advance_shared_tree`
grew a fifth blocker class on 2026-09-18 for exactly this shape (`generated_output_verdicts` — *"a
PRODUCER'S OWN OUTPUT: never hash-equal because its producer rewrites it every tick"*).

**It does not reach them.** One-variable control, run against the shared tree's own copy:

```
origin_reconcile._split_generated(['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'])
  -> ([], ['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'], '')
```

Generated list **empty**; the path is classified **authored**. `docs/staging/` is an authored tree,
so a regenerated document living inside it is invisible to the oracle — and under the module's own
all-or-nothing rule one permanently unresolvable path is fatal to every other class beside it.

This repo already names the shape in the opposite direction:
`tests/tools/test_a_generated_path_in_an_authored_tree_is_still_generated.py` exists, and
`file_scope_generated_paths` carries `AUTHORED_UNDER_A_GENERATED_TREE`. The mirror case — a
GENERATED path under an AUTHORED tree — is the one live here, and it is the blocker.

**Cause 2: the gate's run lock starves the reconciler.** Over the last 40 logged cadences:

| outcome | count |
|---|---|
| `GATE_RUNNING` | **19** |
| `REFUSED_CONFLICT` | 10 |
| `NOT_ADVANCED` | 7 |
| `LEVEL` | 4 |

The reconciler stands down for the publish gate on roughly half of all cadences and never reaches
a decision window at all. The two most recent entries (04:55Z, 05:00Z) are both `GATE_RUNNING`.
This is the deadlock already in this seat's memory — the gate is slow/red partly *for being
behind*, and the thing that would fix behind stands down for the gate.

## The recursion, which is this item's whole thesis one turn deeper

`background/alarm_repetition.py` differs between the checkout and origin by **130 insertions and
375 deletions** — a substantial rework (`9640ca528`, `6ccae119e`, `22ec75803`, `465a0dfca`) sitting
on origin and absent from the box. The daemon rewriting the blocking documents is running the OLD
code, and the new code cannot reach it because those rewrites are what blocks the advance.

**A producer's output blocks the checkout that carries the producer's repair.**

## NOT established, and recorded rather than guessed

Whether the reworked `alarm_repetition.py` would actually stop rewriting those 9 documents. One of
the landed notes is titled *"the alarm document is no longer its own store **and the collision is
still there by design**"*, which reads as saying it would NOT. If so, Cause 1 is the whole remedy
and the recursion is a compounding factor rather than the mechanism. **Do not assume the restart
fixes it** — that assumption is the same shape this claim exists to refuse.

## The remedy, in the order the evidence supports

1. **Teach the generated-path oracle that `docs/staging/WORKER_FINDING_REPEATING_ALARM_*.md` is
   producer output**, so class five can clear it. This is the load-bearing step and it is the only
   one that makes the tree advanceable without a person. Note `file_scope_generated_paths` is a
   frozen-count census with membership pinned by tests — this is its own careful piece of work, not
   a one-line addition, which is why it is handed on rather than half-built here.
2. Re-measure with `deploy_restart.checkout_drift()`. It is now the honest oracle:
   `merge-base --is-ancestor`, never `reconcile-watch`'s exit code.
3. **Only then** restart the daemons. Doing it before the checkout advances clears all eleven
   `stamp-predates-process` verdicts and delivers none of the repair — see the result note.
4. Separately: `GATE_RUNNING` starving the reconciler on half of all cadences is a second,
   independent defect and wants its own measurement.

## What this turn did NOT do, deliberately

Advance the shared tree. It is diverged and its 9 blocking paths are another lane's uncommitted
producer output; clearing them by hand is the judgement `origin_reconcile` refuses to make
unattended, and this turn's isolation from the shared index is the reason it was allowed to run.
The refusal's own words: *"THE STEP IS TO LAND OR REVERT THOSE PATHS, NOT TO RE-RUN THIS MODULE."*

---

## 2026-09-24 — remedy step 1 is LANDED. Steps 2–4 are still open and this document stays live.

`GENERATED_STEMS` and `stem_written_artefacts()` are in `tools/file_scope_generated_paths.py`, folded
into `written_artefacts()` so `origin_reconcile`'s hard-coded pair of oracle names picks them up with
no change at the consumer. Measured on the real tree at the landing:

- `stem_written_artefacts()` resolves **11** paths, every one of the live
  `WORKER_FINDING_REPEATING_ALARM_*` family.
- `_split_generated()` now returns those as **generated** and leaves `SEAT_FINDING_*`,
  `PLANNER_MINTED_*` and `CLAUDE.md` **authored** — the separation the whole mechanism turns on,
  because the remedy class five applies to a generated path is REVERT.
- `gate_violations() == []` and the stem set is disjoint from `generated_artefacts()`, so the
  fail-closed `file_scope` starvation gate and its `FROZEN` census did not move.

**The premise this item was drawn on was spent by the time it was drawn, and not by this work.**
The shared tree read 0 behind / 0 ahead / 0 gap paths at `ed4092d13` — the wedge that motivated the
item had already cleared by another route. The oracle defect was still live at HEAD, so the fix is
the durable repair rather than the wedge-clearing, and that is what was landed. It was found
**built-and-unlanded in the shared working tree** (129 lines, mtime 06:51, test file untracked), so
what this turn added is the verification and one control repair, not the mechanism.

### The control repair, and it is this project's own recurring shape

Three legs of the new test file were **keyed to today's answer**: a named live member
(`..._SEAT_CLAIM_2026-09-15.md`) and a `len(...) > 1` floor. `alarm_repetition.reask(apply=True)`
writes a cleared document into `done/` and then **unlinks** the staging-root copy — so an emptying
family is the mechanism *succeeding*, and those legs would have reddened **every lane** at exactly
the moment the repair this oracle exists to unblock did its job, naming a file the offending commit
never touched. The file's own docstring claimed no leg pinned a count; two did.

Repaired to the property: the real-tree legs now quantify over whatever the family holds, and the
carve-out leg **injects** its subject so it asks about the ORDER of two set operations and nothing
else. That is not fail-open, because "is this declaration worth anything" is answered without tree
state by `test_every_declared_stem_is_REACHED_BY_ITS_PRODUCER_in_the_real_tree` — a stem whose
producer is gone or no longer spells it fails there whether the family is empty or not.

Mutation-proven rather than asserted: under the wrong order — `(scan - carve) | stems` instead of
`(scan | stems) - carve` — the injected subject is re-admitted and the leg fails. The order is the
only thing that leg can be green about.

### Still open, unchanged by this landing

Steps 2–4 above. In particular **step 4**: `GATE_RUNNING` starved the reconciler on 19 of the last
40 cadences, which this item did not cover and this landing does not touch.

---

## 2026-09-24, step 2 run — step 1 WAS load-bearing and it WORKED. The gap grew anyway because the blocker set refilled from a different class, and the door that would clear THAT class fail-closes on a sound preservation.

Step 2 is re-measurement, and it refutes the reading the draw was carrying (*"step 1 landed and the
gap grew from 12 to 20 anyway"*, which invites the conclusion that step 1 missed). It did not miss.

**Step 1 graded, one variable, on the shared tree:**

```
origin_reconcile._split_generated(['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'])
  -> (['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'], [], '')
```

Generated, where it read **authored** before. All **9** of the `WORKER_FINDING_REPEATING_ALARM_*`
paths that headed the blocking list are **gone from it**. `stem_written_artefacts()` is present at
HEAD, on `origin/main` and on disk (`ef7a8f89e`), so this is the fix running, not the fix pending.

**Step 2, `deploy_restart.checkout_drift()` on the shared tree:**

```
{'behind': 28, 'ahead': 3, 'contains_origin': False, 'gap_paths': 47}
```

Still diverged — and **for a different reason than the one this document was opened on.** Of the 13
paths now blocking the fast-forward, **8 are byte-identical twins** the reconciler's own sweeps
clear unattended (3 `identical_tracked_twins`, 5 `identical_untracked_twins`). The residue is **5**,
and all five are one event: they are byte-for-byte identical to
`refs/preserved/shared-tree-stash-pop-2026-09-24` (verified path by path with `git hash-object`),
committed 15:01:09, and every one carries mtime `15:02:31` to the fraction of a second. **One stash
pop, restored over a tree that had moved 28 commits past it, and it restamped the clock that would
have identified it as the older draft** — the subject of
`SEAT_FINDING_A_STASH_POP_RESTAMPED_321_FILES_AND_DEFEATED_THE_STALE_COPY_CLOCK_BY_38_SECONDS_2026-09-24.md`,
here as a live cause rather than a note.

### The door exists, is correctly gated, and REFUSES ON ITS OWN SOUND WORK

`refresh_to_head --base origin/main --base-wins` is the door, and `--base origin/main` is mandatory
here because HEAD is itself the stale base (against `--base HEAD` all 5 are refused, correctly).
Judged that way the tool admits two of the five as REPLACEMENT copies on the clock's word, not the
operator's. Run with `--write`, it fail-closed:

```
❌ PRESERVATION FAILED for docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md:
   `git log --all -S` does not find ed77aa59d -- the advertised recovery route does not reach it.
```

**The preservation was sound and the verification asked the wrong parent.** `preserve()` parents the
commit on **HEAD**, so the commit's own diff — which is what `-S` searches — is against HEAD. But
`_probe(verdict)` picks its search line out of `verdict.discarded`, which was computed against the
**judgement base**, `origin/main`. One variable:

```
probe = '11 of these instances are BLOCKING, so this class document is BLOCKING in `H_harness` ...'
git show HEAD:<path>        | grep -c '<probe>'   -> 1     # HEAD ALREADY HAS IT
git show origin/main:<path> | grep -c '<probe>'   -> 0
git log --all -S <probe> -- <path>  -> 89e94ec5a, 9ded3a80e   # neither is ed77aa59d
```

The line was chosen because **origin** lacks it; HEAD carries it; so across `ed77aa59d`'s own diff
the occurrence count does not change and `-S` cannot report it. The first leg — *is the stored blob
the bytes on disk* — **passed**. `git show ed77aa59d:<path>` returns the copy exactly. The bytes are
preserved and recoverable; only the advertised route's self-test is wrong.

It is base-dependent, not universal, which is why it has never been seen: for
`tests/tools/test_refresh_to_head.py` in the same run the probe line is absent from HEAD too, and
`-S` **did** find `ed77aa59d`. The all-or-nothing rule then discarded that pass along with the
failure. **So the tool's admission gate and its preservation are both right, and the one leg between
them refuses whenever the probe line happens to exist at HEAD.**

This is a control that cannot pass rather than one that cannot fail, and it is keyed to today's
answer in the same way §"the control repair" above describes: the probe is a property of the
*commit's parent*, and it is being read off the *judgement base*.

**The defect is on the TRUNK, not in this tree's stale checkout — which is the first thing a reader
of the above should doubt, because every other finding in this family turned out to be a checkout
gap.** Asked directly:

```
diff <(git show origin/main:tools/refresh_to_head.py | sed -n '/def verify_recoverable/,/^def _trivial/p') \
     <(sed -n '/def verify_recoverable/,/^def _trivial/p' tools/refresh_to_head.py)
```

`verify_recoverable` and `_probe` are **byte-identical on `origin/main` and on disk**. The only
differences in that span are additions — `_clear_index_entry`, the `staged_too` parameter and its
CLI flag — i.e. the unlanded `--staged-too` holder work, which is remedy 3's subject and not this.
So advancing the tree would **not** fix this, and a session that reads "stale checkout" here and
stops will leave the door broken on the trunk.

### The remedy, smallest first

1. **`_probe` must be computed against the preserved commit's actual parent (HEAD), not against the
   judgement base.** `verify_recoverable` already knows the commit; the discarded-line set it needs
   is `_discarded_lines(<HEAD text>, work_text)`. One call site, and the mutation that proves it is
   a probe line present at HEAD — under the current code the leg raises, under the fix it finds the
   commit. **Do not "fix" it by dropping the `-S` leg**: that leg is the only thing standing between
   this tool and `git checkout <path>` with a nicer name.
2. Then re-run the `--base origin/main --base-wins` refresh over the 5. Two are admitted outright.
3. The other three are **not** refresh subjects and must not be forced:
   `tools/refresh_to_head.py` (supplies `_clear_index_entry`, `_index_bytes`, `STAGED_DISAGREES` —
   origin supplies nothing it lacks, so it is strictly additive holder work, landable hunks 1/3/4/7)
   and `tests/background/test_publish_gate_wedge_draw.py` (landable hunk 1). The door for those is
   `isolate_hunks --survey` + `surgical_land --content`, **and then** a refresh, because `--content`
   does not write the working tree and the copy keeps blocking until it is refreshed.
4. `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` has **no
   door at all**: its only loss against origin is a landed **comment**, so `judge_copy` returns
   `refused_head_does_not_supersede_it` and every landing door would land the revert. That is
   exactly `SEAT_FINDING_NO_RULE_IN_THE_STALE_COPY_MODULE_CAN_SEE_A_COPY_WHOSE_ONLY_LOSS_IS_A_LANDED_COMMENT_2026-09-24.md`,
   and it is now load-bearing on the publish path rather than latent.

### A sixth blocker class, same shape as step 1, found while grading it

`docs/staging/reference/CLASS_*.md` is **producer output** — `background/finding_classes.py:1439`
(`_write_class_documents` → `doc.write_text(render_class_document(...))`) rewrites it, and
`--check` re-derives its membership from the filesystem. Step 1 taught the oracle about
`WORKER_FINDING_REPEATING_ALARM_*`; the register family the *same module* writes is still classified
authored, and `CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` is one of the 5 residue paths because
of it. Adding that stem is the same careful `GENERATED_STEMS` work step 1 was, and it clears one of
the five without any of the above.

### Not established, and recorded rather than guessed

Whether remedy 1 alone makes the tree advanceable. It clears at most 2 of 5 residue paths, and the
advance is all-or-nothing, so **the honest prediction is that it does not** — 3 and 4 above are
required too. Written before running it, so it can refute me.

### What this turn did NOT do

Advance the tree; `contains_origin` is still `False`. `origin_reconcile` was **already mid-merge**
(pid 2311389, `surgical_land --merge origin/main`, 11+ minutes) throughout this turn, so the ahead
leg is its work and was left to it — and it will return `NOT_ADVANCED` with `pushed: True` again,
because the 5 residue paths above are untouched. That is the 49th time, and the reason is now named
rather than repeated.

---

## 2026-09-24, step 2 re-run — THE PRE-REGISTERED PREDICTION HOLDS, and the residue is 2 rather than 5 because origin moved past three of them. One of the two is now repaired at the oracle; the other has no door and that is what `contains_origin` is still waiting on.

**The prediction is graded first, because it was written before the answer.** §"Not established" above
predicted that remedy 1 alone "clears at most 2 of 5 residue paths, and the advance is all-or-nothing,
so **the honest prediction is that it does not**" advance the tree. **Confirmed.** `contains_origin`
is still `False` at the end of this turn. It was right about the conclusion and wrong about the
arithmetic, and the arithmetic is the interesting part.

### The residue is 2, not 5, and the draw carried the stale count

Measured this turn on the shared tree, `checkout_drift()` → `{'behind': 33, 'ahead': 4,
'contains_origin': False, 'gap_paths': 55}`. `paths_blocking_fast_forward` returns **11**, and the
classes partition them completely:

| class | count | who clears it |
|---|---|---|
| `identical_tracked_twins` | 3 | the reconciler's own sweep, unattended |
| `identical_untracked_twins` | 6 | the reconciler's own sweep, unattended |
| **residue** | **2** | needs a door |

Three of the five paths this document named as residue — `site/test_the_book_is_bounded_by_compute_
reaches_the_reader.py`, `tests/background/test_harden_rung_pass_ceiling.py`,
`tests/tools/test_discovery_pass_ceiling.py` — are now **byte-identical to `origin/main`** and grade
`already_at_head` against it. They did not get fixed; **origin moved to where the copies already
were.** A residue count is a function of a base that moves, so it decays on its own, and the draw
that carried "5" and named `tools/refresh_to_head.py` (itself now identical to HEAD) was reading a
count that had aged. *This is the same shape as `feedback: a residue whose size is a function of the
remedy must be recounted after the landing, not before` — except the mover was the trunk, not a
remedy.*

### Residue path 1 — REPAIRED AT THE ORACLE, and the false verdict was pointing at a destructive door

`tests/background/test_publish_gate_wedge_draw.py` graded
`refused_supplies_names_head_lacks`: *"this copy SUPPLIES 1 name(s) origin/main does not have, so it
is ... holder work. Use `isolate_hunks --survey` and land hunk(s) 1."* The name was `prc`.

**Origin binds `prc` four times, at function scope** (lines 838/1260/1282/1314), and the copy is 49
insertions against **171 deletions** — a draft from before two landings. One variable, with a placebo:

```
symbols('def f():\n    from background import process_run_complete as prc\n    return prc\n', 'x.py')
  -> ['f']          # the function-scope import is INVISIBLE
symbols('from background import process_run_complete as prc\n', 'x.py')
  -> ['prc']        # the module-scope spelling of the same import is not
```

`stale_copy_refusal.symbols()` walked `tree.body` only. So the copy's redundant module-level spelling
of a name origin already holds read as capability origin lacked — and because `--base-wins` excludes
`SUPPLIES_NEW` by design, **the one blocker with nothing worth keeping was the one with no door at
all.** `cut_of` does not cover it either: it resolves the base's history through the same module-scope
reader, and origin's history never bound `prc` at module scope, so it honestly returned `None`.

Landed this turn: `_imports_at_any_scope()` in `tools/stale_copy_refusal.py`, folded into `symbols()`
beside `_bound_names` and `_class_members`. `_bound_names` is **not** widened — it answers *"what does
importing this module supply"*, which is `symbol_landing_check`'s question and module scope is right
for it. **Imports only, not every nested binding**, and that boundary is the safety argument: an
import's scope is placement, a local variable's existence is not, and this set licenses a door that
overwrites bytes, so widening past imports fails in the byte-destroying direction.

Mutation-proven, each leg by the mutation written for it — contributor removed reds the FUNCTION-scope
leg; filter widened to any `ast.Name` reds the IMPORTS-ONLY leg. The first leg's anti-tautology arm is
keyed to the **old reader**, not to a word from the live case.

Effect, measured after the change: that path now grades `[refreshable]` — *"supplies no name
origin/main lacks ... origin/main strictly supersedes it"*.

**The 48 lines a refresh discards were read, not waved through.** They are the redundant import plus
one banner comment block; origin carries the same argument folded into
`test_a_spent_wedge_stops_drawing_once_its_failures_age_out_of_the_window`'s docstring, which is the
later landed form. What is genuinely only in the copy is the 2026-09-06 measurement line
("three failures at 18:04/18:07/18:33Z"), about a defect since fixed and documented — and it is
recoverable from the preserved commit. That is the sign-off this tool asks its operator for and it is
recorded here rather than implied.

### Residue path 2 — NO DOOR, and this is now the only thing between the tree and `contains_origin`

`tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py`,
`refused_head_does_not_supersede_it`. Asked directly rather than taken from the earlier entry:

```
git diff --numstat origin/main -- <path>   ->  4  6
```

and filtering the diff for lines that are not `#`-comments leaves **nothing**. The entire difference
from origin, in both directions, is a comment — origin's is the newer landed one (it describes the
stub-drift repair), the copy's is the older draft. No symbol moves, no behaviour moves, and the clock
has no complaint, so every rule in the module honestly declines. That is exactly
`SEAT_FINDING_NO_RULE_IN_THE_STALE_COPY_MODULE_CAN_SEE_A_COPY_WHOSE_ONLY_LOSS_IS_A_LANDED_COMMENT_2026-09-24.md`,
and it has gone from latent to **the single remaining blocker on the publish path**. Forcing it is
`git checkout <path>` with a nicer name and is refused here for the reason the module gives.

**Pre-registered, before anyone runs it:** clearing residue path 2 is sufficient — the other 9 are
twins the sweep clears unattended and path 1 is now refreshable — so the next turn that gives that
copy a door should see `contains_origin` go `True` in the same run. If it does not, the sweep's own
all-or-nothing rule is hiding a tenth blocker and that is the finding, not the door.

### Two reds standing on the shared worktree, both established NOT mine by a placebo arm

Each was re-run with this turn's two files reverted to HEAD, and each reproduced unchanged:

1. `tests/architecture/test_a_test_module_imports_a_name_that_exists.py` dies
   `FileNotFoundError` on `tests/tools/test_the_clock_could_not_answer_was_read_as_no_complaint.py`.
   `git status` grades that path ` D` — **tracked at HEAD and on origin, deleted in the working tree
   and the deletion unstaged.** A test module red at HEAD makes its file uneditable by any lane
   (`SEAT_FINDING_A_TEST_MODULE_WITH_A_RED_AT_HEAD_IS_UNEDITABLE_BY_ANY_LANE_2026-09-24.md`), and
   this one is red for a file nobody committed a deletion of.
2. The frozen ruff census reds at `{'I001': 1305} != {'I001': 1306}` — one **below** frozen, which is
   the equality biting on an absent file rather than on new lint. Already live as
   `WORKER_FINDING_THE_RUFF_CENSUS_REDS_IN_THE_SHARED_WORKTREE_AND_IS_CLEAN_AT_HEAD_2026-09-24.md`.
   Checked and **not** caused by the ` D` path above: that file carries no `I001` at HEAD.

### What this turn did NOT do

Advance the tree. `contains_origin` is `False`, so by this item's own machine grade the direction is
**not** done, and it is handed on with the residue at 1 and that one named. Step 4 —
`GATE_RUNNING` starving the reconciler — is still untouched.

### CORRECTION, found mid-turn and it refutes this item's framing including my own pre-registration above

A concurrent lane in a linked worktree (pid 2920133, `surgical_land --content`, started 20:02) has
measured the **binding** cause, and it is not the residue at all:

```
promote_worktree_landing:  REFUSED: 13203ed91 carries no verifying surgical_land receipt,
                           so it was not gated
```

Two of the four ahead commits carry no receipt — `13203ed91` ("delivery seat: direction for the next
stretch") and `61b67fa0d` (a daemon liveness heartbeat, which is a daemon's own commit, not a seat's).
**An ungated commit anywhere in the ahead leg makes the entire leg unpromotable by construction,
permanently, however clean the working tree becomes.** The tree is DIVERGED, so no fast-forward is
possible until the ahead leg reaches origin — and the ahead leg cannot reach origin at all.

**So my pre-registration two sections up is REFUTED, and I am leaving it above rather than revising
it.** I predicted that giving residue path 2 a door would take `contains_origin` to `True` in the same
run. It would not have: resolving every residue path leaves the tree diverged with an unpromotable
ahead leg. I was measuring a real blocker on the wrong leg of an `and`. That the residue work is
*necessary* does not make it *sufficient*, and I asserted sufficiency from a count.

This also explains the recurrence honestly for the first time: 48 refusals with cause `behind_origin`
over 65.7h, and every turn that attacked the contested dirty paths was working a leg that could not
have closed it. The reconciler's own `NOT_ADVANCED ... pushed: True` was telling the truth in both
halves and nothing read the second half.

**What survives from this turn unchanged:** the `symbols()` scope repair is a defect on the trunk,
measured and mutation-proven, and it stands on its own — a false `holder work` verdict routes an
operator to `surgical_land --content`, which would land a 171-line revert's base plus a redundant
import. It is worth having whether or not it was on the critical path, and it was not.

**The next subject is the ungated ahead leg, not the residue.** The rival lane is enacting the
re-land-as-content route now; nothing should start a second copy of it.

### WHAT THE `symbols()` REPAIR WIDENS IN THE UNATTENDED PATH, asked because I nearly assumed it did not

The repair was reached through `--base-wins`, so the tempting reading is that it only changes what a
person can force. **It does not, and the honest check was to grade the path without the flag:**

```
refresh_to_head --base origin/main <path>     # no --base-wins
  -> [refreshable]  "rival copy: supplies no name origin/main lacks, and the stale-copy control
                     refuses it [strict_symbol_subset]. origin/main strictly supersedes it."
```

`origin_reconcile` calls `judge_copy(project, path, base="origin/main")` with no `base_wins`, requires
`REFRESHABLE`, and then calls `refresh(..., write=True)`. So this copy is now in the class the
reconciler **discards unattended**, where before it was refused.

That is the right population: this copy supplies nothing origin lacks *and* drops names origin has
(`strict_symbol_subset`), which is a stale rival by both rules, and auto-refreshing it is exactly what
the class exists for. The repair moved it out of a false verdict and into a correct one.

**The residual hole, stated rather than left for the reader.** A copy whose only gain is a
module-level import *and* which edits an existing function body to use it now auto-refreshes, where
the accidental `SUPPLIES_NEW` refusal used to put it in front of a person. The body edit is
recoverable from the preserved commit, but nobody is asked.

**This is not a hole the repair opened.** A copy that edits a function body and adds no import is
*already* auto-refreshed today when rule 2 complains — rule 1 has never read function bodies, and the
module says so in `_discarded_lines`' own docstring. What the repair removes is a coincidental shield
over one narrow subset, not a guard. Widening rule 1 to read function bodies is a separate and much
larger question, and it is **not established** that it should be: it would have to distinguish an edit
from a revert without a clock, which is the problem this whole module exists because of.

### THE AHEAD LEG CLOSED MID-TURN, and that makes the residue load-bearing again rather than beside the point

The rival lane's `--content` re-land succeeded while this turn was gating. Measured immediately after:

```
git rev-list --left-right --count HEAD...origin/main   ->   0   34
deploy_restart.checkout_drift()  ->  {'behind': 34, 'ahead': 0, 'contains_origin': False,
                                      'gap_paths': 46}
```

**`ahead` is 0.** The tree is no longer DIVERGED — it is purely behind, and a fast-forward is now
possible for the first time in this whole sequence. So the correction I wrote above is right about
what was binding *and* it has already been discharged, and the consequence is that the residue paths
are now the only thing left. **Both halves of the `and` were real; the other one just closed first.**

Blockers re-measured on the new base — 13, and the partition has moved:

| class | count |
|---|---|
| `identical_tracked_twins` | 3 |
| `identical_untracked_twins` | 6 |
| **residue** | **4** |

Two of those four are **this turn's own in-flight work** (`tools/stale_copy_refusal.py`,
`tests/tools/test_stale_copy_refusal.py`), dirty because the landing was still in the gate when the
count was taken. They clear when it lands and reaches origin. *A residue count taken while your own
commit is gating includes your own commit — recording it because the number is otherwise unreadable
by the next session.*

So the standing residue is **2**, and after the refresh this turn's repair licenses it is **1**:
`tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py`, whose entire
difference from origin is a comment.

**Pre-registered, replacing the prediction the correction above refuted:** with the ahead leg closed,
the twins swept and path 1 refreshed, `contains_origin` goes `True` exactly when that last
comment-only copy is resolved — and on the merits it must resolve in **origin's** favour, because
origin's comment is the later landed one describing the stub-drift repair and the working copy's is the
earlier draft. Two routes exist and only one is legal: extending the stale-copy control to see a landed
comment (the named door, and the durable fix), or committing the copy and settling it as a merge
conflict — which reaches the same place through a sanctioned resolution rather than `git checkout`, but
lands a documentation regression first. **Do not force it with `--base-wins`**: `judge` has no
complaint about that copy, so rule 2 is unsatisfied and the flag does not reach it by design.

### CLOSING STATE OF THIS TURN, by the machine and not by my having done work

`cfb5f34c4` landed ("the base spelled its import inside the function, so a pure revert was graded
holder work and had no door") and is bound to `advance-the-checkout-and-let-the-publisher-publish`.
The refresh it licensed then ran for real:

```
refresh_to_head --base origin/main --write --slug residue-path-1-wedge-draw-2026-09-24
  ✅ refreshed 1 path(s); preserved as refs/preserved/refresh-to-head/... (a6e6cef89)
  recover with: git log --all -S 'WIDENED FROM A STRING GREP TO THE AST (2026-09-17), ...'
```

The `-S` recovery leg **passed** here, so the probe defect named in the previous entry's remedy 1 is
still live on the trunk and simply did not bite on this path — its probe line is absent from HEAD too.
That remedy stays open; nothing in this turn addressed it.

Re-measured immediately after:

```
checkout_drift()  ->  {'behind': 34, 'ahead': 1, 'contains_origin': False, 'gap_paths': 46}
blockers 10  |  tracked twins 3  |  untracked twins 6  |  RESIDUE 1
  RESIDUE: tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py
```

**Residue 5 → 1 over the turn, and the pre-registration above is confirmed on its numbers:** the
twins are all sweep-clearable, path 1 is cleared, and the single remaining blocker is the comment-only
copy. `ahead: 1` is this turn's own gated commit.

### DONE was defined as `contains_origin: True`, and it is NOT met. Saying so plainly.

By the item's own machine grade this direction is **not finished**. `contains_origin` is `False`, and
it is false for exactly one path now instead of a partition nobody had separated. The publisher's next
attempt will still record `behind_origin`.

**Why I did not force the last one.** `judge` has no complaint about that copy — its whole difference
from origin is a comment — so rule 2 is unsatisfied, `--base-wins` does not reach it by construction,
and every other door lands the revert. The two legal routes are both real pieces of work:

1. **Extend the stale-copy control to see a landed comment** — the durable fix, and the subject of
   `SEAT_FINDING_NO_RULE_IN_THE_STALE_COPY_MODULE_CAN_SEE_A_COPY_WHOSE_ONLY_LOSS_IS_A_LANDED_COMMENT_2026-09-24.md`,
   which has gone from latent to **the single remaining blocker on the publish path**. It is closer
   than it looks: `_trivial(ln, comments_are_evidence=True)` already exists in the clock's own line
   selection, so the module has a notion of a comment being evidence when nothing else is. It still
   needs a rule that separates a *landed* comment from an *edited* one without a trustworthy clock —
   and the clock here is untrustworthy for a known reason
   (`SEAT_FINDING_A_STASH_POP_RESTAMPED_321_FILES_AND_DEFEATED_THE_STALE_COPY_CLOCK_BY_38_SECONDS`).
2. Commit the copy and settle it as a merge conflict in origin's favour. Mechanically available and
   legal, and it lands a documentation regression as an intermediate commit. Worse than (1) and
   recorded so the next session does not have to re-derive that it is available.

**I deliberately did not half-build (1).** A control over a byte-destroying door, built with the
context left in a bounded turn, is how this repository acquires controls that cannot fail — and this
document already carries one instance of exactly that being caught and repaired.

**Step 4 is still untouched:** `GATE_RUNNING` starving the reconciler. With the ahead leg closed and
the residue at 1, it is now the second-order subject rather than the third.
