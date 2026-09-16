**Severity:** RECORDED · **Lane:** A_strategy_governance · **Priority:** P1 · **Proportionality:** reversible / narrow

**Knowledge:** none newly established. This is a machine finding about a control, not about the
world: the fold's arithmetic and the producer's were already meant to agree, and what was missing
was anything able to notice when they stopped.

# The control guarding the fold would have gone tautological the moment the fold ran

Lane 0's next step is to fold nine new seeds into the family the reader is served from —
`docs/observability/value_cycle_ab_s1_noise_floor.json`. The control that makes the fold's
arithmetic unable to drift from the producer's read *that same path*, and its own docstring stated
the premise it depended on: that it compares `summarise` against "a summary IT DID NOT COMPUTE".

Folding writes `summarise`'s own output to that path. From the first fold onward the assertion is
`summarise(rows) == summarise(rows)`.

## Measured, not argued

`summarise` drifted to double the sem, run against both kinds of artefact:

| subject | control catches the drift? | published sem | true sem |
|---|---|---|---|
| producer-made artefact | **yes** — red | 603.50 | 603.50 |
| folded artefact | **no** — green | **1207.00** | 603.50 |

The page would have carried a standard error twice the real one, on the one figure this project's
thesis turns on, with the guarding control green.

**The poison round did not cover this.** `test_summarise_moves_at_all_...` proves `summarise`
responds to its rows; it says nothing about whether the two sides of the comparison are
independent. A live function and an independent witness are different properties, and only the
first one was being proved.

## What changed

`tests/tools/test_fold_noise_floor_family.py` only. The witness is now selected by the property
that makes it a witness — **nobody folded it** — and never by its path: `_producer_made_floors()`
takes the newest floor artefact carrying no `folded` flag. Three legs hold it:

- the first control now **asserts its own premise** (`not live["folded"]`) rather than assuming it;
- an all-folded tree **raises** instead of skipping — "we cannot tell" is a result, and a skip there
  would be the fail-open the fix removes;
- both sides of the partition are asserted, so a selector returning nothing cannot satisfy
  "never folded" vacuously.

Mutation-proven: with the folded-guard forced false, exactly one leg goes red — the new one. The
first poison attempt removed the guard's lines and produced an `IndentationError`; a collection
error proves nothing, so it was redone as an always-false condition.

## This is an instance of a class already on the register

`SEAT_FINDING_THE_PRODUCERS_NAMED_WITNESS_AND_THE_CONTROLS_REAL_ONE_DIVERGED_WHEN_A_PROMOTION_OVERWROTE_THE_PATH_2026-09-09.md`
is live and BLOCKING in lane W2_customer_generator, and it is the same shape: **a control that
names its witness by PATH stops witnessing the moment something else writes that path.** There it
was a promotion; here it would have been a fold. Both times the control stayed green and both times
the thing it guarded was free to drift.

The fix here is the general one — select the witness by the property that makes it a witness, not
by where it happens to live — so the W2 instance should be repaired the same way rather than by
re-pointing its path. Filed as a class note, not a second document.

## Also settled, cheaply, while the run draws

- **The fold will not refuse on world.** `world_identity.digest` is `39a192ce04c1eda8` unbroken from
  2026-09-03 through today's run. Mode `all` and clock `settled-realised` match across every
  candidate member. All four refusal dimensions are clear.
- **The fold round-trips real production bytes.** Splitting the served nine into 4+5 and folding
  them back reproduces mean −1078.17, stdev 1810.50, sem 603.50, sems-from-zero 1.787 exactly.
  Before today the happy path had only ever run on fixtures — no two artefacts on disk have
  disjoint seeds in mode `all`.
- **`--level-arm` is a no-op on the floor path.** `run_value_cycle_ab` line 4811 forces
  `level_arm=True` for `--noise-floor-seeds` regardless of the flag, which is why runs launched
  without it still carry `level_advantage_gbp`. The drawn item's instruction to pass it is harmless
  but not load-bearing, and the fold needs no fifth refusal for it.

## What was actually blocking every lane's commit — and it was not HEAD

Landing this hit `[test-gate] A WALKER-INVISIBLE WALL CHANNEL HAS GROWN IN THIS COMMIT'S TREE`,
naming `generated_at -> saas/reporting/annual_report.py`. Measuring `--rev HEAD` reproduced it, and
I first read that as a pre-existing HEAD red wedging every lane. **That was wrong, and the reason it
was wrong is worth more than the refusal.**

`wall_channel_census` loads its baseline from `BASELINE_PATH` — the **working-tree file** — while
measuring the *rev* under test. So `--rev HEAD` grades HEAD's code against whatever baseline happens
to be on disk, and a dirty baseline manufactures a HEAD red that exists in no commit. The refusal
also names the wrong subject: a reader follows it to `annual_report.py:10717`, finds a line
byte-identical at HEAD, and concludes a business module changed. Nothing there moved.

**What had actually happened**: the worktree baseline dropped exactly one row —
`generated_at -> saas/reporting/annual_report.py` — plus its `F_nested_schema` pin and both prose
fields (`last_freeze`, `nested_freeze_note`). That row was hand-ruled and landed on 2026-09-09 with
a full written reason. Its own prose says: *"WHAT WAS DELIBERATELY NOT DONE: a whole-tree
`--freeze`. This worktree carries other lanes' daemon writes, and a freeze from it would bank rows
nobody ruled."* A whole-tree `--freeze` is then exactly what happened — the tell is
`frozen_at_rev: b3cb4886…`, which is a **tree** hash from `git write-tree` on a dirty index, not a
commit. It cannot be checked out and names no landing.

So the freeze banked two channel-A/B rows nobody ruled, deleted a ruled row, and replaced the
reasons with boilerplate — an amnesty in both directions at once, and the gate then blamed a
business module.

**Repaired additively in the working tree**: the ruled row, its nested pin and both prose fields
restored; the other lane's `frozen_at_rev`, `rule` and two A/B rows left untouched. Census now
exits 0 at HEAD with no new crossings. **The baseline is deliberately NOT in this commit** — the
repair returns those fields to HEAD's bytes, so there is nothing of mine to land in it, and a
pathspec would sweep that lane's unreviewed freeze into my commit. It stays theirs.

Two things still want doing and are not mine to do here: `frozen_at_rev` should name a commit, not
a write-tree hash, or provenance is unfollowable; and the census's refusal should say *which
baseline it read* and that the baseline is read from disk, because a working-tree-only cause
currently renders as a HEAD red pointing at an innocent file.

## Hand-off — the run is live, do not relaunch it

`longjob-arms-rerun-20260910b`, PID 1146711, seeds `111111…999999`, launched 2026-09-10T15:06:45Z.
Healthy at 99.9% CPU, 7 of 27 passes at 16:40Z, so **expect it about 21:00Z**. Artefact:
`docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` — absent until it finishes.

**When folding: keep a producer-made member on disk.** `..._20260909b.json` is the current witness
and `fold` never removes what it names in `folded_from`. Delete the producer-made members and the
control above now refuses rather than passing quietly — which is the point.

The pre-registration this grades against is
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_NINE_MORE_SEEDS_DO_TO_THE_SELECTION_LEGS_MEAN_AND_ITS_SIGN_2026-09-10.md`,
filed before the launch. Nothing here reads the new seeds; they do not exist yet.
