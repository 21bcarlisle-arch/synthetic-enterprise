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

## 2026-09-24 20:25 — remedy step 2 is RUN. The answer is "step 1 was not the load-bearing step", and the ahead leg is a FLOW, not a state.

`deploy_restart.checkout_drift()` on the shared tree, measured across one turn:

| time | behind | ahead | `contains_origin` | `gap_paths` |
|---|---|---|---|---|
| 19:39 | 33 | 4 | `false` | 32 |
| **20:25** | **34** | **1** | **`false`** | **46** |

Step 1 landed, the ahead leg closed (the reconciler pushed it at 20:09 as `d8576cdca`, unaided),
and **`behind` grew and `gap_paths` grew by 14**. So the question this document's step 2 was written
to ask is answered, and the answer is the unflattering one it explicitly invited:

> **"step 1 was not the load-bearing step" — that is the answer.**

The ahead leg is not a state that can be closed. It is a **flow**: the shared tree commits every
~12–60 minutes (9 commits in the 3 hours sampled) and the reconciler batches them up afterwards, so
the leg reopens before any actor can build on its being shut. It had already reopened at 20:23
(`cfb5f34c4`) before the 20:09 push could be observed. A one-shot action against the ahead leg
cannot win, and the turn that tried is the proof.

**Step 3 must therefore NOT be run.** Restarting the daemons now would do exactly what this document
warned: clear the `stamp-predates-process` verdicts against a checkout that still lacks the repair,
and blind the detector to gap 1. The precondition it named — *"only then"* — is not met.

Two further defects found on the way and written up separately in
`SEAT_FINDING_THE_SEATS_PUSH_DOOR_REFUSES_UNGATED_ANCESTORS_AND_THE_RECONCILER_PUSHES_THEM_ANYWAY_2026-09-24.md`:

1. **The seat's push door and the reconciler's disagree about what is promotable.**
   `promote_worktree_landing` refuses any leg containing a commit with no `surgical_land` receipt;
   the reconciler pushed those same commits thirty minutes later. Work a seat is forbidden to push,
   a daemon pushes unexamined. Whether the refused commits were genuinely ungated, or merely
   committed by a route that leaves no receipt while still running the hook, is **NOT established**
   and is the cheap next measurement.
2. `promote_worktree_landing` exits **0** on that refusal.

The BEHIND leg remains this document's live subject and the publisher's actual wedge: 15 blockers,
9 of them *"modified here, and origin changes it too"*. Two are the `CLASS_` registers that step 1's
sibling (`63356067f`, now on origin) teaches the oracle to clear; the remaining set is the
`refresh_to_head` rework under `enact-the-four-path-base-wins-decision-on-the-shared-tree`. **That
claim, not this one, is where the publisher's darkness ends.**
