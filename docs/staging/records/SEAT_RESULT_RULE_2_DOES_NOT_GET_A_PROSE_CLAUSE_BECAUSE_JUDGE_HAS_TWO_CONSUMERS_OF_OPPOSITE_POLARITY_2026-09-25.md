**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — rule 2 does not get a prose clause of its own, and the reason is that `judge` has two consumers of OPPOSITE polarity

Drawn as `guard-rule-2-against-refreshing-a-copy-that-adds-prose`. The item asked: give
`stale_copy_refusal.judge`'s rule 2 (`SUBSET`) the same prose guard the `KEY_SUBSET` leg carries,
**or establish that it does not need one**. It is the second branch, and the guard the hazard
actually needed is landed here one layer up.

Left open by
`docs/staging/records/SEAT_RESULT_THE_KEY_LEVEL_TERM_ANSWERS_BOTH_DIRECTIONS_AND_THE_LOSS_HALF_IS_A_SENTENCE_NOT_A_LICENCE_2026-09-24.md`.

---

## The premise, re-measured first

The draw's own premise check said the cited commit `41681f9f5` is already an ancestor of
`origin/main` — true, and it is the DETECTION half, which was never the ask. The ask's premise is a
claim about rule 2's behaviour at HEAD, and that was measured directly rather than taken on the
item's word. On a scratch repo whose HEAD lands a helper, a working copy that **carries the
landing's distinctive lines, deletes `alpha`, adds no name and adds two comment lines**:

```
judge      -> strict_symbol_subset   (detail: ('alpha',))
judge_copy -> refreshable            <- at HEAD, the ONLY leg past `_judge_copy` is the dict-key one
```

So the item's claim is true and its hazard is real: `background.origin_reconcile.refreshable_paths`
calls `judge_copy` and acts on `REFRESHABLE` with no person in the loop, and the two comment lines
go to a `refs/preserved/*` ref nothing points at.

## What was already built, and unlanded

The general answer was **in the shared working tree and in no commit**: `tools/refresh_to_head.py`
and `tests/tools/test_refresh_to_head.py` (mtime 2026-09-25 02:26) carried a complete `PROSE_GAIN`
leg in the `judge_copy` wrapper, with `--discard-prose` as its only exit and three mutation-proven
controls. The door's own classifier graded both copies `refused_supplies_names_head_lacks` — holder
work, deleting nothing HEAD has. `PROSE_GAIN` was at neither HEAD nor `origin/main`.

That leg is the same sentence one population to the left of `WHITELIST_GAIN`, and it covers rule 1,
rule 1b, rule 2, `KEY_SUBSET` and every leg added later. It is landed by this commit.

## Why rule 2 does NOT get the clause it was asked for

`judge` has **two consumers whose polarity is opposite**, and only one of them is the hazard:

* `tools/git-hooks/pre-commit` line 57 runs `python3 -m tools.stale_copy_refusal --staged || exit 1`.
  There a Loss is a **refusal to land a revert**.
* `refresh_to_head.judge_copy` turns any Loss into **`REFRESHABLE`** — a licence to overwrite.

A prose clause inside rule 2 repairs the second by **weakening the first**: "add a comment block and
the revert gate lets you past", on the one control whose entire subject is a revert. `KEY_SUBSET`
could afford that clause because it was a new leg firing zero times, so it withdrew no refusal that
existed. Rule 2 is the old leg. One requirement implemented once, in the wrapper, is also what stops
this becoming the VAT shape: a prose clause per rule is five copies of one rule.

## The numbers, at real inputs

| Question | Measured 2026-09-25 |
|---|---|
| rule 2 fires, last 200 commits of `origin/main` (150 readable path/commit pairs) | **2** |
| …of those, the copy ALSO supplies prose — what the clause would WITHDRAW | **0** |
| rule 2 fires on today's shared tree (46 readable dirty paths) | **0** |
| `REFRESHABLE` copies on the shared tree that supply prose (the leg's live population) | 2 of 2, per the leg's own note |

So the asked-for clause would withdraw **no refusal that exists today** — it is inert where it would
be safe and a loosening in the one direction that matters whenever it does fire. That is a
measurement and not a symmetry argument, which is the only reason it is worth stating.

## What this turn added over the unlanded work

The three controls that were already written key `PROSE_GAIN` to **rule 1's** population
(`RIVAL_KIND_A` plus a comment block). The item's subject is rule 2, which had none. Two controls,
both mutation-proven:

| Control | Mutation | Result |
|---|---|---|
| `test_a_strict_symbol_subset_holding_prose_is_not_refreshable_either` | delete the `PROSE_GAIN` branch | FAILED (with 3 siblings) |
| `test_the_guard_did_not_buy_its_honesty_from_the_commit_gate` | move the guard into rule 2 — the item's own design | FAILED |

The first asserts its own population (`judge` must answer `SUBSET` on the fixture) before asserting
anything about the grade, because the sibling test reaches `PROSE_GAIN` through rule 1 and without
that leg this would be a second copy of it.

### A prediction filed before the mutation, and refuted by it

Written into the second test's docstring before it ran: *"this FIRES while the test above stays
green"*. **Refuted.** Under the rival design both fire, because a clause in rule 2 makes `judge`
silent, so the copy never reaches the grade the wrapper's leg withdraws and the leg never runs. The
wrong prediction is kept beside the answer in the docstring. What it got wrong is the point: **both
arrangements close the destroying grade**, so no test asking only `judge_copy` can separate them —
the separating leg had to be about the OTHER consumer, and that is the second control.

## The cost this carries, named rather than found later

`origin_reconcile.advance_shared_tree` is all-or-nothing, so a blocker holding prose now **refuses**
where it used to be overwritten, and the advance holds on it. That is the intended direction on a
door that destroys bytes, and the exit is `--discard-prose` — a flag on the tool a person runs, never
on the daemon's call, proven by `test_the_daemon_has_no_route_to_the_flag`.

## Suites

`tests/tools/test_refresh_to_head.py` + `tests/tools/test_stale_copy_refusal.py`: **145 passed**
(138 before this leg, 143 with it, 145 with the two controls here).

---

## ADDENDUM, a later turn on the same item, 2026-09-25 05:34

**"It is landed by this commit" was written while this note was UNTRACKED and no such commit
existed.** The code it describes sat in the shared working tree for two hours with nothing pointing
at it. It is landed now, by `ec8e19ca2` (`tools/refresh_to_head.py`, `tests/tools/test_refresh_to_head.py`;
receipt consistent, tree `7733f96cc`, gate-rc 0), and this note lands beside it. The 145-pass figure
above was re-run against the landed tree, not carried over: **145 passed**.

**The draw re-offered this item, and its PATH CHECK could not see any of the above.** The check
graded exactly ONE path — the 2026-09-24 record this item cites as its provenance — and called it
`already landed`. It never named `tools/refresh_to_head.py`, the subject, because the check resolves
path-shaped tokens out of the ITEM'S PROSE and this item's prose names where it came from rather
than what it touches. So a finished, unlanded subject is invisible to it, and the brief taken at its
word asks for a second implementation of a guard already on disk. That is filed here rather than as
a new finding document: the register carries 37 owed reds today and this is the same subject, not a
new one.
