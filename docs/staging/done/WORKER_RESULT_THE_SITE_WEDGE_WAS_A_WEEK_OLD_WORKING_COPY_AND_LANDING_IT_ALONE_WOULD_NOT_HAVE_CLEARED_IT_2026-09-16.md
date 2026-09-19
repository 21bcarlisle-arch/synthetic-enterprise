**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the site lane is wedged by a one-week-old working copy of customer_events)

# The site wedge was a week-old working copy, and landing it was only half the repair — the commit does not touch the working tree that held the defect

**2026-09-16, scheduled tick, worker seat.** The drawn item's diagnosis was right in every
particular, and its done-condition could not have been reached by the route it prescribed alone.
Both halves are recorded here because the second one is the generalisable part.

## The premise, re-measured

The draw's own premise check said the one commit it cites — `9fd8ca3c3` — is already an ancestor of
`origin/main`, and asked whether the work had landed by another route. It had not. `9fd8ca3c3` is
not the fix; it is the commit whose work the stale copy was *reverting*. Measured at turn start:

    ImportError: cannot import name 'departure_decision_leg' from 'simulation.customer_events'

Live. The premise was not spent.

## What the file held

`simulation/customer_events.py`, working copy, mtime **2026-09-09T16:33** — seven days behind a
trunk that moved. Six hunks against HEAD:

| hunk | content | kept? |
|---|---|---|
| 1 | removes `from collections.abc import Container` | **dropped** — HEAD needs it for `departure_decision_leg` |
| 2 | `+ bill_scale_for,` in the import list | **KEPT** |
| 3 | deletes `_DOMESTIC_SEGMENTS` + `_bill_scale_for`, adds the alias and its five-line comment | **KEPT** |
| 4 | deletes `churn_roll_for_renewal` whole | **dropped** — reverts `9fd8ca3c3` |
| 5 | reverts `roll_lifecycle_event`'s docstring to the pre-gas-only prose | **dropped** |
| 6 | inlines the roll back over `churn_roll_for_renewal` | **dropped** |

Ten lines supplied, 126 deleted. Landing the working copy would have reverted the gas-only
departure fix that landed the same morning; refreshing it to HEAD would have destroyed a real
authored move. Neither is the answer, which is precisely what `tools.isolate_hunks` exists for.

## The pair refusal was right and its question was the wrong one

`isolate_hunks --keep 2 --keep 3` **refused**, and correctly: the isolated bytes import
`market_switching_propensity.bill_scale_for`, which existed only in an uncommitted file, so landing
that path alone reds the tree for every lane.

But `pair_refusal` asks its question against **one path at a time, against `HEAD`**. It has no
notion of "these two paths are landing in the same commit" — and neither does
`tools/landing_pair.py`, which accepts multiple paths and then grades each one independently against
`--tree`. Naming both halves does not satisfy it. There is no flag that says *the pair is the
landing*.

The honest route is not to override the refusal but to ask the question it was trying to ask:
rebuild the bytes with the same pure functions (`head_lines` / `group_opcodes` / `reconstruct`,
both reconstruction invariants asserted — all-kept reproduces the working copy, none-kept
reproduces HEAD), then hand both paths to `surgical_land`, which gates **the tree the commit would
create**. That tree has the name. The gate is the right judge; `pair_refusal` is a cheaper
approximation of it that cannot see a two-path landing.

**This is a latent hole worth naming:** the pair refusal is unreachable-by-construction for any
correct pair landing. Every legitimate use of it must route around it. That is the shape of a
control that can only be satisfied by not using the tool.

## Landed

`edded3973`, two paths, one commit, gate-rc 0, receipt verified. `simulation/customer_events.py`
via `--content` from the isolated bytes; `simulation/market_switching_propensity.py` from its
working copy, which was purely additive (+48/−0) and held nothing but the moved function.

## The half the prescribed route could not reach

`surgical_land --content` **never touches the working tree** — that is the whole point of it, and
it is documented as such. So the commit landed correct bytes into HEAD and left the defective
week-old copy sitting on disk, still wedging every lane that runs in the shared tree.

The done-condition — *`pytest site/` collects without ImportError* — is measured in the working
tree. A commit alone cannot satisfy it. This is the same shape already recorded as *a refusal
comparing HEAD to the working tree cannot be cleared by a commit alone*, arriving here from the
other direction: **the fix landing correctly is not the same event as the defect leaving the disk.**

What made the working-tree write safe was not a judgement call but a measurement. After the landing,
the remaining delta between the working copy and the new HEAD was three lines:

    +    Call only for electricity legs (`commodity == "electricity"`) at
    +    `term_index >= 1` — gas legs share the billing-account-level decision.
    +    roll = _random.Random(f"{billing_account}_{term_start_str}").random()

All three are reverts of today's commits. **Zero unlanded authored content remained**, so writing
HEAD's bytes over it discarded nothing. The pre-sync copy is kept at
`~/.cache/ce_isolate/working_copy_before_sync.py`. Had that delta contained one authored line, the
move would have been illegal and the answer a second isolation.

## Measured, before and after, in the shared working tree

| | `pytest site/ -q` | occurrences of `departure_decision_leg` |
|---|---|---|
| turn start | **35 failed, 757 passed, 37 skipped, 16 errors** | **102** |
| after landing + working-tree sync | **807 passed, 38 skipped, 0 failed, 0 errors** | **0** |

51 failures — 35 + 16, exactly the count the draw named — from one file. The site lane is not
merely unwedged; it is wholly green. `python3 -c "import simulation.run_phase2b"` imports.

## Why six days of attribution missed it

The draw explains it and the measurement confirms it: the import was **clean at HEAD the entire
time** and broken only in the shared working tree. The defect was never in any commit, so every
three-tree probe that graded HEAD against a clean extract found HEAD innocent — correctly — and
went looking elsewhere. The site lane's own refusal text says a red `site/**` test can never wedge
the `tests/` publish gate and is caught at commit instead, which is the sentence that kept pointing
attribution at the commit and away from the disk.

**The generalisable tell:** when a red is invisible to every clean-extract probe *and* the file
carrying it has an mtime older than the commits it disagrees with, the subject is the working tree,
not any tree git can name.
