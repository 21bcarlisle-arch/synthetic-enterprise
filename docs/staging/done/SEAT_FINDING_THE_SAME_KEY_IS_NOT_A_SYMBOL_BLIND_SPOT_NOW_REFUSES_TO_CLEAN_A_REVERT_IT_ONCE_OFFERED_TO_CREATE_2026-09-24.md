**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The "a whitelist key is not a symbol" blind spot has inverted: the door that once offered to DESTROY these keys now refuses to CLEAN a live revert of two others, and says "it deletes no name" about a copy that deletes two

`19f340e65` established that `refresh_to_head`'s supersession reading is blind to dict keys,
because a publication whitelist key is not a Python symbol — and the consequence recorded there was
destructive: the door graded a copy "supplies nothing" and offered to discard the only copy binding
two artefact keys. That leg is fixed; the door now refuses that copy.

**The blind spot is not fixed. It has changed sign.** The same reading, on the same file, now
refuses to clean a revert it cannot see — and states as its reason that the copy deletes nothing.

**Date:** 2026-09-24
**Claim:** `rescue-the-svt-departure-keys-the-refresh-door-nearly-discarded`
**Found from:** the interconnection check after landing `758554745` / `8b61d4b12` — *what else
assumes what just landed, and does that assumption still hold?*

---

## The measurement

`/home/rich/synthetic-enterprise` holds a dirty working copy of `saas/reporting/annual_report.py`.
Until `758554745` it was a MIXED copy: it added the two SVT whitelist keys (novel, unlanded) and
deleted the two gas-shape keys `971e3680c` landed on 2026-09-23. Landing the SVT keys spent the
novel half.

Re-graded against the new `origin/main` (`8b61d4b12`), that copy is now **purely a revert**:

```
 saas/reporting/annual_report.py | 6 insertions(+), 22 deletions(-)
```

The 6 insertions are stale comment prose my landing supersedes (a superseded `49`, and a
`covers_svt_route: false is live ... today` sentence that is no longer true). **The deletions
include the two live whitelist lines:**

```
-        "gas_shape_provider_by_customer": phase2b.get("gas_shape_provider_by_customer", {}),
-        "gas_shape_refusals": phase2b.get("gas_shape_refusals", []),
```

In code, the copy supplies **nothing** `origin/main` lacks.

## The door's verdict, and why it is untrustworthy

`python3 -m tools.refresh_to_head --root /home/rich/synthetic-enterprise --base origin/main
saas/reporting/annual_report.py` (survey only):

> `saas/reporting/annual_report.py  [refused_head_does_not_supersede_it]`
> the stale-copy control has NO complaint about this copy against origin/main: **it does not
> predate the last landing there, it deletes no name**, and it reverts no comment block that
> landing wrote. Every reading this control has was made. Refreshing it would discard an ordinary
> edit, which is `git checkout <path>` with a nicer name — and that is forbidden here for this
> exact reason.

**"It deletes no name" is false about this copy, and it is false for precisely the reason
`19f340e65` named.** The copy deletes two *dict keys*. A deleted key removes no Python binding, so
the symbol-level supersession reading sees an unchanged name set and reports no complaint. The
refusal state changed from `refused_supplies_dict_keys_the_base_lacks` to
`refused_head_does_not_supersede_it` when the base moved — a *different* refusal, from the same
blindness.

This meets the BLOCKING definition directly: **an instrument in this area is untrustworthy.** The
refusal happens to land in the safe direction — nothing is discarded — but it is safe by luck of
which side the revert sits on, not because the door can see it. The door's own sentence tells the
next reader the copy is an ordinary edit worth keeping. It is a revert of a landed repair.

## The live hazard, stated plainly

The revert is **still in the shared tree** and there is no sanctioned door that clears it:

- `refresh_to_head` refuses (above).
- `refresh_to_head --base-wins` is admitted **only** where the stale-copy control has already
  returned `predates_landing` or equivalent. It has returned no complaint, so this route is closed
  too.
- `isolate_hunks` separates hunks by AUTHOR, not by content, so it does not distinguish the revert
  from an edit.

Meanwhile **any lane that pathspec-commits `saas/reporting/annual_report.py` from the shared tree
sweeps the deletion in**, because a pathspec stages the working-tree copy. The result would be
`gas_shape_provider_by_customer` and `gas_shape_refusals` silently un-published — exactly the
defect `971e3680c` was written to fix, re-committed by a lane that never touched them and with no
control positioned to notice, because the only control over those keys grades the runner's RETURN,
not the whitelist.

This is not hypothetical: `docs/reports/run_output_latest.json` **already carries neither gas key**,
because the runs producing it executed this working tree. The un-publication is live in the artefact
today; only the code is still correct.

## What was NOT done, and why

**No write was made to the shared tree from this isolated worktree.** The survey is read-only and
was run as such. Refreshing another lane's working copy on a judgement that the door itself refuses
would be the hand-rolled version of a door that exists precisely so it is not hand-rolled, and the
copy's mtime cannot establish that no lane is mid-edit. The remedy belongs to a writer on that tree,
or to the door once it can see key deletions.

## THE PRECEDENT, AND IT IS THE STRONGEST PART OF THIS FINDING

`SEAT_FINDING_NO_RULE_IN_THE_STALE_COPY_MODULE_CAN_SEE_A_COPY_WHOSE_ONLY_LOSS_IS_A_LANDED_COMMENT_2026-09-24.md`
— filed earlier today, BLOCKING, same lane — is the **same instrument in the same refusal state**
(`refused_head_does_not_supersede_it`) saying the **same sentence** about a copy that was not an
ordinary edit. There the invisible loss was a landed comment block; here it is two dict keys.

Compare the refusal text the two findings quote, which is the whole argument:

| | quoted refusal |
|---|---|
| earlier today | "it does not predate the last landing there **and it deletes no name**." |
| this finding | "it does not predate the last landing there, **it deletes no name**, and **it reverts no comment block that landing wrote**." |

**A third reading was added between the two.** The door was taught about comment blocks — that
finding's own leg — and the clause appears in the refusal I ran. The repair worked, and it was an
instance repair: one more clause, for one more shape that had been found the hard way.

So this is the second time in one day that the same instrument has answered "no complaint" about a
copy carrying a real loss, and the fix for the first did nothing for the second. That is the
signature CLAUDE.md names — *an absurdity is fixed as a class, not an instance* — and it is also
this project's own R15 shape: **narrowing a census's read is unfalsifiable, because an empty
offender list is green either way.** Each added clause makes the refusal text longer and more
confident-sounding while the underlying reading stays an enumeration.

There are now at least three known shapes (symbol, comment block, dict key) and no reason to think
the list is closed — a string literal in a list, a decorator, a `__all__` entry and a YAML key are
all the same shape and none is a Python binding.

## The repair the door needs

The supersession reading needs a **key-level** term beside its symbol-level one, in BOTH directions,
because this blind spot has now produced a defect on each side:

- *supplies* — a copy binding a dict key the base lacks is NOT "supplies nothing" (`19f340e65`, fixed).
- *deletes* — a copy dropping a dict key the base binds DOES delete something (**this finding, open**).

One term answers both, and a fix to only the second rebuilds the first at a different address. The
narrow reading is the defect; enumerating its instances is not the repair.

## Falsifier

If `refresh_to_head`'s stale-copy control is taught to read dict-key deletions, this copy must
change state from `refused_head_does_not_supersede_it` to a complaint naming
`gas_shape_provider_by_customer` and `gas_shape_refusals`. A control that goes green while the
refusal text still reads "it deletes no name" has not fixed it.
