**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# A held baseline row cannot survive a freeze, and the one placed on 2026-09-08 was gone in four commits

Found while re-measuring the premise of a drawn Lane 0 item that instructed *"delete its held row
from `docs/design/orphan_baseline.json`"*. There was no row to delete. Nobody deleted it on
purpose.

## The measurement

| commit | orphans | `epg_reconciliation_register` row | `_doc` |
|---|---|---|---|
| `2e4fa042a` — placed the hold | 408 | present | HELD paragraph, with a delete-me condition |
| `0388be7c1` | 409 | present | HELD paragraph |
| `0b3efd0a7` — *"one launcher, so a long job stops rediscovering the cgroup by dying"* | 408 | **gone** | **canned** |
| `656a45f54` (HEAD at draw) | 407 | gone | canned |

`0b3efd0a7` is a daemon-launcher commit. It has nothing to do with reachability. It re-froze the
floor as ordinary hygiene and, in doing so, silently erased a deliberate exception and the only
written record of why it existed.

## Why it could not have gone any other way

`tools/orphan_ratchet.freeze()` is four lines of data:

```python
data = {
    "_doc": "THE RATCHET FLOOR for the no-caller class. ...",   # a LITERAL
    "orphans": state["orphans"],                                # RECOMPUTED
    "entrypoint_count": len(state["entrypoints"]),
    "module_count": state["module_count"],
}
```

Both channels a hold needs are overwritten unconditionally. The list is recomputed from the tree,
so a row held **past** its computed reachability is by definition not in it; the `_doc` is a string
constant, so the reason is replaced with boilerplate. `freeze()` has no memory and no way to
acquire one. **The hold was unsurvivable from the moment it was written, and neither the commit
that placed it nor the commit that erased it could tell.**

There is no refusal, no note, no diff a reader would look twice at — the row simply is not there,
and the file reads as a normal floor. `baseline_tree_note` exists precisely to catch a floor frozen
in the wrong tree; it compares `module_count` and is blind to this, because this freeze was taken
in the right tree and is arithmetically correct. **The floor was never wrong. The exception was
just gone.**

## Why this is not being fixed here, and what would fix it

It is filed rather than patched because the hold it protected is now discharged: the docstring
prune landed in the same commit as this finding, `epg_reconciliation_register` is in the floor on
its own computed reachability, and there is no held row anywhere in the tree today. Building a
`held` channel into `freeze()` right now would be a mechanism with zero live subjects — the shape
`CLAUDE.md` names as *"a control that only guards your own controls"*.

**What to build the day a second hold is wanted**, and not before:

- A `held` list in the baseline, unioned into `orphans` at load and preserved verbatim by `freeze()`,
  each entry carrying its reason and its delete-me condition.
- The control that makes it real: `freeze()` must be proven to PRESERVE a held row. A test that
  merely checks a held row is honoured at load would pass against today's code, which drops it at
  the next freeze — the exact failure above.
- A staleness leg: a held row whose computed reachability has since disappeared is a hold that
  should have been discharged, and it should say so rather than sit there.

**The transferable lesson, which is the reason this is filed at all.** A deliberate exception
written into a file that a routine regenerates is not an exception — it is a comment awaiting
deletion. Before placing one, ask what regenerates the file and whether that routine can see the
exception. `freeze()` could not. The place the exception actually survived is
`docs/design/ORPHAN_DISPOSITION_REGISTER.md` §6, a hand-authored document nothing regenerates, and
that paragraph is what carried the work forward to this commit. The correction now sits beside it.

## Where this touches the record

- `docs/design/ORPHAN_DISPOSITION_REGISTER.md` §6 claimed *"That standing baseline row is the marker
  for this paragraph."* Corrected in place, beside the claim rather than over it.
- Related: `SEAT_FINDING_A_DOCSTRING_PATH_STOPS_BEING_AN_EDGE_AND_THE_PROSE_HOLDING_SEVENTEEN_MODULES_UP_WAS_PROSE_DENYING_THEM_2026-09-08.md`.
